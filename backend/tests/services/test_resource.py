"""
Resource service tests.
Tests for resource management logic.

TDD Status: GREEN (tests and implementation complete)
"""
import pytest

from app.services.resource_service import ResourceService, Resources, ResourceType


class TestInitialResources:
    """Tests for initial resources."""

    def test_get_initial_resources(self):
        """Should return correct initial resources."""
        resources = ResourceService.get_initial_resources()

        assert resources.wood == 2
        assert resources.stone == 2
        assert resources.tile == 0
        assert resources.ink == 0

    def test_initial_resources_are_new_instances(self):
        """Should return new instance each time."""
        resources1 = ResourceService.get_initial_resources()
        resources2 = ResourceService.get_initial_resources()

        resources1.wood = 100
        assert resources2.wood == 2  # Not affected


class TestAddResource:
    """Tests for adding resources."""

    def test_add_single_resource(self):
        """Should add single resource type."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)

        result = ResourceService.add_resource(resources, ResourceType.WOOD, 3)

        assert result.wood == 5
        assert result.stone == 2  # Unchanged
        assert resources.wood == 2  # Original unchanged

    def test_add_resource_respects_max_limit(self):
        """Should not exceed maximum limit."""
        resources = Resources(wood=8, stone=2, tile=0, ink=0)

        result = ResourceService.add_resource(resources, ResourceType.WOOD, 5)

        assert result.wood == 10  # Max limit for wood

    def test_add_zero_resources(self):
        """Should handle zero amount."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)

        result = ResourceService.add_resource(resources, ResourceType.WOOD, 0)

        assert result.wood == 2

    def test_add_negative_raises_error(self):
        """Should raise error for negative amount."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)

        with pytest.raises(ValueError):
            ResourceService.add_resource(resources, ResourceType.WOOD, -1)

    def test_add_multiple_resources(self):
        """Should add multiple resource types at once."""
        resources = Resources(wood=0, stone=0, tile=0, ink=0)

        result = ResourceService.add_multiple(resources, {
            ResourceType.WOOD: 2,
            ResourceType.STONE: 3,
            ResourceType.INK: 1,
        })

        assert result.wood == 2
        assert result.stone == 3
        assert result.tile == 0
        assert result.ink == 1


class TestConsumeResource:
    """Tests for consuming resources."""

    def test_consume_single_resource(self):
        """Should consume single resource if available."""
        resources = Resources(wood=5, stone=3, tile=2, ink=1)

        result = ResourceService.consume_resource(resources, ResourceType.WOOD, 3)

        assert result.wood == 2
        assert result.stone == 3  # Unchanged

    def test_consume_all_resources(self):
        """Should consume all of a resource type."""
        resources = Resources(wood=3, stone=2, tile=0, ink=0)

        result = ResourceService.consume_resource(resources, ResourceType.WOOD, 3)

        assert result.wood == 0

    def test_consume_insufficient_raises_error(self):
        """Should raise error when insufficient resources."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)

        with pytest.raises(ValueError) as exc_info:
            ResourceService.consume_resource(resources, ResourceType.WOOD, 5)

        assert "Not enough wood" in str(exc_info.value)

    def test_consume_zero_is_valid(self):
        """Should handle consuming zero."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)

        result = ResourceService.consume_resource(resources, ResourceType.WOOD, 0)

        assert result.wood == 2

    def test_consume_negative_raises_error(self):
        """Should raise error for negative amount."""
        resources = Resources(wood=5, stone=2, tile=0, ink=0)

        with pytest.raises(ValueError):
            ResourceService.consume_resource(resources, ResourceType.WOOD, -1)


class TestCanAfford:
    """Tests for resource affordability check."""

    def test_can_afford_true(self):
        """Should return True when can afford cost."""
        resources = Resources(wood=5, stone=3, tile=2, ink=1)
        cost = {
            ResourceType.WOOD: 3,
            ResourceType.STONE: 2,
        }

        assert ResourceService.can_afford(resources, cost) is True

    def test_can_afford_exact_amount(self):
        """Should return True for exact amount."""
        resources = Resources(wood=3, stone=2, tile=0, ink=0)
        cost = {
            ResourceType.WOOD: 3,
            ResourceType.STONE: 2,
        }

        assert ResourceService.can_afford(resources, cost) is True

    def test_can_afford_false_single_resource(self):
        """Should return False when cannot afford single resource."""
        resources = Resources(wood=2, stone=3, tile=0, ink=0)
        cost = {
            ResourceType.WOOD: 5,
        }

        assert ResourceService.can_afford(resources, cost) is False

    def test_can_afford_false_multiple_resources(self):
        """Should return False when cannot afford one of multiple resources."""
        resources = Resources(wood=5, stone=1, tile=0, ink=0)
        cost = {
            ResourceType.WOOD: 3,
            ResourceType.STONE: 2,  # Only have 1
        }

        assert ResourceService.can_afford(resources, cost) is False

    def test_can_afford_empty_cost(self):
        """Should return True for empty cost."""
        resources = Resources(wood=2, stone=2, tile=0, ink=0)

        assert ResourceService.can_afford(resources, {}) is True


class TestPayCost:
    """Tests for paying resource costs."""

    def test_pay_cost_success(self):
        """Should deduct resources when paying cost."""
        resources = Resources(wood=5, stone=3, tile=2, ink=1)
        cost = {
            ResourceType.WOOD: 2,
            ResourceType.STONE: 1,
        }

        result = ResourceService.pay_cost(resources, cost)

        assert result.wood == 3
        assert result.stone == 2
        assert result.tile == 2  # Unchanged
        assert result.ink == 1  # Unchanged

    def test_pay_cost_insufficient_raises_error(self):
        """Should raise error when cannot afford."""
        resources = Resources(wood=1, stone=3, tile=0, ink=0)
        cost = {
            ResourceType.WOOD: 2,
        }

        with pytest.raises(ValueError) as exc_info:
            ResourceService.pay_cost(resources, cost)

        assert "Cannot afford" in str(exc_info.value)


class TestResourceScore:
    """Tests for resource score calculation."""

    def test_calculate_score_multiple_of_three(self):
        """Should calculate score for resources divisible by 3."""
        resources = Resources(wood=3, stone=3, tile=3, ink=0)  # Total: 9

        score = ResourceService.calculate_resource_score(resources)

        assert score == 3  # 9 / 3 = 3

    def test_calculate_score_with_remainder(self):
        """Should truncate when not divisible by 3."""
        resources = Resources(wood=4, stone=3, tile=1, ink=0)  # Total: 8

        score = ResourceService.calculate_resource_score(resources)

        assert score == 2  # 8 / 3 = 2 (truncated)

    def test_calculate_score_zero(self):
        """Should return 0 for no resources."""
        resources = Resources(wood=0, stone=0, tile=0, ink=0)

        score = ResourceService.calculate_resource_score(resources)

        assert score == 0

    def test_calculate_score_less_than_three(self):
        """Should return 0 for less than 3 total resources."""
        resources = Resources(wood=1, stone=1, tile=0, ink=0)  # Total: 2

        score = ResourceService.calculate_resource_score(resources)

        assert score == 0


class TestResourceSerialization:
    """Tests for resource serialization."""

    def test_to_dict(self):
        """Should serialize to dictionary."""
        resources = Resources(wood=5, stone=3, tile=2, ink=1)

        data = resources.to_dict()

        assert data == {"wood": 5, "stone": 3, "tile": 2, "ink": 1}

    def test_from_dict(self):
        """Should deserialize from dictionary."""
        data = {"wood": 5, "stone": 3, "tile": 2, "ink": 1}

        resources = Resources.from_dict(data)

        assert resources.wood == 5
        assert resources.stone == 3
        assert resources.tile == 2
        assert resources.ink == 1

    def test_from_dict_with_missing_keys(self):
        """Should handle missing keys with defaults."""
        data = {"wood": 5}

        resources = Resources.from_dict(data)

        assert resources.wood == 5
        assert resources.stone == 0
        assert resources.tile == 0
        assert resources.ink == 0
