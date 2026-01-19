import { useEffect, useCallback, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useGameStore } from '../stores/gameStore'
import { useAuthStore } from '../stores/authStore'
import { useGameWebSocket, useToast } from '../hooks'
import { GameBoard, PlayerPanel, TileSelector, BlueprintSelector, BlueprintPanel } from '../components/game'
import { Toast } from '../components/ui'
import { apiClient as client } from '../api/client'
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

  // AI turn handling state
  const [isAITurnProcessing, setIsAITurnProcessing] = useState(false)
  const [aiTurnMessage, setAITurnMessage] = useState<string | null>(null)

  // Toast notifications
  const { toast, showTurnNotification, showSuccess, hideToast } = useToast()

  // WebSocket callbacks
  const handleYourTurn = useCallback(() => {
    showTurnNotification('당신의 턴입니다!')
  }, [showTurnNotification])

  const handleGameEnded = useCallback((winnerId: number, winnerName: string) => {
    showSuccess(`게임 종료! 우승: ${winnerName}`)
    setTimeout(() => navigate(`/game/${gameId}/result`), 2000)
  }, [gameId, navigate, showSuccess])

  // WebSocket connection
  const { isConnected, connectionState } = useGameWebSocket({
    gameId: gameId || 0,
    onYourTurn: handleYourTurn,
    onGameEnded: handleGameEnded,
  })

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

  // Redirect to result page when game is finished
  useEffect(() => {
    if (gameState?.status === 'finished') {
      navigate(`/game/${gameId}/result`)
    }
  }, [gameState?.status, gameId, navigate])

  // Find current player (me)
  const currentPlayer = gameState?.players.find((p) => p.user_id === user?.id)
  // NOTE: current_turn_player_id is actually user_id, not player.id
  const isMyTurn = currentPlayer?.user_id === gameState?.current_turn_player_id

  // Check if current turn is AI
  const currentTurnPlayer = gameState?.players.find(
    (p) => p.user_id === gameState?.current_turn_player_id
  )
  const isAITurn = currentTurnPlayer?.is_ai === true

  // Auto-execute AI turns
  useEffect(() => {
    const executeAITurns = async () => {
      if (!gameId || !isAITurn || isAITurnProcessing || gameState?.status !== 'in_progress') {
        return
      }

      setIsAITurnProcessing(true)
      setAITurnMessage(`${currentTurnPlayer?.username || 'AI'}가 생각 중...`)

      try {
        // Call auto-play endpoint to execute all AI turns
        const response = await client.post(`/solo/${gameId}/auto-play`, {
          max_turns: 10,
        })

        if (response.data.game_state) {
          // Update game state
          fetchGameState(gameId)
          fetchValidActions(gameId)
          fetchPlayerBlueprints(gameId)
        }

        if (response.data.is_your_turn) {
          showTurnNotification('당신의 턴입니다!')
        }

        // Show AI actions in message
        const actionsCount = response.data.turns_executed || 0
        if (actionsCount > 0) {
          setAITurnMessage(`AI가 ${actionsCount}개의 액션을 수행했습니다`)
          setTimeout(() => setAITurnMessage(null), 2000)
        } else {
          setAITurnMessage(null)
        }
      } catch (err) {
        console.error('AI turn execution failed:', err)
        setAITurnMessage(null)
      } finally {
        setIsAITurnProcessing(false)
      }
    }

    // Small delay to show "AI is thinking" message
    const timer = setTimeout(executeAITurns, 1000)
    return () => clearTimeout(timer)
  }, [gameId, isAITurn, isAITurnProcessing, gameState?.status, currentTurnPlayer?.username, fetchGameState, fetchValidActions, fetchPlayerBlueprints, showTurnNotification])

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

  // Determine guidance message based on current state
  const getGuidanceMessage = (): { message: string; type: 'action' | 'wait' | 'ai' } => {
    // AI turn
    if (isAITurn) {
      return {
        message: `${currentTurnPlayer?.username || 'AI'}가 턴을 진행 중입니다...`,
        type: 'ai',
      }
    }

    // Not my turn (other human player)
    if (!isMyTurn) {
      const turnPlayerName = currentTurnPlayer?.username || '상대방'
      return {
        message: `${turnPlayerName}의 턴입니다.`,
        type: 'wait',
      }
    }

    // My turn - check what actions are available
    if (availableBlueprints.length > 0) {
      return {
        message: '청사진을 선택하세요. 게임 종료 시 조건 충족으로 보너스 점수를 받습니다.',
        type: 'action',
      }
    }

    if (availableTiles.length > 0 && !selectedTile) {
      return {
        message: '건물 타일을 선택하고 보드에 배치하세요.',
        type: 'action',
      }
    }

    if (selectedTile) {
      return {
        message: '타일을 배치할 위치를 선택하세요. (하이라이트된 칸)',
        type: 'action',
      }
    }

    if (selectedWorker) {
      return {
        message: `${selectedWorker === 'apprentice' ? '견습생' : '관리'}을 배치할 건물을 선택하세요.`,
        type: 'action',
      }
    }

    // Check if worker placement is available
    const workerActions = validActions.filter((a) => a.action_type === 'place_worker')
    if (workerActions.length > 0) {
      return {
        message: '일꾼을 선택하여 건물에 배치하거나 턴을 종료하세요.',
        type: 'action',
      }
    }

    return {
      message: '턴을 종료하세요.',
      type: 'action',
    }
  }

  const guidance = getGuidanceMessage()

  return (
    <div className="min-h-screen bg-hanyang-cream p-4">
      {/* Toast notifications */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={hideToast}
        duration={3000}
      />

      {/* Header */}
      <header className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-hanyang-brown">
          한양: 도읍의 설계자들
        </h1>
        <div className="flex items-center gap-4">
          {/* WebSocket connection indicator */}
          <span
            className={`flex items-center gap-1 text-sm ${
              isConnected ? 'text-green-600' : 'text-red-500'
            }`}
            title={connectionState}
          >
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            {isConnected ? '실시간' : '연결 끊김'}
          </span>
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

      {/* Contextual Guidance Banner */}
      <div
        className={`
          mb-4 p-3 rounded-lg border-2 flex items-center justify-center gap-3 transition-all
          ${guidance.type === 'action' ? 'bg-hanyang-gold/20 border-hanyang-gold text-hanyang-brown' : ''}
          ${guidance.type === 'wait' ? 'bg-gray-200 border-gray-400 text-gray-600' : ''}
          ${guidance.type === 'ai' ? 'bg-blue-100 border-blue-400 text-blue-700' : ''}
        `}
      >
        {guidance.type === 'ai' && (
          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {guidance.type === 'action' && (
          <span className="text-xl">👆</span>
        )}
        {guidance.type === 'wait' && (
          <span className="text-xl">⏳</span>
        )}
        <span className="font-medium text-lg">{guidance.message}</span>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Left sidebar - Players */}
        <aside className="col-span-3 space-y-4">
          <h2 className="text-lg font-bold text-hanyang-brown mb-2">플레이어</h2>
          {gameState.players.map((player) => (
            <PlayerPanel
              key={player.id}
              player={player}
              isCurrentPlayer={player.user_id === user?.id}
              isCurrentTurn={player.user_id === gameState.current_turn_player_id}
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
            <div className="mt-4 text-center">
              {aiTurnMessage ? (
                <div className="flex items-center justify-center gap-2 text-hanyang-gold">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                  <span>{aiTurnMessage}</span>
                </div>
              ) : (
                <span className="text-hanyang-brown/70">
                  {isAITurn ? 'AI가 턴을 진행합니다...' : '다른 플레이어의 턴입니다...'}
                </span>
              )}
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
