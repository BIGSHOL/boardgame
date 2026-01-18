# Coding Convention & AI Collaboration Guide

> Hanyang: The Foundation - 개발 규칙 및 AI 협업 가이드

---

## MVP 캡슐

| # | 항목 | 내용 |
|---|------|------|
| 1 | 목표 | 보드게임 프로토타입을 디지털로 테스트하여 실제 제작 전 밸런싱 검증 |
| 2 | 페르소나 | 보드게임 동호회 회원 및 게임 디자이너 본인 |
| 3 | 핵심 기능 | FEAT-2: 워커 파견 및 자원 관리 (전략적 선택의 핵심) |
| 4 | 성공 지표 (노스스타) | 동호회원 5명이 완전한 게임 1판 테스트 완료 |
| 5 | 입력 지표 | 테스트 세션 수, 수집된 피드백 수 |
| 6 | 비기능 요구 | 빠른 게임 시작 (3분 이내 세팅), 실시간 멀티플레이 지원 |
| 7 | Out-of-scope | AI 상대, 랭킹 시스템, 모바일 네이티브 앱 |
| 8 | Top 리스크 | 복잡한 게임 룰로 인한 구현 난이도 |
| 9 | 완화/실험 | 핵심 메카닉(워커/자원)부터 점진적 구현 |
| 10 | 다음 단계 | 기본 게임 보드 UI 및 워커 배치 로직 구현 |

---

## 1. 핵심 원칙

### 1.1 신뢰하되, 검증하라 (Don't Trust, Verify)

AI가 생성한 코드는 반드시 검증해야 합니다:

- [ ] 코드 리뷰: 생성된 코드 직접 확인
- [ ] 테스트 실행: 자동화 테스트 통과 확인
- [ ] 보안 검토: 민감 정보 노출 여부 확인
- [ ] 동작 확인: 실제로 실행하여 기대 동작 확인

### 1.2 최종 책임은 인간에게

- AI는 도구이고, 최종 결정과 책임은 개발자에게 있습니다
- 이해하지 못하는 코드는 사용하지 않습니다
- 의심스러운 부분은 반드시 질문합니다

### 1.3 게임 로직 검증

- 게임 룰 구현 시 기획서(docs/design/01_hanyang_game_design.md) 참조 필수
- 새로운 메카닉 추가 전 기획서 업데이트
- 밸런스 변경 시 변경 로그 기록

---

## 2. 프로젝트 구조

### 2.1 디렉토리 구조

