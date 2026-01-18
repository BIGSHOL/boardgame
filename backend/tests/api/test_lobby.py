"""
Lobby API tests.
Tests for /api/v1/lobbies/* endpoints.

TDD Status: GREEN (tests and implementation complete)
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def create_user_and_get_token(client: AsyncClient, email: str, username: str) -> str:
    """Helper to create a user and get their access token."""
    # Register
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": username,
            "password": "password123",
        },
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "password123",
        },
    )
    return response.json()["tokens"]["access_token"]


class TestCreateLobby:
    """Tests for POST /api/v1/lobbies"""

    async def test_create_lobby_success(self, client: AsyncClient):
        """Should create a new lobby and return lobby info."""
        token = await create_user_and_get_token(client, "host@example.com", "hostuser")

        response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Test Lobby", "max_players": 4},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Lobby"
        assert data["max_players"] == 4
        assert "invite_code" in data
        assert len(data["invite_code"]) == 6
        assert data["status"] == "waiting"
        assert len(data["players"]) == 1
        assert data["players"][0]["is_host"] is True

    async def test_create_lobby_unauthorized(self, client: AsyncClient):
        """Should return 401 without auth token."""
        response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Test Lobby"},
        )
        assert response.status_code == 401

    async def test_create_lobby_default_max_players(self, client: AsyncClient):
        """Should default to 4 max players."""
        token = await create_user_and_get_token(client, "host2@example.com", "host2")

        response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Default Lobby"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201
        assert response.json()["max_players"] == 4


class TestGetLobby:
    """Tests for GET /api/v1/lobbies/{id}"""

    async def test_get_lobby_success(self, client: AsyncClient):
        """Should return lobby info."""
        token = await create_user_and_get_token(client, "get_host@example.com", "gethost")

        # Create lobby
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Get Test Lobby"},
            headers={"Authorization": f"Bearer {token}"},
        )
        lobby_id = create_response.json()["id"]

        # Get lobby
        response = await client.get(f"/api/v1/lobbies/{lobby_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == lobby_id
        assert data["name"] == "Get Test Lobby"

    async def test_get_lobby_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent lobby."""
        response = await client.get("/api/v1/lobbies/99999")
        assert response.status_code == 404


