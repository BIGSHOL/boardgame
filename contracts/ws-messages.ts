/**
 * WebSocket Message Types
 * 실시간 통신 메시지 계약 정의
 */

import type { GameState, GameAction, Player, LobbyStatus } from './types';

// ============================================
// 클라이언트 → 서버 메시지
// ============================================

/** 클라이언트 메시지 유니온 */
export type ClientMessage =
  | JoinGameMessage
  | LeaveGameMessage
  | GameActionMessage
  | PingMessage;

export interface JoinGameMessage {
  type: 'join_game';
  payload: {
    game_id: number;
    token: string;  // JWT access token
  };
}

export interface LeaveGameMessage {
  type: 'leave_game';
  payload: {
    game_id: number;
  };
}

export interface GameActionMessage {
  type: 'game_action';
  payload: {
    game_id: number;
    action: GameAction;
  };
}

export interface PingMessage {
  type: 'ping';
  payload: {
    timestamp: number;
  };
}

// ============================================
// 서버 → 클라이언트 메시지
// ============================================

/** 서버 메시지 유니온 */
export type ServerMessage =
  | GameStateMessage
  | GameActionResultMessage
  | PlayerJoinedMessage
  | PlayerLeftMessage
  | TurnChangedMessage
  | GameEndedMessage
  | ErrorMessage
  | PongMessage;

export interface GameStateMessage {
  type: 'game_state';
  payload: {
    state: GameState;
  };
}

export interface GameActionResultMessage {
  type: 'action_result';
  payload: {
    action: GameAction;
    new_state: GameState;
    success: boolean;
    message?: string;
    bonus_awarded?: {
      fengshui_bonus?: number;
      adjacency_bonus?: number;
    };
  };
}

export interface PlayerJoinedMessage {
  type: 'player_joined';
  payload: {
    player: Player;
    game_id: number;
  };
}

export interface PlayerLeftMessage {
  type: 'player_left';
  payload: {
    player_id: number;
    game_id: number;
    reason: 'disconnect' | 'leave';
  };
}

export interface TurnChangedMessage {
  type: 'turn_changed';
  payload: {
    current_player_id: number;
    round: number;
    remaining_time?: number;  // 턴 제한 시간 (초)
  };
}

export interface GameEndedMessage {
  type: 'game_ended';
  payload: {
    game_id: number;
    winner_id: number;
    rankings: Array<{
      player_id: number;
      username: string;
      rank: number;
      score: number;
    }>;
  };
}

export interface ErrorMessage {
  type: 'error';
  payload: {
    code: string;
    message: string;
    recoverable: boolean;
  };
}

export interface PongMessage {
  type: 'pong';
  payload: {
    timestamp: number;
    server_time: number;
  };
}

// ============================================
// 로비 WebSocket 메시지
// ============================================

/** 로비 클라이언트 메시지 */
export type LobbyClientMessage =
  | JoinLobbyWsMessage
  | LeaveLobbyWsMessage
  | ReadyStatusMessage
  | StartGameMessage;

export interface JoinLobbyWsMessage {
  type: 'join_lobby';
  payload: {
    lobby_id: number;
    token: string;
  };
}

export interface LeaveLobbyWsMessage {
  type: 'leave_lobby';
  payload: {
    lobby_id: number;
  };
}

export interface ReadyStatusMessage {
  type: 'ready_status';
  payload: {
    lobby_id: number;
    is_ready: boolean;
  };
}

export interface StartGameMessage {
  type: 'start_game';
  payload: {
    lobby_id: number;
  };
}

/** 로비 서버 메시지 */
export type LobbyServerMessage =
  | LobbyStateMessage
  | LobbyPlayerJoinedMessage
  | LobbyPlayerLeftMessage
  | LobbyPlayerReadyMessage
  | LobbyGameStartingMessage;

export interface LobbyStateMessage {
  type: 'lobby_state';
  payload: {
    lobby_id: number;
    status: LobbyStatus;
    players: Player[];
    host_id: number;
  };
}

export interface LobbyPlayerJoinedMessage {
  type: 'lobby_player_joined';
  payload: {
    player: Player;
  };
}

export interface LobbyPlayerLeftMessage {
  type: 'lobby_player_left';
  payload: {
    player_id: number;
    new_host_id?: number;  // 호스트 변경 시
  };
}

export interface LobbyPlayerReadyMessage {
  type: 'lobby_player_ready';
  payload: {
    player_id: number;
    is_ready: boolean;
  };
}

export interface LobbyGameStartingMessage {
  type: 'lobby_game_starting';
  payload: {
    game_id: number;
    countdown: number;  // 시작까지 남은 초
  };
}

// ============================================
// WebSocket 연결 URL
// ============================================

/**
 * 게임 WebSocket: ws://localhost:8000/ws/game/{game_id}
 * 로비 WebSocket: ws://localhost:8000/ws/lobby/{lobby_id}
 *
 * 연결 시 token을 쿼리 파라미터로 전달:
 * ws://localhost:8000/ws/game/{game_id}?token={access_token}
 */
