/**
 * MSW handlers for lobby API.
 */
import { http, HttpResponse, delay } from 'msw';
import type { Lobby, Player } from '../../../contracts/types';

// Mock lobby database
const lobbies: Map<number, Lobby> = new Map();
let nextLobbyId = 1;

function generateInviteCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars[Math.floor(Math.random() * chars.length)];
  }
  return code;
}

export const lobbyHandlers = [
  // POST /api/v1/lobbies - Create lobby
  http.post('/api/v1/lobbies', async ({ request }) => {
    await delay(100);

    const authHeader = request.headers.get('Authorization');
    if (!authHeader) {
      return HttpResponse.json({ detail: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json() as { name: string; max_players?: number };
    const { name, max_players = 4 } = body;

    const lobby: Lobby = {
      id: nextLobbyId++,
      name,
      hostId: 1, // Mock host
      inviteCode: generateInviteCode(),
      status: 'waiting',
      maxPlayers: max_players,
      players: [
        {
          id: 1,
          userId: 1,
          username: 'Host Player',
          color: 'blue',
          turnOrder: 0,
          isHost: true,
          isReady: false,
        },
      ],
      createdAt: new Date().toISOString(),
    };

    lobbies.set(lobby.id, lobby);

    return HttpResponse.json(lobby, { status: 201 });
  }),

  // GET /api/v1/lobbies - List lobbies
  http.get('/api/v1/lobbies', async () => {
    await delay(50);

    return HttpResponse.json({
      lobbies: Array.from(lobbies.values()),
      total: lobbies.size,
    });
  }),

  // GET /api/v1/lobbies/:id - Get lobby
  http.get('/api/v1/lobbies/:id', async ({ params }) => {
    await delay(50);

    const id = parseInt(params.id as string, 10);
    const lobby = lobbies.get(id);

    if (!lobby) {
      return HttpResponse.json({ detail: 'Lobby not found' }, { status: 404 });
    }

    return HttpResponse.json(lobby);
  }),

  // POST /api/v1/lobbies/:id/join - Join lobby
  http.post('/api/v1/lobbies/:id/join', async ({ params, request }) => {
    await delay(100);

    const id = parseInt(params.id as string, 10);
    const lobby = lobbies.get(id);

    if (!lobby) {
      return HttpResponse.json({ detail: 'Lobby not found' }, { status: 404 });
    }

    if (lobby.players.length >= lobby.maxPlayers) {
      return HttpResponse.json({ detail: 'Lobby is full' }, { status: 400 });
    }

    if (lobby.status !== 'waiting') {
      return HttpResponse.json({ detail: 'Game already started' }, { status: 400 });
    }

    const colors: Array<'blue' | 'red' | 'green' | 'yellow'> = ['blue', 'red', 'green', 'yellow'];
    const usedColors = lobby.players.map(p => p.color);
    const availableColor = colors.find(c => !usedColors.includes(c)) || 'blue';

    const newPlayer: Player = {
      id: lobby.players.length + 1,
      userId: lobby.players.length + 1,
      username: `Player ${lobby.players.length + 1}`,
      color: availableColor,
      turnOrder: lobby.players.length,
      isHost: false,
      isReady: false,
    };

    lobby.players.push(newPlayer);

    return HttpResponse.json({
      lobby,
      player: newPlayer,
    });
  }),

  // POST /api/v1/lobbies/:id/ready - Toggle ready
  http.post('/api/v1/lobbies/:id/ready', async ({ params, request }) => {
    await delay(50);

    const id = parseInt(params.id as string, 10);
    const lobby = lobbies.get(id);

    if (!lobby) {
      return HttpResponse.json({ detail: 'Lobby not found' }, { status: 404 });
    }

    const body = await request.json() as { is_ready: boolean };

    // Toggle first player's ready status for mock
    if (lobby.players.length > 0) {
      lobby.players[0].isReady = body.is_ready;
    }

    // Check if all players ready
    const allReady = lobby.players.every(p => p.isReady || p.isHost);
    if (allReady && lobby.players.length >= 2) {
      lobby.status = 'ready';
    } else {
      lobby.status = 'waiting';
    }

    return HttpResponse.json(lobby);
  }),

  // POST /api/v1/lobbies/:id/start - Start game
  http.post('/api/v1/lobbies/:id/start', async ({ params }) => {
    await delay(100);

    const id = parseInt(params.id as string, 10);
    const lobby = lobbies.get(id);

    if (!lobby) {
      return HttpResponse.json({ detail: 'Lobby not found' }, { status: 404 });
    }

    if (lobby.players.length < 2) {
      return HttpResponse.json({ detail: 'Not enough players' }, { status: 400 });
    }

    lobby.status = 'started';

    return HttpResponse.json({ game_id: 1 });
  }),

  // GET /api/v1/lobbies/join/:inviteCode - Get lobby by invite code
  http.get('/api/v1/lobbies/join/:inviteCode', async ({ params }) => {
    await delay(50);

    const inviteCode = params.inviteCode as string;

    for (const lobby of lobbies.values()) {
      if (lobby.inviteCode === inviteCode) {
        return HttpResponse.json(lobby);
      }
    }

    return HttpResponse.json({ detail: 'Invalid invite code' }, { status: 404 });
  }),
];