```
hanyang/
├── frontend/                      # React + Vite 프론트엔드
│   ├── src/
│   │   ├── components/           # 재사용 컴포넌트
│   │   │   ├── common/           # 공통 UI (Button, Card, Modal)
│   │   │   ├── board/            # 보드 관련 (MainBoard, PersonalBoard)
│   │   │   ├── game/             # 게임 UI (ActionPanel, TurnIndicator)
│   │   │   └── lobby/            # 로비 UI (LobbyList, PlayerList)
│   │   ├── pages/                # 페이지 컴포넌트
│   │   │   ├── Home.tsx
│   │   │   ├── Lobby.tsx
│   │   │   ├── Game.tsx
│   │   │   └── Result.tsx
│   │   ├── hooks/                # 커스텀 훅
│   │   │   ├── useGame.ts        # 게임 상태 관리
│   │   │   ├── useWebSocket.ts   # WebSocket 연결
│   │   │   └── useAuth.ts        # 인증 상태
│   │   ├── stores/               # Zustand 스토어
│   │   │   ├── gameStore.ts      # 게임 상태
│   │   │   ├── authStore.ts      # 인증 상태
│   │   │   └── uiStore.ts        # UI 상태
│   │   ├── services/             # API 호출
│   │   │   ├── api.ts            # API 클라이언트 (ky)
│   │   │   ├── authService.ts
│   │   │   ├── gameService.ts
│   │   │   └── lobbyService.ts
│   │   ├── utils/                # 유틸리티 함수
│   │   │   ├── gameLogic.ts      # 게임 로직 헬퍼
│   │   │   ├── fengshui.ts       # 풍수지리 계산
│   │   │   └── validation.ts     # 액션 검증
│   │   ├── types/                # TypeScript 타입
│   │   │   ├── game.ts           # 게임 관련 타입
│   │   │   ├── api.ts            # API 응답 타입
│   │   │   └── player.ts         # 플레이어 타입
│   │   ├── assets/               # 정적 에셋
│   │   │   ├── images/           # 건물, 타일 이미지
│   │   │   └── icons/            # 자원, UI 아이콘
│   │   └── mocks/                # MSW 목 핸들러
│   │       ├── handlers/
│   │       └── data/
│   └── e2e/                      # Playwright E2E 테스트
│
├── backend/                       # FastAPI 백엔드
│   ├── app/
│   │   ├── models/               # SQLAlchemy 모델
│   │   │   ├── user.py
│   │   │   ├── game.py
│   │   │   ├── lobby.py
│   │   │   └── master_data.py    # 건물, 카드 마스터
│   │   ├── schemas/              # Pydantic 스키마
│   │   │   ├── auth.py
│   │   │   ├── game.py
│   │   │   ├── lobby.py
│   │   │   └── action.py         # 게임 액션 스키마
│   │   ├── routers/              # API 라우터
│   │   │   ├── auth.py
│   │   │   ├── game.py
│   │   │   ├── lobby.py
│   │   │   └── websocket.py
│   │   ├── services/             # 비즈니스 로직
│   │   │   ├── auth_service.py
│   │   │   ├── game_service.py   # 게임 로직 (핵심!)
│   │   │   ├── lobby_service.py
│   │   │   └── fengshui_service.py
│   │   ├── core/                 # 핵심 설정
│   │   │   ├── config.py
│   │   │   ├── security.py       # JWT, 해싱
│   │   │   └── database.py
│   │   └── utils/
│   │       ├── game_validator.py # 액션 검증
│   │       └── score_calculator.py
│   ├── tests/
│   │   ├── api/                  # API 테스트
│   │   ├── services/             # 서비스 단위 테스트
│   │   └── ws/                   # WebSocket 테스트
│   └── alembic/                  # DB 마이그레이션
│
├── contracts/                     # API 계약 (BE/FE 공유)
│   ├── types.ts                  # 공통 타입
│   ├── auth.contract.ts
│   ├── game.contract.ts
│   ├── lobby.contract.ts
│   └── ws-messages.ts            # WebSocket 메시지 타입
│
├── docs/
│   ├── design/                   # 게임 기획서
│   │   └── 01_hanyang_game_design.md
│   └── planning/                 # 소크라테스 산출물
│       ├── 01-prd.md
│       ├── 02-trd.md
│       ├── 03-user-flow.md
│       ├── 04-database-design.md
│       ├── 05-design-system.md
│       ├── 06-tasks.md           # tasks-generator가 생성
│       └── 07-coding-convention.md
│
├── docker-compose.yml
├── .env.example
└── README.md
```

### 2.2 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일 (컴포넌트) | PascalCase | `MainBoard.tsx`, `GameCard.tsx` |
| 파일 (훅) | camelCase + use | `useGame.ts`, `useWebSocket.ts` |
| 파일 (Python) | snake_case | `game_service.py`, `fengshui_service.py` |
| React 컴포넌트 | PascalCase | `MainBoard`, `ActionPanel` |
| 함수/변수 (JS/TS) | camelCase | `calculateFengshui`, `playerState` |
| 함수/변수 (Python) | snake_case | `calculate_fengshui`, `player_state` |
| 상수 | UPPER_SNAKE | `MAX_PLAYERS`, `FENGSHUI_BONUS` |
| CSS 클래스 | kebab-case | `main-board`, `action-button` |
| 타입/인터페이스 | PascalCase | `GameState`, `PlayerAction` |
| Enum | PascalCase | `ActionType`, `BuildingCategory` |

### 2.3 게임 도메인 용어

