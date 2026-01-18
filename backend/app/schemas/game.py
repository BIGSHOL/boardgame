"""
Game schemas - Pydantic models for game state and actions.
Synchronized with contracts/types.ts and contracts/game.contract.ts
"""
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ============================================
# Enums
# ============================================

class ResourceType(str, Enum):
    WOOD = "wood"
    STONE = "stone"
    TILE = "tile"
    INK = "ink"


class WorkerType(str, Enum):
    APPRENTICE = "apprentice"
    OFFICIAL = "official"


class BuildingCategory(str, Enum):
    PALACE = "palace"
    GOVERNMENT = "government"
    RELIGIOUS = "religious"
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"
    GATE = "gate"


class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class PlayerColor(str, Enum):
    BLUE = "blue"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"


class ActionType(str, Enum):
    PLACE_WORKER = "place_worker"
    RECALL_WORKER = "recall_worker"
    PLACE_TILE = "place_tile"
    DRAW_BLUEPRINT = "draw_blueprint"
    END_TURN = "end_turn"
    PASS = "pass"


class TerrainType(str, Enum):
    NORMAL = "normal"
    MOUNTAIN = "mountain"
    WATER = "water"


# ============================================
# Resource & Worker
# ============================================

class Resources(BaseModel):
    """자원 보유량"""
    wood: int = 0
    stone: int = 0
    tile: int = 0
    ink: int = 0


class WorkerState(BaseModel):
    """워커 상태"""
    total: int
    available: int
    placed: int = 0


class PlayerWorkers(BaseModel):
    """플레이어 워커 전체 상태"""
    apprentices: WorkerState
    officials: WorkerState


# ============================================
# Board
# ============================================

class BoardPosition(BaseModel):
    """보드 좌표"""
    row: int = Field(..., ge=0, le=4)
    col: int = Field(..., ge=0, le=4)


class PlacedWorker(BaseModel):
    """배치된 워커"""
    player_id: int
    worker_type: WorkerType
    slot_index: int


class PlacedTile(BaseModel):
    """배치된 타일"""
    tile_id: str
    owner_id: int
    placed_workers: list[PlacedWorker] = []
    fengshui_active: bool = False


class BoardCell(BaseModel):
    """보드 셀"""
    position: BoardPosition
    terrain: TerrainType = TerrainType.NORMAL
    tile: PlacedTile | None = None


# ============================================
# Player
# ============================================

class PlayerBase(BaseModel):
    """플레이어 기본 정보"""
    id: int
    user_id: int
    username: str
    color: PlayerColor
    turn_order: int
    is_host: bool = False
    is_ready: bool = False


class GamePlayer(PlayerBase):
    """게임 내 플레이어 상태"""
    resources: Resources = Field(default_factory=Resources)
    workers: PlayerWorkers
    blueprints: list[str] = []
    score: int = 0
    placed_tiles: list[str] = []


# ============================================
# Action Payloads
# ============================================

class PlaceWorkerPayload(BaseModel):
    """워커 배치 페이로드"""
    type: Literal["place_worker"] = "place_worker"
    worker_type: WorkerType
    target_position: BoardPosition
    slot_index: int


class RecallWorkerPayload(BaseModel):
    """워커 회수 페이로드"""
    type: Literal["recall_worker"] = "recall_worker"
    worker_type: WorkerType
    from_position: BoardPosition
    slot_index: int


class PlaceTilePayload(BaseModel):
    """타일 배치 페이로드"""
    type: Literal["place_tile"] = "place_tile"
    tile_id: str
    position: BoardPosition


class DrawBlueprintPayload(BaseModel):
    """청사진 드로우 페이로드"""
    type: Literal["draw_blueprint"] = "draw_blueprint"
    blueprint_id: str


class EndTurnPayload(BaseModel):
    """턴 종료 페이로드"""
    type: Literal["end_turn"] = "end_turn"


class PassPayload(BaseModel):
    """패스 페이로드"""
    type: Literal["pass"] = "pass"


ActionPayload = (
    PlaceWorkerPayload
    | RecallWorkerPayload
    | PlaceTilePayload
    | DrawBlueprintPayload
    | EndTurnPayload
    | PassPayload
)


# ============================================
# Game Action
# ============================================

class GameActionRequest(BaseModel):
    """게임 액션 요청"""
    action_type: ActionType
    payload: ActionPayload


class GameAction(BaseModel):
    """게임 액션"""
    id: int
    game_id: int
    player_id: int
    action_type: ActionType
    payload: dict  # JSON serialized payload
    timestamp: datetime


# ============================================
# Game State
# ============================================

class GameState(BaseModel):
    """게임 전체 상태"""
    id: int
    lobby_id: int
    status: GameStatus
    current_round: int
    total_rounds: int
    current_turn_player_id: int
    turn_order: list[int]
    board: list[list[BoardCell]]  # 5x5 grid
    players: list[GamePlayer]
    available_tiles: list[str]
    discarded_tiles: list[str]
    last_action: GameAction | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Response Types
# ============================================

class BonusAwarded(BaseModel):
    """보너스 정보"""
    fengshui_bonus: int | None = None
    adjacency_bonus: int | None = None
    blueprint_completed: str | None = None


class GameActionResponse(BaseModel):
    """게임 액션 응답"""
    action: GameAction
    new_state: GameState
    bonus_awarded: BonusAwarded | None = None


class ValidActionOption(BaseModel):
    """유효 액션 옵션"""
    position: BoardPosition | None = None
    tile_id: str | None = None
    worker_type: WorkerType | None = None
    slot_index: int | None = None


class ValidAction(BaseModel):
    """유효 액션"""
    action_type: ActionType
    options: list[ValidActionOption] = []


class ValidActionsResponse(BaseModel):
    """유효 액션 목록"""
    valid_actions: list[ValidAction]


class ScoreBreakdown(BaseModel):
    """점수 상세"""
    building_points: int = 0
    fengshui_bonus: int = 0
    adjacency_bonus: int = 0
    blueprint_bonus: int = 0
    remaining_resources: int = 0
    total: int = 0


class PlayerRanking(BaseModel):
    """플레이어 랭킹"""
    player_id: int
    username: str
    rank: int
    score_breakdown: ScoreBreakdown


class GameResultResponse(BaseModel):
    """게임 결과 응답"""
    game_id: int
    winner_id: int
    rankings: list[PlayerRanking]
    duration_minutes: int
    total_rounds: int


class SubmitFeedbackRequest(BaseModel):
    """피드백 제출 요청"""
    rating: int = Field(..., ge=1, le=5)
    comments: str
    balance_feedback: str | None = None
    bug_reports: str | None = None
