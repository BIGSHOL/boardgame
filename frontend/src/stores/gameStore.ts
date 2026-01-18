import { create } from 'zustand'
import type {
  GameState,
  GameStoreState,
  WorkerType,
  BoardPosition,
  GameActionRequest,
  ValidAction,
} from '../types/game'
import { gameApi } from '../api/game'

export const useGameStore = create<GameStoreState>((set, get) => ({
  gameState: null,
  validActions: [],
  selectedWorker: null,
  selectedTile: null,
  selectedPosition: null,
  isLoading: false,
  error: null,

  fetchGameState: async (gameId: number) => {
    set({ isLoading: true, error: null })
    try {
      const gameState = await gameApi.getGameState(gameId)
      set({ gameState, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch game state',
        isLoading: false,
      })
    }
  },

  fetchValidActions: async (gameId: number) => {
    try {
      const response = await gameApi.getValidActions(gameId)
      set({ validActions: response.valid_actions })
    } catch (error) {
      console.error('Failed to fetch valid actions:', error)
    }
  },

  performAction: async (gameId: number, action: GameActionRequest) => {
    set({ isLoading: true, error: null })
    try {
      const response = await gameApi.performAction(gameId, action)
      set({
        gameState: response.new_state,
        selectedWorker: null,
        selectedTile: null,
        selectedPosition: null,
        isLoading: false,
      })
      // Refresh valid actions after performing action
      get().fetchValidActions(gameId)
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to perform action',
        isLoading: false,
      })
      throw error
    }
  },

  selectWorker: (workerType: WorkerType | null) => {
    set({ selectedWorker: workerType, selectedTile: null, selectedPosition: null })
  },

  selectTile: (tileId: string | null) => {
    set({ selectedTile: tileId, selectedWorker: null, selectedPosition: null })
  },

  selectPosition: (position: BoardPosition | null) => {
    set({ selectedPosition: position })
  },

  clearError: () => {
    set({ error: null })
  },
}))

export default useGameStore
