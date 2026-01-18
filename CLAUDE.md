# Hanyang: The Foundation - 한양: 도읍의 설계자들

## 프로젝트 개요

조선 초기 한양 건설 전략 보드게임의 디지털 프로토타입입니다.

## 기술 스택

- **백엔드**: FastAPI + SQLAlchemy + PostgreSQL + Redis
- **프론트엔드**: React 19 + Vite + TypeScript + TailwindCSS
- **인증**: JWT (Access Token + Refresh Token)
- **실시간**: WebSocket

## 프로젝트 구조

```
hanyang/
├── .claude/
│   ├── agents/         # AI 에이전트 설정
│   └── commands/       # 오케스트레이터 명령
├── backend/
│   ├── app/
│   │   ├── api/routes/ # API 엔드포인트
│   │   ├── core/       # 설정, 보안, DB
│   │   ├── models/     # SQLAlchemy 모델
│   │   ├── schemas/    # Pydantic 스키마
│   │   ├── services/   # 비즈니스 로직
│   │   └── websocket/  # WebSocket 핸들러
│   ├── tests/          # pytest 테스트
│   └── alembic/        # DB 마이그레이션
├── frontend/
│   ├── src/
│   │   ├── api/        # API 클라이언트
│   │   ├── components/ # React 컴포넌트
│   │   ├── hooks/      # 커스텀 훅
│   │   ├── routes/     # 페이지 컴포넌트
│   │   ├── stores/     # Zustand 스토어
│   │   └── types/      # TypeScript 타입
│   └── e2e/            # Playwright E2E 테스트
├── contracts/          # API 계약 (BE/FE 공유)
└── docs/planning/      # 기획 문서
```

## 명령어

### 개발 환경 시작

```bash
# Docker 시작 (PostgreSQL + Redis)
docker compose up -d

# 백엔드
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 프론트엔드
cd frontend
npm install
npm run dev
```

### 테스트

```bash
# 백엔드 테스트
cd backend && pytest -v

# 프론트엔드 테스트
cd frontend && npm run test

# E2E 테스트
cd frontend && npx playwright test
```

### 마이그레이션

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## 게임 도메인 용어

| 한글 | 영문 | 코드명 |
|------|------|--------|
| 건물 타일 | Building Tile | BuildingTile |
| 청사진 카드 | Blueprint Card | BlueprintCard |
| 견습생 | Apprentice | WorkerType.APPRENTICE |
| 관리 | Official | WorkerType.OFFICIAL |
| 목재 | Wood | ResourceType.WOOD |
| 석재 | Stone | ResourceType.STONE |
| 기와 | Tile | ResourceType.TILE |
| 먹 | Ink | ResourceType.INK |
| 풍수지리 | Feng Shui | FengShui |
| 배산임수 | Baesanimsu | Baesanimsu |

## Lessons Learned

<!-- 개발 중 난관 극복 시 기록 -->
