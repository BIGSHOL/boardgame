"""
WebSocket Game Handler

Handles WebSocket connections and messages for game synchronization.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import logging

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.game import Game, GamePlayer
from app.models.user import User
from app.websocket.game_manager import game_manager, GameMessage, MessageType

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_current_user_ws(
    token: str,
    db: AsyncSession
) -> Optional[User]:
    """
    Authenticate WebSocket connection via token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        User if authenticated, None otherwise
    """
    try:
        payload = decode_access_token(token)
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await db.get(User, int(user_id))
        return user
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        return None


async def validate_game_player(
    game_id: int,
    user_id: int,
    db: AsyncSession
) -> Optional[GamePlayer]:
    """
    Validate that user is a player in the game.

    Args:
        game_id: Game ID
        user_id: User ID
        db: Database session

    Returns:
        GamePlayer if valid, None otherwise
    """
    from sqlalchemy import select

    result = await db.execute(
        select(GamePlayer).where(
            GamePlayer.game_id == game_id,
            GamePlayer.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


@router.websocket("/ws/game/{game_id}")
async def game_websocket(
    websocket: WebSocket,
    game_id: int,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for game synchronization.

    Connect with: ws://host/ws/game/{game_id}?token={jwt_token}

    Message format:
    {
        "type": "message_type",
        "data": { ... }
    }

    Supported client messages:
    - ping: Keep-alive ping
    - action: Game action (handled via REST API, this is for future use)

    Server broadcasts:
    - game_state_update: Full game state update
    - turn_changed: Turn has changed to another player
    - your_turn: It's now your turn
    - player_action: Another player performed an action
    - game_ended: Game has ended
    """
    # Authenticate user
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # Validate player is in game
    game_player = await validate_game_player(game_id, user.id, db)
    if not game_player:
        await websocket.close(code=4003, reason="Not a player in this game")
        return

    # Connect to game room
    await game_manager.connect(websocket, game_id, game_player.id)

    # Notify other players
    await game_manager.broadcast_to_game(
        game_id,
        GameMessage(
            type=MessageType.PLAYER_JOINED,
            data={
                "player_id": game_player.id,
                "username": user.username
            }
        ),
        exclude_player_id=game_player.id
    )

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type", "")

                # Handle ping
                if msg_type == "ping":
                    await websocket.send_json(
                        GameMessage(type=MessageType.PONG, data={}).to_dict()
                    )

                # Other message types can be handled here
                # For now, game actions go through REST API

            except json.JSONDecodeError:
                await websocket.send_json(
                    GameMessage(
                        type=MessageType.ERROR,
                        data={"message": "Invalid JSON"}
                    ).to_dict()
                )

    except WebSocketDisconnect:
        logger.info(f"Player {game_player.id} disconnected from game {game_id}")
    except Exception as e:
        logger.error(f"WebSocket error for player {game_player.id}: {e}")
    finally:
        # Disconnect and notify others
        game_manager.disconnect(game_id, game_player.id)

        await game_manager.broadcast_to_game(
            game_id,
            GameMessage(
                type=MessageType.PLAYER_LEFT,
                data={
                    "player_id": game_player.id,
                    "username": user.username
                }
            )
        )
