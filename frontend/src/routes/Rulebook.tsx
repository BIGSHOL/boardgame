import { Link } from 'react-router-dom'

export default function Rulebook() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-hanyang-navy to-slate-800">
      {/* Header */}
      <header className="bg-hanyang-navy/50 backdrop-blur-sm border-b border-hanyang-gold/20 py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <Link to="/" className="font-display text-2xl text-hanyang-gold hover:text-yellow-400 transition-colors">
            한양: 도읍의 설계자들
          </Link>
          <nav className="flex gap-4">
            <Link to="/" className="text-white hover:text-hanyang-gold transition-colors">
              홈으로
            </Link>
            <Link to="/solo" className="text-white hover:text-hanyang-gold transition-colors">
              솔로플레이
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto bg-white/95 rounded-lg shadow-xl p-8">
          <h1 className="font-display text-4xl text-hanyang-navy text-center mb-8">
            게임 룰북
          </h1>

          {/* Game Overview */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              게임 개요
            </h2>
            <p className="text-hanyang-stone leading-relaxed mb-4">
              <strong>한양: 도읍의 설계자들</strong>은 1394년 조선 태조의 명을 받아 한양 천도를 위한
              도성 건설에 참여하는 전략 보드게임입니다. 플레이어들은 풍수지리의 지혜를 활용하여
              건물을 배치하고, 일꾼을 파견하여 자원을 확보하며, 청사진을 완성해 점수를 획득합니다.
            </p>
            <ul className="list-disc list-inside text-hanyang-stone space-y-1">
              <li>인원: 2-4명</li>
              <li>시간: 30-45분</li>
              <li>나이: 10세 이상</li>
            </ul>
          </section>

          {/* Game Setup */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              게임 준비
            </h2>
            <ol className="list-decimal list-inside text-hanyang-stone space-y-2">
              <li>각 플레이어에게 시작 자원을 지급합니다: 목재 2, 석재 1, 기와 1, 먹 0</li>
              <li>각 플레이어에게 견습생 3명, 관리 1명을 지급합니다</li>
              <li>청사진 카드 3장을 배분하고, 각자 1장을 선택합니다</li>
              <li>건물 타일을 섞어 시장에 6장을 공개합니다</li>
              <li>시작 플레이어를 정하고 게임을 시작합니다</li>
            </ol>
          </section>

          {/* Turn Structure */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              턴 진행
            </h2>
            <p className="text-hanyang-stone mb-4">
              자신의 턴에 다음 행동 중 하나를 수행할 수 있습니다:
            </p>

            <div className="space-y-4">
              <div className="bg-hanyang-cream/50 p-4 rounded">
                <h3 className="font-bold text-hanyang-navy mb-2">1. 건물 타일 배치</h3>
                <ul className="text-hanyang-stone space-y-1 text-sm">
                  <li>- 시장에서 건물 타일 1장을 선택합니다</li>
                  <li>- 타일 비용만큼 자원을 지불합니다</li>
                  <li>- 보드의 빈 칸에 타일을 배치합니다</li>
                  <li>- 배산임수 조건 충족 시 추가 점수를 획득합니다</li>
                </ul>
              </div>

              <div className="bg-hanyang-cream/50 p-4 rounded">
                <h3 className="font-bold text-hanyang-navy mb-2">2. 일꾼 배치</h3>
                <ul className="text-hanyang-stone space-y-1 text-sm">
                  <li>- 견습생 또는 관리를 건물에 배치합니다</li>
                  <li>- 견습생: 건물의 기본 효과를 발동합니다</li>
                  <li>- 관리: 건물의 강화 효과를 발동합니다</li>
                  <li>- 배치한 일꾼은 라운드 종료 시 회수됩니다</li>
                </ul>
              </div>

              <div className="bg-hanyang-cream/50 p-4 rounded">
                <h3 className="font-bold text-hanyang-navy mb-2">3. 턴 종료</h3>
                <p className="text-hanyang-stone text-sm">
                  행동을 하지 않고 턴을 넘길 수 있습니다.
                  모든 플레이어가 턴을 종료하면 라운드가 끝납니다.
                </p>
              </div>
            </div>
          </section>

          {/* Resources */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              자원
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-amber-100 rounded">
                <div className="text-3xl mb-2">🪵</div>
                <div className="font-bold text-hanyang-navy">목재</div>
                <div className="text-sm text-hanyang-stone">기본 건축 자원</div>
              </div>
              <div className="text-center p-4 bg-gray-200 rounded">
                <div className="text-3xl mb-2">🪨</div>
                <div className="font-bold text-hanyang-navy">석재</div>
                <div className="text-sm text-hanyang-stone">튼튼한 건축 자원</div>
              </div>
              <div className="text-center p-4 bg-orange-100 rounded">
                <div className="text-3xl mb-2">🧱</div>
                <div className="font-bold text-hanyang-navy">기와</div>
                <div className="text-sm text-hanyang-stone">지붕 건축 자원</div>
              </div>
              <div className="text-center p-4 bg-slate-200 rounded">
                <div className="text-3xl mb-2">🖤</div>
                <div className="font-bold text-hanyang-navy">먹</div>
                <div className="text-sm text-hanyang-stone">문서/청사진용</div>
              </div>
            </div>
          </section>

          {/* Workers */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              일꾼
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded border border-blue-200">
                <h3 className="font-bold text-hanyang-navy mb-2">견습생 (Apprentice)</h3>
                <ul className="text-hanyang-stone text-sm space-y-1">
                  <li>- 시작 시 3명 보유</li>
                  <li>- 건물의 기본 효과 발동</li>
                  <li>- 1개의 일꾼 슬롯 사용</li>
                </ul>
              </div>
              <div className="p-4 bg-purple-50 rounded border border-purple-200">
                <h3 className="font-bold text-hanyang-navy mb-2">관리 (Official)</h3>
                <ul className="text-hanyang-stone text-sm space-y-1">
                  <li>- 시작 시 1명 보유</li>
                  <li>- 건물의 강화 효과 발동</li>
                  <li>- 2개의 일꾼 슬롯 사용</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Feng Shui */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              배산임수 (풍수지리)
            </h2>
            <p className="text-hanyang-stone mb-4">
              한국 전통 건축의 핵심 원리인 배산임수를 적용하면 추가 점수를 획득합니다:
            </p>
            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded border">
              <ul className="text-hanyang-stone space-y-2">
                <li><strong>배산(背山)</strong>: 건물 뒤에 산이 있으면 +1점</li>
                <li><strong>임수(臨水)</strong>: 건물 앞에 물이 있으면 +1점</li>
                <li><strong>배산임수</strong>: 두 조건을 모두 충족하면 추가 +2점 (총 +4점)</li>
              </ul>
            </div>
          </section>

          {/* Building Types */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              건물 종류
            </h2>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-red-50 rounded border-l-4 border-red-500">
                <div className="font-bold text-hanyang-navy">궁궐 (Palace)</div>
                <div className="text-hanyang-stone">높은 점수, 높은 비용</div>
              </div>
              <div className="p-3 bg-blue-50 rounded border-l-4 border-blue-500">
                <div className="font-bold text-hanyang-navy">관청 (Government)</div>
                <div className="text-hanyang-stone">먹 생산, 청사진 관련</div>
              </div>
              <div className="p-3 bg-amber-50 rounded border-l-4 border-amber-500">
                <div className="font-bold text-hanyang-navy">종교 (Religious)</div>
                <div className="text-hanyang-stone">점수 및 특수 효과</div>
              </div>
              <div className="p-3 bg-green-50 rounded border-l-4 border-green-500">
                <div className="font-bold text-hanyang-navy">생산 (Production)</div>
                <div className="text-hanyang-stone">목재, 석재, 기와 생산</div>
              </div>
              <div className="p-3 bg-purple-50 rounded border-l-4 border-purple-500">
                <div className="font-bold text-hanyang-navy">상업 (Commercial)</div>
                <div className="text-hanyang-stone">자원 교환, 추가 행동</div>
              </div>
              <div className="p-3 bg-gray-100 rounded border-l-4 border-gray-500">
                <div className="font-bold text-hanyang-navy">주거 (Residential)</div>
                <div className="text-hanyang-stone">일꾼 관련 효과</div>
              </div>
            </div>
          </section>

          {/* Game End */}
          <section className="mb-8">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4 border-b-2 border-hanyang-gold pb-2">
              게임 종료 및 점수 계산
            </h2>
            <p className="text-hanyang-stone mb-4">
              4라운드가 끝나면 게임이 종료됩니다. 다음 항목으로 점수를 계산합니다:
            </p>
            <ul className="text-hanyang-stone space-y-2">
              <li><strong>건물 점수:</strong> 배치한 건물의 기본 점수 합계</li>
              <li><strong>배산임수 점수:</strong> 풍수지리 보너스 점수</li>
              <li><strong>청사진 점수:</strong> 완성한 청사진 카드 점수</li>
              <li><strong>자원 점수:</strong> 남은 자원 5개당 1점</li>
            </ul>
            <p className="text-hanyang-navy font-bold mt-4">
              가장 높은 점수를 획득한 플레이어가 승리합니다!
            </p>
          </section>

          {/* Tips */}
          <section className="bg-hanyang-gold/10 p-6 rounded-lg">
            <h2 className="text-2xl font-bold text-hanyang-navy mb-4">
              전략 팁
            </h2>
            <ul className="text-hanyang-stone space-y-2">
              <li>- 초반에는 생산 건물로 자원을 확보하세요</li>
              <li>- 배산임수 보너스를 적극 활용하세요</li>
              <li>- 청사진 조건을 미리 확인하고 계획적으로 건설하세요</li>
              <li>- 관리는 핵심 건물에 신중하게 배치하세요</li>
              <li>- 다른 플레이어의 전략을 관찰하고 대응하세요</li>
            </ul>
          </section>

          {/* Back Button */}
          <div className="mt-8 text-center">
            <Link
              to="/solo"
              className="inline-block px-8 py-3 bg-hanyang-gold text-hanyang-navy font-bold rounded-lg hover:bg-yellow-400 transition-colors"
            >
              솔로플레이 시작하기
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}
