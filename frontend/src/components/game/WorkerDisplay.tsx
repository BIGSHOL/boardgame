import type { PlayerWorkers, WorkerType } from '../../types/game'

interface WorkerDisplayProps {
  workers: PlayerWorkers
  onSelectWorker?: (type: WorkerType) => void
  selectedWorker?: WorkerType | null
  disabled?: boolean
}

export function WorkerDisplay({
  workers,
  onSelectWorker,
  selectedWorker,
  disabled = false,
}: WorkerDisplayProps) {
  const canPlaceApprentice = workers.apprentices.available > 0
  const canPlaceOfficial = workers.officials.available > 0

  return (
    <div className="flex gap-4 p-3 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
      {/* Apprentices */}
      <button
        type="button"
        className={`flex flex-col items-center gap-1 px-4 py-2 rounded transition-all ${
          selectedWorker === 'apprentice'
            ? 'bg-hanyang-gold ring-2 ring-hanyang-brown'
            : canPlaceApprentice && !disabled
            ? 'bg-white/50 hover:bg-hanyang-gold/20 cursor-pointer'
            : 'bg-gray-100 opacity-50 cursor-not-allowed'
        }`}
        onClick={() => onSelectWorker?.('apprentice')}
        disabled={disabled || !canPlaceApprentice}
        aria-label="견습생 선택"
        aria-pressed={selectedWorker === 'apprentice'}
      >
        <div className="flex items-center gap-1">
          <span className="text-2xl" role="img" aria-label="견습생">
            👷
          </span>
          <span className="text-sm font-medium text-hanyang-brown">견습생</span>
        </div>
        <div className="flex gap-1">
          {Array.from({ length: workers.apprentices.total }).map((_, i) => (
            <div
              key={i}
              className={`w-3 h-3 rounded-full border border-hanyang-brown ${
                i < workers.apprentices.available
                  ? 'bg-hanyang-blue'
                  : 'bg-gray-300'
              }`}
              title={i < workers.apprentices.available ? '사용 가능' : '배치됨'}
            />
          ))}
        </div>
        <span className="text-xs text-hanyang-brown/70">
          {workers.apprentices.available}/{workers.apprentices.total}
        </span>
      </button>

      {/* Officials */}
      <button
        type="button"
        className={`flex flex-col items-center gap-1 px-4 py-2 rounded transition-all ${
          selectedWorker === 'official'
            ? 'bg-hanyang-gold ring-2 ring-hanyang-brown'
            : canPlaceOfficial && !disabled
            ? 'bg-white/50 hover:bg-hanyang-gold/20 cursor-pointer'
            : 'bg-gray-100 opacity-50 cursor-not-allowed'
        }`}
        onClick={() => onSelectWorker?.('official')}
        disabled={disabled || !canPlaceOfficial}
        aria-label="관리 선택"
        aria-pressed={selectedWorker === 'official'}
      >
        <div className="flex items-center gap-1">
          <span className="text-2xl" role="img" aria-label="관리">
            🧑‍💼
          </span>
          <span className="text-sm font-medium text-hanyang-brown">관리</span>
        </div>
        <div className="flex gap-1">
          {Array.from({ length: workers.officials.total }).map((_, i) => (
            <div
              key={i}
              className={`w-3 h-3 rounded-full border border-hanyang-brown ${
                i < workers.officials.available
                  ? 'bg-hanyang-red'
                  : 'bg-gray-300'
              }`}
              title={i < workers.officials.available ? '사용 가능' : '배치됨'}
            />
          ))}
        </div>
        <span className="text-xs text-hanyang-brown/70">
          {workers.officials.available}/{workers.officials.total}
        </span>
      </button>
    </div>
  )
}

export default WorkerDisplay
