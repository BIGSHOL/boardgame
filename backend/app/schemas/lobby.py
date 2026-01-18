"""
Lobby schemas - Pydantic models for lobby management.
Synchronized with contracts/lobby.contract.ts
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.game import PlayerColor


class LobbyStatus(str, Enum):
    WAITING = "waiting"
    READY = "ready"
    STARTING = "starting"
    STARTED = "started"


# ============================================
# Player
# ============================================

class LobbyPlayer(BaseModel):
    """로비 플레이어"""
    id: int
    user_id: int
    username: str
    color: PlayerColor
    turn_order: int
    is_host: bool = False
    is_ready: bool = False

    class Config:
        from_attributes = True


# Alias for router compatibility
LobbyPlayerResponse = LobbyPlayer


# ============================================
# Request Types
# ============================================

class CreateLobbyRequest(BaseModel):
    """로비 생성 요청"""
    name: str = Field(..., min_length=1, max_length=50)
    max_players: int = Field(default=4, ge=2, le=4)


class JoinLobbyRequest(BaseModel):
    """로비 참가 요청"""
    invite_code: str = Field(..., min_length=6, max_length=6)


class ReadyRequest(BaseModel):
    """준비 상태 변경 요청"""
    is_ready: bool


# ============================================
# Response Types
# ============================================

class LobbyResponse(BaseModel):
    """로비 응답"""
    id: int
    name: str
    host_id: int
    invite_code: str
    status: LobbyStatus
    max_players: int
    game_id: int | None = None
    players: list[LobbyPlayer]
    created_at: datetime

    class Config:
        from_attributes = True


class LobbyListResponse(BaseModel):
    """로비 목록 응답"""
    lobbies: list[LobbyResponse]
    total: int


class JoinLobbyResponse(BaseModel):
    """로비 참가 응답"""
    lobby: LobbyResponse
    player: LobbyPlayer


class StartGameResponse(BaseModel):
    """게임 시작 응답"""
    game_id: int
