import apiClient from './client'
import type {
  GameState,
  GameActionRequest,
  GameActionResponse,
  ValidActionsResponse,
  GameResultResponse,
  PlayerBlueprintsResponse,
} from '../types/game'

export const gameApi = {
  /**
   * Get game state by ID
   */
  getGameState: async (gameId: number): Promise<GameState> => {
    const response = await apiClient.get<GameState>(`/games/${gameId}`)
    return response.data
  },

  /**
   * Create game from lobby
   */
  createFromLobby: async (lobbyId: number): Promise<GameState> => {
    const response = await apiClient.post<GameState>(`/games/from-lobby/${lobbyId}`)
    return response.data
  },

  /**
   * Perform a game action
   */
  performAction: async (
    gameId: number,
    action: GameActionRequest
  ): Promise<GameActionResponse> => {
    const response = await apiClient.post<GameActionResponse>(
      `/games/${gameId}/action`,
      action
    )
    return response.data
  },

  /**
   * Get valid actions for current player
   */
  getValidActions: async (gameId: number): Promise<ValidActionsResponse> => {
    const response = await apiClient.get<ValidActionsResponse>(
      `/games/${gameId}/valid-actions`
    )
    return response.data
  },

  /**
   * Get game result (only for finished games)
   */
  getGameResult: async (gameId: number): Promise<GameResultResponse> => {
    const response = await apiClient.get<GameResultResponse>(
      `/games/${gameId}/result`
    )
    return response.data
  },

  /**
   * Get player's blueprints (dealt and selected)
   */
  getPlayerBlueprints: async (gameId: number): Promise<PlayerBlueprintsResponse> => {
    const response = await apiClient.get<PlayerBlueprintsResponse>(
      `/games/${gameId}/blueprints`
    )
    return response.data
  },
}

export default gameApi
