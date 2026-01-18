"""
Worker service tests.
Tests for worker placement and recall logic.

TDD Status: RED (skeleton tests, implementation pending)
"""
import pytest

from app.schemas.game import WorkerType, BoardPosition

pytestmark = pytest.mark.asyncio


class TestPlaceApprentice:
    """Tests for placing apprentice workers."""

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_place_apprentice_success(self):
        """Should place apprentice on valid slot."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_place_apprentice_no_available(self):
        """Should raise error when no apprentices available."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_place_apprentice_slot_occupied(self):
        """Should raise error when slot already occupied."""
        # TODO: Implement in Phase 2
        pass


class TestRecallApprentice:
    """Tests for recalling apprentice workers."""

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_recall_all_apprentices(self):
        """Should recall all apprentices at turn end."""
        # TODO: Implement in Phase 2
        pass


class TestPlaceOfficial:
    """Tests for placing official workers."""

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_place_official_success(self):
        """Should place official on main board permanently."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_place_official_no_available(self):
        """Should raise error when no officials available."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_official_not_recalled(self):
        """Official should not be recalled at turn end."""
        # TODO: Implement in Phase 2
        pass


class TestWorkerAvailability:
    """Tests for worker availability checks."""

    @pytest.mark.skip(reason="Worker service not implemented yet")
    async def test_get_available_workers(self):
        """Should return correct count of available workers."""
        # TODO: Implement in Phase 2
        pass
