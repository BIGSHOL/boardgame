"""
Solo play API endpoints.
Allows single player games against AI opponents.
"""
import json
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, get_token_from_header
from app.models.game import Game, GameStatus
from app.models.user import User
from app.services.game_service import GameService
from app.services.ai_service import (
    AIService,
    AIPlayer,
    AIDifficulty,
    AIDecision,
    create_ai_opponent,
    AI_PERSONALITIES,
)
from app.services.resource_service import ResourceService
from app.services.worker_service import WorkerService
from app.services.blueprint_service import BlueprintService

router = APIRouter()


class CreateSoloGameRequest(BaseModel):
    """Request to create a solo game."""
    num_ai_opponents: int = Field(default=1, ge=1, le=3)
    ai_difficulty: str = Field(default="medium")


class SoloGameResponse(BaseModel):
    """Response for solo game creation."""
    game_id: int
    message: str


class AIActionResponse(BaseModel):
    """Response for AI action execution."""
    action_type: str
    action_result: dict
    next_player_id: int
    is_ai_turn: bool


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


@router.get("/personalities")
async def get_ai_personalities():
    """Get available AI personalities."""
    return {
        "personalities": [
            {
                "id": key,
                "name": data["name"],
                "name_en": data["name_en"],
                "difficulty": data["difficulty"].value,
                "strategy": data["strategy"],
            }
            for key, data in AI_PERSONALITIES.items()
        ]
    }


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_solo_game(
    request: CreateSoloGameRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
) -> dict:
    """
    Create a new solo game with AI opponents.

    Args:
        request: Solo game configuration
        db: Database session
        authorization: Auth header

    Returns:
        Created game information
    """
    user = await get_current_user(db, authorization)

    # Map difficulty string to enum
    difficulty_map = {
        "easy": AIDifficulty.EASY,
        "medium": AIDifficulty.MEDIUM,
        "hard": AIDifficulty.HARD,
    }
    difficulty = difficulty_map.get(request.ai_difficulty.lower(), AIDifficulty.MEDIUM)

    # Create initial board
    board = GameService.create_initial_board()

    # Deal blueprints for all players
    total_players = 1 + request.num_ai_opponents
    blueprint_hands = BlueprintService.deal_blueprints(total_players, cards_per_player=3)

    # Create human player state
    human_player = GameService.create_initial_player(
        player_id=1,
        user_id=user.id,
        username=user.username,
        color="blue",
        turn_order=0,
        is_host=True,
    )
    human_player["dealt_blueprints"] = blueprint_hands[0]
    human_player["blueprints"] = []
    human_player["is_ai"] = False

    players = [human_player]
    turn_order_list = [user.id]

    # Create AI player states
    ai_colors = ["red", "green", "yellow"]
    ai_names = ["AI - 자원 수집가", "AI - 풍수 대가", "AI - 초보 도전자"]

    for i in range(request.num_ai_opponents):
        ai_user_id = -(i + 1)  # Negative IDs for AI
        ai_player = GameService.create_initial_player(
            player_id=i + 2,
            user_id=ai_user_id,
            username=ai_names[i % len(ai_names)],
            color=ai_colors[i % len(ai_colors)],
            turn_order=i + 1,
            is_host=False,
        )
        ai_player["dealt_blueprints"] = blueprint_hands[i + 1]
        ai_player["blueprints"] = []
        ai_player["is_ai"] = True
        ai_player["ai_difficulty"] = difficulty.value

        players.append(ai_player)
        turn_order_list.append(ai_user_id)

    # Generate tile pool
    available_tiles = GameService.generate_tile_pool()

    # Create game
    game = Game(
        lobby_id=None,  # Solo games have no lobby
        status=GameStatus.IN_PROGRESS,
        current_round=1,
        total_rounds=GameService.TOTAL_ROUNDS,
        current_turn_player_id=turn_order_list[0],
        turn_order_json=json.dumps(turn_order_list),
        board_json=json.dumps(board),
        players_json=json.dumps(players),
        available_tiles_json=json.dumps(available_tiles),
        discarded_tiles_json=json.dumps([]),
    )

    db.add(game)
    await db.commit()
    await db.refresh(game)

    return {
        "game_id": game.id,
        "message": f"Solo game created with {request.num_ai_opponents} AI opponent(s)",
        "players": [
            {
                "id": p["id"],
                "username": p["username"],
                "is_ai": p.get("is_ai", False),
            }
            for p in players
        ],
    }


