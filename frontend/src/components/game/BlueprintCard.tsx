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
  palace_proximity: '\uD83C\uDFEF', // Castle emoji
  category_collection: '\uD83D\uDCDA', // Books emoji
  pattern: '\uD83D\uDD73\uFE0F', // Pattern emoji
  special: '\u2728', // Sparkles emoji
}

const CATEGORY_NAMES: Record<BlueprintCategory, string> = {
  palace_proximity: '\uAD81\uAD90 \uC778\uC811',
  category_collection: '\uAC74\uBB3C \uC218\uC9D1',
  pattern: '\uD328\uD134',
  special: '\uD2B9\uC218',
}

export function BlueprintCard({
  blueprint,
  isSelected = false,
  isSelectable = false,
  onSelect,
  showProgress = false,
}: BlueprintCardProps) {
  const categoryColor = CATEGORY_COLORS[blueprint.category] || 'bg-gray-100 border-gray-400'
  const categoryIcon = CATEGORY_ICONS[blueprint.category] || '\uD83D\uDCDC'
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
      aria-label={`${blueprint.name_ko} \uCCAD\uC0AC\uC9C4`}
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
          <div className="text-xs text-hanyang-brown/60">\uC810</div>
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
            {blueprint.is_completed ? '\u2713 \uC644\uB8CC' : '\uBBF8\uC644\uB8CC'}
          </span>
          {blueprint.current_score !== undefined && blueprint.current_score > 0 && (
            <span className="text-green-600 font-medium">
              +{blueprint.current_score}\uC810 \uD68D\uB4DD
            </span>
          )}
        </div>
      )}
    </button>
  )
}

export default BlueprintCard
