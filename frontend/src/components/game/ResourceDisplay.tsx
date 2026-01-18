import type { Resources, ResourceType } from '../../types/game'

interface ResourceDisplayProps {
  resources: Resources
  showMax?: boolean
}

const RESOURCE_CONFIG: Record<ResourceType, { label: string; icon: string; max: number }> = {
  wood: { label: '목재', icon: '🪵', max: 10 },
  stone: { label: '석재', icon: '🪨', max: 10 },
  tile: { label: '기와', icon: '🧱', max: 6 },
  ink: { label: '먹', icon: '🖤', max: 4 },
}

export function ResourceDisplay({ resources, showMax = true }: ResourceDisplayProps) {
  return (
    <div className="flex gap-4 p-3 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
      {(Object.keys(RESOURCE_CONFIG) as ResourceType[]).map((type) => {
        const config = RESOURCE_CONFIG[type]
        const value = resources[type]
        const isFull = value >= config.max

        return (
          <div
            key={type}
            className={`flex items-center gap-2 px-3 py-1 rounded ${
              isFull ? 'bg-hanyang-gold/20' : 'bg-white/50'
            }`}
            title={config.label}
          >
            <span className="text-lg" role="img" aria-label={config.label}>
              {config.icon}
            </span>
            <span className="font-medium text-hanyang-brown">
              {value}
              {showMax && <span className="text-hanyang-brown/50">/{config.max}</span>}
            </span>
          </div>
        )
      })}
    </div>
  )
}

export default ResourceDisplay
