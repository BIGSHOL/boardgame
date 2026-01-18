"""
Resource service tests.
Tests for resource management logic.

TDD Status: RED (skeleton tests, implementation pending)
"""
import pytest

from app.schemas.game import Resources, ResourceType

pytestmark = pytest.mark.asyncio


class TestAddResource:
    """Tests for adding resources."""

    @pytest.mark.skip(reason="Resource service not implemented yet")
    async def test_add_single_resource(self):
        """Should add single resource type."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Resource service not implemented yet")
    async def test_add_multiple_resources(self):
        """Should add multiple resource types."""
        # TODO: Implement in Phase 2
        pass


class TestConsumeResource:
    """Tests for consuming resources."""

    @pytest.mark.skip(reason="Resource service not implemented yet")
    async def test_consume_single_resource(self):
        """Should consume single resource if available."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Resource service not implemented yet")
    async def test_consume_insufficient_resource(self):
        """Should raise error when insufficient resources."""
        # TODO: Implement in Phase 2
        pass


class TestCanAfford:
    """Tests for resource affordability check."""

    @pytest.mark.skip(reason="Resource service not implemented yet")
    async def test_can_afford_true(self):
        """Should return True when can afford cost."""
        # TODO: Implement in Phase 2
        pass

    @pytest.mark.skip(reason="Resource service not implemented yet")
    async def test_can_afford_false(self):
        """Should return False when cannot afford cost."""
        # TODO: Implement in Phase 2
        pass
