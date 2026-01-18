import { motion, AnimatePresence } from 'framer-motion'
import type { BoardCell as BoardCellType, BoardPosition, WorkerType } from '../../types/game'

interface BoardCellProps {
  cell: BoardCellType
  isSelected: boolean
  isValidTarget: boolean
  onSelect: (position: BoardPosition) => void
}

// Animation variants
const tileVariants = {
  initial: { opacity: 0, scale: 0.5, y: -20 },
  animate: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.8 },
}

const workerVariants = {
  initial: { opacity: 0, scale: 0, rotate: -180 },
  animate: { opacity: 1, scale: 1, rotate: 0 },
  exit: { opacity: 0, scale: 0 },
}

const TERRAIN_STYLES: Record<string, string> = {
  normal: 'bg-hanyang-cream hover:bg-hanyang-gold/20',
  mountain: 'bg-gray-400 cursor-not-allowed',
  water: 'bg-blue-300 cursor-not-allowed',
}

const PLAYER_COLORS: Record<number, string> = {
  1: 'bg-blue-500',
  2: 'bg-red-500',
  3: 'bg-green-500',
  4: 'bg-yellow-500',
}

export function BoardCell({ cell, isSelected, isValidTarget, onSelect }: BoardCellProps) {
  // Clickable if: (1) has tile (for worker placement), or (2) is valid target (for tile placement)
  const isClickable = (cell.terrain === 'normal' && cell.tile !== null) || isValidTarget
  const hasWorkers = cell.tile?.placed_workers && cell.tile.placed_workers.length > 0

  return (
    <motion.button
      type="button"
      className={`
        w-full aspect-square border border-hanyang-brown/30 rounded
        flex flex-col items-center justify-center
        transition-colors duration-200
        ${TERRAIN_STYLES[cell.terrain]}
        ${isSelected ? 'ring-2 ring-hanyang-gold ring-offset-2' : ''}
        ${isValidTarget ? 'ring-2 ring-green-500' : ''}
        ${!isClickable && cell.terrain === 'normal' ? 'opacity-70' : ''}
        ${isClickable ? 'cursor-pointer' : 'cursor-not-allowed'}
      `}
      onClick={() => isClickable && onSelect(cell.position)}
      disabled={!isClickable}
      aria-label={`셀 ${cell.position.row},${cell.position.col}`}
      whileHover={isClickable ? { scale: 1.05 } : undefined}
      whileTap={isClickable ? { scale: 0.95 } : undefined}
      animate={isValidTarget ? { boxShadow: ['0 0 0 0 rgba(34, 197, 94, 0)', '0 0 8px 4px rgba(34, 197, 94, 0.4)', '0 0 0 0 rgba(34, 197, 94, 0)'] } : {}}
      transition={isValidTarget ? { duration: 1.5, repeat: Infinity } : { type: 'spring', stiffness: 400, damping: 17 }}
    >
      {/* Terrain indicator for special cells */}
      {cell.terrain === 'mountain' && (
        <span className="text-2xl" role="img" aria-label="산">
          ⛰️
        </span>
      )}
      {cell.terrain === 'water' && (
        <span className="text-2xl" role="img" aria-label="물">
          💧
        </span>
      )}

      {/* Tile with animation */}
      <AnimatePresence>
        {cell.tile && (
          <motion.div
            className="flex flex-col items-center gap-1"
            variants={tileVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
            key={cell.tile.tile_id}
          >
            <span className="text-xs font-medium text-hanyang-brown truncate max-w-full px-1">
              {getTileDisplayName(cell.tile.tile_id)}
            </span>

            {/* Placed workers with animation */}
            {hasWorkers && (
              <div className="flex gap-0.5">
                <AnimatePresence>
                  {cell.tile.placed_workers.map((worker, idx) => (
                    <motion.div
                      key={`${worker.player_id}-${worker.slot_index}-${idx}`}
                      className={`w-3 h-3 rounded-full ${PLAYER_COLORS[worker.player_id] || 'bg-gray-500'}`}
                      title={`${worker.worker_type === 'apprentice' ? '견습생' : '관리'} (플레이어 ${worker.player_id})`}
                      variants={workerVariants}
                      initial="initial"
                      animate="animate"
                      exit="exit"
                      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                    />
                  ))}
                </AnimatePresence>
              </div>
            )}

            {/* Worker slots indicator */}
            {cell.tile && !hasWorkers && (
              <div className="flex gap-0.5">
                <div className="w-2 h-2 rounded-full border border-hanyang-brown/30 bg-white/50" />
                <div className="w-2 h-2 rounded-full border border-hanyang-brown/30 bg-white/50" />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty cell indicator */}
      {cell.terrain === 'normal' && !cell.tile && (
        <span className="text-hanyang-brown/30 text-xs">빈 칸</span>
      )}
    </motion.button>
  )
}

function getTileDisplayName(tileId: string): string {
  const [type, num] = tileId.split('_')
  const typeNames: Record<string, string> = {
    palace: '궁궐',
    government: '관아',
    religious: '사찰',
    commercial: '시전',
    residential: '민가',
    gate: '성문',
  }
  return `${typeNames[type] || type} ${num}`
}

export default BoardCell
