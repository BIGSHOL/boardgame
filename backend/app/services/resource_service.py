"""
Resource management service.
Handles resource addition, consumption, and validation.
"""
from dataclasses import dataclass
from enum import Enum


class ResourceType(str, Enum):
    """Resource types in the game."""
    WOOD = "wood"
    STONE = "stone"
    TILE = "tile"
    INK = "ink"


@dataclass
class Resources:
    """Player resources."""
    wood: int = 0
    stone: int = 0
    tile: int = 0
    ink: int = 0

    def to_dict(self) -> dict:
        return {
            "wood": self.wood,
            "stone": self.stone,
            "tile": self.tile,
            "ink": self.ink,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Resources":
        return cls(
            wood=data.get("wood", 0),
            stone=data.get("stone", 0),
            tile=data.get("tile", 0),
            ink=data.get("ink", 0),
        )


class ResourceService:
    """Service for managing player resources."""

    # Initial resources for each player
    INITIAL_RESOURCES = Resources(wood=2, stone=2, tile=0, ink=0)

    # Maximum resources a player can hold
    MAX_RESOURCES = {
        ResourceType.WOOD: 10,
        ResourceType.STONE: 10,
        ResourceType.TILE: 6,
        ResourceType.INK: 4,
    }

    @staticmethod
    def get_initial_resources() -> Resources:
        """Get initial resources for a new player."""
        return Resources(
            wood=ResourceService.INITIAL_RESOURCES.wood,
            stone=ResourceService.INITIAL_RESOURCES.stone,
            tile=ResourceService.INITIAL_RESOURCES.tile,
            ink=ResourceService.INITIAL_RESOURCES.ink,
        )

    @staticmethod
    def add_resource(
        resources: Resources,
        resource_type: ResourceType,
        amount: int,
    ) -> Resources:
        """
        Add resources to player's inventory.
        Respects maximum limits.

        Args:
            resources: Current resources
            resource_type: Type of resource to add
            amount: Amount to add

        Returns:
            Updated resources (new instance)
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        current = getattr(resources, resource_type.value)
        max_limit = ResourceService.MAX_RESOURCES[resource_type]
        new_value = min(current + amount, max_limit)

        new_resources = Resources(
            wood=resources.wood,
            stone=resources.stone,
            tile=resources.tile,
            ink=resources.ink,
        )
        setattr(new_resources, resource_type.value, new_value)
        return new_resources

    @staticmethod
    def consume_resource(
        resources: Resources,
        resource_type: ResourceType,
        amount: int,
    ) -> Resources:
        """
        Consume resources from player's inventory.

        Args:
            resources: Current resources
            resource_type: Type of resource to consume
            amount: Amount to consume

        Returns:
            Updated resources (new instance)

        Raises:
            ValueError: If not enough resources
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        current = getattr(resources, resource_type.value)
        if current < amount:
            raise ValueError(
                f"Not enough {resource_type.value}: have {current}, need {amount}"
            )

        new_resources = Resources(
            wood=resources.wood,
            stone=resources.stone,
            tile=resources.tile,
            ink=resources.ink,
        )
        setattr(new_resources, resource_type.value, current - amount)
        return new_resources

    @staticmethod
    def can_afford(resources: Resources, cost: dict[ResourceType, int]) -> bool:
        """
        Check if player can afford a cost.

        Args:
            resources: Current resources
            cost: Dictionary of resource type to amount needed

        Returns:
            True if player can afford, False otherwise
        """
        for resource_type, amount in cost.items():
            current = getattr(resources, resource_type.value)
            if current < amount:
                return False
        return True

    @staticmethod
    def pay_cost(resources: Resources, cost: dict[ResourceType, int]) -> Resources:
        """
        Pay a cost from player's resources.

        Args:
            resources: Current resources
            cost: Dictionary of resource type to amount needed

        Returns:
            Updated resources after paying

        Raises:
            ValueError: If not enough resources
        """
        if not ResourceService.can_afford(resources, cost):
            raise ValueError("Cannot afford cost")

        result = resources
        for resource_type, amount in cost.items():
            result = ResourceService.consume_resource(result, resource_type, amount)
        return result

    @staticmethod
    def add_multiple(
        resources: Resources,
        additions: dict[ResourceType, int],
    ) -> Resources:
        """
        Add multiple resources at once.

        Args:
            resources: Current resources
            additions: Dictionary of resource type to amount to add

        Returns:
            Updated resources after additions
        """
        result = resources
        for resource_type, amount in additions.items():
            result = ResourceService.add_resource(result, resource_type, amount)
        return result

    @staticmethod
    def calculate_resource_score(resources: Resources) -> int:
        """
        Calculate score from remaining resources at game end.
        Every 3 resources = 1 point.

        Args:
            resources: Player's remaining resources

        Returns:
            Score from remaining resources
        """
        total = resources.wood + resources.stone + resources.tile + resources.ink
        return total // 3
