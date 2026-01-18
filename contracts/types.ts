/**
 * Hanyang: The Foundation - Core Type Definitions
 * 조선 초기 한양 건설 전략 보드게임
 *
 * 이 파일은 BE/FE 공유 타입 정의입니다.
 * Pydantic 스키마와 1:1 매칭되어야 합니다.
 */

// ============================================
// 기본 열거형 (Enums)
// ============================================

/** 자원 타입 */
export type ResourceType = 'wood' | 'stone' | 'tile' | 'ink';

/** 워커 타입 */
export type WorkerType = 'apprentice' | 'official';

/** 건물 카테고리 */
export type BuildingCategory = 'palace' | 'government' | 'religious' | 'commercial' | 'residential' | 'gate';

/** 게임 상태 */
export type GameStatus = 'waiting' | 'in_progress' | 'finished';

/** 로비 상태 */
export type LobbyStatus = 'waiting' | 'ready' | 'starting' | 'started';

/** 플레이어 색상 */
export type PlayerColor = 'blue' | 'red' | 'green' | 'yellow';

/** 게임 액션 타입 */
export type ActionType =
  | 'place_worker'      // 워커 배치
  | 'recall_worker'     // 워커 회수
  | 'place_tile'        // 타일 배치
  | 'draw_blueprint'    // 청사진 드로우
  | 'end_turn'          // 턴 종료
  | 'pass';             // 패스

// ============================================
// 자원 및 워커
// ============================================

/** 자원 보유량 */
export interface Resources {
  wood: number;
  stone: number;
  tile: number;
  ink: number;
}

/** 워커 상태 */
export interface WorkerState {
  total: number;      // 총 보유 수
  available: number;  // 사용 가능 수
  placed: number;     // 배치된 수
}

/** 플레이어 워커 전체 상태 */
export interface PlayerWorkers {
  apprentices: WorkerState;  // 견습생 (턴마다 회수)
  officials: WorkerState;    // 관리 (영구 배치)
}

// ============================================
// 건물 및 청사진
// ============================================

/** 건물 타일 정의 (마스터 데이터) */
export interface BuildingTile {
  id: string;
  name: string;
  nameKo: string;
  category: BuildingCategory;
  cost: Partial<Resources>;
  points: number;
  workerSlots: number;        // 워커 배치 가능 슬롯 수
  adjacencyBonus?: AdjacencyBonus[];
  fengshuiBonus?: FengshuiBonus;
}

/** 청사진 카드 정의 (마스터 데이터) */
export interface BlueprintCard {
  id: string;
  name: string;
  nameKo: string;
  description: string;
  condition: BlueprintCondition;
  points: number;
}

/** 청사진 조건 */
export interface BlueprintCondition {
  type: 'building_count' | 'category_set' | 'adjacency' | 'fengshui';
  target: string | string[];
  count?: number;
}

// ============================================
// 풍수지리 및 보너스
// ============================================

/** 풍수지리 보너스 */
export interface FengshuiBonus {
  baesanimsu: boolean;  // 배산임수 완성
  mountain: boolean;    // 북쪽 산 (배산)
  water: boolean;       // 남쪽 물 (임수)
  bonusPoints: number;
}

/** 인접 보너스 */
export interface AdjacencyBonus {
  adjacentCategory: BuildingCategory;
  bonusPoints: number;
}

// ============================================
// 보드 상태
// ============================================

/** 보드 좌표 */
export interface BoardPosition {
  row: number;  // 0-4
  col: number;  // 0-4
}

/** 보드 셀 */
export interface BoardCell {
  position: BoardPosition;
  terrain: 'normal' | 'mountain' | 'water';
  tile: PlacedTile | null;
}

/** 배치된 타일 */
export interface PlacedTile {
  tileId: string;
  ownerId: number;          // 배치한 플레이어 ID
  placedWorkers: PlacedWorker[];
  fengshuiActive: boolean;  // 풍수지리 보너스 활성화
}

/** 배치된 워커 */
export interface PlacedWorker {
  playerId: number;
  workerType: WorkerType;
  slotIndex: number;
}

// ============================================
// 플레이어 상태
// ============================================

/** 플레이어 정보 */
export interface Player {
  id: number;
  userId: number;
  username: string;
  color: PlayerColor;
  turnOrder: number;
  isHost: boolean;
  isReady: boolean;
}

/** 게임 내 플레이어 상태 */
export interface GamePlayer extends Player {
  resources: Resources;
  workers: PlayerWorkers;
  blueprints: string[];      // 보유 청사진 ID 목록
  score: number;
  placedTiles: string[];     // 배치한 타일 ID 목록
}

// ============================================
// 게임 상태
// ============================================

/** 게임 전체 상태 */
export interface GameState {
  id: number;
  lobbyId: number;
  status: GameStatus;
  currentRound: number;
  totalRounds: number;
  currentTurnPlayerId: number;
  turnOrder: number[];
  board: BoardCell[][];      // 5x5 메인 보드
  players: GamePlayer[];
  availableTiles: string[];  // 드로우 가능한 타일 ID
  discardedTiles: string[]; // 버려진 타일 ID
  lastAction: GameAction | null;
  createdAt: string;
  updatedAt: string;
}

/** 게임 액션 */
export interface GameAction {
  id: number;
  gameId: number;
  playerId: number;
  actionType: ActionType;
  payload: ActionPayload;
  timestamp: string;
}

/** 액션 페이로드 (유니온 타입) */
export type ActionPayload =
  | PlaceWorkerPayload
  | RecallWorkerPayload
  | PlaceTilePayload
  | DrawBlueprintPayload
  | EndTurnPayload
  | PassPayload;

export interface PlaceWorkerPayload {
  type: 'place_worker';
  workerType: WorkerType;
  targetPosition: BoardPosition;
  slotIndex: number;
}

export interface RecallWorkerPayload {
  type: 'recall_worker';
  workerType: WorkerType;
  fromPosition: BoardPosition;
  slotIndex: number;
}

export interface PlaceTilePayload {
  type: 'place_tile';
  tileId: string;
  position: BoardPosition;
}

export interface DrawBlueprintPayload {
  type: 'draw_blueprint';
  blueprintId: string;
}

export interface EndTurnPayload {
  type: 'end_turn';
}

export interface PassPayload {
  type: 'pass';
}

// ============================================
// API 응답 래퍼
// ============================================

/** 성공 응답 */
export interface ApiResponse<T> {
  data: T;
  meta?: {
    page?: number;
    total?: number;
  };
}

/** 에러 응답 */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Array<{
      field: string;
      message: string;
    }>;
  };
}

// ============================================
// 로비
// ============================================

/** 로비 정보 */
export interface Lobby {
  id: number;
  name: string;
  hostId: number;
  inviteCode: string;
  status: LobbyStatus;
  maxPlayers: number;
  players: Player[];
  createdAt: string;
}
