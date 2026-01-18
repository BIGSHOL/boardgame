"""
Worker service tests.
Tests for worker placement and management logic.

TDD Status: GREEN (tests and implementation complete)
"""
import pytest

from app.services.worker_service import (
    WorkerService,
    WorkerType,
    WorkerState,
    PlayerWorkers,
    PlacedWorker,
)


class TestInitialWorkers:
    """Tests for initial worker setup."""

    def test_get_initial_workers(self):
        """Should return correct initial workers."""
        workers = WorkerService.get_initial_workers()

        assert workers.apprentices.total == 3
        assert workers.apprentices.available == 3
        assert workers.apprentices.placed == 0
        assert workers.officials.total == 2
        assert workers.officials.available == 2
        assert workers.officials.placed == 0

    def test_initial_workers_are_new_instances(self):
        """Should return new instance each time."""
        workers1 = WorkerService.get_initial_workers()
        workers2 = WorkerService.get_initial_workers()

        workers1.apprentices.available = 0
        assert workers2.apprentices.available == 3  # Not affected


class TestCanPlaceWorker:
    """Tests for worker placement availability check."""

    def test_can_place_apprentice_when_available(self):
        """Should return True when apprentices available."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=2, placed=1),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        assert WorkerService.can_place_worker(workers, WorkerType.APPRENTICE) is True

    def test_cannot_place_apprentice_when_none_available(self):
        """Should return False when no apprentices available."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=0, placed=3),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        assert WorkerService.can_place_worker(workers, WorkerType.APPRENTICE) is False

    def test_can_place_official_when_available(self):
        """Should return True when officials available."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=1, placed=1),
        )

        assert WorkerService.can_place_worker(workers, WorkerType.OFFICIAL) is True

    def test_cannot_place_official_when_none_available(self):
        """Should return False when no officials available."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=0, placed=2),
        )

        assert WorkerService.can_place_worker(workers, WorkerType.OFFICIAL) is False


class TestPlaceWorker:
    """Tests for placing workers."""

    def test_place_apprentice(self):
        """Should decrement available and increment placed for apprentice."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        result = WorkerService.place_worker(workers, WorkerType.APPRENTICE)

        assert result.apprentices.available == 2
        assert result.apprentices.placed == 1
        assert result.officials.available == 2  # Unchanged

    def test_place_official(self):
        """Should decrement available and increment placed for official."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        result = WorkerService.place_worker(workers, WorkerType.OFFICIAL)

        assert result.officials.available == 1
        assert result.officials.placed == 1
        assert result.apprentices.available == 3  # Unchanged

    def test_place_returns_new_instance(self):
        """Should not modify original workers."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        result = WorkerService.place_worker(workers, WorkerType.APPRENTICE)

        assert workers.apprentices.available == 3  # Original unchanged
        assert result.apprentices.available == 2

    def test_place_no_available_raises_error(self):
        """Should raise error when no workers available."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=0, placed=3),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        with pytest.raises(ValueError) as exc_info:
            WorkerService.place_worker(workers, WorkerType.APPRENTICE)

        assert "No apprentice workers available" in str(exc_info.value)


