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
from app.websocket.game_manager import game_manager, GameMessage, MessageType

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
    from app.models.lobby import LobbyPlayer
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
        elif request.action_type == ActionType.PLACE_TILE:
            payload = request.payload
            result = await GameService.place_tile(
                db,
                game,
                player["id"],
                payload.tile_id,
                payload.position.model_dump(),
            )
        elif request.action_type == ActionType.SELECT_BLUEPRINT:
            payload = request.payload
            result = await GameService.select_blueprint(
                db,
                game,
                player["id"],
                payload.blueprint_id,
            )
        elif request.action_type == ActionType.END_TURN:
            result = await GameService.end_turn(db, game, player["id"])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Action type {request.action_type} not yet implemented",
            )

        await db.commit()

        # Broadcast game state update to all players via WebSocket
        new_state = GameService.to_game_state_response(game)
        await game_manager.broadcast_to_game(
            game_id,
            GameMessage(
                type=MessageType.GAME_STATE_UPDATE,
                data={"game_state": new_state}
            )
        )

        # If turn changed, notify new current player
        if game.current_turn_player_id != player["id"]:
            await game_manager.send_to_player(
                game_id,
                game.current_turn_player_id,
                GameMessage(
                    type=MessageType.YOUR_TURN,
                    data={"message": "It's your turn!", "round": game.current_round}
                )
            )

        # If game ended, broadcast game ended message
        if game.status == GameStatus.FINISHED:
            final_scores = GameService.calculate_final_scores(game)
            winner = final_scores[0] if final_scores else None
            await game_manager.broadcast_to_game(
                game_id,
                GameMessage(
                    type=MessageType.GAME_ENDED,
                    data={
                        "winner_id": winner["player_id"] if winner else None,
                        "winner_name": winner["username"] if winner else None,
                        "rankings": final_scores
                    }
                )
            )

        return {
            "success": True,
            "action_result": result,
            "new_state": new_state,
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
    from app.services.tile_service import TileService
    from app.services.resource_service import Resources

    workers = PlayerWorkers.from_dict(player["workers"])
    resources = Resources.from_dict(player["resources"])

    # Tile placement options
    available_tiles = game.available_tiles[:3] if game.available_tiles else []
    affordable_tiles = []
    for tile_id in available_tiles:
        if TileService.can_afford_tile(resources, tile_id):
            tile_def = TileService.get_tile_definition(tile_id)
            affordable_tiles.append({
                "tile_id": tile_id,
                "name_ko": tile_def.name_ko if tile_def else tile_id,
                "cost": tile_def.cost.to_dict() if tile_def else {},
                "base_points": tile_def.base_points if tile_def else 0,
            })

    if affordable_tiles:
        valid_actions.append({
            "action_type": "place_tile",
            "available_tiles": affordable_tiles,
            "valid_positions": _get_valid_tile_positions(game),
        })

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

    # Blueprint selection (if player has dealt blueprints to select from)
    dealt_blueprints = player.get("dealt_blueprints", [])
    if dealt_blueprints:
        from app.services.blueprint_service import BlueprintService
        blueprint_options = []
        for bp_id in dealt_blueprints:
            bp = BlueprintService.get_blueprint(bp_id)
            if bp:
                blueprint_options.append({
                    "blueprint_id": bp_id,
                    "name_ko": bp.name_ko,
                    "description_ko": bp.description_ko,
                    "bonus_points": bp.bonus_points,
                    "category": bp.category.value,
                })
        if blueprint_options:
            valid_actions.append({
                "action_type": "select_blueprint",
                "available_blueprints": blueprint_options,
            })

    # End turn is always valid
    valid_actions.append({"action_type": "end_turn"})

    return {"valid_actions": valid_actions}


def _get_valid_tile_positions(game: Game) -> list[dict]:
    """Get valid positions for tile placement."""
    valid_positions = []
    board = game.board

    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            # Skip mountains and occupied cells
            if cell["terrain"] == "mountain":
                continue
            if cell["tile"] is not None:
                continue
            valid_positions.append({"row": row_idx, "col": col_idx})

    return valid_positions


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


@router.get("/{game_id}/blueprints")
async def get_player_blueprints(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Get player's blueprint cards (dealt and selected)."""
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

    from app.services.blueprint_service import BlueprintService

    # Get dealt blueprints (not yet selected)
    dealt = []
    for bp_id in player.get("dealt_blueprints", []):
        bp = BlueprintService.get_blueprint(bp_id)
        if bp:
            dealt.append(bp.to_dict())

    # Get selected blueprints
    selected = []
    for bp_id in player.get("blueprints", []):
        bp = BlueprintService.get_blueprint(bp_id)
        if bp:
            bp_dict = bp.to_dict()
            # Calculate current progress for this blueprint
            current_score = BlueprintService.evaluate_blueprint(bp_id, game.board, player)
            bp_dict["current_score"] = current_score
            bp_dict["is_completed"] = current_score > 0
            selected.append(bp_dict)

    return {
        "dealt_blueprints": dealt,
        "selected_blueprints": selected,
    }


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

    # Calculate final scores using GameService
    final_scores = GameService.calculate_final_scores(game)

    # Format response
    rankings = []
    for score_data in final_scores:
        rankings.append({
            "player_id": score_data["player_id"],
            "username": score_data["username"],
            "rank": score_data["rank"],
            "score_breakdown": {
                "building_points": score_data["base_score"],
                "fengshui_bonus": 0,  # Already included in base_score
                "adjacency_bonus": 0,  # Already included in base_score
                "blueprint_bonus": score_data["blueprint_score"],
                "worker_score": score_data["worker_score"],
                "remaining_resources": score_data["resource_penalty"],
                "total": score_data["total_score"],
            },
        })

    winner = final_scores[0] if final_scores else None

    return {
        "game_id": game.id,
        "winner_id": winner["player_id"] if winner else None,
        "rankings": rankings,
        "duration_minutes": 0,  # TODO: Calculate from timestamps
        "total_rounds": game.total_rounds,
    }
