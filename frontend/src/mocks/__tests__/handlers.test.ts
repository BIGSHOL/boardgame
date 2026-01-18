/**
 * MSW Handlers integration test
 */
import { describe, it, expect } from 'vitest';

describe('MSW Setup', () => {
  it('should have MSW server configured', async () => {
    // 단순히 MSW가 설정되었는지 확인
    const response = await fetch('/api/v1/lobbies');
    expect(response.ok).toBe(true);

    const data = await response.json();
    expect(data).toHaveProperty('lobbies');
    expect(data).toHaveProperty('total');
  });

  it('should handle auth register endpoint', async () => {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
      }),
    });

    expect(response.status).toBe(201);
    const data = await response.json();
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('email', 'test@example.com');
    expect(data).toHaveProperty('username', 'testuser');
  });

  it('should handle auth login endpoint', async () => {
    // 먼저 등록
    await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'login@example.com',
        username: 'loginuser',
        password: 'password123',
      }),
    });

    // 그 다음 로그인
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'login@example.com',
        password: 'password123',
      }),
    });

    expect(response.ok).toBe(true);
    const data = await response.json();
    expect(data).toHaveProperty('user');
    expect(data).toHaveProperty('tokens');
    expect(data.tokens).toHaveProperty('access_token');
    expect(data.tokens).toHaveProperty('refresh_token');
  });

  it('should handle game state endpoint', async () => {
    const response = await fetch('/api/v1/games/1');
    expect(response.ok).toBe(true);

    const data = await response.json();
    expect(data).toHaveProperty('id', 1);
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('board');
    expect(data).toHaveProperty('players');
  });
});
