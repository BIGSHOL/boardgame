import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function Profile() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-hanyang-cream">
      {/* Header */}
      <header className="bg-hanyang-navy text-white py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <Link to="/" className="font-display text-2xl text-hanyang-gold">
            한양: 도읍의 설계자들
          </Link>
          <nav className="flex gap-4 items-center">
            <span className="text-sm">안녕하세요, {user.username}님</span>
            <button onClick={handleLogout} className="btn-secondary text-sm">
              로그아웃
            </button>
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="font-display text-3xl text-hanyang-navy mb-8">
            프로필
          </h1>

          <div className="card mb-6">
            <h2 className="font-display text-xl text-hanyang-navy mb-4">
              계정 정보
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-hanyang-stone">
                  사용자명
                </label>
                <p className="text-hanyang-navy">{user.username}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-hanyang-stone">
                  이메일
                </label>
                <p className="text-hanyang-navy">{user.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-hanyang-stone">
                  가입일
                </label>
                <p className="text-hanyang-navy">
                  {new Date(user.created_at).toLocaleDateString('ko-KR')}
                </p>
              </div>
            </div>
          </div>

          <div className="card mb-6">
            <h2 className="font-display text-xl text-hanyang-navy mb-4">
              게임 통계
            </h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-3xl font-bold text-hanyang-gold">0</p>
                <p className="text-sm text-hanyang-stone">플레이 횟수</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-hanyang-gold">0</p>
                <p className="text-sm text-hanyang-stone">승리</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-hanyang-gold">-</p>
                <p className="text-sm text-hanyang-stone">평균 점수</p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="font-display text-xl text-hanyang-navy mb-4">
              계정 관리
            </h2>
            <div className="space-y-4">
              <button className="btn-secondary w-full">
                비밀번호 변경
              </button>
              <button
                onClick={handleLogout}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded transition-colors"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
