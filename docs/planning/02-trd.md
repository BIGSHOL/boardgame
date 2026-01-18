# TRD (기술 요구사항 정의서)

> Hanyang: The Foundation - 기술 문서

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

## 1. 시스템 아키텍처

### 1.1 고수준 아키텍처

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Client        │────▶│   Server        │────▶│   Database      │
│   (React+Vite)  │◀────│   (FastAPI)     │◀────│   (PostgreSQL)  │
│                 │     │                 │     │                 │
│   - Game UI     │     │   - REST API    │     │   - Users       │
│   - WebSocket   │◀───▶│   - WebSocket   │     │   - Games       │
│   - State Mgmt  │     │   - Game Logic  │     │   - Game States │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │
         │                      │
         ▼                      ▼
┌─────────────────┐     ┌─────────────────┐
│   Canvas/SVG    │     │   Redis         │
│   (Board Render)│     │   (WebSocket)   │
│                 │     │   (Session)     │
└─────────────────┘     └─────────────────┘
```

### 1.2 컴포넌트 설명

| 컴포넌트 | 역할 | 왜 이 선택? |
|----------|------|-------------|
| Frontend (React+Vite) | 게임 UI, 보드 렌더링, 실시간 상태 관리 | Canvas/SVG 라이브러리 풍부, 컴포넌트 기반 재사용성 |
| Backend (FastAPI) | REST API, WebSocket, 게임 로직 처리 | WebSocket 네이티브 지원, 빠른 개발, 자동 API 문서 |
| Database (PostgreSQL) | 사용자, 게임, 게임 상태 저장 | JSON 필드로 복잡한 게임 상태 유연하게 저장 |
| Redis | WebSocket 세션 관리, 게임 방 상태 캐싱 | 실시간 통신에 필요한 pub/sub 지원 |

---

## 2. 권장 기술 스택

### 2.1 프론트엔드

| 항목 | 선택 | 이유 | 벤더 락인 리스크 |
|------|------|------|-----------------|
| 프레임워크 | React 19 + Vite | 빠른 HMR, 보드게임 UI 컴포넌트화 용이 | 낮음 |
| 언어 | TypeScript 5.x | 타입 안전성, 게임 상태 모델링 | - |
| 스타일링 | TailwindCSS 3.x | 빠른 UI 개발, 반응형 지원 | 낮음 |
| 상태관리 | Zustand | 가벼움, 게임 상태 관리에 적합 | 낮음 |
| HTTP 클라이언트 | ky | 가벼움, fetch 기반 | 낮음 |
| WebSocket | native WebSocket + reconnecting-websocket | 재연결 로직 내장 | 낮음 |
| 보드 렌더링 | React-Konva (Canvas) | 성능, 복잡한 보드게임 UI 지원 | 낮음 |

### 2.2 백엔드

| 항목 | 선택 | 이유 | 벤더 락인 리스크 |
|------|------|------|-----------------|
| 프레임워크 | FastAPI 0.110+ | WebSocket 지원, 자동 API 문서, 비동기 | 낮음 |
| 언어 | Python 3.12+ | 빠른 개발, 게임 로직 구현 용이 | - |
| ORM | SQLAlchemy 2.0 | 비동기 지원, PostgreSQL 호환 | 낮음 |
| 검증 | Pydantic v2 | FastAPI 통합, 게임 상태 검증 | 낮음 |
| 마이그레이션 | Alembic | SQLAlchemy 연동 | 낮음 |
| WebSocket | Starlette WebSocket | FastAPI 내장 | 낮음 |

### 2.3 데이터베이스

| 항목 | 선택 | 이유 |
|------|------|------|
| 메인 DB | PostgreSQL 16 | JSONB로 게임 상태 저장, 안정성 |
| 캐시/Pub-Sub | Redis 7 | WebSocket 메시지 브로커, 게임 방 상태 캐싱 |

### 2.4 인프라

| 항목 | 선택 | 이유 |
|------|------|------|
| 컨테이너 | Docker + Docker Compose | 로컬 개발 일관성, PostgreSQL/Redis 쉬운 실행 |
| 호스팅 (FE) | Vercel | 무료 티어, 빠른 배포 |
| 호스팅 (BE) | Railway / Render | WebSocket 지원, PostgreSQL 제공 |

---

## 3. 비기능 요구사항

### 3.1 성능

| 항목 | 요구사항 | 측정 방법 |
|------|----------|----------|
| API 응답 시간 | < 200ms (P95) | FastAPI 미들웨어 로깅 |
| WebSocket 지연 | < 100ms | 클라이언트 측 측정 |
| 초기 로딩 | < 3s (FCP) | Lighthouse |
| 보드 렌더링 | 60fps | Canvas 성능 프로파일링 |

### 3.2 보안

| 항목 | 요구사항 |
|------|----------|
| 인증 | JWT + Refresh Token (httpOnly cookie) |
| 비밀번호 | bcrypt 해싱 (cost factor 12) |
| HTTPS | 필수 (프로덕션) |
| 입력 검증 | Pydantic으로 서버 측 검증 |
| WebSocket | 인증된 사용자만 게임 방 접속 |

### 3.3 확장성

| 항목 | 현재 (MVP) | 목표 (v2) |
|------|------------|-----------|
| 동시 게임 세션 | 10개 | 100개 |
| 동시 사용자 | 50명 | 500명 |
| 게임 데이터 용량 | 100MB | 1GB |

---

## 4. 외부 API 연동

### 4.1 인증

| 서비스 | 용도 | 필수/선택 | 연동 방식 |
|--------|------|----------|----------|
| 이메일/비밀번호 | 기본 로그인 | 필수 | JWT |
| Google OAuth | 소셜 로그인 | 선택 (v2) | OAuth 2.0 |

### 4.2 기타 서비스

| 서비스 | 용도 | 필수/선택 | 비고 |
|--------|------|----------|------|
| 없음 | MVP에서는 외부 API 최소화 | - | 단순함 유지 |

---

## 5. 접근제어/권한 모델

### 5.1 역할 정의

| 역할 | 설명 | 권한 |
|------|------|------|
| Guest | 비로그인 | 게임 관전만 가능 |
| User | 일반 사용자 | 게임 생성/참여, 본인 프로필 관리 |
| Host | 게임 방장 | 게임 설정, 플레이어 초대/추방 |
| Admin | 관리자 | 전체 접근, 사용자 관리 |

### 5.2 권한 매트릭스

| 리소스 | Guest | User | Host | Admin |
|--------|-------|------|------|-------|
| 게임 관전 | O | O | O | O |
| 게임 참여 | - | O | O | O |
| 게임 생성 | - | O | O | O |
| 게임 설정 변경 | - | - | O | O |
| 플레이어 초대/추방 | - | - | O | O |
| 사용자 관리 | - | - | - | O |

---

## 6. 데이터 생명주기

### 6.1 원칙

- **최소 수집**: 게임 플레이에 필요한 데이터만 수집
- **세션 기반**: 게임 상태는 세션 종료 시 정리 (저장 옵션 제공)
- **보존 기한**: 완료된 게임은 30일 후 자동 삭제

### 6.2 데이터 흐름

```
게임 시작 → 실시간 상태 (Redis) → 게임 종료 → DB 저장 (선택) → 30일 후 삭제
```

| 데이터 유형 | 보존 기간 | 삭제/익명화 |
|------------|----------|------------|
| 계정 정보 | 탈퇴 후 30일 | 완전 삭제 |
| 진행 중 게임 | 24시간 (미완료 시 삭제) | 자동 삭제 |
| 완료된 게임 | 30일 | 완전 삭제 (또는 요청 시 영구 보관) |

---

## 7. 테스트 전략 (Contract-First TDD)

### 7.1 개발 방식: Contract-First Development

본 프로젝트는 **계약 우선 개발(Contract-First Development)** 방식을 채택합니다.
BE/FE가 독립적으로 병렬 개발하면서도 통합 시 호환성을 보장합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    Contract-First 흐름                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 계약 정의 (Phase 0)                                     │
│     ├─ API 계약: contracts/*.contract.ts                   │
│     ├─ WebSocket 메시지: contracts/ws-messages.ts          │
│     ├─ BE 스키마: backend/app/schemas/*.py                 │
│     └─ 타입 동기화: TypeScript ↔ Pydantic                  │
│                                                             │
│  2. 테스트 선행 작성 (RED)                                   │
│     ├─ BE 테스트: tests/api/*.py, tests/ws/*.py            │
│     ├─ FE 테스트: src/__tests__/**/*.test.ts               │
│     └─ 모든 테스트가 실패하는 상태 (정상!)                  │
│                                                             │
│  3. Mock 생성 (FE 독립 개발용)                              │
│     └─ MSW 핸들러: src/mocks/handlers/*.ts                 │
│                                                             │
│  4. 병렬 구현 (RED → GREEN)                                 │
│     ├─ BE: 테스트 통과 목표로 구현                          │
│     └─ FE: Mock API로 개발 → 나중에 실제 API 연결          │
│                                                             │
│  5. 통합 검증                                               │
│     └─ Mock 제거 → E2E 테스트                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 테스트 피라미드

| 레벨 | 도구 | 커버리지 목표 | 위치 |
|------|------|-------------|------|
| Unit | pytest / Vitest | >= 80% | tests/unit/, src/__tests__/ |
| Integration | pytest / Vitest + MSW | Critical paths | tests/integration/ |
| E2E | Playwright | Key user flows | e2e/ |

### 7.3 테스트 도구

**백엔드:**
| 도구 | 용도 |
|------|------|
| pytest | 테스트 실행 |
| pytest-asyncio | 비동기 테스트 |
| httpx | API 클라이언트 |
| Factory Boy | 테스트 데이터 생성 |
| pytest-cov | 커버리지 측정 |

**프론트엔드:**
| 도구 | 용도 |
|------|------|
| Vitest | 테스트 실행 |
| React Testing Library | 컴포넌트 테스트 |
| MSW (Mock Service Worker) | API 모킹 |
| Playwright | E2E 테스트 |

### 7.4 계약 파일 구조

```
project/
├── contracts/                    # API 계약 (BE/FE 공유)
│   ├── types.ts                 # 공통 타입 정의
│   ├── auth.contract.ts         # 인증 API 계약
│   ├── game.contract.ts         # 게임 API 계약
│   ├── lobby.contract.ts        # 로비 API 계약
│   └── ws-messages.ts           # WebSocket 메시지 타입
│
├── backend/
│   ├── app/schemas/             # Pydantic 스키마 (계약과 동기화)
│   │   ├── auth.py
│   │   ├── game.py
│   │   └── lobby.py
│   └── tests/
│       ├── api/                 # REST API 테스트
│       │   ├── test_auth.py
│       │   ├── test_game.py
│       │   └── test_lobby.py
│       └── ws/                  # WebSocket 테스트
│           └── test_game_ws.py
│
└── frontend/
    ├── src/
    │   ├── mocks/
    │   │   ├── handlers/        # MSW Mock 핸들러
    │   │   │   ├── auth.ts
    │   │   │   ├── game.ts
    │   │   │   └── lobby.ts
    │   │   └── data/            # Mock 데이터
    │   │       └── gameState.ts
    │   └── __tests__/
    │       └── api/             # API 테스트 (계약 기반)
    └── e2e/                     # E2E 테스트
