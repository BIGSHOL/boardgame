"""
WebSocket Broadcast Service

Service layer for broadcasting game events to connected players.
"""
from typing import Any, Dict, Optional
import logging

from app.websocket.game_manager import game_manager, GameMessage, MessageType
from app.models.game import Game, GamePlayer

logger = logging.getLogger(__name__)


class GameBroadcastService:
    """
    Service for broadcasting game events via WebSocket.

    Provides high-level methods for common game events.
    """

    @staticmethod
    async def broadcast_game_state(
        game: Game,
        exclude_player_id: Optional[int] = None
    ) -> None:
        """
        Broadcast full game state update to all players.

        Args:
            game: The game object
            exclude_player_id: Optional player to exclude
        """
        game_state = GameBroadcastService._serialize_game_state(game)

        await game_manager.broadcast_to_game(
            game.id,
            GameMessage(
                type=MessageType.GAME_STATE_UPDATE,
                data={"game_state": game_state}
            ),
            exclude_player_id=exclude_player_id
        )

    @staticmethod
    async def broadcast_action_performed(
        game: Game,
        player_id: int,
        action_type: str,
        action_result: Dict[str, Any]
    ) -> None:
        """
        Broadcast that a player performed an action.

        Args:
            game: The game object
            player_id: Player who performed the action
            action_type: Type of action performed
            action_result: Result of the action
        """
        # Find player username
        player = next((p for p in game.players if p.id == player_id), None)
        username = player.user.username if player and player.user else "Unknown"

        # Broadcast action to all other players
        await game_manager.broadcast_to_game(
            game.id,
            GameMessage(
                type=MessageType.PLAYER_ACTION,
                data={
                    "player_id": player_id,
                    "username": username,
                    "action_type": action_type,
                    "result": action_result
                }
            ),
            exclude_player_id=player_id
        )

        # Broadcast updated game state to all players
        await GameBroadcastService.broadcast_game_state(game)

    @staticmethod
    async def notify_turn_change(
        game: Game,
        previous_player_id: int,
        new_player_id: int
    ) -> None:
        """
        Notify players about turn change.

        Args:
            game: The game object
            previous_player_id: Player whose turn ended
            new_player_id: Player whose turn is starting
        """
        # Find player usernames
        prev_player = next((p for p in game.players if p.id == previous_player_id), None)
        new_player = next((p for p in game.players if p.id == new_player_id), None)

        # Broadcast turn change to all players
        await game_manager.broadcast_to_game(
            game.id,
            GameMessage(
                type=MessageType.TURN_CHANGED,
                data={
                    "previous_player_id": previous_player_id,
                    "current_player_id": new_player_id,
                    "current_player_name": new_player.user.username if new_player and new_player.user else "Unknown"
                }
            )
        )

        # Send YOUR_TURN message to new current player
        await game_manager.send_to_player(
            game.id,
            new_player_id,
            GameMessage(
                type=MessageType.YOUR_TURN,
                data={
                    "message": "It's your turn!",
                    "current_round": game.current_round
                }
            )
        )

    @staticmethod
    async def notify_round_change(
        game: Game,
        new_round: int
    ) -> None:
        """
        Notify players about round change.

        Args:
            game: The game object
            new_round: The new round number
        """
        await game_manager.broadcast_to_game(
            game.id,
            GameMessage(
                type=MessageType.ROUND_CHANGED,
                data={
                    "previous_round": new_round - 1,
                    "current_round": new_round,
                    "total_rounds": game.total_rounds
                }
            )
        )

    @staticmethod
    async def notify_game_started(game: Game) -> None:
        """
        Notify players that game has started.

        Args:
            game: The game object
        """
        game_state = GameBroadcastService._serialize_game_state(game)

        await game_manager.broadcast_to_game(
            game.id,
            GameMessage(
                type=MessageType.GAME_STARTED,
                data={
                    "game_id": game.id,
                    "game_state": game_state
                }
            )
        )

        # Notify first player it's their turn
        first_player_id = game.current_turn_player_id
        if first_player_id:
            await game_manager.send_to_player(
                game.id,
                first_player_id,
                GameMessage(
                    type=MessageType.YOUR_TURN,
                    data={"message": "Game started! It's your turn!"}
                )
            )

    @staticmethod
    async def notify_game_ended(
        game: Game,
        winner_id: int,
        rankings: list
    ) -> None:
        """
        Notify players that game has ended.

        Args:
            game: The game object
            winner_id: ID of the winning player
            rankings: Final rankings
        """
        winner = next((p for p in game.players if p.id == winner_id), None)

        await game_manager.broadcast_to_game(
            game.id,
            GameMessage(
                type=MessageType.GAME_ENDED,
                data={
                    "game_id": game.id,
                    "winner_id": winner_id,
                    "winner_name": winner.user.username if winner and winner.user else "Unknown",
                    "rankings": rankings
                }
            )
        )

    @staticmethod
    def _serialize_game_state(game: Game) -> Dict[str, Any]:
        """
        Serialize game state for WebSocket transmission.

        Args:
            game: The game object

        Returns:
            Serialized game state dictionary
        """
        return {
            "id": game.id,
            "status": game.status.value if hasattr(game.status, 'value') else game.status,
            "current_round": game.current_round,
            "total_rounds": game.total_rounds,
            "current_turn_player_id": game.current_turn_player_id,
            "turn_order": game.turn_order,
            "board": game.board,
            "available_tiles": game.available_tiles,
            "players": [
                {
                    "id": p.id,
                    "user_id": p.user_id,
                    "username": p.user.username if p.user else "Unknown",
                    "color": p.color.value if hasattr(p.color, 'value') else p.color,
                    "turn_order": p.turn_order,
                    "resources": p.resources,
                    "workers": p.workers,
                    "score": p.score,
                    "placed_tiles": p.placed_tiles,
                    "blueprints": p.blueprints
                }
                for p in game.players
            ]
        }


# Global broadcast service instance
broadcast_service = GameBroadcastService()