| 영문 | 한글 | 코드 사용 |
|------|------|----------|
| Main Board | 메인 보드 (한양 지도) | `mainBoard` |
| Personal Board | 개인 보드 (건축가의 책상) | `personalBoard` |
| Apprentice | 견습공 | `apprentice` |
| Official | 관료 | `official` |
| Worker | 워커 (견습공+관료 총칭) | `worker` |
| Fengshui | 풍수지리 | `fengshui` |
| Baesanimsu | 배산임수 | `baesanimsu` |
| Blueprint | 청사진 (카드) | `blueprintCard` |
| Building Tile | 건물 타일 | `buildingTile` |

---

## 3. 아키텍처 원칙

### 3.1 뼈대 먼저 (Skeleton First)

1. 전체 구조를 먼저 잡고
2. 빈 함수/컴포넌트로 스켈레톤 생성
3. 하나씩 구현 채워나가기

### 3.2 작은 모듈로 분해

- 한 파일에 200줄 이하 권장
- 한 함수에 50줄 이하 권장
- 한 컴포넌트에 100줄 이하 권장

### 3.3 관심사 분리

| 레이어 | 역할 | 예시 |
|--------|------|------|
| UI | 화면 표시 | React 컴포넌트 |
| 상태 | 데이터 관리 | Zustand 스토어 |
| 서비스 | API 통신 | ky 래퍼 |
| 유틸 | 순수 함수 | 풍수지리 계산, 검증 |

### 3.4 게임 로직 위치

| 로직 | 위치 | 이유 |
|------|------|------|
| 액션 검증 | 백엔드 (필수) + 프론트엔드 (UX) | 보안, 치팅 방지 |
| 점수 계산 | 백엔드 | 일관성 |
| 풍수지리 보너스 | 백엔드 | 복잡한 로직 |
| UI 상태 | 프론트엔드 | 반응성 |
| 애니메이션 | 프론트엔드 | 사용자 경험 |

---

## 4. AI 소통 원칙

### 4.1 하나의 채팅 = 하나의 작업

- 한 번에 하나의 명확한 작업만 요청
- 작업 완료 후 다음 작업 진행
- 컨텍스트가 길어지면 새 대화 시작

### 4.2 컨텍스트 명시

**좋은 예:**
> "TASKS 문서의 P1-T2 (워커 파견 API)를 구현해주세요.
> Database Design의 GAME_PLAYER 테이블을 참조하고,
> TRD의 Contract-First TDD 방식을 따라주세요.
> 먼저 테스트를 작성하고, 그 다음 구현해주세요."

**나쁜 예:**
> "워커 시스템 만들어줘"

### 4.3 기존 코드 재사용

- 새로 만들기 전에 기존 코드 확인 요청
- 중복 코드 방지
- 일관성 유지

### 4.4 프롬프트 템플릿

```
## 작업
{{무엇을 해야 하는지}}

## 참조 문서
- 기획서: docs/design/01_hanyang_game_design.md
- PRD: docs/planning/01-prd.md 섹션 {{번호}}
- TRD: docs/planning/02-trd.md 섹션 {{번호}}
- DB: docs/planning/04-database-design.md

## 제약 조건
- Contract-First TDD 방식 (테스트 먼저)
- 기존 코드 패턴 따르기
- {{추가 제약}}

## 예상 결과
- {{생성될 파일}}
- {{기대 동작}}
```

---

## 5. 코딩 스타일

### 5.1 TypeScript (프론트엔드)

```typescript
// 타입 정의 예시
interface GameState {
  id: string;
  currentRound: number;
  currentTurn: number;
  phase: 'setup' | 'action' | 'scoring' | 'end';
  boardState: BoardState;
  players: GamePlayer[];
}

// 컴포넌트 예시
interface MainBoardProps {
  gameState: GameState;
  onTilePlace: (position: Position, tileId: string) => void;
}

export function MainBoard({ gameState, onTilePlace }: MainBoardProps) {
  // 구현
}

// 훅 예시
export function useGame(gameId: string) {
  const { gameState, setGameState } = useGameStore();

  // WebSocket 연결, 상태 관리 등

  return {
    gameState,
    placeWorker,
    buildTile,
    endTurn,
  };
}
```

### 5.2 Python (백엔드)

