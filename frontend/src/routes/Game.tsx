import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useGameStore } from '../stores/gameStore'
import { useAuthStore } from '../stores/authStore'
import { GameBoard, PlayerPanel, TileSelector, BlueprintSelector, BlueprintPanel } from '../components/game'
import type { WorkerType, BoardPosition, TileInfo, BlueprintInfo } from '../types/game'

export function Game() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()
  const {
    gameState,
    validActions,
    selectedWorker,
    selectedTile,
    selectedBlueprint,
    selectedPosition,
    playerBlueprints,
    isLoading,
    error,
    fetchGameState,
    fetchValidActions,
    fetchPlayerBlueprints,
    performAction,
    selectWorker,
    selectTile,
    selectBlueprint,
    selectPosition,
    clearError,
  } = useGameStore()

  const gameId = id ? parseInt(id, 10) : null

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  // Fetch game state on mount
  useEffect(() => {
    if (gameId) {
      fetchGameState(gameId)
      fetchValidActions(gameId)
      fetchPlayerBlueprints(gameId)
    }
  }, [gameId, fetchGameState, fetchValidActions, fetchPlayerBlueprints])

  // Find current player
  const currentPlayer = gameState?.players.find((p) => p.user_id === user?.id)
  const isMyTurn = currentPlayer?.id === gameState?.current_turn_player_id

  // Handle worker selection
  const handleSelectWorker = (workerType: WorkerType) => {
    if (selectedWorker === workerType) {
      selectWorker(null)
    } else {
      selectWorker(workerType)
    }
  }

  // Handle tile selection
  const handleSelectTile = (tileId: string | null) => {
    selectTile(tileId)
  }

  // Handle cell selection for worker or tile placement
  const handleSelectCell = (position: BoardPosition) => {
    if (!gameId || !isMyTurn) return

    // Handle tile placement
    if (selectedTile) {
      const tileAction = validActions.find((a) => a.action_type === 'place_tile') as any
      if (tileAction?.valid_positions) {
        const isValidPosition = tileAction.valid_positions.some(
          (p: BoardPosition) => p.row === position.row && p.col === position.col
        )
        if (isValidPosition) {
          performAction(gameId, {
            action_type: 'place_tile',
            payload: {
              type: 'place_tile',
              tile_id: selectedTile,
              position: position,
            },
          })
        }
      }
      return
    }

    // Handle worker placement
    if (selectedWorker) {
      const workerAction = validActions.find(
        (a) => a.action_type === 'place_worker' && a.worker_type === selectedWorker
      )
      const validSlot = workerAction?.available_slots?.find(
        (s) => s.position?.row === position.row && s.position?.col === position.col
      )

      if (validSlot) {
        performAction(gameId, {
          action_type: 'place_worker',
          payload: {
            type: 'place_worker',
            worker_type: selectedWorker,
            target_position: position,
            slot_index: validSlot.slot_index ?? 0,
          },
        })
      }
    }
  }

  // Get available tiles from valid actions
  const tileAction = validActions.find((a) => a.action_type === 'place_tile') as any
  const availableTiles: TileInfo[] = tileAction?.available_tiles || []
  const validTilePositions: BoardPosition[] = tileAction?.valid_positions || []

  // Get available blueprints from valid actions
  const blueprintAction = validActions.find((a) => a.action_type === 'select_blueprint') as any
  const availableBlueprints: BlueprintInfo[] = blueprintAction?.available_blueprints || []

  // Handle blueprint selection confirmation
  const handleConfirmBlueprintSelection = () => {
    if (!gameId || !selectedBlueprint) return

    performAction(gameId, {
      action_type: 'select_blueprint',
      payload: {
        type: 'select_blueprint',
        blueprint_id: selectedBlueprint,
      },
    })
  }

  // Handle end turn
  const handleEndTurn = () => {
    if (!gameId || !isMyTurn) return

    performAction(gameId, {
      action_type: 'end_turn',
      payload: { type: 'end_turn' },
    })
  }

  if (isLoading && !gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-hanyang-brown text-xl">게임 로딩 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <div className="text-red-500 text-xl">{error}</div>
        <button
          type="button"
          className="px-4 py-2 bg-hanyang-blue text-white rounded hover:bg-hanyang-blue/80"
          onClick={() => {
            clearError()
            if (gameId) fetchGameState(gameId)
          }}
        >
          다시 시도
        </button>
      </div>
    )
  }

  if (!gameState) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-hanyang-brown text-xl">게임을 찾을 수 없습니다.</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-hanyang-cream p-4">
      {/* Header */}
      <header className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-hanyang-brown">
          한양: 도읍의 설계자들
        </h1>
        <div className="flex items-center gap-4">
          <span className="text-hanyang-brown">
            라운드 {gameState.current_round}/{gameState.total_rounds}
          </span>
          <span
            className={`px-3 py-1 rounded ${
              gameState.status === 'in_progress'
                ? 'bg-green-500 text-white'
                : 'bg-gray-500 text-white'
            }`}
          >
            {gameState.status === 'in_progress' ? '게임 진행 중' : gameState.status}
          </span>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-4">
        {/* Left sidebar - Players */}
        <aside className="col-span-3 space-y-4">
          <h2 className="text-lg font-bold text-hanyang-brown mb-2">플레이어</h2>
          {gameState.players.map((player) => (
            <PlayerPanel
              key={player.id}
              player={player}
              isCurrentPlayer={player.user_id === user?.id}
              isCurrentTurn={player.id === gameState.current_turn_player_id}
              onSelectWorker={handleSelectWorker}
              selectedWorker={selectedWorker}
            />
          ))}
        </aside>

        {/* Main board area */}
        <main className="col-span-6">
          <GameBoard
            board={gameState.board}
            selectedPosition={selectedPosition}
            validActions={validActions}
            selectedWorkerType={selectedWorker}
            selectedTileId={selectedTile}
            validTilePositions={validTilePositions}
            onSelectCell={handleSelectCell}
          />

          {/* Action buttons */}
          {isMyTurn && (
            <div className="mt-4 flex justify-center gap-4">
              {(selectedWorker || selectedTile) && (
                <button
                  type="button"
                  className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                  onClick={() => {
                    selectWorker(null)
                    selectTile(null)
                  }}
                >
                  선택 취소
                </button>
              )}
              <button
                type="button"
                className="px-6 py-2 bg-hanyang-red text-white rounded hover:bg-hanyang-red/80"
                onClick={handleEndTurn}
                disabled={isLoading}
              >
                턴 종료
              </button>
            </div>
          )}

          {!isMyTurn && (
            <div className="mt-4 text-center text-hanyang-brown/70">
              다른 플레이어의 턴입니다...
            </div>
          )}
        </main>

        {/* Right sidebar - Tile/Blueprint Selection */}
        <aside className="col-span-3 space-y-4">
          {/* Blueprint Selection (if available) */}
          {isMyTurn && availableBlueprints.length > 0 && (
            <BlueprintSelector
              availableBlueprints={availableBlueprints}
              selectedBlueprintId={selectedBlueprint}
              onSelectBlueprint={selectBlueprint}
              onConfirmSelection={handleConfirmBlueprintSelection}
              disabled={isLoading}
            />
          )}

          {/* Tile Selection */}
          {isMyTurn && availableTiles.length > 0 && currentPlayer && (
            <TileSelector
              availableTiles={availableTiles}
              playerResources={currentPlayer.resources}
              selectedTileId={selectedTile}
              onSelectTile={handleSelectTile}
              disabled={isLoading}
            />
          )}

          {/* Player's Blueprints */}
          {playerBlueprints && playerBlueprints.selected_blueprints.length > 0 && (
            <BlueprintPanel
              blueprints={playerBlueprints.selected_blueprints}
              showProgress={true}
            />
          )}

          {/* Game info */}
          <div className="p-4 bg-hanyang-paper rounded border border-hanyang-brown/20">
            <h3 className="font-bold text-hanyang-brown mb-2">게임 정보</h3>
            <ul className="text-sm text-hanyang-brown/70 space-y-1">
              <li>게임 ID: {gameState.id}</li>
              <li>라운드: {gameState.current_round}/{gameState.total_rounds}</li>
              <li>플레이어 수: {gameState.players.length}명</li>
              <li>남은 타일: {gameState.available_tiles.length}장</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default Game
