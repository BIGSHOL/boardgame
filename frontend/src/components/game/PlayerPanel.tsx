import type { GamePlayer, WorkerType } from '../../types/game'
import { ResourceDisplay } from './ResourceDisplay'
import { WorkerDisplay } from './WorkerDisplay'

interface PlayerPanelProps {
  player: GamePlayer
  isCurrentPlayer: boolean
  isCurrentTurn: boolean
  onSelectWorker?: (type: WorkerType) => void
  selectedWorker?: WorkerType | null
}

export function PlayerPanel({
  player,
  isCurrentPlayer,
  isCurrentTurn,
  onSelectWorker,
  selectedWorker,
}: PlayerPanelProps) {
  const colorStyles: Record<string, string> = {
    blue: 'border-l-blue-500',
    red: 'border-l-red-500',
    green: 'border-l-green-500',
    yellow: 'border-l-yellow-500',
  }

  return (
    <div
      className={`p-4 rounded-lg border-l-4 ${colorStyles[player.color]} ${
        isCurrentTurn
          ? 'bg-hanyang-gold/10 ring-2 ring-hanyang-gold'
          : 'bg-hanyang-paper'
      } ${isCurrentPlayer ? 'shadow-lg' : ''}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-bold text-lg text-hanyang-brown">
            {player.username}
          </span>
          {player.is_host && (
            <span className="px-2 py-0.5 text-xs bg-hanyang-gold text-hanyang-brown rounded">
              방장
            </span>
          )}
          {isCurrentPlayer && (
            <span className="px-2 py-0.5 text-xs bg-hanyang-blue text-white rounded">
              나
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isCurrentTurn && (
            <span className="px-2 py-1 text-xs bg-hanyang-red text-white rounded animate-pulse">
              턴 진행 중
            </span>
          )}
          <span className="font-bold text-xl text-hanyang-gold">
            {player.score}점
          </span>
        </div>
      </div>

      {/* Resources */}
      <div className="mb-3">
        <ResourceDisplay resources={player.resources} />
      </div>

      {/* Workers - only interactive for current player on their turn */}
      <WorkerDisplay
        workers={player.workers}
        onSelectWorker={isCurrentPlayer && isCurrentTurn ? onSelectWorker : undefined}
        selectedWorker={isCurrentPlayer ? selectedWorker : null}
        disabled={!isCurrentPlayer || !isCurrentTurn}
      />

      {/* Blueprints count */}
      {player.blueprints.length > 0 && (
        <div className="mt-3 text-sm text-hanyang-brown/70">
          청사진: {player.blueprints.length}장
        </div>
      )}
    </div>
  )
}

export default PlayerPanel
