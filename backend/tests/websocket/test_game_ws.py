"""
WebSocket game synchronization tests
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket, WebSocketDisconnect
from app.websocket.game_manager import GameConnectionManager, GameMessage, MessageType


class TestGameConnectionManager:
    """Test GameConnectionManager"""

    @pytest.fixture
    def manager(self):
        """Create a fresh manager for each test"""
        return GameConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket"""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_json = AsyncMock()
        ws.close = AsyncMock()
        return ws

    # Connection tests
    @pytest.mark.asyncio
    async def test_connect_adds_connection_to_game(self, manager, mock_websocket):
        """Test that connect adds websocket to game room"""
        game_id = 1
        player_id = 100

        await manager.connect(mock_websocket, game_id, player_id)

        assert game_id in manager.active_connections
        assert player_id in manager.active_connections[game_id]
        assert manager.active_connections[game_id][player_id] == mock_websocket
        mock_websocket.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_multiple_players_same_game(self, manager, mock_websocket):
        """Test multiple players can connect to same game"""
        game_id = 1
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)

        await manager.connect(ws1, game_id, player_id=1)
        await manager.connect(ws2, game_id, player_id=2)

        assert len(manager.active_connections[game_id]) == 2
        assert 1 in manager.active_connections[game_id]
        assert 2 in manager.active_connections[game_id]

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection(self, manager, mock_websocket):
        """Test that disconnect removes websocket from game room"""
        game_id = 1
        player_id = 100

        await manager.connect(mock_websocket, game_id, player_id)
        manager.disconnect(game_id, player_id)

        assert player_id not in manager.active_connections.get(game_id, {})

    @pytest.mark.asyncio
    async def test_disconnect_cleans_up_empty_game(self, manager, mock_websocket):
        """Test that empty game rooms are cleaned up"""
        game_id = 1
        player_id = 100

        await manager.connect(mock_websocket, game_id, player_id)
        manager.disconnect(game_id, player_id)

        assert game_id not in manager.active_connections

    # Broadcast tests
    @pytest.mark.asyncio
    async def test_broadcast_to_game_sends_to_all_players(self, manager):
        """Test broadcast sends message to all players in game"""
        game_id = 1
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)

        await manager.connect(ws1, game_id, player_id=1)
        await manager.connect(ws2, game_id, player_id=2)

        message = GameMessage(
            type=MessageType.GAME_STATE_UPDATE,
            data={"current_round": 1}
        )
        await manager.broadcast_to_game(game_id, message)

        ws1.send_json.assert_called_once()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_excludes_sender(self, manager):
        """Test broadcast can exclude sender"""
        game_id = 1
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)

        await manager.connect(ws1, game_id, player_id=1)
        await manager.connect(ws2, game_id, player_id=2)

        message = GameMessage(
            type=MessageType.PLAYER_ACTION,
            data={"action": "place_tile"}
        )
        await manager.broadcast_to_game(game_id, message, exclude_player_id=1)

        ws1.send_json.assert_not_called()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_player_sends_to_specific_player(self, manager):
        """Test send_to_player sends only to specific player"""
        game_id = 1
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)

        await manager.connect(ws1, game_id, player_id=1)
        await manager.connect(ws2, game_id, player_id=2)

        message = GameMessage(
            type=MessageType.YOUR_TURN,
            data={"message": "It's your turn"}
        )
        await manager.send_to_player(game_id, player_id=1, message=message)

        ws1.send_json.assert_called_once()
        ws2.send_json.assert_not_called()

    # Message type tests
    def test_game_message_serialization(self):
        """Test GameMessage serializes correctly"""
        message = GameMessage(
            type=MessageType.GAME_STATE_UPDATE,
            data={"round": 1, "player_id": 5}
        )

        result = message.to_dict()

        assert result["type"] == "game_state_update"
        assert result["data"]["round"] == 1
        assert result["data"]["player_id"] == 5

    def test_message_types_exist(self):
        """Test all required message types exist"""
        assert MessageType.GAME_STATE_UPDATE
        assert MessageType.PLAYER_ACTION
        assert MessageType.YOUR_TURN
        assert MessageType.TURN_CHANGED
        assert MessageType.PLAYER_JOINED
        assert MessageType.PLAYER_LEFT
        assert MessageType.GAME_STARTED
        assert MessageType.GAME_ENDED
        assert MessageType.ERROR

    # Error handling tests
    @pytest.mark.asyncio
    async def test_broadcast_handles_disconnected_client(self, manager):
        """Test broadcast handles disconnected clients gracefully"""
        game_id = 1
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        ws1.send_json.side_effect = Exception("Connection closed")

        await manager.connect(ws1, game_id, player_id=1)
        await manager.connect(ws2, game_id, player_id=2)

        message = GameMessage(type=MessageType.GAME_STATE_UPDATE, data={})

        # Should not raise exception
        await manager.broadcast_to_game(game_id, message)

        # ws2 should still receive the message
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_connected_players(self, manager):
        """Test getting list of connected players"""
        game_id = 1
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)

        await manager.connect(ws1, game_id, player_id=1)
        await manager.connect(ws2, game_id, player_id=2)

        players = manager.get_connected_players(game_id)

        assert set(players) == {1, 2}

    @pytest.mark.asyncio
    async def test_get_connected_players_empty_game(self, manager):
        """Test getting connected players for non-existent game"""
        players = manager.get_connected_players(999)
        assert players == []

    @pytest.mark.asyncio
    async def test_is_player_connected(self, manager, mock_websocket):
        """Test checking if player is connected"""
        game_id = 1
        player_id = 100

        assert not manager.is_player_connected(game_id, player_id)

        await manager.connect(mock_websocket, game_id, player_id)

        assert manager.is_player_connected(game_id, player_id)


class TestGameWebSocketEndpoint:
    """Test WebSocket endpoint integration"""

    @pytest.mark.asyncio
    async def test_websocket_authentication_required(self):
        """Test that WebSocket requires authentication"""
        # This would be an integration test with actual FastAPI test client
        pass

    @pytest.mark.asyncio
    async def test_websocket_player_must_be_in_game(self):
        """Test that player must be participant in game"""
        # This would be an integration test
        pass
