"""
Lobby API endpoints.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token, get_token_from_header
from app.models.lobby import Lobby, LobbyPlayer, LobbyStatus, PlayerColor
from app.models.user import User
from app.schemas.lobby import (
    CreateLobbyRequest,
    JoinLobbyResponse,
    LobbyPlayerResponse,
    LobbyResponse,
    ReadyRequest,
    StartGameResponse,
)

router = APIRouter()


async def get_current_user(
    db: AsyncSession,
    authorization: str | None,
) -> User:
    """Get current user from token."""
    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


def get_available_color(players: list[LobbyPlayer]) -> PlayerColor:
    """Get the first available player color."""
    used_colors = {p.color for p in players}
    for color in PlayerColor:
        if color not in used_colors:
            return color
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No available colors",
    )


@router.post("", response_model=LobbyResponse, status_code=status.HTTP_201_CREATED)
async def create_lobby(
    request: CreateLobbyRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Create a new lobby."""
    user = await get_current_user(db, authorization)

    # Create lobby
    lobby = Lobby(
        name=request.name,
        host_id=user.id,
        max_players=request.max_players,
    )
    db.add(lobby)
    await db.flush()

    # Add host as first player
    host_player = LobbyPlayer(
        lobby_id=lobby.id,
        user_id=user.id,
        color=PlayerColor.BLUE,
        turn_order=0,
        is_ready=False,  # Host doesn't need to be ready
    )
    db.add(host_player)
    await db.flush()
    await db.refresh(lobby)

    # Load relationships
    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.id == lobby.id)
    )
    lobby = result.scalar_one()

    return _to_lobby_response(lobby, user.id)


@router.get("", response_model=dict)
async def list_lobbies(
    db: AsyncSession = Depends(get_db),
):
    """List all waiting lobbies."""
    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.status == LobbyStatus.WAITING)
        .order_by(Lobby.created_at.desc())
    )
    lobbies = result.scalars().all()

    return {
        "lobbies": [_to_lobby_response(lobby) for lobby in lobbies],
        "total": len(lobbies),
    }


@router.get("/{lobby_id}", response_model=LobbyResponse)
async def get_lobby(
    lobby_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get lobby by ID."""
    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.id == lobby_id)
    )
    lobby = result.scalar_one_or_none()

    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )

    return _to_lobby_response(lobby)


@router.get("/join/{invite_code}", response_model=LobbyResponse)
async def get_lobby_by_invite_code(
    invite_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Get lobby by invite code."""
    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.invite_code == invite_code.upper())
    )
    lobby = result.scalar_one_or_none()

    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code",
        )

    return _to_lobby_response(lobby)


@router.post("/{lobby_id}/join", response_model=JoinLobbyResponse)
async def join_lobby(
    lobby_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Join a lobby."""
    user = await get_current_user(db, authorization)

    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.id == lobby_id)
    )
    lobby = result.scalar_one_or_none()

    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )

    # Check if already in lobby
    for player in lobby.players:
        if player.user_id == user.id:
            return JoinLobbyResponse(
                lobby=_to_lobby_response(lobby, user.id),
                player=_to_player_response(player),
            )

    # Check lobby status
    if lobby.status != LobbyStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game already started",
        )

    # Check capacity
    if len(lobby.players) >= lobby.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lobby is full",
        )

    # Add player
    new_player = LobbyPlayer(
        lobby_id=lobby.id,
        user_id=user.id,
        color=get_available_color(lobby.players),
        turn_order=len(lobby.players),
        is_ready=False,
    )
    db.add(new_player)
    await db.flush()
    await db.refresh(lobby)

    # Reload lobby with relationships
    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.id == lobby.id)
    )
    lobby = result.scalar_one()

    # Find the new player
    for player in lobby.players:
        if player.user_id == user.id:
            return JoinLobbyResponse(
                lobby=_to_lobby_response(lobby, user.id),
                player=_to_player_response(player),
            )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to join lobby",
    )


@router.post("/{lobby_id}/ready", response_model=LobbyResponse)
async def toggle_ready(
    lobby_id: int,
    request: ReadyRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Toggle ready status."""
    user = await get_current_user(db, authorization)

    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.id == lobby_id)
    )
    lobby = result.scalar_one_or_none()

    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )

    # Find player in lobby
    player = None
    for p in lobby.players:
        if p.user_id == user.id:
            player = p
            break

    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not in this lobby",
        )

    # Host doesn't toggle ready
    if lobby.host_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Host cannot toggle ready status",
        )

    # Update ready status
    player.is_ready = request.is_ready
    await db.flush()

    # Check if all non-host players are ready
    all_ready = all(p.is_ready for p in lobby.players if p.user_id != lobby.host_id)
    if all_ready and len(lobby.players) >= 2:
        lobby.status = LobbyStatus.READY
    else:
        lobby.status = LobbyStatus.WAITING

    await db.flush()
    await db.refresh(lobby)

    return _to_lobby_response(lobby, user.id)


@router.post("/{lobby_id}/start", response_model=StartGameResponse)
async def start_game(
    lobby_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Start the game (host only)."""
    user = await get_current_user(db, authorization)

    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(LobbyPlayer.user))
        .where(Lobby.id == lobby_id)
    )
    lobby = result.scalar_one_or_none()

    if not lobby:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lobby not found",
        )

    # Check if user is host
    if lobby.host_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only host can start the game",
        )

    # Check minimum players
    if len(lobby.players) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough players",
        )

    # Check all non-host players are ready
    all_ready = all(p.is_ready for p in lobby.players if p.user_id != lobby.host_id)
    if not all_ready:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not all players are ready",
        )

    # Update lobby status (game creation will be handled in Phase 2)
    lobby.status = LobbyStatus.STARTED
    await db.flush()

    # For now, return a placeholder game_id
    return StartGameResponse(game_id=1)


def _to_player_response(player: LobbyPlayer) -> LobbyPlayerResponse:
    """Convert LobbyPlayer to response model."""
    return LobbyPlayerResponse(
        id=player.id,
        user_id=player.user_id,
        username=player.user.username if player.user else "Unknown",
        color=player.color.value,
        turn_order=player.turn_order,
        is_host=False,  # Will be set by _to_lobby_response
        is_ready=player.is_ready,
    )


def _to_lobby_response(lobby: Lobby, current_user_id: int | None = None) -> LobbyResponse:
    """Convert Lobby to response model."""
    players = []
    for p in sorted(lobby.players, key=lambda x: x.turn_order):
        player_response = _to_player_response(p)
        player_response.is_host = p.user_id == lobby.host_id
        players.append(player_response)

    return LobbyResponse(
        id=lobby.id,
        name=lobby.name,
        host_id=lobby.host_id,
        invite_code=lobby.invite_code,
        status=lobby.status.value,
        max_players=lobby.max_players,
        players=players,
        created_at=lobby.created_at.isoformat(),
    )