class TestJoinLobby:
    """Tests for POST /api/v1/lobbies/{id}/join"""

    async def test_join_lobby_success(self, client: AsyncClient):
        """Should join lobby successfully."""
        # Create host and lobby
        host_token = await create_user_and_get_token(client, "join_host@example.com", "joinhost")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Join Test Lobby"},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # Create second user and join
        player_token = await create_user_and_get_token(client, "joiner@example.com", "joiner")
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/join",
            headers={"Authorization": f"Bearer {player_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["lobby"]["players"]) == 2
        assert data["player"]["username"] == "joiner"

    async def test_join_lobby_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent lobby."""
        token = await create_user_and_get_token(client, "joinerfail@example.com", "joinerfail")
        response = await client.post(
            "/api/v1/lobbies/99999/join",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_join_lobby_full(self, client: AsyncClient):
        """Should return 400 when lobby is full."""
        # Create host and lobby with max 2 players
        host_token = await create_user_and_get_token(client, "fullhost@example.com", "fullhost")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Full Lobby", "max_players": 2},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # Second player joins
        player2_token = await create_user_and_get_token(client, "player2@example.com", "player2")
        await client.post(
            f"/api/v1/lobbies/{lobby_id}/join",
            headers={"Authorization": f"Bearer {player2_token}"},
        )

        # Third player tries to join
        player3_token = await create_user_and_get_token(client, "player3@example.com", "player3")
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/join",
            headers={"Authorization": f"Bearer {player3_token}"},
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestLobbyReady:
    """Tests for POST /api/v1/lobbies/{id}/ready"""

    async def test_ready_toggle_success(self, client: AsyncClient):
        """Should toggle ready status."""
        # Create host and lobby
        host_token = await create_user_and_get_token(client, "readyhost@example.com", "readyhost")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Ready Test Lobby"},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # Second player joins
        player_token = await create_user_and_get_token(client, "readyplayer@example.com", "readyplayer")
        await client.post(
            f"/api/v1/lobbies/{lobby_id}/join",
            headers={"Authorization": f"Bearer {player_token}"},
        )

        # Toggle ready
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/ready",
            json={"is_ready": True},
            headers={"Authorization": f"Bearer {player_token}"},
        )
        assert response.status_code == 200
        data = response.json()

        # Find the non-host player
        non_host_player = next(p for p in data["players"] if not p["is_host"])
        assert non_host_player["is_ready"] is True
        assert data["status"] == "ready"  # All non-host players ready

    async def test_ready_not_in_lobby(self, client: AsyncClient):
        """Should return 400 when user not in lobby."""
        # Create host and lobby
        host_token = await create_user_and_get_token(client, "notinhost@example.com", "notinhost")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Not In Lobby"},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # User not in lobby tries to ready
        other_token = await create_user_and_get_token(client, "notinplayer@example.com", "notinplayer")
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/ready",
            json={"is_ready": True},
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert response.status_code == 400


class TestStartGame:
    """Tests for POST /api/v1/lobbies/{id}/start"""

    async def test_start_game_success(self, client: AsyncClient):
        """Should start game when all players ready."""
        # Create host and lobby
        host_token = await create_user_and_get_token(client, "starthost@example.com", "starthost")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Start Test Lobby"},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # Second player joins and readies
        player_token = await create_user_and_get_token(client, "startplayer@example.com", "startplayer")
        await client.post(
            f"/api/v1/lobbies/{lobby_id}/join",
            headers={"Authorization": f"Bearer {player_token}"},
        )
        await client.post(
            f"/api/v1/lobbies/{lobby_id}/ready",
            json={"is_ready": True},
            headers={"Authorization": f"Bearer {player_token}"},
        )

        # Host starts game
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/start",
            headers={"Authorization": f"Bearer {host_token}"},
        )
        assert response.status_code == 200
        assert "game_id" in response.json()

    async def test_start_game_not_host(self, client: AsyncClient):
        """Should return 403 when non-host tries to start."""
        # Create host and lobby
        host_token = await create_user_and_get_token(client, "nothoststart@example.com", "nothoststart")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Not Host Start"},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # Second player joins
        player_token = await create_user_and_get_token(client, "nonhostplayer@example.com", "nonhostplayer")
        await client.post(
            f"/api/v1/lobbies/{lobby_id}/join",
            headers={"Authorization": f"Bearer {player_token}"},
        )

        # Non-host tries to start
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/start",
            headers={"Authorization": f"Bearer {player_token}"},
        )
        assert response.status_code == 403

    async def test_start_game_not_all_ready(self, client: AsyncClient):
        """Should return 400 when not all players ready."""
        # Create host and lobby
        host_token = await create_user_and_get_token(client, "notreadyhost@example.com", "notreadyhost")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Not Ready Lobby"},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # Second player joins but doesn't ready
        player_token = await create_user_and_get_token(client, "notreadyplayer@example.com", "notreadyplayer")
        await client.post(
            f"/api/v1/lobbies/{lobby_id}/join",
            headers={"Authorization": f"Bearer {player_token}"},
        )

        # Host tries to start
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/start",
            headers={"Authorization": f"Bearer {host_token}"},
        )
        assert response.status_code == 400
        assert "not all players are ready" in response.json()["detail"].lower()

    async def test_start_game_not_enough_players(self, client: AsyncClient):
        """Should return 400 when only host in lobby."""
        # Create host and lobby
        host_token = await create_user_and_get_token(client, "alonehost@example.com", "alonehost")
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Alone Lobby"},
            headers={"Authorization": f"Bearer {host_token}"},
        )
        lobby_id = create_response.json()["id"]

        # Host tries to start alone
        response = await client.post(
            f"/api/v1/lobbies/{lobby_id}/start",
            headers={"Authorization": f"Bearer {host_token}"},
        )
        assert response.status_code == 400
        assert "not enough players" in response.json()["detail"].lower()


class TestGetLobbyByInviteCode:
    """Tests for GET /api/v1/lobbies/join/{invite_code}"""

    async def test_get_by_invite_code_success(self, client: AsyncClient):
        """Should return lobby by invite code."""
        token = await create_user_and_get_token(client, "invitehost@example.com", "invitehost")

        # Create lobby
        create_response = await client.post(
            "/api/v1/lobbies",
            json={"name": "Invite Code Lobby"},
            headers={"Authorization": f"Bearer {token}"},
        )
        invite_code = create_response.json()["invite_code"]

        # Get by invite code
        response = await client.get(f"/api/v1/lobbies/join/{invite_code}")
        assert response.status_code == 200
        assert response.json()["name"] == "Invite Code Lobby"

    async def test_get_by_invite_code_not_found(self, client: AsyncClient):
        """Should return 404 for invalid invite code."""
        response = await client.get("/api/v1/lobbies/join/INVALD")
        assert response.status_code == 404
