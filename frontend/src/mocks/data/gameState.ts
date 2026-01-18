/**
 * Mock game state data for testing and development.
 */
import type {
  GameState,
  GamePlayer,
  BoardCell,
  Resources,
  PlayerWorkers,
  WorkerState,
} from '../../../contracts/types';

// ============================================
// Helper functions
// ============================================

function createWorkerState(total: number, available: number): WorkerState {
  return {
    total,
    available,
    placed: total - available,
  };
}

function createResources(wood = 2, stone = 2, tile = 1, ink = 1): Resources {
  return { wood, stone, tile, ink };
}

function createPlayerWorkers(): PlayerWorkers {
  return {
    apprentices: createWorkerState(5, 5),
    officials: createWorkerState(4, 4),
  };
}

function createEmptyBoard(): BoardCell[][] {
  const board: BoardCell[][] = [];

  for (let row = 0; row < 5; row++) {
    const rowCells: BoardCell[] = [];
    for (let col = 0; col < 5; col++) {
      let terrain: 'normal' | 'mountain' | 'water' = 'normal';

      // Mountains in the north (row 0)
      if (row === 0 && col >= 1 && col <= 3) {
        terrain = 'mountain';
      }
      // Water in the south (row 4)
      if (row === 4 && col >= 1 && col <= 3) {
        terrain = 'water';
      }

      rowCells.push({
        position: { row, col },
        terrain,
        tile: null,
      });
    }
    board.push(rowCells);
  }

  return board;
}

// ============================================
// Mock Players
// ============================================

export const mockPlayers: GamePlayer[] = [
  {
    id: 1,
    userId: 1,
    username: '도편수',
    color: 'blue',
    turnOrder: 0,
    isHost: true,
    isReady: true,
    resources: createResources(3, 2, 2, 1),
    workers: createPlayerWorkers(),
    blueprints: ['bp-001', 'bp-002'],
    score: 0,
    placedTiles: [],
  },
  {
    id: 2,
    userId: 2,
    username: '정도전',
    color: 'red',
    turnOrder: 1,
    isHost: false,
    isReady: true,
    resources: createResources(2, 3, 1, 2),
    workers: createPlayerWorkers(),
    blueprints: ['bp-003'],
    score: 0,
    placedTiles: [],
  },
];

// ============================================
// Mock Game State
// ============================================

export const mockGameState: GameState = {
  id: 1,
  lobbyId: 1,
  status: 'in_progress',
  currentRound: 1,
  totalRounds: 8,
  currentTurnPlayerId: 1,
  turnOrder: [1, 2],
  board: createEmptyBoard(),
  players: mockPlayers,
  availableTiles: [
    'tile-palace-01',
    'tile-gov-01',
    'tile-temple-01',
    'tile-market-01',
    'tile-house-01',
  ],
  discardedTiles: [],
  lastAction: null,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

// ============================================
// Mock Building Tiles (Master Data)
// ============================================

export const mockBuildingTiles = [
  {
    id: 'tile-palace-01',
    name: 'Gyeongbokgung',
    nameKo: '경복궁',
    category: 'palace' as const,
    cost: { wood: 3, stone: 3, tile: 2, ink: 1 },
    points: 10,
    workerSlots: 3,
    fengshuiBonus: { baesanimsu: true, mountain: true, water: true, bonusPoints: 5 },
  },
  {
    id: 'tile-gov-01',
    name: 'Uijeongbu',
    nameKo: '의정부',
    category: 'government' as const,
    cost: { wood: 2, stone: 2, tile: 1 },
    points: 6,
    workerSlots: 2,
  },
  {
    id: 'tile-temple-01',
    name: 'Jogyesa',
    nameKo: '조계사',
    category: 'religious' as const,
    cost: { wood: 2, stone: 1, tile: 1, ink: 1 },
    points: 5,
    workerSlots: 1,
  },
  {
    id: 'tile-market-01',
    name: 'Namdaemun Market',
    nameKo: '남대문시장',
    category: 'commercial' as const,
    cost: { wood: 2, stone: 1 },
    points: 4,
    workerSlots: 2,
    adjacencyBonus: [{ adjacentCategory: 'residential', bonusPoints: 2 }],
  },
  {
    id: 'tile-house-01',
    name: 'Hanok',
    nameKo: '한옥',
    category: 'residential' as const,
    cost: { wood: 1, stone: 1 },
    points: 2,
    workerSlots: 1,
  },
  {
    id: 'tile-gate-01',
    name: 'Sungnyemun',
    nameKo: '숭례문 (남대문)',
    category: 'gate' as const,
    cost: { wood: 2, stone: 3, tile: 1 },
    points: 7,
    workerSlots: 0,
  },
];

// ============================================
// Mock Blueprint Cards
// ============================================

export const mockBlueprintCards = [
  {
    id: 'bp-001',
    name: 'Royal District',
    nameKo: '왕실 구역',
    description: '궁궐과 관청을 인접하게 배치',
    condition: {
      type: 'adjacency' as const,
      target: ['palace', 'government'],
    },
    points: 5,
  },
  {
    id: 'bp-002',
    name: 'Merchant Quarter',
    nameKo: '상업 지구',
    description: '시장 3개 건설',
    condition: {
      type: 'building_count' as const,
      target: 'commercial',
      count: 3,
    },
    points: 4,
  },
  {
    id: 'bp-003',
    name: 'Perfect Fengshui',
    nameKo: '완벽한 풍수',
    description: '배산임수 조건을 충족하는 건물 2개 이상',
    condition: {
      type: 'fengshui' as const,
      target: ['baesanimsu'],
      count: 2,
    },
    points: 6,
  },
];