class TestRecallWorker:
    """Tests for recalling workers."""

    def test_recall_apprentice(self):
        """Should increment available and decrement placed for apprentice."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=1, placed=2),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        result = WorkerService.recall_worker(workers, WorkerType.APPRENTICE)

        assert result.apprentices.available == 2
        assert result.apprentices.placed == 1

    def test_recall_official(self):
        """Should increment available and decrement placed for official."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=0, placed=2),
        )

        result = WorkerService.recall_worker(workers, WorkerType.OFFICIAL)

        assert result.officials.available == 1
        assert result.officials.placed == 1

    def test_recall_returns_new_instance(self):
        """Should not modify original workers."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=1, placed=2),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        result = WorkerService.recall_worker(workers, WorkerType.APPRENTICE)

        assert workers.apprentices.available == 1  # Original unchanged
        assert result.apprentices.available == 2

    def test_recall_none_placed_raises_error(self):
        """Should raise error when no workers placed."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        with pytest.raises(ValueError) as exc_info:
            WorkerService.recall_worker(workers, WorkerType.APPRENTICE)

        assert "No apprentice workers to recall" in str(exc_info.value)

    def test_recall_official_none_placed_raises_error(self):
        """Should raise error when no officials placed."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=3, placed=0),
            officials=WorkerState(total=2, available=2, placed=0),
        )

        with pytest.raises(ValueError) as exc_info:
            WorkerService.recall_worker(workers, WorkerType.OFFICIAL)

        assert "No official workers to recall" in str(exc_info.value)


class TestRecallAllWorkers:
    """Tests for recalling all workers at once."""

    def test_recall_all_workers(self):
        """Should make all workers available."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=0, placed=3),
            officials=WorkerState(total=2, available=0, placed=2),
        )

        result = WorkerService.recall_all_workers(workers)

        assert result.apprentices.available == 3
        assert result.apprentices.placed == 0
        assert result.officials.available == 2
        assert result.officials.placed == 0

    def test_recall_all_with_partial_placement(self):
        """Should work with partially placed workers."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=1, placed=2),
            officials=WorkerState(total=2, available=1, placed=1),
        )

        result = WorkerService.recall_all_workers(workers)

        assert result.apprentices.available == 3
        assert result.apprentices.placed == 0
        assert result.officials.available == 2
        assert result.officials.placed == 0

    def test_recall_all_preserves_total(self):
        """Should preserve total worker count."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=5, available=2, placed=3),
            officials=WorkerState(total=3, available=1, placed=2),
        )

        result = WorkerService.recall_all_workers(workers)

        assert result.apprentices.total == 5
        assert result.officials.total == 3


class TestCanPlaceOnTile:
    """Tests for tile slot placement validation."""

    def test_can_place_apprentice_on_empty_slot(self):
        """Should allow placing on empty slot."""
        placed_workers: list[PlacedWorker] = []

        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.APPRENTICE, slot_index=0
        ) is True

    def test_cannot_place_apprentice_on_occupied_slot(self):
        """Should not allow placing on occupied slot."""
        placed_workers = [
            PlacedWorker(player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=0)
        ]

        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.APPRENTICE, slot_index=0
        ) is False

    def test_can_place_apprentice_on_different_slot(self):
        """Should allow placing on different slot."""
        placed_workers = [
            PlacedWorker(player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=0)
        ]

        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.APPRENTICE, slot_index=1
        ) is True

    def test_cannot_place_apprentice_invalid_slot_index(self):
        """Should not allow invalid slot index for apprentice."""
        placed_workers: list[PlacedWorker] = []

        # Apprentice has slots 0 and 1 (APPRENTICE_SLOTS = 2)
        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.APPRENTICE, slot_index=2
        ) is False

    def test_cannot_place_apprentice_negative_slot(self):
        """Should not allow negative slot index."""
        placed_workers: list[PlacedWorker] = []

        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.APPRENTICE, slot_index=-1
        ) is False

    def test_can_place_official_on_empty_slot(self):
        """Should allow placing official on empty slot."""
        placed_workers: list[PlacedWorker] = []

        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.OFFICIAL, slot_index=0
        ) is True

    def test_cannot_place_official_invalid_slot_index(self):
        """Should not allow invalid slot index for official."""
        placed_workers: list[PlacedWorker] = []

        # Official has only slot 0 (OFFICIAL_SLOTS = 1)
        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.OFFICIAL, slot_index=1
        ) is False

    def test_different_worker_types_use_different_slots(self):
        """Apprentice and official slots are independent."""
        placed_workers = [
            PlacedWorker(player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=0)
        ]

        # Official slot 0 is still available even though apprentice slot 0 is taken
        assert WorkerService.can_place_on_tile(
            placed_workers, WorkerType.OFFICIAL, slot_index=0
        ) is True


