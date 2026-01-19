import { BlueprintCard } from './BlueprintCard'
import type { BlueprintInfo } from '../../types/game'

interface BlueprintSelectorProps {
  availableBlueprints: BlueprintInfo[]
  selectedBlueprintId: string | null
  onSelectBlueprint: (blueprintId: string | null) => void
  onConfirmSelection: () => void
  disabled?: boolean
}

export function BlueprintSelector({
  availableBlueprints,
  selectedBlueprintId,
  onSelectBlueprint,
  onConfirmSelection,
  disabled = false,
}: BlueprintSelectorProps) {
  if (availableBlueprints.length === 0) {
    return null
  }

  return (
    <div className="p-4 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
      <h3 className="text-lg font-bold text-hanyang-brown mb-2">
        청사진 선택
      </h3>
      <p className="text-sm text-hanyang-brown/70 mb-4">
        게임 종료 시 조건을 충족하면 보너스 점수를 받습니다.
        하나를 선택하세요.
      </p>

      <div className="space-y-3 mb-4">
        {availableBlueprints.map((blueprint) => (
          <BlueprintCard
            key={blueprint.blueprint_id}
            blueprint={blueprint}
            isSelected={selectedBlueprintId === blueprint.blueprint_id}
            isSelectable={!disabled}
            onSelect={() => {
              if (selectedBlueprintId === blueprint.blueprint_id) {
                onSelectBlueprint(null)
              } else {
                onSelectBlueprint(blueprint.blueprint_id)
              }
            }}
          />
        ))}
      </div>

      <button
        type="button"
        className={`
          w-full py-2 rounded font-medium transition-colors
          ${selectedBlueprintId
            ? 'bg-hanyang-gold text-white hover:bg-hanyang-gold/90'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'}
        `}
        onClick={onConfirmSelection}
        disabled={!selectedBlueprintId || disabled}
      >
        {selectedBlueprintId ? '청사진 선택 확정' : '청사진을 선택하세요'}
      </button>
    </div>
  )
}

export default BlueprintSelector
