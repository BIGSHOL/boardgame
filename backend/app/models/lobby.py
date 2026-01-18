"""
Lobby and LobbyPlayer models for game lobby system.
"""
import random
import string
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LobbyStatus(str, Enum):
    """Lobby status enum."""
    WAITING = "waiting"
    READY = "ready"
    STARTED = "started"
    CANCELLED = "cancelled"


class PlayerColor(str, Enum):
    """Player color enum."""
    BLUE = "blue"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"


def generate_invite_code() -> str:
    """Generate a 6-character invite code (excluding ambiguous characters)."""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choice(chars) for _ in range(6))


class Lobby(Base):
    """Lobby model for game rooms."""

    __tablename__ = "lobbies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    invite_code: Mapped[str] = mapped_column(
        String(6), unique=True, index=True, nullable=False, default=generate_invite_code
    )
    status: Mapped[LobbyStatus] = mapped_column(
        SQLEnum(LobbyStatus), default=LobbyStatus.WAITING
    )
    max_players: Mapped[int] = mapped_column(default=4)
    game_id: Mapped[int | None] = mapped_column(ForeignKey("games.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    host = relationship("User", foreign_keys=[host_id])
    players: Mapped[list["LobbyPlayer"]] = relationship(
        "LobbyPlayer", back_populates="lobby", cascade="all, delete-orphan"
    )


class LobbyPlayer(Base):
    """Player in a lobby."""

    __tablename__ = "lobby_players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lobby_id: Mapped[int] = mapped_column(ForeignKey("lobbies.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    color: Mapped[PlayerColor] = mapped_column(SQLEnum(PlayerColor), nullable=False)
    turn_order: Mapped[int] = mapped_column(nullable=False)
    is_ready: Mapped[bool] = mapped_column(default=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    lobby: Mapped[Lobby] = relationship("Lobby", back_populates="players")
    user = relationship("User")