```

### 7.5 TDD 사이클

모든 기능 개발은 다음 사이클을 따릅니다:

```
RED    → 실패하는 테스트 먼저 작성
GREEN  → 테스트를 통과하는 최소한의 코드 구현
REFACTOR → 테스트 통과 유지하며 코드 개선
```

### 7.6 품질 게이트

**병합 전 필수 통과:**
- [ ] 모든 단위 테스트 통과
- [ ] 커버리지 >= 80%
- [ ] 린트 통과 (ruff / ESLint)
- [ ] 타입 체크 통과 (mypy / tsc)
- [ ] E2E 테스트 통과 (해당 기능)

**검증 명령어:**
```bash
# 백엔드
pytest --cov=app --cov-report=term-missing
ruff check .
mypy app/

# 프론트엔드
npm run test -- --coverage
npm run lint
npm run type-check

# E2E
npx playwright test
```

---

## 8. API 설계 원칙

### 8.1 RESTful 규칙

| 메서드 | 용도 | 예시 |
|--------|------|------|
| GET | 조회 | GET /api/v1/games/{id} |
| POST | 생성 | POST /api/v1/games |
| PUT | 전체 수정 | PUT /api/v1/games/{id} |
| PATCH | 부분 수정 | PATCH /api/v1/games/{id} |
| DELETE | 삭제 | DELETE /api/v1/games/{id} |

### 8.2 게임 특화 API

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| /api/v1/lobbies | POST | 게임 로비 생성 |
| /api/v1/lobbies/{id}/join | POST | 로비 참가 |
| /api/v1/lobbies/{id}/start | POST | 게임 시작 |
| /api/v1/games/{id}/action | POST | 게임 액션 수행 |
| /ws/games/{id} | WebSocket | 실시간 게임 통신 |

### 8.3 응답 형식

**성공 응답:**
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

**에러 응답:**
```json
{
  "error": {
    "code": "INVALID_ACTION",
    "message": "자원이 부족합니다.",
    "details": {
      "required": { "wood": 3 },
      "available": { "wood": 1 }
    }
  }
}
```

### 8.4 WebSocket 메시지 형식

```typescript
// 클라이언트 → 서버
interface ClientMessage {
  type: 'GAME_ACTION' | 'CHAT' | 'PING';
  payload: {
    action?: GameAction;
    message?: string;
  };
}

