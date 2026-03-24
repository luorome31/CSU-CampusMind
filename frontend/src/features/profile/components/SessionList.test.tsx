import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SessionList } from './SessionList';

vi.mock('../profileStore', () => ({
  profileStore: vi.fn(() => ({
    sessions: [
      {
        session_id: '1',
        device: 'Chrome on Windows',
        location: '北京市',
        created_at: Math.floor(Date.now() / 1000) - 2 * 60 * 60, // 2 hours ago
        is_current: true,
      },
      {
        session_id: '2',
        device: 'Safari on iPhone',
        location: '北京市',
        created_at: Math.floor(Date.now() / 1000) - 5 * 60, // 5 minutes ago
        is_current: false,
      },
    ],
    revokeSession: vi.fn(),
  })),
}));

describe('SessionList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders sessions', () => {
    render(<SessionList />);
    expect(screen.getByText('Chrome on Windows')).toBeInTheDocument();
    expect(screen.getByText('Safari on iPhone')).toBeInTheDocument();
    expect(screen.getByText('当前')).toBeInTheDocument();
  });

  it('renders session title', () => {
    render(<SessionList />);
    expect(screen.getByText('活跃会话')).toBeInTheDocument();
  });

  it('shows revoke button for non-current sessions', () => {
    render(<SessionList />);
    const revokeButtons = screen.getAllByText('登出');
    expect(revokeButtons).toHaveLength(1);
  });

  it('shows location for sessions', () => {
    render(<SessionList />);
    // There are two sessions, both with location '北京市'
    const locations = screen.getAllByText('北京市');
    expect(locations).toHaveLength(2);
  });
});
