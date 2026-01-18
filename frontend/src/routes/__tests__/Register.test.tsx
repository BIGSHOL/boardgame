/**
 * Register page tests
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Register from '../Register';
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

function renderRegister() {
  return render(
    <BrowserRouter>
      <Register />
    </BrowserRouter>
  );
}

describe('Register Page', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    useAuthStore.getState().clearError();
    useAuthStore.setState({ user: null, isLoading: false, error: null });
  });

  describe('Rendering', () => {
    it('should render registration form', () => {
      renderRegister();

      expect(screen.getByRole('heading', { name: /회원가입/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/이메일/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/사용자명/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^비밀번호$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/비밀번호 확인/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /회원가입/i })).toBeInTheDocument();
    });

    it('should render link to login page', () => {
      renderRegister();

      expect(screen.getByRole('link', { name: /로그인/i })).toHaveAttribute(
        'href',
        '/login'
      );
    });

    it('should render link to home page', () => {
      renderRegister();

      expect(screen.getByRole('link', { name: /홈으로 돌아가기/i })).toHaveAttribute(
        'href',
        '/'
      );
    });
  });

  describe('Form Interaction', () => {
    it('should allow typing in all fields', async () => {
      const user = userEvent.setup();
      renderRegister();

      const emailInput = screen.getByLabelText(/이메일/i);
      const usernameInput = screen.getByLabelText(/사용자명/i);
      const passwordInput = screen.getByLabelText(/^비밀번호$/i);
      const confirmPasswordInput = screen.getByLabelText(/비밀번호 확인/i);

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');

      expect(emailInput).toHaveValue('test@example.com');
      expect(usernameInput).toHaveValue('testuser');
      expect(passwordInput).toHaveValue('password123');
      expect(confirmPasswordInput).toHaveValue('password123');
    });
  });

  describe('Validation', () => {
    it('should show error when passwords do not match', async () => {
      const user = userEvent.setup();
      renderRegister();

      const emailInput = screen.getByLabelText(/이메일/i);
      const usernameInput = screen.getByLabelText(/사용자명/i);
      const passwordInput = screen.getByLabelText(/^비밀번호$/i);
      const confirmPasswordInput = screen.getByLabelText(/비밀번호 확인/i);
      const submitButton = screen.getByRole('button', { name: /회원가입/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'differentpassword');
      await user.click(submitButton);

      expect(screen.getByText(/비밀번호가 일치하지 않습니다/i)).toBeInTheDocument();
    });

    it('should show error when password is too short', async () => {
      const user = userEvent.setup();
      renderRegister();

      const emailInput = screen.getByLabelText(/이메일/i);
      const usernameInput = screen.getByLabelText(/사용자명/i);
      const passwordInput = screen.getByLabelText(/^비밀번호$/i);
      const confirmPasswordInput = screen.getByLabelText(/비밀번호 확인/i);
      const submitButton = screen.getByRole('button', { name: /회원가입/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'short');
      await user.type(confirmPasswordInput, 'short');
      await user.click(submitButton);

      expect(screen.getByText(/비밀번호는 8자 이상이어야 합니다/i)).toBeInTheDocument();
    });
  });

  describe('Registration Success', () => {
    it('should navigate to login on successful registration', async () => {
      const user = userEvent.setup();
      renderRegister();

      const emailInput = screen.getByLabelText(/이메일/i);
      const usernameInput = screen.getByLabelText(/사용자명/i);
      const passwordInput = screen.getByLabelText(/^비밀번호$/i);
      const confirmPasswordInput = screen.getByLabelText(/비밀번호 확인/i);
      const submitButton = screen.getByRole('button', { name: /회원가입/i });

      await user.type(emailInput, 'newuser@example.com');
      await user.type(usernameInput, 'newuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login', expect.any(Object));
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading text when isLoading is true', async () => {
      // Set loading state before render
      useAuthStore.setState({ isLoading: true });
      renderRegister();

      await waitFor(() => {
        const submitButton = screen.getByRole('button', { name: /가입 중.../i });
        expect(submitButton).toBeDisabled();
      });
    });
  });
});
