"""
Worker management service.
Handles worker placement, recall, and validation.
"""
from dataclasses import dataclass, field
from enum import Enum


class WorkerType(str, Enum):
    """Worker types in the game."""
    APPRENTICE = "apprentice"
    OFFICIAL = "official"


@dataclass
class WorkerState:
    """State of a single worker type."""
    total: int
    available: int
    placed: int = 0

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "available": self.available,
            "placed": self.placed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkerState":
        return cls(
            total=data.get("total", 0),
            available=data.get("available", 0),
            placed=data.get("placed", 0),
        )


@dataclass
class PlayerWorkers:
    """All workers for a player."""
    apprentices: WorkerState
    officials: WorkerState

    def to_dict(self) -> dict:
        return {
            "apprentices": self.apprentices.to_dict(),
            "officials": self.officials.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlayerWorkers":
        return cls(
            apprentices=WorkerState.from_dict(data.get("apprentices", {})),
            officials=WorkerState.from_dict(data.get("officials", {})),
        )


@dataclass
class PlacedWorker:
    """A worker placed on the board."""
    player_id: int
    worker_type: WorkerType
    slot_index: int

    def to_dict(self) -> dict:
        return {
            "player_id": self.player_id,
            "worker_type": self.worker_type.value,
            "slot_index": self.slot_index,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlacedWorker":
        return cls(
            player_id=data["player_id"],
            worker_type=WorkerType(data["worker_type"]),
            slot_index=data["slot_index"],
        )


class WorkerService:
    """Service for managing workers."""

    # Initial worker counts
    INITIAL_APPRENTICES = 3
    INITIAL_OFFICIALS = 2

    # Worker slots per tile
    APPRENTICE_SLOTS = 2
    OFFICIAL_SLOTS = 1

    @staticmethod
    def get_initial_workers() -> PlayerWorkers:
        """Get initial workers for a new player."""
        return PlayerWorkers(
            apprentices=WorkerState(
                total=WorkerService.INITIAL_APPRENTICES,
                available=WorkerService.INITIAL_APPRENTICES,
                placed=0,
            ),
            officials=WorkerState(
                total=WorkerService.INITIAL_OFFICIALS,
                available=WorkerService.INITIAL_OFFICIALS,
                placed=0,
            ),
        )

    @staticmethod
    def can_place_worker(
        workers: PlayerWorkers,
        worker_type: WorkerType,
    ) -> bool:
        """
        Check if player can place a worker of given type.

        Args:
            workers: Player's current workers
            worker_type: Type of worker to place

        Returns:
            True if worker can be placed
        """
        if worker_type == WorkerType.APPRENTICE:
            return workers.apprentices.available > 0
        else:
            return workers.officials.available > 0

    @staticmethod
    def place_worker(
        workers: PlayerWorkers,
        worker_type: WorkerType,
    ) -> PlayerWorkers:
        """
        Place a worker (mark as placed).

        Args:
            workers: Current workers
            worker_type: Type of worker to place

        Returns:
            Updated workers state

        Raises:
            ValueError: If no workers available
        """
        if not WorkerService.can_place_worker(workers, worker_type):
            raise ValueError(f"No {worker_type.value} workers available")

        new_workers = PlayerWorkers(
            apprentices=WorkerState(
                total=workers.apprentices.total,
                available=workers.apprentices.available,
                placed=workers.apprentices.placed,
            ),
            officials=WorkerState(
                total=workers.officials.total,
                available=workers.officials.available,
                placed=workers.officials.placed,
            ),
        )

        if worker_type == WorkerType.APPRENTICE:
            new_workers.apprentices.available -= 1
            new_workers.apprentices.placed += 1
        else:
            new_workers.officials.available -= 1
            new_workers.officials.placed += 1

        return new_workers

    @staticmethod
    def recall_worker(
        workers: PlayerWorkers,
        worker_type: WorkerType,
    ) -> PlayerWorkers:
        """
        Recall a worker (mark as available).

        Args:
            workers: Current workers
            worker_type: Type of worker to recall

        Returns:
            Updated workers state

        Raises:
            ValueError: If no workers to recall
        """
        if worker_type == WorkerType.APPRENTICE:
            if workers.apprentices.placed <= 0:
                raise ValueError("No apprentice workers to recall")
        else:
            if workers.officials.placed <= 0:
                raise ValueError("No official workers to recall")

        new_workers = PlayerWorkers(
            apprentices=WorkerState(
                total=workers.apprentices.total,
                available=workers.apprentices.available,
                placed=workers.apprentices.placed,
            ),
            officials=WorkerState(
                total=workers.officials.total,
                available=workers.officials.available,
                placed=workers.officials.placed,
            ),
        )

        if worker_type == WorkerType.APPRENTICE:
            new_workers.apprentices.available += 1
            new_workers.apprentices.placed -= 1
        else:
            new_workers.officials.available += 1
            new_workers.officials.placed -= 1

        return new_workers

    @staticmethod
    def can_place_on_tile(
        placed_workers: list[PlacedWorker],
        worker_type: WorkerType,
        slot_index: int,
    ) -> bool:
        """
        Check if a worker can be placed on a tile slot.

        Args:
            placed_workers: Workers already on the tile
            worker_type: Type of worker to place
            slot_index: Target slot index

        Returns:
            True if placement is valid
        """
        # Check slot index bounds
        if worker_type == WorkerType.APPRENTICE:
            if slot_index < 0 or slot_index >= WorkerService.APPRENTICE_SLOTS:
                return False
        else:
            if slot_index < 0 or slot_index >= WorkerService.OFFICIAL_SLOTS:
                return False

        # Check if slot is already occupied
        for worker in placed_workers:
            if worker.worker_type == worker_type and worker.slot_index == slot_index:
                return False

        return True

    @staticmethod
    def get_worker_production(
        placed_workers: list[PlacedWorker],
        player_id: int,
    ) -> dict:
        """
        Calculate resource production from workers on a tile.

        Args:
            placed_workers: Workers on the tile
            player_id: Player to calculate for

        Returns:
            Dictionary of resources produced
        """
        # Base production per worker type
        # Apprentice: 1 resource
        # Official: 2 resources (or special ability)
        apprentice_count = sum(
            1 for w in placed_workers
            if w.player_id == player_id and w.worker_type == WorkerType.APPRENTICE
        )
        official_count = sum(
            1 for w in placed_workers
            if w.player_id == player_id and w.worker_type == WorkerType.OFFICIAL
        )

        return {
            "apprentice_production": apprentice_count,
            "official_production": official_count * 2,
            "total": apprentice_count + (official_count * 2),
        }

    @staticmethod
    def recall_all_workers(workers: PlayerWorkers) -> PlayerWorkers:
        """
        Recall all placed workers (end of round).

        Args:
            workers: Current workers state

        Returns:
            Workers with all recalled
        """
        return PlayerWorkers(
            apprentices=WorkerState(
                total=workers.apprentices.total,
                available=workers.apprentices.total,
                placed=0,
            ),
            officials=WorkerState(
                total=workers.officials.total,
                available=workers.officials.total,
                placed=0,
            ),
        )
