import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { apiClient as client } from '../api/client'

interface AIPersonality {
  id: string
  name: string
  name_en: string
  difficulty: string
  strategy: string
}

export default function SoloPlay() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [numOpponents, setNumOpponents] = useState(1)
  const [difficulty, setDifficulty] = useState('medium')
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const difficulties = [
    { value: 'easy', label: '쉬움', description: '무작위 결정, 연습용' },
    { value: 'medium', label: '보통', description: '기본 전략 사용' },
    { value: 'hard', label: '어려움', description: '최적화된 전략' },
  ]

  const handleCreateGame = async () => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    setIsCreating(true)
    setError(null)

    try {
      const response = await client.post('/solo/create', {
        num_ai_opponents: numOpponents,
        ai_difficulty: difficulty,
      })

      if (response.data.game_id) {
        navigate(`/game/${response.data.game_id}`)
      }
    } catch (err: any) {
      console.error('Failed to create solo game:', err)
      setError(err.response?.data?.detail || '게임 생성에 실패했습니다')
    } finally {
      setIsCreating(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-hanyang-navy to-slate-800 flex items-center justify-center">
        <div className="card max-w-md mx-4 text-center">
          <h2 className="font-display text-2xl text-hanyang-navy mb-4">로그인 필요</h2>
          <p className="text-hanyang-stone mb-6">
            솔로플레이를 시작하려면 로그인이 필요합니다.
          </p>
          <Link to="/login" className="btn-primary">
            로그인하기
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-hanyang-navy to-slate-800">
      {/* Header */}
      <header className="bg-hanyang-navy/50 backdrop-blur-sm border-b border-hanyang-gold/20 py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <Link to="/" className="font-display text-2xl text-hanyang-gold hover:text-yellow-400 transition-colors">
            한양: 도읍의 설계자들
          </Link>
          <nav>
            <Link to="/" className="text-white hover:text-hanyang-gold transition-colors">
              홈으로
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="font-display text-4xl text-hanyang-gold text-center mb-8">
            솔로플레이
          </h1>

          <div className="card">
            <h2 className="font-display text-xl text-hanyang-navy mb-6 text-center">
              AI 상대 설정
            </h2>

            {/* Number of Opponents */}
            <div className="mb-6">
              <label className="block text-hanyang-navy font-medium mb-2">
                AI 상대 수
              </label>
              <div className="flex gap-2">
                {[1, 2, 3].map((num) => (
                  <button
                    key={num}
                    onClick={() => setNumOpponents(num)}
                    className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                      numOpponents === num
                        ? 'bg-hanyang-navy text-white'
                        : 'bg-gray-100 text-hanyang-navy hover:bg-gray-200'
                    }`}
                  >
                    {num}명
                  </button>
                ))}
              </div>
              <p className="text-sm text-hanyang-stone mt-2">
                {numOpponents + 1}인 게임 (본인 + AI {numOpponents}명)
              </p>
            </div>

            {/* Difficulty */}
            <div className="mb-8">
              <label className="block text-hanyang-navy font-medium mb-2">
                AI 난이도
              </label>
              <div className="space-y-2">
                {difficulties.map((d) => (
                  <button
                    key={d.value}
                    onClick={() => setDifficulty(d.value)}
                    className={`w-full p-4 rounded-lg text-left transition-all ${
                      difficulty === d.value
                        ? 'bg-hanyang-navy text-white'
                        : 'bg-gray-100 text-hanyang-navy hover:bg-gray-200'
                    }`}
                  >
                    <div className="font-medium">{d.label}</div>
                    <div className={`text-sm ${difficulty === d.value ? 'text-gray-300' : 'text-hanyang-stone'}`}>
                      {d.description}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600 text-center">
                {error}
              </div>
            )}

            {/* Start Button */}
            <button
              onClick={handleCreateGame}
              disabled={isCreating}
              className={`w-full py-4 rounded-lg font-display text-xl transition-all ${
                isCreating
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-hanyang-gold text-hanyang-navy hover:bg-yellow-400'
              }`}
            >
              {isCreating ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                  게임 생성 중...
                </span>
              ) : (
                '게임 시작'
              )}
            </button>
          </div>

          {/* Game Rules Summary */}
          <div className="mt-8 card bg-white/90">
            <h3 className="font-display text-lg text-hanyang-navy mb-4">
              게임 방법 요약
            </h3>
            <ul className="space-y-2 text-hanyang-stone">
              <li className="flex gap-2">
                <span className="text-hanyang-gold">1.</span>
                <span>건물 시장에서 타일을 선택하여 보드에 배치합니다</span>
              </li>
              <li className="flex gap-2">
                <span className="text-hanyang-gold">2.</span>
                <span>일꾼(견습생/관리)을 건물에 배치하여 자원을 생산합니다</span>
              </li>
              <li className="flex gap-2">
                <span className="text-hanyang-gold">3.</span>
                <span>풍수지리(배산임수)를 활용하면 추가 점수를 얻습니다</span>
              </li>
              <li className="flex gap-2">
                <span className="text-hanyang-gold">4.</span>
                <span>4라운드 후 가장 높은 점수를 획득한 플레이어가 승리!</span>
              </li>
            </ul>
            <div className="mt-4 pt-4 border-t border-gray-200">
              <Link
                to="/docs/rulebook"
                className="text-hanyang-navy hover:text-hanyang-gold transition-colors text-sm"
              >
                자세한 룰북 보기 →
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
