/**
 * LobbyList page tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import LobbyList from '../LobbyList';
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

function renderLobbyList() {
  return render(
    <BrowserRouter>
      <LobbyList />
    </BrowserRouter>
  );
}

describe('LobbyList Page', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    useAuthStore.setState({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  describe('Unauthenticated', () => {
    it('should show login prompt when not authenticated', () => {
      renderLobbyList();

      expect(screen.getByText(/로그인이 필요합니다/i)).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /로그인하기/i })).toBeInTheDocument();
    });
  });

  describe('Authenticated', () => {
    beforeEach(() => {
      useAuthStore.setState({
        user: { id: 1, email: 'test@example.com', username: 'testuser' },
        tokens: { access_token: 'test-token', refresh_token: 'refresh-token', token_type: 'bearer' },
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    });

    it('should render lobby list page', async () => {
      renderLobbyList();

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /게임 로비/i })).toBeInTheDocument();
      });
    });

    it('should render create lobby button', async () => {
      renderLobbyList();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /로비 생성/i })).toBeInTheDocument();
      });
    });

    it('should render invite code input', async () => {
      renderLobbyList();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/초대 코드/i)).toBeInTheDocument();
      });
    });

    it('should show create lobby modal when button clicked', async () => {
      const user = userEvent.setup();
      renderLobbyList();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /로비 생성/i })).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /로비 생성/i }));

      expect(screen.getByText(/새 로비 생성/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/로비 이름/i)).toBeInTheDocument();
    });

    it('should convert invite code to uppercase', async () => {
      const user = userEvent.setup();
      renderLobbyList();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/초대 코드/i)).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText(/초대 코드/i);
      await user.type(input, 'abcdef');

      expect(input).toHaveValue('ABCDEF');
    });

    it('should fetch and display lobbies', async () => {
      renderLobbyList();

      await waitFor(() => {
        expect(screen.getByText(/대기 중인 로비/i)).toBeInTheDocument();
      });
    });
  });
});
