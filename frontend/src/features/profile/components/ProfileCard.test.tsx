import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ProfileCard } from './ProfileCard';

vi.mock('../profileStore', () => ({
  profileStore: vi.fn(() => ({
    user: {
      id: '1',
      username: 'testuser',
      display_name: 'Test User',
      avatar_url: null,
      email: 'test@example.com',
      phone: '1234567890',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
    updateProfile: vi.fn(),
    isLoading: false,
  })),
}));

describe('ProfileCard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders user information', () => {
    render(<ProfileCard />);
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('1234567890')).toBeInTheDocument();
  });

  it('shows avatar placeholder with first letter', () => {
    render(<ProfileCard />);
    expect(screen.getByText('T')).toBeInTheDocument();
  });

  it('renders all field labels', () => {
    render(<ProfileCard />);
    expect(screen.getByText('显示名称')).toBeInTheDocument();
    expect(screen.getByText('用户名')).toBeInTheDocument();
    expect(screen.getByText('邮箱')).toBeInTheDocument();
    expect(screen.getByText('手机号')).toBeInTheDocument();
  });
});
