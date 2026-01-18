"""
Lobby API tests.
Tests for /api/v1/lobbies/* endpoints.

TDD Status: RED (skeleton tests, implementation pending)
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestCreateLobby:
    """Tests for POST /api/v1/lobbies"""

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_create_lobby_success(self, client: AsyncClient):
        """Should create a new lobby and return lobby info."""
        # TODO: Implement in Phase 1
        response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Test Lobby", "max_players": 4},
            headers={"Authorization": "Bearer valid-token"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Lobby"
        assert data["max_players"] == 4
        assert "invite_code" in data
        assert len(data["invite_code"]) == 6

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_create_lobby_unauthorized(self, client: AsyncClient):
        """Should return 401 without auth token."""
        response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Test Lobby"},
        )
        assert response.status_code == 401


class TestGetLobby:
    """Tests for GET /api/v1/lobbies/{id}"""

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_get_lobby_success(self, client: AsyncClient):
        """Should return lobby info."""
        # TODO: Implement in Phase 1
        pass

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_get_lobby_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent lobby."""
        response = await client.get("/api/v1/lobbies/99999")
        assert response.status_code == 404


class TestJoinLobby:
    """Tests for POST /api/v1/lobbies/{id}/join"""

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_join_lobby_success(self, client: AsyncClient):
        """Should join lobby with valid invite code."""
        # TODO: Implement in Phase 1
        pass

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_join_lobby_invalid_code(self, client: AsyncClient):
        """Should return 404 for invalid invite code."""
        response = await client.post(
            "/api/v1/lobbies/1/join",
            json={"invite_code": "INVALID"},
            headers={"Authorization": "Bearer valid-token"},
        )
        assert response.status_code == 404

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_join_lobby_full(self, client: AsyncClient):
        """Should return 400 when lobby is full."""
        # TODO: Implement in Phase 1
        pass


class TestLobbyReady:
    """Tests for POST /api/v1/lobbies/{id}/ready"""

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_ready_toggle_success(self, client: AsyncClient):
        """Should toggle ready status."""
        # TODO: Implement in Phase 1
        pass

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_ready_not_in_lobby(self, client: AsyncClient):
        """Should return 400 when user not in lobby."""
        # TODO: Implement in Phase 1
        pass


class TestStartGame:
    """Tests for POST /api/v1/lobbies/{id}/start"""

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_start_game_success(self, client: AsyncClient):
        """Should start game when all players ready."""
        # TODO: Implement in Phase 1
        pass

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_start_game_not_host(self, client: AsyncClient):
        """Should return 403 when non-host tries to start."""
        # TODO: Implement in Phase 1
        pass

    @pytest.mark.skip(reason="Lobby API not implemented yet")
    async def test_start_game_not_all_ready(self, client: AsyncClient):
        """Should return 400 when not all players ready."""
        # TODO: Implement in Phase 1
        pass
