/**
 * Lobby API Contract
 * 로비 관련 API 계약 정의
 */

import type { Lobby, Player, LobbyStatus } from './types';

// ============================================
// Request Types
// ============================================

/** 로비 생성 요청 */
export interface CreateLobbyRequest {
  name: string;
  max_players?: number;  // 기본값: 4
}

/** 로비 참가 요청 */
export interface JoinLobbyRequest {
  invite_code: string;
}

/** 준비 상태 변경 요청 */
export interface ReadyRequest {
  is_ready: boolean;
}

// ============================================
// Response Types
// ============================================

/** 로비 응답 */
export interface LobbyResponse extends Lobby {}

/** 로비 목록 응답 */
export interface LobbyListResponse {
  lobbies: LobbyResponse[];
  total: number;
}

/** 로비 참가 응답 */
export interface JoinLobbyResponse {
  lobby: LobbyResponse;
  player: Player;
}

// ============================================
// API Endpoints
// ============================================

/**
 * POST /api/v1/lobbies
 * - Request: CreateLobbyRequest
 * - Response: LobbyResponse (201 Created)
 * - Headers: Authorization required
 */

/**
 * GET /api/v1/lobbies
 * - Response: LobbyListResponse
 * - Query: status?, page?, limit?
 */

/**
 * GET /api/v1/lobbies/{id}
 * - Response: LobbyResponse
 * - Errors: 404 (not found)
 */

/**
 * POST /api/v1/lobbies/{id}/join
 * - Request: JoinLobbyRequest
 * - Response: JoinLobbyResponse
 * - Errors: 400 (full/started), 404 (not found)
 */

/**
 * POST /api/v1/lobbies/{id}/leave
 * - Response: 204 No Content
 * - Errors: 404 (not found)
 */

/**
 * POST /api/v1/lobbies/{id}/ready
 * - Request: ReadyRequest
 * - Response: LobbyResponse
 * - Errors: 400 (not in lobby), 404 (not found)
 */

/**
 * POST /api/v1/lobbies/{id}/start
 * - Response: { game_id: number }
 * - Errors: 400 (not all ready), 403 (not host)
 */

/**
 * GET /api/v1/lobbies/join/{invite_code}
 * - Response: LobbyResponse
 * - Errors: 404 (invalid code)
 */
