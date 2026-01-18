import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { gameApi } from '../api/game'
import type { GameResultResponse, PlayerRanking } from '../types/game'

const RANK_COLORS: Record<number, string> = {
  1: 'bg-yellow-400 text-yellow-900',
  2: 'bg-gray-300 text-gray-800',
  3: 'bg-orange-400 text-orange-900',
  4: 'bg-gray-200 text-gray-700',
}

const RANK_ICONS: Record<number, string> = {
  1: '\uD83E\uDD47',
  2: '\uD83E\uDD48',
  3: '\uD83E\uDD49',
  4: '4',
}

function ScoreCard({ ranking, isCurrentUser }: { ranking: PlayerRanking; isCurrentUser: boolean }) {
  const { score_breakdown } = ranking
  const rankColor = RANK_COLORS[ranking.rank] || 'bg-gray-100 text-gray-700'
  const rankIcon = RANK_ICONS[ranking.rank] || ranking.rank.toString()

  return (
    <div
      className={`
        p-4 rounded-lg border-2 transition-all
        ${isCurrentUser ? 'border-hanyang-gold ring-2 ring-hanyang-gold/50' : 'border-hanyang-brown/20'}
        ${ranking.rank === 1 ? 'bg-yellow-50' : 'bg-hanyang-paper'}
      `}
    >
      {/* Header */}
      <div className="flex items-center gap-4 mb-4">
        <div
          className={`
            w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold
            ${rankColor}
          `}
        >
          {rankIcon}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-hanyang-brown">{ranking.username}</span>
            {isCurrentUser && (
              <span className="text-xs px-2 py-0.5 bg-hanyang-gold/20 text-hanyang-gold rounded">
                \uB098
              </span>
            )}
          </div>
          <div className="text-sm text-hanyang-brown/60">
            {ranking.rank === 1 ? '\uC6B0\uC2B9!' : `${ranking.rank}\uC704`}
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-hanyang-brown">{score_breakdown.total}</div>
          <div className="text-sm text-hanyang-brown/60">\uCD1D\uC810</div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">\uAC74\uBB3C \uC810\uC218</span>
          <span className="font-medium text-hanyang-brown">+{score_breakdown.building_points}</span>
        </div>
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">\uCCAD\uC0AC\uC9C4 \uBCF4\uB108\uC2A4</span>
          <span className="font-medium text-green-600">+{score_breakdown.blueprint_bonus}</span>
        </div>
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">\uC77C\uAFBC \uC810\uC218</span>
          <span className="font-medium text-blue-600">+{score_breakdown.worker_score || 0}</span>
        </div>
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">\uC790\uC6D0 \uD328\uB110\uD2F0</span>
          <span className="font-medium text-red-600">{score_breakdown.remaining_resources}</span>
        </div>
      </div>
    </div>
  )
}

export function GameResult() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()
  const [result, setResult] = useState<GameResultResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const gameId = id ? parseInt(id, 10) : null

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    if (gameId) {
      loadResult()
    }
  }, [gameId])

  const loadResult = async () => {
    if (!gameId) return

    setIsLoading(true)
    setError(null)

    try {
      const data = await gameApi.getGameResult(gameId)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '\uACB0\uACFC\uB97C \uBD88\uB7EC\uC62C \uC218 \uC5C6\uC2B5\uB2C8\uB2E4.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
        <div className="text-hanyang-brown text-xl">\uACB0\uACFC \uB85C\uB529 \uC911...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-hanyang-cream">
        <div className="text-red-500 text-xl">{error}</div>
        <button
          type="button"
          className="px-4 py-2 bg-hanyang-blue text-white rounded hover:bg-hanyang-blue/80"
          onClick={loadResult}
        >
          \uB2E4\uC2DC \uC2DC\uB3C4
        </button>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
        <div className="text-hanyang-brown text-xl">\uACB0\uACFC\uB97C \uCC3E\uC744 \uC218 \uC5C6\uC2B5\uB2C8\uB2E4.</div>
      </div>
    )
  }

  const winner = result.rankings[0]
  const isWinner = winner && user && result.rankings.find(r => r.player_id === winner.player_id)?.username === user.username

  return (
    <div className="min-h-screen bg-hanyang-cream p-4">
      {/* Header */}
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold text-hanyang-brown mb-2">
          \uAC8C\uC784 \uC885\uB8CC
        </h1>
        <p className="text-hanyang-brown/70">
          {result.total_rounds}\uB77C\uC6B4\uB4DC \uC644\uB8CC
        </p>
      </header>

      {/* Winner Announcement */}
      <div className="max-w-md mx-auto mb-8 p-6 bg-gradient-to-br from-yellow-100 to-yellow-200 rounded-xl border-2 border-yellow-400 text-center">
        <div className="text-6xl mb-2">\uD83C\uDFC6</div>
        <div className="text-2xl font-bold text-yellow-800 mb-1">
          {winner?.username}
        </div>
        <div className="text-yellow-700">
          {winner?.score_breakdown.total}\uC810\uC73C\uB85C \uC6B0\uC2B9!
        </div>
        {isWinner && (
          <div className="mt-2 text-lg text-yellow-800 font-medium">
            \uCD95\uD558\uD569\uB2C8\uB2E4! \uB2F9\uC2E0\uC774 \uC6B0\uC2B9\uD588\uC2B5\uB2C8\uB2E4!
          </div>
        )}
      </div>

      {/* Rankings */}
      <div className="max-w-2xl mx-auto space-y-4">
        <h2 className="text-xl font-bold text-hanyang-brown mb-4">\uCD5C\uC885 \uC21C\uC704</h2>
        {result.rankings.map((ranking) => (
          <ScoreCard
            key={ranking.player_id}
            ranking={ranking}
            isCurrentUser={ranking.username === user?.username}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="max-w-2xl mx-auto mt-8 flex justify-center gap-4">
        <Link
          to="/lobbies"
          className="px-6 py-3 bg-hanyang-blue text-white rounded-lg hover:bg-hanyang-blue/80 transition-colors"
        >
          \uB85C\uBE44 \uBAA9\uB85D\uC73C\uB85C
        </Link>
        <button
          type="button"
          onClick={() => navigate(`/game/${gameId}`)}
          className="px-6 py-3 bg-hanyang-paper border border-hanyang-brown/30 text-hanyang-brown rounded-lg hover:bg-hanyang-cream transition-colors"
        >
          \uAC8C\uC784 \uBCF4\uB4DC \uB2E4\uC2DC \uBCF4\uAE30
        </button>
      </div>

      {/* Game Stats */}
      <div className="max-w-2xl mx-auto mt-8 p-4 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
        <h3 className="font-bold text-hanyang-brown mb-3">\uAC8C\uC784 \uD1B5\uACC4</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">{result.game_id}</div>
            <div className="text-hanyang-brown/60">\uAC8C\uC784 ID</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">{result.total_rounds}</div>
            <div className="text-hanyang-brown/60">\uCD1D \uB77C\uC6B4\uB4DC</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">{result.rankings.length}</div>
            <div className="text-hanyang-brown/60">\uCC38\uAC00\uC790</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">
              {result.duration_minutes > 0 ? `${result.duration_minutes}\uBD84` : '-'}
            </div>
            <div className="text-hanyang-brown/60">\uC18C\uC694 \uC2DC\uAC04</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GameResult
