/**
 * Game types for Hanyang: The Foundation
 */

// Enums
export type ResourceType = 'wood' | 'stone' | 'tile' | 'ink'
export type WorkerType = 'apprentice' | 'official'
export type GameStatus = 'waiting' | 'in_progress' | 'finished'
export type PlayerColor = 'blue' | 'red' | 'green' | 'yellow'
export type TerrainType = 'normal' | 'mountain' | 'water'
export type ActionType = 'place_worker' | 'recall_worker' | 'place_tile' | 'select_blueprint' | 'end_turn' | 'pass'
export type BlueprintCategory = 'palace_proximity' | 'category_collection' | 'pattern' | 'special'

// Resource & Worker
export interface Resources {
  wood: number
  stone: number
  tile: number
  ink: number
}

export interface WorkerState {
  total: number
  available: number
  placed: number
}

export interface PlayerWorkers {
  apprentices: WorkerState
  officials: WorkerState
}

// Board
export interface BoardPosition {
  row: number
  col: number
}

export interface PlacedWorker {
  player_id: number
  worker_type: WorkerType
  slot_index: number
}

export interface PlacedTile {
  tile_id: string
  owner_id: number
  placed_workers: PlacedWorker[]
  fengshui_active: boolean
}

export interface BoardCell {
  position: BoardPosition
  terrain: TerrainType
  tile: PlacedTile | null
}

// Player
export interface GamePlayer {
  id: number
  user_id: number
  username: string
  color: PlayerColor
  turn_order: number
  is_host: boolean
  is_ready: boolean
  resources: Resources
  workers: PlayerWorkers
  dealt_blueprints: string[]  // 선택 전 배분된 청사진
  blueprints: string[]  // 선택한 청사진
  score: number
  placed_tiles: string[]
}

// Game State
export interface GameState {
  id: number
  lobby_id: number
  status: GameStatus
  current_round: number
  total_rounds: number
  current_turn_player_id: number
  turn_order: number[]
  board: BoardCell[][]
  players: GamePlayer[]
  available_tiles: string[]
  discarded_tiles: string[]
  created_at: string
  updated_at: string
}

// Action Payloads
export interface PlaceWorkerPayload {
  type: 'place_worker'
  worker_type: WorkerType
  target_position: BoardPosition
  slot_index: number
}

export interface RecallWorkerPayload {
  type: 'recall_worker'
  worker_type: WorkerType
  from_position: BoardPosition
  slot_index: number
}

export interface PlaceTilePayload {
  type: 'place_tile'
  tile_id: string
  position: BoardPosition
}

export interface SelectBlueprintPayload {
  type: 'select_blueprint'
  blueprint_id: string
}

export interface EndTurnPayload {
  type: 'end_turn'
}

export type ActionPayload = PlaceWorkerPayload | RecallWorkerPayload | PlaceTilePayload | SelectBlueprintPayload | EndTurnPayload

// Tile Types
export type TileCategory = 'palace' | 'government' | 'religious' | 'commercial' | 'residential' | 'gate'

export interface TileCost {
  wood: number
  stone: number
  tile: number
  ink: number
}

export interface TileInfo {
  tile_id: string
  name_ko: string
  cost: TileCost
  base_points: number
}

export interface TilePlacementAction {
  action_type: 'place_tile'
  available_tiles: TileInfo[]
  valid_positions: BoardPosition[]
}

// Blueprint Types
export interface BlueprintInfo {
  blueprint_id: string
  name_ko: string
  name_en: string
  description_ko: string
  category: BlueprintCategory
  bonus_points: number
  condition: {
    type: string
    params: Record<string, unknown>
  }
  current_score?: number
  is_completed?: boolean
}

export interface BlueprintSelectionAction {
  action_type: 'select_blueprint'
  available_blueprints: BlueprintInfo[]
}

export interface PlayerBlueprintsResponse {
  dealt_blueprints: BlueprintInfo[]
  selected_blueprints: BlueprintInfo[]
}

// API Requests
export interface GameActionRequest {
  action_type: ActionType
  payload: ActionPayload
}

// API Responses
export interface GameActionResponse {
  success: boolean
  action_result: Record<string, unknown>
  new_state: GameState
}

export interface ValidActionOption {
  position?: BoardPosition
  slot_index?: number
}

export interface ValidAction {
  action_type: ActionType
  worker_type?: WorkerType
  available_slots?: ValidActionOption[]
}

export interface ValidActionsResponse {
  valid_actions: ValidAction[]
  message?: string
}

// Score
export interface ScoreBreakdown {
  building_points: number
  fengshui_bonus: number
  adjacency_bonus: number
  blueprint_bonus: number
  remaining_resources: number
  total: number
}

export interface PlayerRanking {
  player_id: number
  username: string
  rank: number
  score_breakdown: ScoreBreakdown
}

export interface GameResultResponse {
  game_id: number
  winner_id: number
  rankings: PlayerRanking[]
  duration_minutes: number
  total_rounds: number
}

// Store State
export interface GameStoreState {
  gameState: GameState | null
  validActions: ValidAction[]
  selectedWorker: WorkerType | null
  selectedTile: string | null
  selectedBlueprint: string | null
  selectedPosition: BoardPosition | null
  playerBlueprints: PlayerBlueprintsResponse | null
  isLoading: boolean
  error: string | null

  // Actions
  fetchGameState: (gameId: number) => Promise<void>
  fetchValidActions: (gameId: number) => Promise<void>
  fetchPlayerBlueprints: (gameId: number) => Promise<void>
  performAction: (gameId: number, action: GameActionRequest) => Promise<void>
  selectWorker: (workerType: WorkerType | null) => void
  selectTile: (tileId: string | null) => void
  selectBlueprint: (blueprintId: string | null) => void
  selectPosition: (position: BoardPosition | null) => void
  clearError: () => void
}
