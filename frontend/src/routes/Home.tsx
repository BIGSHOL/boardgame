import { Link } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function Home() {
  const { isAuthenticated, user, logout } = useAuthStore()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-hanyang-navy text-white py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <h1 className="font-display text-2xl text-hanyang-gold">
            한양: 도읍의 설계자들
          </h1>
          <nav className="flex gap-4 items-center">
            {isAuthenticated ? (
              <>
                <span className="text-sm">안녕하세요, {user?.username}님</span>
                <Link to="/profile" className="text-hanyang-gold hover:underline">
                  프로필
                </Link>
                <button onClick={logout} className="btn-secondary text-sm">
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-hanyang-gold hover:underline">
                  로그인
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  회원가입
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-display text-4xl text-hanyang-navy mb-6">
            조선의 새 수도를 설계하라
          </h2>
          <p className="text-lg text-hanyang-stone mb-8">
            1394년, 조선 태조의 명을 받아 한양 천도를 위한 도성 건설에 참여하세요.
            풍수지리의 지혜를 활용하고, 워커를 파견하여 경복궁부터 시장까지
            조선의 새로운 수도를 완성하세요.
          </p>

          {isAuthenticated ? (
            <div className="flex flex-col gap-4 items-center">
              <div className="flex gap-4 justify-center">
                <Link to="/lobbies" className="btn-primary text-lg px-8 py-3 inline-block">
                  멀티플레이
                </Link>
                <Link to="/solo" className="btn-secondary text-lg px-8 py-3 inline-block bg-hanyang-gold text-hanyang-navy hover:bg-yellow-400">
                  솔로플레이
                </Link>
              </div>
              <p className="text-sm text-hanyang-stone">
                솔로플레이로 AI 상대와 연습하거나 멀티플레이로 다른 플레이어와 대전하세요
              </p>
            </div>
          ) : (
            <Link to="/register" className="btn-primary text-lg px-8 py-3 inline-block">
              지금 시작하기
            </Link>
          )}

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="card">
              <div className="text-4xl mb-4">🏛️</div>
              <h3 className="font-display text-xl text-hanyang-navy mb-2">
                건물 건설
              </h3>
              <p className="text-hanyang-stone">
                6각형 타일을 배치하여 경복궁, 종묘, 시장 등 다양한 건물을 건설하세요.
              </p>
            </div>
            <div className="card">
              <div className="text-4xl mb-4">👷</div>
              <h3 className="font-display text-xl text-hanyang-navy mb-2">
                워커 파견
              </h3>
              <p className="text-hanyang-stone">
                견습생과 관리를 전략적으로 배치하여 자원을 확보하고 건설을 진행하세요.
              </p>
            </div>
            <div className="card">
              <div className="text-4xl mb-4">🌊</div>
              <h3 className="font-display text-xl text-hanyang-navy mb-2">
                배산임수
              </h3>
              <p className="text-hanyang-stone">
                풍수지리 원칙에 따라 건물을 배치하여 추가 점수를 획득하세요.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-hanyang-navy text-white py-6">
        <div className="container mx-auto px-4 text-center text-sm">
          <p>Hanyang: The Foundation - 보드게임 프로토타입</p>
          <p className="text-hanyang-gold mt-2">버전 0.1.0</p>
        </div>
      </footer>
    </div>
  )
}