// 서버 → 클라이언트
interface ServerMessage {
  type: 'GAME_STATE' | 'PLAYER_JOINED' | 'PLAYER_LEFT' | 'CHAT' | 'ERROR';
  payload: {
    gameState?: GameState;
    player?: Player;
    message?: string;
    error?: ErrorDetail;
  };
}
```

### 8.5 API 버저닝

| 방식 | 예시 | 채택 여부 |
|------|------|----------|
| URL 경로 | /api/v1/games | 채택 |

---

## 9. 병렬 개발 지원 (Git Worktree)

### 9.1 개요

BE/FE를 완전히 독립된 환경에서 병렬 개발할 때 Git Worktree를 사용합니다.

### 9.2 Worktree 구조

```
~/projects/
├── hanyang/                   # 메인 (main 브랜치)
├── hanyang-auth-be/           # Worktree: feature/auth-be
├── hanyang-auth-fe/           # Worktree: feature/auth-fe
├── hanyang-game-be/           # Worktree: feature/game-be
├── hanyang-game-fe/           # Worktree: feature/game-fe
└── hanyang-board-fe/          # Worktree: feature/board-fe
```

### 9.3 명령어

```bash
# Worktree 생성
git worktree add ../hanyang-game-be -b feature/game-be
git worktree add ../hanyang-game-fe -b feature/game-fe

