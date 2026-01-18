/**
 * Login page tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
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

function renderLogin() {
  return render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );
}

describe('Login Page', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    useAuthStore.getState().clearError();
    useAuthStore.setState({ user: null, isLoading: false, error: null });
  });

  describe('Rendering', () => {
    it('should render login form', () => {
      renderLogin();

      expect(screen.getByRole('heading', { name: /로그인/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/이메일/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/비밀번호/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /로그인/i })).toBeInTheDocument();
    });

    it('should render link to register page', () => {
      renderLogin();

      expect(screen.getByRole('link', { name: /회원가입/i })).toHaveAttribute(
        'href',
        '/register'
      );
    });

    it('should render link to home page', () => {
      renderLogin();

      expect(screen.getByRole('link', { name: /홈으로 돌아가기/i })).toHaveAttribute(
        'href',
        '/'
      );
    });
  });

  describe('Form Interaction', () => {
    it('should allow typing in email and password fields', async () => {
      const user = userEvent.setup();
      renderLogin();

      const emailInput = screen.getByLabelText(/이메일/i);
      const passwordInput = screen.getByLabelText(/비밀번호/i);

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');

      expect(emailInput).toHaveValue('test@example.com');
      expect(passwordInput).toHaveValue('password123');
    });

    it('should submit form with email and password', async () => {
      const user = userEvent.setup();
      renderLogin();

      const emailInput = screen.getByLabelText(/이메일/i);
      const passwordInput = screen.getByLabelText(/비밀번호/i);
      const submitButton = screen.getByRole('button', { name: /로그인/i });

      await user.type(emailInput, 'login@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      // Wait for loading state
      await waitFor(() => {
        expect(screen.queryByText(/로그인 중.../i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Login Success', () => {
    it('should navigate to home on successful login', async () => {
      const user = userEvent.setup();

      // Register user first (MSW handles this)
      await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'logintest@example.com',
          username: 'logintest',
          password: 'password123',
        }),
      });

      renderLogin();

      const emailInput = screen.getByLabelText(/이메일/i);
      const passwordInput = screen.getByLabelText(/비밀번호/i);
      const submitButton = screen.getByRole('button', { name: /로그인/i });

      await user.type(emailInput, 'logintest@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/');
      });
    });
  });

  describe('Login Failure', () => {
    it('should display error on wrong password', async () => {
      const user = userEvent.setup();

      // Register user first
      await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'wrongpass@example.com',
          username: 'wrongpassuser',
          password: 'password123',
        }),
      });

      renderLogin();

      const emailInput = screen.getByLabelText(/이메일/i);
      const passwordInput = screen.getByLabelText(/비밀번호/i);
      const submitButton = screen.getByRole('button', { name: /로그인/i });

      await user.type(emailInput, 'wrongpass@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);

      await waitFor(() => {
        // Error message should appear
        expect(useAuthStore.getState().error).toBeTruthy();
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading text when isLoading is true', async () => {
      // Set loading state before render
      useAuthStore.setState({ isLoading: true });
      renderLogin();

      await waitFor(() => {
        const submitButton = screen.getByRole('button', { name: /로그인 중.../i });
        expect(submitButton).toBeDisabled();
      });
    });
  });
});
