"""
WebSocket Game Connection Manager

Manages real-time WebSocket connections for game synchronization.
"""
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    # Game state
    GAME_STATE_UPDATE = "game_state_update"
    VALID_ACTIONS_UPDATE = "valid_actions_update"

    # Turn management
    YOUR_TURN = "your_turn"
    TURN_CHANGED = "turn_changed"

    # Player actions
    PLAYER_ACTION = "player_action"
    ACTION_RESULT = "action_result"

    # Player presence
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    PLAYER_RECONNECTED = "player_reconnected"

    # Game lifecycle
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
    ROUND_CHANGED = "round_changed"

    # System
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


@dataclass
class GameMessage:
    """WebSocket message structure"""
    type: MessageType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "data": self.data
        }
        if self.timestamp:
            result["timestamp"] = self.timestamp
        return result


class GameConnectionManager:
    """
    Manages WebSocket connections for game rooms.

    Each game has its own room with multiple player connections.
    Supports broadcasting to all players or specific players.
    """

    def __init__(self):
        # game_id -> {player_id -> WebSocket}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: int, player_id: int) -> None:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection
            game_id: The game room ID
            player_id: The player ID
        """
        await websocket.accept()

        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}

        self.active_connections[game_id][player_id] = websocket
        logger.info(f"Player {player_id} connected to game {game_id}")

    def disconnect(self, game_id: int, player_id: int) -> None:
        """
        Remove a WebSocket connection.

        Args:
            game_id: The game room ID
            player_id: The player ID
        """
        if game_id in self.active_connections:
            if player_id in self.active_connections[game_id]:
                del self.active_connections[game_id][player_id]
                logger.info(f"Player {player_id} disconnected from game {game_id}")

            # Clean up empty game rooms
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
                logger.info(f"Game room {game_id} cleaned up (no connections)")

    async def broadcast_to_game(
        self,
        game_id: int,
        message: GameMessage,
        exclude_player_id: Optional[int] = None
    ) -> None:
        """
        Broadcast a message to all players in a game.

        Args:
            game_id: The game room ID
            message: The message to broadcast
            exclude_player_id: Optional player ID to exclude from broadcast
        """
        if game_id not in self.active_connections:
            return

        message_dict = message.to_dict()
        failed_players = []

        for player_id, websocket in self.active_connections[game_id].items():
            if exclude_player_id and player_id == exclude_player_id:
                continue

            try:
                await websocket.send_json(message_dict)
            except Exception as e:
                logger.warning(f"Failed to send to player {player_id}: {e}")
                failed_players.append(player_id)

        # Clean up failed connections
        for player_id in failed_players:
            self.disconnect(game_id, player_id)

    async def send_to_player(
        self,
        game_id: int,
        player_id: int,
        message: GameMessage
    ) -> bool:
        """
        Send a message to a specific player.

        Args:
            game_id: The game room ID
            player_id: The target player ID
            message: The message to send

        Returns:
            True if sent successfully, False otherwise
        """
        if game_id not in self.active_connections:
            return False

        if player_id not in self.active_connections[game_id]:
            return False

        websocket = self.active_connections[game_id][player_id]
        try:
            await websocket.send_json(message.to_dict())
            return True
        except Exception as e:
            logger.warning(f"Failed to send to player {player_id}: {e}")
            self.disconnect(game_id, player_id)
            return False

    def get_connected_players(self, game_id: int) -> List[int]:
        """
        Get list of connected player IDs for a game.

        Args:
            game_id: The game room ID

        Returns:
            List of connected player IDs
        """
        if game_id not in self.active_connections:
            return []
        return list(self.active_connections[game_id].keys())

    def is_player_connected(self, game_id: int, player_id: int) -> bool:
        """
        Check if a player is connected to a game.

        Args:
            game_id: The game room ID
            player_id: The player ID

        Returns:
            True if connected, False otherwise
        """
        return (
            game_id in self.active_connections
            and player_id in self.active_connections[game_id]
        )

    def get_game_connection_count(self, game_id: int) -> int:
        """
        Get number of connections for a game.

        Args:
            game_id: The game room ID

        Returns:
            Number of active connections
        """
        if game_id not in self.active_connections:
            return 0
        return len(self.active_connections[game_id])


# Global connection manager instance
game_manager = GameConnectionManager()
