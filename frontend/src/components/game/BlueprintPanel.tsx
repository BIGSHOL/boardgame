import { BlueprintCard } from './BlueprintCard'
import type { BlueprintInfo } from '../../types/game'

interface BlueprintPanelProps {
  blueprints: BlueprintInfo[]
  title?: string
  showProgress?: boolean
}

export function BlueprintPanel({
  blueprints,
  title = '\uB0B4 \uCCAD\uC0AC\uC9C4',
  showProgress = true,
}: BlueprintPanelProps) {
  if (blueprints.length === 0) {
    return (
      <div className="p-4 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
        <h3 className="text-sm font-bold text-hanyang-brown mb-2">{title}</h3>
        <p className="text-sm text-hanyang-brown/50 text-center py-4">
          \uC544\uC9C1 \uC120\uD0DD\uD55C \uCCAD\uC0AC\uC9C4\uC774 \uC5C6\uC2B5\uB2C8\uB2E4.
        </p>
      </div>
    )
  }

  const totalPotentialScore = blueprints.reduce((sum, bp) => sum + bp.bonus_points, 0)
  const earnedScore = blueprints.reduce((sum, bp) => sum + (bp.current_score || 0), 0)
  const completedCount = blueprints.filter((bp) => bp.is_completed).length

  return (
    <div className="p-4 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-hanyang-brown">{title}</h3>
        {showProgress && (
          <div className="text-xs text-hanyang-brown/70">
            <span className="text-green-600 font-medium">{completedCount}</span>
            <span>/{blueprints.length} \uC644\uB8CC</span>
          </div>
        )}
      </div>

      <div className="space-y-2">
        {blueprints.map((blueprint) => (
          <BlueprintCard
            key={blueprint.blueprint_id}
            blueprint={blueprint}
            showProgress={showProgress}
          />
        ))}
      </div>

      {showProgress && (
        <div className="mt-3 pt-3 border-t border-hanyang-brown/20">
          <div className="flex justify-between text-sm">
            <span className="text-hanyang-brown/70">\uCCAD\uC0AC\uC9C4 \uC810\uC218</span>
            <span className="font-medium text-hanyang-brown">
              <span className="text-green-600">{earnedScore}</span>
              <span className="text-hanyang-brown/50"> / {totalPotentialScore}\uC810</span>
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default BlueprintPanel
