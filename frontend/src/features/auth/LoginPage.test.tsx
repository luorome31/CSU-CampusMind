import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginPage } from './LoginPage';
import { authStore } from './authStore';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../../api/auth', () => ({
  authApi: {
    login: vi.fn(),
    logout: vi.fn(),
    refresh: vi.fn(),
  },
}));

describe('LoginPage', () => {
  beforeEach(() => {
    authStore.setState({
      user: null,
      token: null,
      sessionId: null,
      isAuthenticated: false,
      isLoading: false,
    });
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('renders login form', () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    expect(screen.getByText('Welcome back to CampusMind')).toBeInTheDocument();
  });

  it('renders username input', () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
  });

  it('renders password input', () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('renders submit button with Sign In text', () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
  });

  it('calls login with form values on submit', async () => {
    const { authApi } = await import('../../api/auth');
    vi.mocked(authApi.login).mockResolvedValue({
      token: 'test-token',
      user_id: 'user-1',
      session_id: 'session-1',
      expires_in: 3600,
    });

    render(<MemoryRouter><LoginPage /></MemoryRouter>);

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } });

    const form = document.querySelector('form');
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith('testuser', 'password123');
    });
  });

  it('displays error message on login failure', async () => {
    const { authApi } = await import('../../api/auth');
    vi.mocked(authApi.login).mockRejectedValue(new Error('Invalid credentials'));

    render(<MemoryRouter><LoginPage /></MemoryRouter>);

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrong' } });

    const form = document.querySelector('form');
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  it('shows loading state on button during login', async () => {
    const { authApi } = await import('../../api/auth');
    vi.mocked(authApi.login).mockImplementation(() => new Promise(() => {}));

    render(<MemoryRouter><LoginPage /></MemoryRouter>);

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password' } });

    const form = document.querySelector('form');
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Signing in...' })).toBeInTheDocument();
    });
  });

  it('disables button during loading', async () => {
    const { authApi } = await import('../../api/auth');
    vi.mocked(authApi.login).mockImplementation(() => new Promise(() => {}));

    render(<MemoryRouter><LoginPage /></MemoryRouter>);

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password' } });

    const form = document.querySelector('form');
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Signing in...' })).toBeDisabled();
    });
  });
});
