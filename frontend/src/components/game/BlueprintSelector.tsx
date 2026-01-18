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
        \uCCAD\uC0AC\uC9C4 \uC120\uD0DD
      </h3>
      <p className="text-sm text-hanyang-brown/70 mb-4">
        \uAC8C\uC784 \uC885\uB8CC \uC2DC \uC870\uAC74\uC744 \uCDA9\uC871\uD558\uBA74 \uBCF4\uB108\uC2A4 \uC810\uC218\uB97C \uBC1B\uC2B5\uB2C8\uB2E4.
        \uD558\uB098\uB97C \uC120\uD0DD\uD558\uC138\uC694.
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
        {selectedBlueprintId ? '\uCCAD\uC0AC\uC9C4 \uC120\uD0DD \uD655\uC815' : '\uCCAD\uC0AC\uC9C4\uC744 \uC120\uD0DD\uD558\uC138\uC694'}
      </button>
    </div>
  )
}

export default BlueprintSelector
