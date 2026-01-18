import type { TileInfo, Resources } from '../../types/game'

interface TileSelectorProps {
  availableTiles: TileInfo[]
  playerResources: Resources
  selectedTileId: string | null
  onSelectTile: (tileId: string | null) => void
  disabled?: boolean
}

const CATEGORY_ICONS: Record<string, string> = {
  palace: '🏯',
  government: '🏛️',
  religious: '⛩️',
  commercial: '🏪',
  residential: '🏠',
  gate: '🚪',
}

const CATEGORY_COLORS: Record<string, string> = {
  palace: 'bg-purple-100 border-purple-400',
  government: 'bg-blue-100 border-blue-400',
  religious: 'bg-yellow-100 border-yellow-400',
  commercial: 'bg-green-100 border-green-400',
  residential: 'bg-orange-100 border-orange-400',
  gate: 'bg-gray-100 border-gray-400',
}

function getTileCategory(tileId: string): string {
  return tileId.split('_')[0]
}

function canAfford(resources: Resources, cost: TileInfo['cost']): boolean {
  return (
    resources.wood >= cost.wood &&
    resources.stone >= cost.stone &&
    resources.tile >= cost.tile &&
    resources.ink >= cost.ink
  )
}

export function TileSelector({
  availableTiles,
  playerResources,
  selectedTileId,
  onSelectTile,
  disabled = false,
}: TileSelectorProps) {
  if (availableTiles.length === 0) {
    return (
      <div className="p-4 bg-hanyang-paper rounded-lg border border-hanyang-brown/20 text-center text-hanyang-brown/50">
        사용 가능한 타일이 없습니다
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-bold text-hanyang-brown">타일 선택</h3>
      <div className="space-y-2">
        {availableTiles.map((tile) => {
          const category = getTileCategory(tile.tile_id)
          const affordable = canAfford(playerResources, tile.cost)
          const isSelected = selectedTileId === tile.tile_id
          const categoryColor = CATEGORY_COLORS[category] || 'bg-gray-100 border-gray-400'

          return (
            <button
              key={tile.tile_id}
              type="button"
              className={`
                w-full p-3 rounded-lg border-2 text-left transition-all
                ${categoryColor}
                ${isSelected ? 'ring-2 ring-hanyang-gold ring-offset-2' : ''}
                ${!affordable || disabled ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md cursor-pointer'}
              `}
              onClick={() => {
                if (affordable && !disabled) {
                  onSelectTile(isSelected ? null : tile.tile_id)
                }
              }}
              disabled={!affordable || disabled}
              aria-pressed={isSelected}
              aria-label={`${tile.name_ko} 선택`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xl" role="img" aria-label={category}>
                    {CATEGORY_ICONS[category] || '🏗️'}
                  </span>
                  <div>
                    <div className="font-medium text-hanyang-brown">{tile.name_ko}</div>
                    <div className="text-xs text-hanyang-brown/60">
                      기본 점수: {tile.base_points}점
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs font-medium text-hanyang-brown">비용</div>
                  <div className="flex gap-1 text-xs">
                    {tile.cost.wood > 0 && (
                      <span className={playerResources.wood >= tile.cost.wood ? '' : 'text-red-500'}>
                        🪵{tile.cost.wood}
                      </span>
                    )}
                    {tile.cost.stone > 0 && (
                      <span className={playerResources.stone >= tile.cost.stone ? '' : 'text-red-500'}>
                        🪨{tile.cost.stone}
                      </span>
                    )}
                    {tile.cost.tile > 0 && (
                      <span className={playerResources.tile >= tile.cost.tile ? '' : 'text-red-500'}>
                        🧱{tile.cost.tile}
                      </span>
                    )}
                    {tile.cost.ink > 0 && (
                      <span className={playerResources.ink >= tile.cost.ink ? '' : 'text-red-500'}>
                        🖤{tile.cost.ink}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </button>
          )
        })}
      </div>
      {selectedTileId && (
        <p className="text-xs text-hanyang-brown/70 text-center">
          보드에서 배치할 위치를 선택하세요
        </p>
      )}
    </div>
  )
}

export default TileSelector
