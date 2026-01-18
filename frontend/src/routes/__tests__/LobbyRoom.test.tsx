/**
 * LobbyRoom page tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import LobbyRoom from '../LobbyRoom';
import { useAuthStore } from '../../stores/authStore';

// Mock navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock fetch for lobby data
const mockLobby = {
  id: 1,
  name: 'Test Lobby',
  host_id: 1,
  invite_code: 'ABC123',
  status: 'waiting',
  max_players: 4,
  players: [
    {
      id: 1,
      user_id: 1,
      username: 'testuser',
      color: 'blue',
      turn_order: 0,
      is_host: true,
      is_ready: false,
    },
  ],
  created_at: new Date().toISOString(),
};

function renderLobbyRoom(lobbyId: string = '1') {
  return render(
    <MemoryRouter initialEntries={[`/lobby/${lobbyId}`]}>
      <Routes>
        <Route path="/lobby/:id" element={<LobbyRoom />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('LobbyRoom Page', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    useAuthStore.setState({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });

    // Mock fetch
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockLobby),
    });
  });

  describe('Unauthenticated', () => {
    it('should show login prompt when not authenticated', () => {
      renderLobbyRoom();

      expect(screen.getByText(/로그인이 필요합니다/i)).toBeInTheDocument();
    });
  });

  describe('Authenticated as Host', () => {
    beforeEach(() => {
      useAuthStore.setState({
        user: { id: 1, email: 'test@example.com', username: 'testuser' },
        tokens: { access_token: 'test-token', refresh_token: 'refresh-token', token_type: 'bearer' },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    });

    it('should render lobby room with name', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Test Lobby/i })).toBeInTheDocument();
      });
    });

    it('should display invite code', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByText('ABC123')).toBeInTheDocument();
      });
    });

    it('should show host badge', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByText(/호스트/i)).toBeInTheDocument();
      });
    });

    it('should show start game button for host', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /게임 시작/i })).toBeInTheDocument();
      });
    });

    it('should disable start button when not enough players', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        const startButton = screen.getByRole('button', { name: /게임 시작/i });
        expect(startButton).toBeDisabled();
      });
    });

    it('should show minimum players message', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByText(/최소 2명의 플레이어가 필요합니다/i)).toBeInTheDocument();
      });
    });

    it('should have copy button for invite code', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByText('ABC123')).toBeInTheDocument();
      });

      // Verify copy button exists
      expect(screen.getByText(/복사/i)).toBeInTheDocument();
    });
  });

  describe('Authenticated as Non-Host', () => {
    beforeEach(() => {
      useAuthStore.setState({
        user: { id: 2, email: 'player@example.com', username: 'player' },
        tokens: { access_token: 'test-token', refresh_token: 'refresh-token', token_type: 'bearer' },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      // Mock fetch with player in lobby
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          ...mockLobby,
          players: [
            ...mockLobby.players,
            {
              id: 2,
              user_id: 2,
              username: 'player',
              color: 'red',
              turn_order: 1,
              is_host: false,
              is_ready: false,
            },
          ],
        }),
      });
    });

    it('should show ready button for non-host', async () => {
      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /준비 완료/i })).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      useAuthStore.setState({
        user: { id: 1, email: 'test@example.com', username: 'testuser' },
        tokens: { access_token: 'test-token', refresh_token: 'refresh-token', token_type: 'bearer' },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    });

    it('should show error when lobby not found', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
      });

      renderLobbyRoom();

      await waitFor(() => {
        expect(screen.getByText(/로비를 찾을 수 없습니다/i)).toBeInTheDocument();
      });
    });
  });
});
