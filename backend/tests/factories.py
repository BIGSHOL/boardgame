"""
Test factories for generating test data.
Uses Factory Boy for model factories.
"""
import factory
from factory import LazyAttribute, Sequence
from datetime import datetime, timezone

from app.models.user import User
from app.schemas.game import (
    Resources,
    WorkerState,
    PlayerWorkers,
    BoardPosition,
    BoardCell,
    TerrainType,
    GamePlayer,
    PlayerColor,
)


class UserFactory(factory.Factory):
    """User model factory."""

    class Meta:
        model = User

    id = Sequence(lambda n: n + 1)
    email = LazyAttribute(lambda o: f"user{o.id}@example.com")
    username = LazyAttribute(lambda o: f"player{o.id}")
    hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTX0Y5P6Q3kMqW"  # "password"
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class ResourcesFactory(factory.Factory):
    """Resources factory."""

    class Meta:
        model = Resources

    wood = 2
    stone = 2
    tile = 1
    ink = 1


class WorkerStateFactory(factory.Factory):
    """WorkerState factory."""

    class Meta:
        model = WorkerState

    total = 5
    available = 5
    placed = 0


class PlayerWorkersFactory(factory.Factory):
    """PlayerWorkers factory."""

    class Meta:
        model = PlayerWorkers

    apprentices = factory.SubFactory(WorkerStateFactory, total=5, available=5)
    officials = factory.SubFactory(WorkerStateFactory, total=4, available=4)


class BoardPositionFactory(factory.Factory):
    """BoardPosition factory."""

    class Meta:
        model = BoardPosition

    row = 0
    col = 0


class BoardCellFactory(factory.Factory):
    """BoardCell factory."""

    class Meta:
        model = BoardCell

    position = factory.SubFactory(BoardPositionFactory)
    terrain = TerrainType.NORMAL
    tile = None


class GamePlayerFactory(factory.Factory):
    """GamePlayer factory."""

    class Meta:
        model = GamePlayer

    id = Sequence(lambda n: n + 1)
    user_id = Sequence(lambda n: n + 1)
    username = LazyAttribute(lambda o: f"player{o.id}")
    color = factory.Iterator([PlayerColor.BLUE, PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW])
    turn_order = Sequence(lambda n: n)
    is_host = False
    is_ready = True
    resources = factory.SubFactory(ResourcesFactory)
    workers = factory.SubFactory(PlayerWorkersFactory)
    blueprints = []
    score = 0
    placed_tiles = []


def create_empty_board() -> list[list[BoardCell]]:
    """Create an empty 5x5 game board."""
    board = []
    for row in range(5):
        row_cells = []
        for col in range(5):
            terrain = TerrainType.NORMAL
            # Add mountains in the north (row 0)
            if row == 0 and col in [1, 2, 3]:
                terrain = TerrainType.MOUNTAIN
            # Add water in the south (row 4)
            if row == 4 and col in [1, 2, 3]:
                terrain = TerrainType.WATER

            cell = BoardCellFactory(
                position=BoardPosition(row=row, col=col),
                terrain=terrain,
            )
            row_cells.append(cell)
        board.append(row_cells)
    return board


def create_game_players(count: int = 2) -> list[GamePlayer]:
    """Create a list of game players."""
    colors = [PlayerColor.BLUE, PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW]
    players = []
    for i in range(count):
        player = GamePlayerFactory(
            id=i + 1,
            user_id=i + 1,
            username=f"player{i + 1}",
            color=colors[i],
            turn_order=i,
            is_host=(i == 0),
        )
        players.append(player)
    return players
