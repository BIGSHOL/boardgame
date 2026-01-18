"""
Game API tests.
Tests for /api/v1/games/* endpoints.

TDD Status: RED (skeleton tests, implementation pending)
"""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestGetGameState:
    """Tests for GET /api/v1/games/{id}"""

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_get_game_state_success(self, client: AsyncClient):
        """Should return current game state."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_get_game_state_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent game."""
        response = await client.get(
            "/api/v1/games/99999",
            headers={"Authorization": "Bearer valid-token"},
        )
        assert response.status_code == 404

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_get_game_state_not_in_game(self, client: AsyncClient):
        """Should return 403 when user not in game."""
        # TODO: Implement in Phase 2
        pass


class TestGameAction:
    """Tests for POST /api/v1/games/{id}/action"""

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_place_worker_success(self, client: AsyncClient):
        """Should place worker and update game state."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_place_tile_success(self, client: AsyncClient):
        """Should place tile and update game state."""
        # TODO: Implement in Phase 3
        pass

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_action_not_your_turn(self, client: AsyncClient):
        """Should return 403 when action on other player's turn."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_action_invalid(self, client: AsyncClient):
        """Should return 400 for invalid action."""
        # TODO: Implement in Phase 2
        pass


class TestValidActions:
    """Tests for GET /api/v1/games/{id}/valid-actions"""

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_get_valid_actions(self, client: AsyncClient):
        """Should return list of valid actions for current player."""
        # TODO: Implement in Phase 2
        pass


class TestGameResult:
    """Tests for GET /api/v1/games/{id}/result"""

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_get_result_success(self, client: AsyncClient):
        """Should return game results when game finished."""
        # TODO: Implement in Phase 5
        pass

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_get_result_game_not_finished(self, client: AsyncClient):
        """Should return 400 when game not finished."""
        # TODO: Implement in Phase 5
        pass


class TestSubmitFeedback:
    """Tests for POST /api/v1/games/{id}/feedback"""

    @pytest.mark.skip(reason="Game API not implemented yet")
    async def test_submit_feedback_success(self, client: AsyncClient):
        """Should submit feedback after game."""
        # TODO: Implement in Phase 5
        pass