```python
# Pydantic 스키마 예시
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ActionType(str, Enum):
    DRAFT = "draft"
    GATHER = "gather"
    BUILD = "build"
    REGISTER = "register"

class GameAction(BaseModel):
    action_type: ActionType
    tile_id: Optional[str] = None
    position: Optional[tuple[int, int]] = None
    card_id: Optional[str] = None

# 서비스 예시
class GameService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_action(
        self,
        game_id: str,
        player_id: str,
        action: GameAction
    ) -> GameState:
        """게임 액션을 실행하고 새 상태를 반환합니다."""
        # 1. 게임 상태 조회
        game = await self._get_game(game_id)

        # 2. 액션 검증
        self._validate_action(game, player_id, action)

        # 3. 액션 실행
        new_state = self._apply_action(game, action)

        # 4. 상태 저장
        await self._save_game_state(game_id, new_state)

        return new_state
```

### 5.3 게임 로직 패턴

```python
# 풍수지리 보너스 계산 예시
def calculate_fengshui_bonus(
    position: Position,
    board_state: BoardState,
    building_tile: BuildingTile
) -> int:
    """건물 배치 시 풍수지리 보너스를 계산합니다."""
    bonus = 0

    # 배산 조건 (북쪽에 산)
    if building_tile.fengshui_bonus.get("backToMountain"):
        if _has_mountain_to_north(position, board_state):
            bonus += building_tile.fengshui_bonus.get("bonusPoints", 0)

    # 임수 조건 (남쪽에 물)
    if building_tile.fengshui_bonus.get("faceToWater"):
        if _has_water_to_south(position, board_state):
            bonus += building_tile.fengshui_bonus.get("bonusPoints", 0)

    return bonus
```

---

## 6. 보안 체크리스트

### 6.1 절대 금지

- [ ] 비밀정보 하드코딩 금지 (API 키, 비밀번호, JWT 시크릿)
- [ ] .env 파일 커밋 금지
- [ ] SQL 직접 문자열 조합 금지 (SQLAlchemy ORM 사용)
- [ ] 사용자 입력 그대로 출력 금지 (XSS)

### 6.2 필수 적용

- [ ] 모든 사용자 입력 검증 (Pydantic 서버 측)
- [ ] 비밀번호 해싱 (bcrypt)
- [ ] HTTPS 사용 (프로덕션)
- [ ] CORS 설정
- [ ] 인증된 요청만 게임 API 접근
- [ ] WebSocket 연결 시 토큰 검증

### 6.3 게임 특화 보안

- [ ] 액션 검증은 반드시 서버에서 (치팅 방지)
- [ ] 다른 플레이어의 비공개 정보(손패) 노출 금지
- [ ] 게임 상태 조작 시도 로깅

### 6.4 환경 변수 관리

```bash
# .env.example (커밋 O)
DATABASE_URL=postgresql://user:password@localhost:5432/hanyang
JWT_SECRET=your-secret-key-here
REDIS_URL=redis://localhost:6379

# .env (커밋 X)
DATABASE_URL=postgresql://prod:secret@prod-db:5432/hanyang
JWT_SECRET=actual-production-secret
REDIS_URL=redis://prod-redis:6379
```

---

## 7. 테스트 워크플로우

### 7.1 TDD 사이클

```
RED    → 실패하는 테스트 먼저 작성
GREEN  → 테스트를 통과하는 최소한의 코드 구현
REFACTOR → 테스트 통과 유지하며 코드 개선
```

### 7.2 즉시 실행 검증

코드 작성 후 바로 테스트:

```bash
# 백엔드
pytest backend/tests/ -v --cov=app

# 프론트엔드
npm run test

# E2E
npx playwright test

# 타입 체크
mypy backend/app/
npm run type-check
```

### 7.3 게임 로직 테스트

```python
# 풍수지리 보너스 테스트 예시
def test_fengshui_baesanimsu_full_bonus():
    """배산임수 조건 모두 충족 시 최대 보너스"""
    board = create_board_with_terrain()
    building = create_building_with_fengshui(
        back_to_mountain=True,
        face_to_water=True,
        bonus_points=3
    )
    position = Position(row=2, col=2)  # 산과 물 사이

    bonus = calculate_fengshui_bonus(position, board, building)

    assert bonus == 6  # 배산 3 + 임수 3
```

