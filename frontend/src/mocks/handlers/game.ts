/**
 * MSW handlers for game API.
 */
import { http, HttpResponse, delay } from 'msw';
import { mockGameState, mockBuildingTiles } from '../data/gameState';
import type { GameState, GameAction } from '../../../contracts/types';

// Clone the mock state so we can mutate it
let currentGameState: GameState = JSON.parse(JSON.stringify(mockGameState));
let actionId = 1;

export const gameHandlers = [
  // GET /api/v1/games/:id - Get game state
  http.get('/api/v1/games/:id', async ({ params }) => {
    await delay(50);

    const id = parseInt(params.id as string, 10);

    if (id !== currentGameState.id) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 });
    }

    return HttpResponse.json(currentGameState);
  }),

  // POST /api/v1/games/:id/action - Perform action
  http.post('/api/v1/games/:id/action', async ({ params, request }) => {
    await delay(100);

    const id = parseInt(params.id as string, 10);

    if (id !== currentGameState.id) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 });
    }

    const body = await request.json() as { action_type: string; payload: Record<string, unknown> };

    // Create action record
    const action: GameAction = {
      id: actionId++,
      gameId: id,
      playerId: currentGameState.currentTurnPlayerId,
      actionType: body.action_type as GameAction['actionType'],
      payload: body.payload as GameAction['payload'],
      timestamp: new Date().toISOString(),
    };

    // Simple action handling
    switch (body.action_type) {
      case 'end_turn': {
        // Switch to next player
        const currentIndex = currentGameState.turnOrder.indexOf(currentGameState.currentTurnPlayerId);
        const nextIndex = (currentIndex + 1) % currentGameState.turnOrder.length;
        currentGameState.currentTurnPlayerId = currentGameState.turnOrder[nextIndex];

        // Check for new round
        if (nextIndex === 0) {
          currentGameState.currentRound++;
        }
        break;
      }

      case 'place_worker': {
        const player = currentGameState.players.find(
          p => p.id === currentGameState.currentTurnPlayerId
        );
        if (player) {
          const payload = body.payload as { worker_type: string };
          if (payload.worker_type === 'apprentice') {
            player.workers.apprentices.available--;
            player.workers.apprentices.placed++;
          } else {
            player.workers.officials.available--;
            player.workers.officials.placed++;
          }
        }
        break;
      }

      case 'place_tile': {
        const player = currentGameState.players.find(
          p => p.id === currentGameState.currentTurnPlayerId
        );
        const payload = body.payload as { tile_id: string; position: { row: number; col: number } };

        if (player) {
          // Find tile cost
          const tile = mockBuildingTiles.find(t => t.id === payload.tile_id);
          if (tile) {
            // Deduct resources
            const cost = tile.cost;
            if (cost.wood) player.resources.wood -= cost.wood;
            if (cost.stone) player.resources.stone -= cost.stone;
            if (cost.tile) player.resources.tile -= cost.tile;
            if (cost.ink) player.resources.ink -= cost.ink;
          }

          // Place tile on board
          const cell = currentGameState.board[payload.position.row][payload.position.col];
          cell.tile = {
            tileId: payload.tile_id,
            ownerId: player.id,
            placedWorkers: [],
            fengshuiActive: false,
          };

          // Remove from available
          currentGameState.availableTiles = currentGameState.availableTiles.filter(
            t => t !== payload.tile_id
          );

          player.placedTiles.push(payload.tile_id);
        }
        break;
      }

      default:
        break;
    }

    currentGameState.lastAction = action;
    currentGameState.updatedAt = new Date().toISOString();

    return HttpResponse.json({
      action,
      new_state: currentGameState,
      bonus_awarded: null,
    });
  }),

  // GET /api/v1/games/:id/valid-actions - Get valid actions
  http.get('/api/v1/games/:id/valid-actions', async ({ params }) => {
    await delay(50);

    const id = parseInt(params.id as string, 10);

    if (id !== currentGameState.id) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 });
    }

    const player = currentGameState.players.find(
      p => p.id === currentGameState.currentTurnPlayerId
    );

    const validActions = [];

    // Can always end turn
    validActions.push({ action_type: 'end_turn', options: [] });

    // Can place workers if available
    if (player && player.workers.apprentices.available > 0) {
      validActions.push({
        action_type: 'place_worker',
        options: [{ worker_type: 'apprentice' }],
      });
    }

    if (player && player.workers.officials.available > 0) {
      validActions.push({
        action_type: 'place_worker',
        options: [{ worker_type: 'official' }],
      });
    }

    // Can place tiles if affordable
    validActions.push({
      action_type: 'place_tile',
      options: currentGameState.availableTiles.map(tileId => ({ tile_id: tileId })),
    });

    return HttpResponse.json({ valid_actions: validActions });
  }),

  // GET /api/v1/games/:id/result - Get game result
  http.get('/api/v1/games/:id/result', async ({ params }) => {
    await delay(50);

    const id = parseInt(params.id as string, 10);

    if (id !== currentGameState.id) {
      return HttpResponse.json({ detail: 'Game not found' }, { status: 404 });
    }

    if (currentGameState.status !== 'finished') {
      return HttpResponse.json({ detail: 'Game not finished' }, { status: 400 });
    }

    // Calculate mock results
    const rankings = currentGameState.players
      .map((p, index) => ({
        player_id: p.id,
        username: p.username,
        rank: index + 1,
        score_breakdown: {
          building_points: p.score,
          fengshui_bonus: 0,
          adjacency_bonus: 0,
          blueprint_bonus: 0,
          remaining_resources: 0,
          total: p.score,
        },
      }))
      .sort((a, b) => b.score_breakdown.total - a.score_breakdown.total);

    return HttpResponse.json({
      game_id: id,
      winner_id: rankings[0]?.player_id || 0,
      rankings,
      duration_minutes: 45,
      total_rounds: currentGameState.currentRound,
    });
  }),

  // POST /api/v1/games/:id/feedback - Submit feedback
  http.post('/api/v1/games/:id/feedback', async () => {
    await delay(100);

    return HttpResponse.json({ message: 'Feedback submitted' }, { status: 201 });
  }),

  // Reset game state (for testing)
  http.post('/api/v1/games/reset', async () => {
    currentGameState = JSON.parse(JSON.stringify(mockGameState));
    actionId = 1;
    return HttpResponse.json({ message: 'Game state reset' });
  }),
];
