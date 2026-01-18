"""
Game API endpoints.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token, get_token_from_header
from app.models.game import Game, GameStatus
from app.models.lobby import Lobby, LobbyStatus
from app.models.user import User
from app.schemas.game import (
    GameActionRequest,
    GameState,
    ActionType,
)
from app.services.game_service import GameService

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


@router.post("/from-lobby/{lobby_id}", status_code=status.HTTP_201_CREATED)
async def create_game_from_lobby(
    lobby_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Create a new game from a lobby (host only)."""
    user = await get_current_user(db, authorization)

    # Get lobby with players
    result = await db.execute(
        select(Lobby)
        .options(selectinload(Lobby.players).selectinload(lambda p: p.user))
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
            detail="Only host can create game",
        )

    # Check lobby status
    if lobby.status != LobbyStatus.STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lobby must be in STARTED status",
        )

    # Check if game already exists
    existing_game = await GameService.get_game_by_lobby(db, lobby_id)
    if existing_game:
        return GameService.to_game_state_response(existing_game)

    # Create game
    game = await GameService.create_game(db, lobby)
    await db.commit()

    return GameService.to_game_state_response(game)


@router.get("/{game_id}")
async def get_game(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Get game state."""
    await get_current_user(db, authorization)

    game = await GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    return GameService.to_game_state_response(game)


@router.post("/{game_id}/action")
async def perform_action(
    game_id: int,
    request: GameActionRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Perform a game action."""
    user = await get_current_user(db, authorization)

    game = await GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    # Check game is in progress
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not in progress",
        )

    # Find player in game
    player = None
    for p in game.players:
        if p["user_id"] == user.id:
            player = p
            break

    if not player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in this game",
        )

    # Process action based on type
    try:
        if request.action_type == ActionType.PLACE_WORKER:
            payload = request.payload
            result = await GameService.place_worker(
                db,
                game,
                player["id"],
                payload.worker_type.value,
                payload.target_position.model_dump(),
                payload.slot_index,
            )
        elif request.action_type == ActionType.END_TURN:
            result = await GameService.end_turn(db, game, player["id"])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Action type {request.action_type} not yet implemented",
            )

        await db.commit()

        return {
            "success": True,
            "action_result": result,
            "new_state": GameService.to_game_state_response(game),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{game_id}/valid-actions")
async def get_valid_actions(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Get list of valid actions for current player."""
    user = await get_current_user(db, authorization)

    game = await GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    # Find player in game
    player = None
    for p in game.players:
        if p["user_id"] == user.id:
            player = p
            break

    if not player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in this game",
        )

    # Check if it's player's turn
    if game.current_turn_player_id != player["id"]:
        return {"valid_actions": [], "message": "Not your turn"}

    valid_actions = []

    # Check worker placement options
    from app.services.worker_service import PlayerWorkers, WorkerType

    workers = PlayerWorkers.from_dict(player["workers"])

    # Apprentice placement
    if workers.apprentices.available > 0:
        valid_actions.append({
            "action_type": "place_worker",
            "worker_type": "apprentice",
            "available_slots": _get_available_worker_slots(game, "apprentice"),
        })

    # Official placement
    if workers.officials.available > 0:
        valid_actions.append({
            "action_type": "place_worker",
            "worker_type": "official",
            "available_slots": _get_available_worker_slots(game, "official"),
        })

    # End turn is always valid
    valid_actions.append({"action_type": "end_turn"})

    return {"valid_actions": valid_actions}


def _get_available_worker_slots(game: Game, worker_type: str) -> list[dict]:
    """Get available slots for worker placement."""
    from app.services.worker_service import WorkerService, WorkerType, PlacedWorker

    w_type = WorkerType(worker_type)
    available_slots = []

    board = game.board
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            if cell["terrain"] == "mountain":
                continue
            if cell["tile"] is None:
                continue

            tile = cell["tile"]
            placed_workers = [
                PlacedWorker.from_dict(w)
                for w in tile.get("placed_workers", [])
            ]

            max_slots = 2 if worker_type == "apprentice" else 1
            for slot_idx in range(max_slots):
                if WorkerService.can_place_on_tile(placed_workers, w_type, slot_idx):
                    available_slots.append({
                        "position": {"row": row_idx, "col": col_idx},
                        "slot_index": slot_idx,
                    })

    return available_slots


@router.get("/{game_id}/result")
async def get_game_result(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Get game result (only for finished games)."""
    await get_current_user(db, authorization)

    game = await GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    if game.status != GameStatus.FINISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not finished",
        )

    # Calculate final scores
    players = game.players
    rankings = []

    for player in players:
        from app.services.resource_service import Resources, ResourceService

        resources = Resources.from_dict(player["resources"])
        resource_score = ResourceService.calculate_resource_score(resources)

        score_breakdown = {
            "building_points": player.get("score", 0),
            "fengshui_bonus": 0,
            "adjacency_bonus": 0,
            "blueprint_bonus": 0,
            "remaining_resources": resource_score,
            "total": player.get("score", 0) + resource_score,
        }

        rankings.append({
            "player_id": player["id"],
            "username": player["username"],
            "score_breakdown": score_breakdown,
        })

    # Sort by total score
    rankings.sort(key=lambda x: x["score_breakdown"]["total"], reverse=True)

    # Add ranks
    for i, ranking in enumerate(rankings):
        ranking["rank"] = i + 1

    winner = rankings[0] if rankings else None

    return {
        "game_id": game.id,
        "winner_id": winner["player_id"] if winner else None,
        "rankings": rankings,
        "duration_minutes": 0,  # TODO: Calculate from timestamps
        "total_rounds": game.total_rounds,
    }
