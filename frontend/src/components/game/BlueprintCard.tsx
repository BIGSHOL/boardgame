import type { BlueprintInfo, BlueprintCategory } from '../../types/game'

interface BlueprintCardProps {
  blueprint: BlueprintInfo
  isSelected?: boolean
  isSelectable?: boolean
  onSelect?: () => void
  showProgress?: boolean
}

const CATEGORY_COLORS: Record<BlueprintCategory, string> = {
  palace_proximity: 'bg-purple-100 border-purple-400',
  category_collection: 'bg-green-100 border-green-400',
  pattern: 'bg-blue-100 border-blue-400',
  special: 'bg-orange-100 border-orange-400',
}

const CATEGORY_ICONS: Record<BlueprintCategory, string> = {
  palace_proximity: '🏯',
  category_collection: '📚',
  pattern: '🔷',
  special: '✨',
}

const CATEGORY_NAMES: Record<BlueprintCategory, string> = {
  palace_proximity: '궁궐 인접',
  category_collection: '건물 수집',
  pattern: '패턴',
  special: '특수',
}

export function BlueprintCard({
  blueprint,
  isSelected = false,
  isSelectable = false,
  onSelect,
  showProgress = false,
}: BlueprintCardProps) {
  const categoryColor = CATEGORY_COLORS[blueprint.category] || 'bg-gray-100 border-gray-400'
  const categoryIcon = CATEGORY_ICONS[blueprint.category] || '📜'
  const categoryName = CATEGORY_NAMES[blueprint.category] || blueprint.category

  return (
    <button
      type="button"
      className={`
        w-full p-3 rounded-lg border-2 text-left transition-all
        ${categoryColor}
        ${isSelected ? 'ring-2 ring-hanyang-gold ring-offset-2' : ''}
        ${isSelectable ? 'hover:shadow-md cursor-pointer' : 'cursor-default'}
        ${blueprint.is_completed ? 'opacity-100' : showProgress ? 'opacity-70' : 'opacity-100'}
      `}
      onClick={() => isSelectable && onSelect?.()}
      disabled={!isSelectable}
      aria-pressed={isSelected}
      aria-label={`${blueprint.name_ko} 청사진`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl" role="img" aria-label={categoryName}>
            {categoryIcon}
          </span>
          <div>
            <div className="font-medium text-hanyang-brown">{blueprint.name_ko}</div>
            <div className="text-xs text-hanyang-brown/60">{categoryName}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-hanyang-gold">+{blueprint.bonus_points}</div>
          <div className="text-xs text-hanyang-brown/60">점</div>
        </div>
      </div>

      {/* Description */}
      <div className="text-sm text-hanyang-brown/80 mb-2">
        {blueprint.description_ko}
      </div>

      {/* Progress indicator */}
      {showProgress && (
        <div className="flex items-center justify-between text-xs">
          <span className={blueprint.is_completed ? 'text-green-600 font-medium' : 'text-hanyang-brown/50'}>
            {blueprint.is_completed ? '✓ 완료' : '미완료'}
          </span>
          {blueprint.current_score !== undefined && blueprint.current_score > 0 && (
            <span className="text-green-600 font-medium">
              +{blueprint.current_score}점 획득
            </span>
          )}
        </div>
      )}
    </button>
  )
}

export default BlueprintCard
