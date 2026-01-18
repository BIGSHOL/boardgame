import type { BoardCell as BoardCellType, BoardPosition, ValidAction } from '../../types/game'
import { BoardCell } from './BoardCell'

interface GameBoardProps {
  board: BoardCellType[][]
  selectedPosition: BoardPosition | null
  validActions: ValidAction[]
  selectedWorkerType: string | null
  selectedTileId: string | null
  validTilePositions: BoardPosition[]
  onSelectCell: (position: BoardPosition) => void
}

export function GameBoard({
  board,
  selectedPosition,
  validActions,
  selectedWorkerType,
  selectedTileId,
  validTilePositions,
  onSelectCell,
}: GameBoardProps) {
  // Get valid positions for the selected worker type
  const validWorkerPositions = new Set<string>()

  if (selectedWorkerType) {
    const workerAction = validActions.find(
      (a) => a.action_type === 'place_worker' && a.worker_type === selectedWorkerType
    )
    if (workerAction?.available_slots) {
      workerAction.available_slots.forEach((slot) => {
        if (slot.position) {
          validWorkerPositions.add(`${slot.position.row},${slot.position.col}`)
        }
      })
    }
  }

  // Get valid positions for tile placement
  const validTilePositionSet = new Set<string>()
  if (selectedTileId && validTilePositions) {
    validTilePositions.forEach((pos) => {
      validTilePositionSet.add(`${pos.row},${pos.col}`)
    })
  }

  // Combined valid positions
  const getValidTarget = (posKey: string): boolean => {
    if (selectedWorkerType) return validWorkerPositions.has(posKey)
    if (selectedTileId) return validTilePositionSet.has(posKey)
    return false
  }

  return (
    <div className="p-4 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
      <div className="grid grid-cols-5 gap-2">
        {board.map((row, rowIdx) =>
          row.map((cell, colIdx) => {
            const posKey = `${rowIdx},${colIdx}`
            const isSelected =
              selectedPosition?.row === rowIdx && selectedPosition?.col === colIdx
            const isValidTarget = getValidTarget(posKey)

            return (
              <BoardCell
                key={posKey}
                cell={cell}
                isSelected={isSelected}
                isValidTarget={isValidTarget}
                onSelect={onSelectCell}
              />
            )
          })
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 flex gap-4 text-sm text-hanyang-brown/70">
        <div className="flex items-center gap-1">
          <span role="img" aria-label="산">⛰️</span>
          <span>산 (건설 불가)</span>
        </div>
        <div className="flex items-center gap-1">
          <span role="img" aria-label="물">💧</span>
          <span>물 (배산임수)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
          <span>배치 가능</span>
        </div>
      </div>
    </div>
  )
}

export default GameBoard