class TestWorkerProduction:
    """Tests for worker production calculation."""

    def test_apprentice_production(self):
        """Each apprentice produces 1 resource."""
        placed_workers = [
            PlacedWorker(player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=0),
            PlacedWorker(player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=1),
        ]

        production = WorkerService.get_worker_production(placed_workers, player_id=1)

        assert production["apprentice_production"] == 2
        assert production["official_production"] == 0
        assert production["total"] == 2

    def test_official_production(self):
        """Each official produces 2 resources."""
        placed_workers = [
            PlacedWorker(player_id=1, worker_type=WorkerType.OFFICIAL, slot_index=0),
        ]

        production = WorkerService.get_worker_production(placed_workers, player_id=1)

        assert production["apprentice_production"] == 0
        assert production["official_production"] == 2
        assert production["total"] == 2

    def test_mixed_production(self):
        """Combined apprentice and official production."""
        placed_workers = [
            PlacedWorker(player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=0),
            PlacedWorker(player_id=1, worker_type=WorkerType.OFFICIAL, slot_index=0),
        ]

        production = WorkerService.get_worker_production(placed_workers, player_id=1)

        assert production["apprentice_production"] == 1
        assert production["official_production"] == 2
        assert production["total"] == 3

    def test_production_only_counts_player_workers(self):
        """Should only count workers belonging to specified player."""
        placed_workers = [
            PlacedWorker(player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=0),
            PlacedWorker(player_id=2, worker_type=WorkerType.APPRENTICE, slot_index=1),
            PlacedWorker(player_id=1, worker_type=WorkerType.OFFICIAL, slot_index=0),
        ]

        production = WorkerService.get_worker_production(placed_workers, player_id=1)

        assert production["apprentice_production"] == 1  # Only player 1's apprentice
        assert production["official_production"] == 2  # Only player 1's official
        assert production["total"] == 3

    def test_no_workers_production(self):
        """Should return zero for no workers."""
        placed_workers: list[PlacedWorker] = []

        production = WorkerService.get_worker_production(placed_workers, player_id=1)

        assert production["total"] == 0


class TestWorkerSerialization:
    """Tests for worker state serialization."""

    def test_worker_state_to_dict(self):
        """Should serialize worker state."""
        state = WorkerState(total=3, available=2, placed=1)

        data = state.to_dict()

        assert data == {"total": 3, "available": 2, "placed": 1}

    def test_worker_state_from_dict(self):
        """Should deserialize worker state."""
        data = {"total": 3, "available": 2, "placed": 1}

        state = WorkerState.from_dict(data)

        assert state.total == 3
        assert state.available == 2
        assert state.placed == 1

    def test_worker_state_from_dict_defaults(self):
        """Should handle missing keys with defaults."""
        data = {"total": 3}

        state = WorkerState.from_dict(data)

        assert state.total == 3
        assert state.available == 0
        assert state.placed == 0

    def test_player_workers_to_dict(self):
        """Should serialize player workers."""
        workers = PlayerWorkers(
            apprentices=WorkerState(total=3, available=2, placed=1),
            officials=WorkerState(total=2, available=1, placed=1),
        )

        data = workers.to_dict()

        assert data == {
            "apprentices": {"total": 3, "available": 2, "placed": 1},
            "officials": {"total": 2, "available": 1, "placed": 1},
        }

    def test_player_workers_from_dict(self):
        """Should deserialize player workers."""
        data = {
            "apprentices": {"total": 3, "available": 2, "placed": 1},
            "officials": {"total": 2, "available": 1, "placed": 1},
        }

        workers = PlayerWorkers.from_dict(data)

        assert workers.apprentices.total == 3
        assert workers.apprentices.available == 2
        assert workers.officials.total == 2
        assert workers.officials.placed == 1

    def test_placed_worker_to_dict(self):
        """Should serialize placed worker."""
        worker = PlacedWorker(
            player_id=1, worker_type=WorkerType.APPRENTICE, slot_index=0
        )

        data = worker.to_dict()

        assert data == {
            "player_id": 1,
            "worker_type": "apprentice",
            "slot_index": 0,
        }

    def test_placed_worker_from_dict(self):
        """Should deserialize placed worker."""
        data = {"player_id": 1, "worker_type": "apprentice", "slot_index": 0}

        worker = PlacedWorker.from_dict(data)

        assert worker.player_id == 1
        assert worker.worker_type == WorkerType.APPRENTICE
        assert worker.slot_index == 0
