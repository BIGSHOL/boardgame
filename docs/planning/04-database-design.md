# Database Design (데이터베이스 설계)

> Hanyang: The Foundation - 데이터베이스 ERD 및 엔티티 정의

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

## 1. ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    %% FEAT-0: 사용자 관리
    USER {
        uuid id PK "고유 식별자"
        string email UK "로그인 이메일"
        string password_hash "암호화된 비밀번호"
        string nickname "표시 이름 (게임 내)"
        string avatar_url "아바타 이미지 URL"
        datetime created_at "가입일"
        datetime updated_at "수정일"
        datetime deleted_at "탈퇴일 (soft delete)"
    }

    %% FEAT-0: 인증 토큰
    AUTH_TOKEN {
        uuid id PK
        uuid user_id FK
        string refresh_token UK
        datetime expires_at
        string device_info "디바이스 정보"
        datetime created_at
    }

    %% 게임 로비
    LOBBY {
        uuid id PK
        uuid host_id FK "방장"
        string name "로비 이름"
        string invite_code UK "초대 코드 (6자리)"
        int max_players "최대 인원 (2-4)"
        string status "waiting/starting/in_game/finished"
        jsonb settings "게임 설정 옵션"
        datetime created_at
        datetime updated_at
    }

    %% 로비 참가자
    LOBBY_PLAYER {
        uuid id PK
        uuid lobby_id FK
        uuid user_id FK
        int seat_number "좌석 번호 (0-3)"
        boolean is_ready "준비 상태"
        datetime joined_at
    }

    %% FEAT-1/2/3: 게임 세션
    GAME {
        uuid id PK
        uuid lobby_id FK UK "원본 로비"
        int current_round "현재 라운드"
        int current_turn "현재 턴 (플레이어 인덱스)"
        string phase "setup/action/scoring/end"
        jsonb board_state "메인 보드 상태 (JSONB)"
        datetime started_at
        datetime ended_at
        datetime updated_at
    }

    %% FEAT-2: 게임 내 플레이어 상태
    GAME_PLAYER {
        uuid id PK
        uuid game_id FK
        uuid user_id FK
        int player_index "플레이어 순서 (0-3)"
        string color "플레이어 색상"
        jsonb resources "자원 상태 {wood, stone, tile, ink}"
        jsonb workers "워커 상태 {apprentices, officials}"
        jsonb personal_board "개인 보드 상태"
        jsonb hand_cards "보유 카드"
        int score "현재 점수"
        datetime updated_at
    }

    %% FEAT-1: 게임 액션 로그
    GAME_ACTION {
        uuid id PK
        uuid game_id FK
        uuid player_id FK
        int round_number "라운드 번호"
        int action_number "액션 순서"
        string action_type "draft/gather/build/register"
        jsonb action_data "액션 상세 데이터"
        jsonb result_data "액션 결과"
        datetime created_at
    }

    %% FEAT-3: 건물 타일 정의 (마스터 데이터)
    BUILDING_TILE {
        uuid id PK
        string name "건물 이름"
        string name_ko "한글 이름"
        string category "palace/gate/market/residence/temple"
        jsonb cost "건설 비용 {wood, stone, tile}"
        int base_points "기본 점수"
        jsonb effects "건물 효과"
        jsonb fengshui_bonus "풍수 보너스 조건"
        string image_url "타일 이미지"
    }

    %% 청사진 카드 정의 (마스터 데이터)
    BLUEPRINT_CARD {
        uuid id PK
        string name "카드 이름"
        string name_ko "한글 이름"
        uuid building_tile_id FK "연결된 건물 (상단 모드)"
        jsonb top_mode "상단: 건설 모드 효과"
        jsonb bottom_mode "하단: 지원 모드 효과"
        string image_url "카드 이미지"
    }

    %% 게임 피드백
    GAME_FEEDBACK {
        uuid id PK
        uuid game_id FK
        uuid user_id FK
        int rating "평점 (1-5)"
        text comment "피드백 내용"
        jsonb tags "태그 {balance, ui, rules}"
        datetime created_at
    }

    %% 관계 정의
    USER ||--o{ AUTH_TOKEN : "has"
    USER ||--o{ LOBBY : "hosts"
    USER ||--o{ LOBBY_PLAYER : "joins"
    USER ||--o{ GAME_PLAYER : "plays"
    USER ||--o{ GAME_FEEDBACK : "writes"

    LOBBY ||--o{ LOBBY_PLAYER : "has"
    LOBBY ||--o| GAME : "starts"

    GAME ||--o{ GAME_PLAYER : "has"
    GAME ||--o{ GAME_ACTION : "logs"
    GAME ||--o{ GAME_FEEDBACK : "receives"

    GAME_PLAYER ||--o{ GAME_ACTION : "performs"

    BUILDING_TILE ||--o{ BLUEPRINT_CARD : "linked_to"
```

---

## 2. 엔티티 상세 정의

### 2.1 USER (사용자) - FEAT-0

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 고유 식별자 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 로그인 이메일 |
| password_hash | VARCHAR(255) | NULL 허용 | bcrypt 해시 (소셜 로그인 시 NULL) |
| nickname | VARCHAR(30) | NOT NULL | 게임 내 표시 이름 |
| avatar_url | VARCHAR(500) | NULL | 아바타 이미지 URL |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 가입일 |
| updated_at | TIMESTAMPTZ | NOT NULL | 최종 수정일 |
| deleted_at | TIMESTAMPTZ | NULL | Soft delete용 |

**인덱스:**
- `idx_user_email` ON email
- `idx_user_nickname` ON nickname

**최소 수집 원칙:**
- 필수: email, nickname
- 선택: avatar_url
- 수집 안 함: 전화번호, 주소, 생년월일

---

### 2.2 LOBBY (게임 로비) - FEAT-0

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 고유 식별자 |
| host_id | UUID | FK → USER.id, NOT NULL | 방장 |
| name | VARCHAR(50) | NOT NULL | 로비 이름 |
| invite_code | VARCHAR(6) | UNIQUE, NOT NULL | 초대 코드 |
| max_players | SMALLINT | NOT NULL, DEFAULT 4, CHECK (2-4) | 최대 인원 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'waiting' | 상태 |
| settings | JSONB | NOT NULL, DEFAULT '{}' | 게임 설정 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 생성일 |
| updated_at | TIMESTAMPTZ | NOT NULL | 수정일 |

**settings JSONB 구조:**
```json
{
  "enableFengshui": true,
  "enableAdjacentBonus": true,
  "roundLimit": 8,
  "turnTimeLimit": 120
}
```

**인덱스:**
- `idx_lobby_invite_code` ON invite_code
- `idx_lobby_host` ON host_id
- `idx_lobby_status` ON status

---

### 2.3 GAME (게임 세션) - FEAT-1/2/3

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 고유 식별자 |
| lobby_id | UUID | FK → LOBBY.id, UNIQUE | 원본 로비 |
| current_round | SMALLINT | NOT NULL, DEFAULT 1 | 현재 라운드 |
| current_turn | SMALLINT | NOT NULL, DEFAULT 0 | 현재 턴 플레이어 |
| phase | VARCHAR(20) | NOT NULL, DEFAULT 'setup' | 게임 페이즈 |
| board_state | JSONB | NOT NULL | 메인 보드 상태 |
| started_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 시작 시간 |
| ended_at | TIMESTAMPTZ | NULL | 종료 시간 |
| updated_at | TIMESTAMPTZ | NOT NULL | 최종 업데이트 |

**board_state JSONB 구조:**
```json
{
  "grid": [
    [null, null, null, null, null],
    [null, {"tile": "uuid", "owner": 0}, null, null, null],
    [null, null, null, null, null],
    [null, null, null, {"tile": "uuid", "owner": 1}, null],
    [null, null, null, null, null]
  ],
  "terrain": {
    "mountain": [[0,0], [0,1], [0,2]],
    "water": [[4,0], [4,1], [4,2]]
  },
  "cardMarket": ["card_uuid_1", "card_uuid_2", "card_uuid_3"],
  "gates": {
    "north": null,
    "south": null,
    "east": null,
    "west": null
  }
}
```

**인덱스:**
- `idx_game_lobby` ON lobby_id
- `idx_game_status` ON phase

---

### 2.4 GAME_PLAYER (게임 내 플레이어) - FEAT-2

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 고유 식별자 |
| game_id | UUID | FK → GAME.id, NOT NULL | 게임 |
| user_id | UUID | FK → USER.id, NOT NULL | 사용자 |
| player_index | SMALLINT | NOT NULL, CHECK (0-3) | 플레이어 순서 |
| color | VARCHAR(20) | NOT NULL | 색상 (navy, gray, yellow, green) |
| resources | JSONB | NOT NULL | 자원 상태 |
| workers | JSONB | NOT NULL | 워커 상태 |
| personal_board | JSONB | NOT NULL | 개인 보드 |
| hand_cards | JSONB | NOT NULL, DEFAULT '[]' | 보유 카드 |
| score | INT | NOT NULL, DEFAULT 0 | 현재 점수 |
| updated_at | TIMESTAMPTZ | NOT NULL | 업데이트 시간 |

**resources JSONB 구조:**
```json
{
  "wood": 2,
  "stone": 3,
  "tile": 1,
  "ink": 2
}
```

**workers JSONB 구조:**
```json
{
  "apprentices": {
    "total": 5,
    "available": 3,
    "deployed": [
      {"location": "quarry", "returnRound": 3}
    ]
  },
  "officials": {
    "total": 4,
    "available": 2,
    "onBoard": [
      {"position": [2, 3], "buildingId": "uuid"}
    ]
  }
}
```

**personal_board JSONB 구조:**
```json
{
  "registeredCards": [
    {"cardId": "uuid", "effect": "passive_stone"}
  ],
  "slots": {
    "quarry": {"unlocked": true, "worker": null},
    "logging": {"unlocked": true, "worker": "apprentice_1"},
    "kiln": {"unlocked": false, "worker": null}
  }
}
```

**인덱스:**
- `idx_game_player_game` ON game_id
- `idx_game_player_user` ON user_id
- UNIQUE(game_id, player_index)
- UNIQUE(game_id, user_id)

---

### 2.5 GAME_ACTION (게임 액션 로그) - FEAT-1/2/3

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 고유 식별자 |
| game_id | UUID | FK → GAME.id, NOT NULL | 게임 |
| player_id | UUID | FK → GAME_PLAYER.id, NOT NULL | 플레이어 |
| round_number | SMALLINT | NOT NULL | 라운드 번호 |
| action_number | INT | NOT NULL | 액션 순서 |
| action_type | VARCHAR(20) | NOT NULL | 액션 타입 |
| action_data | JSONB | NOT NULL | 액션 입력 데이터 |
| result_data | JSONB | NOT NULL | 액션 결과 데이터 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 생성 시간 |

**action_type 값:**
- `draft`: 카드 드래프팅
- `gather`: 자원 획득
- `build`: 건설
- `register`: 카드 등록

**action_data 예시 (build):**
```json
{
  "actionType": "build",
  "tileId": "building_tile_uuid",
  "position": [2, 3],
  "cost": {"wood": 2, "stone": 1}
}
```

**result_data 예시:**
```json
{
  "success": true,
  "pointsGained": 5,
  "fengshuiBonus": 2,
  "adjacencyBonus": 1,
  "officialDeployed": true
}
```

**인덱스:**
- `idx_action_game` ON game_id
- `idx_action_game_round` ON (game_id, round_number)

---

### 2.6 BUILDING_TILE (건물 타일 마스터) - FEAT-1/3

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 고유 식별자 |
| name | VARCHAR(50) | NOT NULL, UNIQUE | 영문 이름 |
| name_ko | VARCHAR(50) | NOT NULL | 한글 이름 |
| category | VARCHAR(20) | NOT NULL | 건물 카테고리 |
| cost | JSONB | NOT NULL | 건설 비용 |
| base_points | SMALLINT | NOT NULL | 기본 점수 |
| effects | JSONB | NOT NULL, DEFAULT '{}' | 건물 효과 |
| fengshui_bonus | JSONB | NOT NULL, DEFAULT '{}' | 풍수 보너스 |
| image_url | VARCHAR(500) | NULL | 타일 이미지 |

**category 값:**
- `palace`: 궁궐
- `gate`: 성문 (사대문)
- `market`: 시장
- `residence`: 주거
- `temple`: 사찰
- `government`: 관청

**cost JSONB 구조:**
```json
{
  "wood": 2,
  "stone": 3,
  "tile": 1
}
```

**fengshui_bonus JSONB 구조:**
```json
{
  "backToMountain": true,
  "faceToWater": true,
  "bonusPoints": 3
}
```

---

### 2.7 GAME_FEEDBACK (게임 피드백) - 테스트 목적

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 고유 식별자 |
| game_id | UUID | FK → GAME.id, NOT NULL | 게임 |
| user_id | UUID | FK → USER.id, NOT NULL | 작성자 |
| rating | SMALLINT | CHECK (1-5) | 평점 |
| comment | TEXT | NULL | 피드백 내용 |
| tags | JSONB | DEFAULT '[]' | 피드백 태그 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 작성일 |

**tags 예시:**
```json
["balance_issue", "ui_confusion", "rule_unclear", "enjoyable"]
```

---

## 3. 관계 정의

| 부모 | 자식 | 관계 | 설명 | ON DELETE |
|------|------|------|------|-----------|
| USER | AUTH_TOKEN | 1:N | 사용자는 여러 토큰 보유 | CASCADE |
| USER | LOBBY | 1:N | 사용자는 여러 로비 생성 | SET NULL |
| USER | LOBBY_PLAYER | 1:N | 사용자는 여러 로비 참가 | CASCADE |
| USER | GAME_PLAYER | 1:N | 사용자는 여러 게임 참여 | CASCADE |
| LOBBY | LOBBY_PLAYER | 1:N | 로비는 여러 참가자 | CASCADE |
| LOBBY | GAME | 1:1 | 로비는 하나의 게임 시작 | CASCADE |
| GAME | GAME_PLAYER | 1:N | 게임은 2-4명의 플레이어 | CASCADE |
| GAME | GAME_ACTION | 1:N | 게임은 여러 액션 로그 | CASCADE |
| GAME_PLAYER | GAME_ACTION | 1:N | 플레이어는 여러 액션 | CASCADE |
| BUILDING_TILE | BLUEPRINT_CARD | 1:N | 타일은 여러 카드와 연결 | SET NULL |

---

## 4. 데이터 생명주기

| 엔티티 | 생성 시점 | 보존 기간 | 삭제 방식 |
|--------|----------|----------|-----------|
| USER | 회원가입 | 탈퇴 후 30일 | Soft delete → Hard delete |
| AUTH_TOKEN | 로그인 | 만료 시 | Hard delete |
| LOBBY | 로비 생성 | 게임 시작 후 24시간 | Hard delete |
| GAME | 게임 시작 | 30일 (또는 요청 시 영구) | Hard delete |
| GAME_PLAYER | 게임과 함께 | 게임과 동일 | Cascade |
| GAME_ACTION | 액션 발생 | 게임과 동일 | Cascade |
| GAME_FEEDBACK | 피드백 작성 | 영구 보관 | - |

---

## 5. 마스터 데이터 초기화

### 5.1 건물 타일 시드 데이터

```sql
-- 궁궐
INSERT INTO building_tile (id, name, name_ko, category, cost, base_points, effects, fengshui_bonus) VALUES
(gen_random_uuid(), 'gyeongbok_palace', '경복궁', 'palace', '{"wood": 5, "stone": 5, "tile": 3}', 15, '{"onBuild": "draw_2_cards"}', '{"backToMountain": true, "bonusPoints": 5}');

-- 성문 (사대문)
INSERT INTO building_tile (id, name, name_ko, category, cost, base_points, effects, fengshui_bonus) VALUES
(gen_random_uuid(), 'heunginjimun', '흥인지문', 'gate', '{"wood": 3, "stone": 4, "tile": 2}', 8, '{"onBuild": "all_gain_resource"}', '{}'),
(gen_random_uuid(), 'donuimun', '돈의문', 'gate', '{"wood": 3, "stone": 4, "tile": 2}', 8, '{"onBuild": "all_gain_resource"}', '{}'),
(gen_random_uuid(), 'sungnyemun', '숭례문', 'gate', '{"wood": 3, "stone": 4, "tile": 2}', 8, '{"onBuild": "all_gain_resource"}', '{}'),
(gen_random_uuid(), 'sukjeongmun', '숙정문', 'gate', '{"wood": 3, "stone": 4, "tile": 2}', 8, '{"onBuild": "all_gain_resource"}', '{}');

-- 시장
INSERT INTO building_tile (id, name, name_ko, category, cost, base_points, effects, fengshui_bonus) VALUES
(gen_random_uuid(), 'market_small', '작은 시장', 'market', '{"wood": 2, "stone": 1}', 3, '{"adjacency": {"residence": 2}}', '{}'),
(gen_random_uuid(), 'market_large', '큰 시장', 'market', '{"wood": 3, "stone": 2, "tile": 1}', 5, '{"adjacency": {"residence": 3}}', '{}');

-- 주거
INSERT INTO building_tile (id, name, name_ko, category, cost, base_points, effects, fengshui_bonus) VALUES
(gen_random_uuid(), 'hanok_small', '작은 한옥', 'residence', '{"wood": 2}', 2, '{}', '{"faceToWater": true, "bonusPoints": 1}'),
(gen_random_uuid(), 'hanok_large', '큰 한옥', 'residence', '{"wood": 3, "tile": 1}', 4, '{}', '{"backToMountain": true, "faceToWater": true, "bonusPoints": 3}');

-- 사찰
INSERT INTO building_tile (id, name, name_ko, category, cost, base_points, effects, fengshui_bonus) VALUES
(gen_random_uuid(), 'temple', '사찰', 'temple', '{"wood": 2, "stone": 2}', 4, '{"adjacency": {"government": 2}}', '{"backToMountain": true, "bonusPoints": 2}');

-- 관청
INSERT INTO building_tile (id, name, name_ko, category, cost, base_points, effects, fengshui_bonus) VALUES
(gen_random_uuid(), 'government_office', '관청', 'government', '{"wood": 2, "stone": 3}', 5, '{"onBuild": "gain_official"}', '{}');
```

---

## 6. 인덱스 전략

### 6.1 읽기 최적화

| 테이블 | 인덱스 | 용도 |
|--------|--------|------|
| USER | email | 로그인 조회 |
| LOBBY | invite_code | 초대 코드 조회 |
| LOBBY | status | 활성 로비 목록 |
| GAME | phase | 진행 중 게임 조회 |
| GAME_ACTION | (game_id, round_number) | 라운드별 액션 조회 |

### 6.2 성능 고려

- JSONB 필드에 GIN 인덱스 고려 (v2)
- 게임 상태 조회 빈도가 높으므로 Redis 캐싱 병행

---

## Decision Log 참조

| ID | 항목 | 선택 | 근거 |
|----|------|------|------|
| D-10 | 게임 상태 저장 | JSONB | 복잡한 보드 상태를 유연하게 저장 |
| D-11 | 액션 로그 | 별도 테이블 | 리플레이, 디버깅, 밸런스 분석용 |
| D-12 | 마스터 데이터 | DB 저장 | 게임 룰 수정 시 DB만 업데이트 |
