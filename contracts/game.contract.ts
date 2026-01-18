/**
 * Game API Contract
 * 게임 관련 API 계약 정의
 */

import type {
  GameState,
  GameAction,
  ActionType,
  ActionPayload,
  BoardPosition,
  WorkerType,
  Resources,
} from './types';

// ============================================
// Request Types
// ============================================

/** 게임 액션 요청 */
export interface GameActionRequest {
  action_type: ActionType;
  payload: ActionPayload;
}

/** 워커 배치 요청 */
export interface PlaceWorkerRequest {
  action_type: 'place_worker';
  payload: {
    type: 'place_worker';
    worker_type: WorkerType;
    target_position: BoardPosition;
    slot_index: number;
  };
}

/** 타일 배치 요청 */
export interface PlaceTileRequest {
  action_type: 'place_tile';
  payload: {
    type: 'place_tile';
    tile_id: string;
    position: BoardPosition;
  };
}

/** 피드백 제출 요청 */
export interface SubmitFeedbackRequest {
  rating: number;           // 1-5
  comments: string;
  balance_feedback?: string;
  bug_reports?: string;
}

// ============================================
// Response Types
// ============================================

/** 게임 상태 응답 */
export interface GameStateResponse extends GameState {}

/** 게임 액션 응답 */
export interface GameActionResponse {
  action: GameAction;
  new_state: GameState;
  bonus_awarded?: BonusAwarded;
}

/** 보너스 정보 */
export interface BonusAwarded {
  fengshui_bonus?: number;
  adjacency_bonus?: number;
  blueprint_completed?: string;
}

/** 유효 액션 목록 */
export interface ValidActionsResponse {
  valid_actions: ValidAction[];
}

export interface ValidAction {
  action_type: ActionType;
  options?: ValidActionOption[];
}

export interface ValidActionOption {
  position?: BoardPosition;
  tile_id?: string;
  worker_type?: WorkerType;
  slot_index?: number;
}

/** 점수 상세 */
export interface ScoreBreakdown {
  building_points: number;
  fengshui_bonus: number;
  adjacency_bonus: number;
  blueprint_bonus: number;
  remaining_resources: number;
  total: number;
}

/** 게임 결과 응답 */
export interface GameResultResponse {
  game_id: number;
  winner_id: number;
  rankings: PlayerRanking[];
  duration_minutes: number;
  total_rounds: number;
}

export interface PlayerRanking {
  player_id: number;
  username: string;
  rank: number;
  score_breakdown: ScoreBreakdown;
}

// ============================================
// API Endpoints
// ============================================

/**
 * GET /api/v1/games/{id}
 * - Response: GameStateResponse
 * - Errors: 404 (not found), 403 (not in game)
 */

/**
 * POST /api/v1/games/{id}/action
 * - Request: GameActionRequest
 * - Response: GameActionResponse
 * - Errors: 400 (invalid action), 403 (not your turn)
 */

/**
 * GET /api/v1/games/{id}/valid-actions
 * - Response: ValidActionsResponse
 * - Errors: 404, 403
 */

/**
 * GET /api/v1/games/{id}/result
 * - Response: GameResultResponse
 * - Errors: 400 (game not finished), 404
 */

/**
 * POST /api/v1/games/{id}/feedback
 * - Request: SubmitFeedbackRequest
 * - Response: 201 Created
 */

/**
 * GET /api/v1/games/{id}/history
 * - Response: { actions: GameAction[] }
 * - Query: from_turn?, to_turn?
 */