# 각 Worktree에서 독립 작업
cd ../hanyang-game-be && pytest tests/api/test_game.py
cd ../hanyang-game-fe && npm run test -- src/__tests__/game/

# 테스트 통과 후 병합
git checkout main
git merge --no-ff feature/game-be
git merge --no-ff feature/game-fe

# Worktree 정리
git worktree remove ../hanyang-game-be
git worktree remove ../hanyang-game-fe
```

### 9.4 병합 규칙

| 조건 | 병합 가능 |
|------|----------|
| 단위 테스트 통과 (GREEN) | 필수 |
| 커버리지 >= 80% | 필수 |
| 린트/타입 체크 통과 | 필수 |
| E2E 테스트 통과 | 권장 |

---

## Decision Log 참조

| ID | 항목 | 선택 | 근거 |
|----|------|------|------|
| D-04 | 백엔드 | FastAPI | WebSocket 네이티브 지원, 빠른 개발 |
| D-04 | 프론트엔드 | React + Vite | Canvas 라이브러리 풍부, 컴포넌트 기반 |
| D-04 | 데이터베이스 | PostgreSQL | JSONB로 게임 상태 유연 저장 |
| D-06 | 보드 렌더링 | React-Konva | Canvas 기반, 60fps 성능 |
| D-07 | 실시간 통신 | WebSocket + Redis | 저지연, pub/sub 지원 |
