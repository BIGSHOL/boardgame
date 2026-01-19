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
  1: '🥇',
  2: '🥈',
  3: '🥉',
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
                나
              </span>
            )}
          </div>
          <div className="text-sm text-hanyang-brown/60">
            {ranking.rank === 1 ? '우승!' : `${ranking.rank}위`}
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-hanyang-brown">{score_breakdown.total}</div>
          <div className="text-sm text-hanyang-brown/60">총점</div>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">건물 점수</span>
          <span className="font-medium text-hanyang-brown">+{score_breakdown.building_points}</span>
        </div>
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">청사진 보너스</span>
          <span className="font-medium text-green-600">+{score_breakdown.blueprint_bonus}</span>
        </div>
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">일꾼 점수</span>
          <span className="font-medium text-blue-600">+{score_breakdown.worker_score || 0}</span>
        </div>
        <div className="flex justify-between p-2 bg-white/50 rounded">
          <span className="text-hanyang-brown/70">자원 패널티</span>
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
      setError(err instanceof Error ? err.message : '결과를 불러올 수 없습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
        <div className="text-hanyang-brown text-xl">결과 로딩 중...</div>
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
          다시 시도
        </button>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
        <div className="text-hanyang-brown text-xl">결과를 찾을 수 없습니다.</div>
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
          게임 종료
        </h1>
        <p className="text-hanyang-brown/70">
          {result.total_rounds}라운드 완료
        </p>
      </header>

      {/* Winner Announcement */}
      <div className="max-w-md mx-auto mb-8 p-6 bg-gradient-to-br from-yellow-100 to-yellow-200 rounded-xl border-2 border-yellow-400 text-center">
        <div className="text-6xl mb-2">🏆</div>
        <div className="text-2xl font-bold text-yellow-800 mb-1">
          {winner?.username}
        </div>
        <div className="text-yellow-700">
          {winner?.score_breakdown.total}점으로 우승!
        </div>
        {isWinner && (
          <div className="mt-2 text-lg text-yellow-800 font-medium">
            축하합니다! 당신이 우승했습니다!
          </div>
        )}
      </div>

      {/* Rankings */}
      <div className="max-w-2xl mx-auto space-y-4">
        <h2 className="text-xl font-bold text-hanyang-brown mb-4">최종 순위</h2>
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
          로비 목록으로
        </Link>
        <button
          type="button"
          onClick={() => navigate(`/game/${gameId}`)}
          className="px-6 py-3 bg-hanyang-paper border border-hanyang-brown/30 text-hanyang-brown rounded-lg hover:bg-hanyang-cream transition-colors"
        >
          게임 보드 다시 보기
        </button>
      </div>

      {/* Game Stats */}
      <div className="max-w-2xl mx-auto mt-8 p-4 bg-hanyang-paper rounded-lg border border-hanyang-brown/20">
        <h3 className="font-bold text-hanyang-brown mb-3">게임 통계</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">{result.game_id}</div>
            <div className="text-hanyang-brown/60">게임 ID</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">{result.total_rounds}</div>
            <div className="text-hanyang-brown/60">총 라운드</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">{result.rankings.length}</div>
            <div className="text-hanyang-brown/60">참가자</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-hanyang-brown">
              {result.duration_minutes > 0 ? `${result.duration_minutes}분` : '-'}
            </div>
            <div className="text-hanyang-brown/60">소요 시간</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GameResult
