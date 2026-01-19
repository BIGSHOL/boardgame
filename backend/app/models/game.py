"""
Game model for game state management.
"""
import json
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GameStatus(str, Enum):
    """Game status enum."""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Game(Base):
    """Game model storing game state."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lobby_id: Mapped[int | None] = mapped_column(ForeignKey("lobbies.id"), nullable=True)
    status: Mapped[GameStatus] = mapped_column(
        SQLEnum(GameStatus), default=GameStatus.WAITING
    )
    current_round: Mapped[int] = mapped_column(default=1)
    total_rounds: Mapped[int] = mapped_column(default=8)
    # Note: Not a ForeignKey because AI players have negative IDs
    current_turn_player_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # JSON fields stored as Text
    turn_order_json: Mapped[str] = mapped_column(Text, default="[]")
    board_json: Mapped[str] = mapped_column(Text, default="[]")
    players_json: Mapped[str] = mapped_column(Text, default="[]")
    available_tiles_json: Mapped[str] = mapped_column(Text, default="[]")
    discarded_tiles_json: Mapped[str] = mapped_column(Text, default="[]")
    last_action_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    lobby = relationship("Lobby", foreign_keys=[lobby_id])
    actions: Mapped[list["GameAction"]] = relationship(
        "GameAction", back_populates="game", cascade="all, delete-orphan"
    )

    @property
    def turn_order(self) -> list[int]:
        return json.loads(self.turn_order_json)

    @turn_order.setter
    def turn_order(self, value: list[int]):
        self.turn_order_json = json.dumps(value)

    @property
    def board(self) -> list[list[dict]]:
        return json.loads(self.board_json)

    @board.setter
    def board(self, value: list[list[dict]]):
        self.board_json = json.dumps(value)

    @property
    def players(self) -> list[dict]:
        return json.loads(self.players_json)

    @players.setter
    def players(self, value: list[dict]):
        self.players_json = json.dumps(value)

    @property
    def available_tiles(self) -> list[str]:
        return json.loads(self.available_tiles_json)

    @available_tiles.setter
    def available_tiles(self, value: list[str]):
        self.available_tiles_json = json.dumps(value)

    @property
    def discarded_tiles(self) -> list[str]:
        return json.loads(self.discarded_tiles_json)

    @discarded_tiles.setter
    def discarded_tiles(self, value: list[str]):
        self.discarded_tiles_json = json.dumps(value)

    @property
    def last_action(self) -> dict | None:
        if self.last_action_json:
            return json.loads(self.last_action_json)
        return None

    @last_action.setter
    def last_action(self, value: dict | None):
        self.last_action_json = json.dumps(value) if value else None


class GameAction(Base):
    """Game action record."""

    __tablename__ = "game_actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    # Note: Not a ForeignKey because AI players have negative IDs (e.g., -1, -2)
    player_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    game: Mapped[Game] = relationship("Game", back_populates="actions")
    # Note: player relationship removed - AI players don't exist in users table

    @property
    def payload(self) -> dict:
        return json.loads(self.payload_json)

    @payload.setter
    def payload(self, value: dict):
        self.payload_json = json.dumps(value)
