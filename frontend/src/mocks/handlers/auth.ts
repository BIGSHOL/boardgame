/**
 * MSW handlers for authentication API.
 */
import { http, HttpResponse, delay } from 'msw';

// Mock user database
const users: Map<string, { id: number; email: string; username: string; password: string }> = new Map();
let nextUserId = 1;

// Mock tokens
function generateToken(userId: number, type: 'access' | 'refresh'): string {
  return `mock-${type}-token-${userId}-${Date.now()}`;
}

export const authHandlers = [
  // POST /api/v1/auth/register
  http.post('/api/v1/auth/register', async ({ request }) => {
    await delay(100);

    const body = await request.json() as { email: string; username: string; password: string };
    const { email, username, password } = body;

    // Check for existing email
    for (const user of users.values()) {
      if (user.email === email) {
        return HttpResponse.json(
          { detail: 'Email already registered' },
          { status: 400 }
        );
      }
      if (user.username === username) {
        return HttpResponse.json(
          { detail: 'Username already taken' },
          { status: 400 }
        );
      }
    }

    // Create new user
    const user = {
      id: nextUserId++,
      email,
      username,
      password,
    };
    users.set(email, user);

    return HttpResponse.json(
      {
        id: user.id,
        email: user.email,
        username: user.username,
        is_active: true,
        created_at: new Date().toISOString(),
      },
      { status: 201 }
    );
  }),

  // POST /api/v1/auth/login
  http.post('/api/v1/auth/login', async ({ request }) => {
    await delay(100);

    const body = await request.json() as { email: string; password: string };
    const { email, password } = body;

    const user = users.get(email);

    if (!user || user.password !== password) {
      return HttpResponse.json(
        { detail: 'Incorrect email or password' },
        { status: 401 }
      );
    }

    return HttpResponse.json({
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        is_active: true,
        created_at: new Date().toISOString(),
      },
      tokens: {
        access_token: generateToken(user.id, 'access'),
        refresh_token: generateToken(user.id, 'refresh'),
        token_type: 'bearer',
      },
    });
  }),

  // POST /api/v1/auth/refresh
  http.post('/api/v1/auth/refresh', async ({ request }) => {
    await delay(50);

    const body = await request.json() as { refresh_token: string };
    const { refresh_token } = body;

    // Simple token validation
    if (!refresh_token || !refresh_token.startsWith('mock-refresh-token-')) {
      return HttpResponse.json(
        { detail: 'Invalid refresh token' },
        { status: 401 }
      );
    }

    // Extract user ID from token
    const parts = refresh_token.split('-');
    const userId = parseInt(parts[3], 10);

    return HttpResponse.json({
      access_token: generateToken(userId, 'access'),
      refresh_token: generateToken(userId, 'refresh'),
      token_type: 'bearer',
    });
  }),

  // GET /api/v1/auth/me
  http.get('/api/v1/auth/me', async ({ request }) => {
    await delay(50);

    const authHeader = request.headers.get('Authorization');

    if (!authHeader || !authHeader.startsWith('Bearer mock-access-token-')) {
      return HttpResponse.json(
        { detail: 'Invalid or missing token' },
        { status: 401 }
      );
    }

    // Extract user ID from token
    const token = authHeader.replace('Bearer ', '');
    const parts = token.split('-');
    const userId = parseInt(parts[3], 10);

    // Find user
    for (const user of users.values()) {
      if (user.id === userId) {
        return HttpResponse.json({
          id: user.id,
          email: user.email,
          username: user.username,
          is_active: true,
          created_at: new Date().toISOString(),
        });
      }
    }

    return HttpResponse.json(
      { detail: 'User not found' },
      { status: 401 }
    );
  }),
];