@router.post("/{game_id}/ai-turn")
async def execute_ai_turn(
    game_id: int,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
) -> dict:
    """
    Execute the current AI player's turn.

    This endpoint is called when it's an AI player's turn.
    It makes a decision and executes the action.
    """
    user = await get_current_user(db, authorization)

    game = await GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not in progress",
        )

    # Find current player
    current_player = None
    for p in game.players:
        if p["user_id"] == game.current_turn_player_id:
            current_player = p
            break

    if not current_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current player not found",
        )

    # Check if it's an AI player's turn
    if not current_player.get("is_ai", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="It's not an AI player's turn",
        )

    # Get AI difficulty
    difficulty = AIDifficulty(current_player.get("ai_difficulty", "medium"))

    # Create game state for AI
    game_state = GameService.to_game_state_response(game)

    # Get AI decision
    decision = AIService.make_decision(game_state, current_player, difficulty)

    # Execute the decision
    result = await _execute_ai_decision(db, game, current_player, decision)

    await db.commit()

    # Check if next turn is also AI
    next_is_ai = False
    for p in game.players:
        if p["user_id"] == game.current_turn_player_id:
            next_is_ai = p.get("is_ai", False)
            break

    return {
        "action_type": decision.action_type,
        "action_result": result,
        "next_player_id": game.current_turn_player_id,
        "is_ai_turn": next_is_ai,
        "game_status": game.status.value,
    }


@router.post("/{game_id}/auto-play")
async def auto_play_ai_turns(
    game_id: int,
    max_turns: int = 10,
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
) -> dict:
    """
    Automatically execute all AI turns until it's the human player's turn.

    Args:
        game_id: Game ID
        max_turns: Maximum number of AI turns to execute (safety limit)
    """
    user = await get_current_user(db, authorization)

    game = await GameService.get_game(db, game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
        )

    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not in progress",
        )

    executed_actions = []
    turns_executed = 0

    while turns_executed < max_turns:
        # Find current player
        current_player = None
        for p in game.players:
            if p["user_id"] == game.current_turn_player_id:
                current_player = p
                break

        if not current_player:
            break

        # Stop if it's human player's turn
        if not current_player.get("is_ai", False):
            break

        # Stop if game ended
        if game.status != GameStatus.IN_PROGRESS:
            break

        # Get AI decision and execute
        difficulty = AIDifficulty(current_player.get("ai_difficulty", "medium"))
        game_state = GameService.to_game_state_response(game)
        decision = AIService.make_decision(game_state, current_player, difficulty)

        result = await _execute_ai_decision(db, game, current_player, decision)

        executed_actions.append({
            "player": current_player["username"],
            "action_type": decision.action_type,
            "params": decision.params,
        })

        turns_executed += 1

    await db.commit()

    # Check current player after all AI turns
    current_player = None
    for p in game.players:
        if p["user_id"] == game.current_turn_player_id:
            current_player = p
            break

    return {
        "turns_executed": turns_executed,
        "actions": executed_actions,
        "current_player_id": game.current_turn_player_id,
        "is_your_turn": current_player and not current_player.get("is_ai", False),
        "game_status": game.status.value,
        "game_state": GameService.to_game_state_response(game),
    }


async def _execute_ai_decision(
    db: AsyncSession,
    game: Game,
    player: dict,
    decision: AIDecision,
) -> dict:
    """Execute an AI decision and return the result."""
    # NOTE: GameService methods check current_turn_player_id which stores user_id, not player.id
    player_id = player["user_id"]

    if decision.action_type == "select_blueprint":
        result = await GameService.select_blueprint(
            db, game, player_id, decision.params["blueprint_id"]
        )
        # AI should also end turn after selecting blueprint
        # Actually, let's just return the blueprint selection result
        return result

    elif decision.action_type == "place_tile":
        result = await GameService.place_tile(
            db,
            game,
            player_id,
            decision.params["tile_id"],
            decision.params["position"],
        )
        return result

    elif decision.action_type == "place_worker":
        result = await GameService.place_worker(
            db,
            game,
            player_id,
            decision.params["worker_type"],
            decision.params["target_position"],
            decision.params["slot_index"],
        )
        return result

    elif decision.action_type == "end_turn":
        result = await GameService.end_turn(db, game, player_id)
        return result

    return {"error": f"Unknown action type: {decision.action_type}"}