### 7.4 오류 로그 공유 규칙

오류 발생 시 AI에게 전달할 정보:

```
## 에러
WebSocket connection failed: TypeError: Cannot read property 'id' of undefined

## 코드
const gameId = gameState.id;  // line 42 in useGame.ts

## 재현
1. 로그인 후 로비에서 게임 시작
2. 다른 플레이어가 참가하기 전에 새로고침
3. WebSocket 연결 시도 시 에러

## 시도한 것
- gameState가 undefined인지 확인 → 맞음
- 초기값 설정 시도 → 여전히 에러
```

---

## 8. Git 워크플로우

### 8.1 브랜치 전략

```
main                    # 프로덕션 (보호됨)
├── develop             # 개발 통합
│   ├── feature/feat-0-auth
│   ├── feature/feat-1-board
│   ├── feature/feat-2-worker
│   ├── feature/feat-3-fengshui
│   └── fix/websocket-reconnect
```

### 8.2 커밋 메시지

```
<type>(<scope>): <subject>

<body>
```

**타입:**
- `feat`: 새 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `docs`: 문서
- `test`: 테스트
- `chore`: 기타 (빌드, 설정)

**스코프 (게임 특화):**
- `auth`: 인증
- `lobby`: 로비
- `board`: 보드 (메인/개인)
- `worker`: 워커 시스템
- `fengshui`: 풍수지리
- `ws`: WebSocket

**예시:**
```
feat(worker): 관료 파견 API 추가

- POST /api/v1/games/{id}/dispatch 엔드포인트
- 관료 영구 배치 로직 구현
- TASKS P1-T2 구현 완료

Refs: #12
```

---

## 9. 코드 품질 도구

### 9.1 필수 설정

| 도구 | 프론트엔드 | 백엔드 |
|------|-----------|--------|
| 린터 | ESLint | Ruff |
| 포매터 | Prettier | Black |
| 타입 체크 | TypeScript (strict) | mypy |
| 테스트 | Vitest | pytest |

### 9.2 설정 파일

**ESLint (.eslintrc.cjs)**
```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'prettier'
  ],
  rules: {
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'react-hooks/exhaustive-deps': 'warn'
  }
};
```

**Ruff (pyproject.toml)**
```toml
[tool.ruff]
select = ["E", "F", "I", "N", "W"]
line-length = 88

[tool.ruff.isort]
known-first-party = ["app"]
```

### 9.3 Pre-commit 훅

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: frontend-lint
        name: Frontend Lint
        entry: npm run lint --prefix frontend
        language: system
        types: [typescript, tsx]

      - id: backend-lint
        name: Backend Lint
        entry: ruff check backend/
        language: system
        types: [python]

      - id: type-check
        name: Type Check
        entry: bash -c 'npm run type-check --prefix frontend && mypy backend/app/'
        language: system
```

---

## 10. 배포 체크리스트

### 10.1 배포 전 확인

- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 린트 통과
- [ ] 환경 변수 설정 확인
- [ ] 데이터베이스 마이그레이션 준비
- [ ] CORS 설정 확인
- [ ] WebSocket 엔드포인트 확인

### 10.2 배포 명령어

```bash
# 데이터베이스 마이그레이션
alembic upgrade head

# 백엔드 시작
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 프론트엔드 빌드
npm run build --prefix frontend
```

---

## Decision Log 참조

| ID | 항목 | 선택 | 근거 |
|----|------|------|------|
| D-04 | 기술 스택 | FastAPI + React + PostgreSQL | WebSocket 지원, 빠른 개발 |
| D-16 | 린터 | Ruff (BE) + ESLint (FE) | 빠른 속도, 일관성 |
| D-17 | 테스트 | pytest + Vitest | TDD 지원, 빠른 실행 |
| D-18 | 액션 검증 | 서버 필수 | 치팅 방지 |
