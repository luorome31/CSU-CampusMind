import { describe, it, expect, beforeEach, vi } from 'vitest';
import { profileStore } from './profileStore';

vi.mock('./api/profile', () => ({
  profileApi: {
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
    getSessions: vi.fn(),
    revokeSession: vi.fn(),
  },
}));

describe('profileStore', () => {
  beforeEach(() => {
    profileStore.setState({
      user: null,
      stats: null,
      sessions: [],
      isLoading: false,
      error: null,
    });
  });

  it('should have initial state', () => {
    const state = profileStore.getState();
    expect(state.user).toBeNull();
    expect(state.stats).toBeNull();
    expect(state.sessions).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should load profile', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      display_name: 'Test User',
      avatar_url: null,
      email: 'test@example.com',
      phone: '1234567890',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };

    const { profileApi } = await import('./api/profile');
    vi.mocked(profileApi.getProfile).mockResolvedValue(mockUser);

    await profileStore.getState().loadProfile();
    expect(profileStore.getState().user).toEqual(mockUser);
    expect(profileStore.getState().isLoading).toBe(false);
  });

  it('should handle load profile error', async () => {
    const { profileApi } = await import('./api/profile');
    vi.mocked(profileApi.getProfile).mockRejectedValue(new Error('Network error'));

    await profileStore.getState().loadProfile();
    expect(profileStore.getState().error).toBe('Network error');
    expect(profileStore.getState().isLoading).toBe(false);
  });

  it('should update profile', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      display_name: 'Updated Name',
      avatar_url: null,
      email: 'updated@example.com',
      phone: '0987654321',
      is_active: true,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };

    const { profileApi } = await import('./api/profile');
    vi.mocked(profileApi.updateProfile).mockResolvedValue(mockUser);

    await profileStore.getState().updateProfile({ display_name: 'Updated Name' });
    expect(profileStore.getState().user).toEqual(mockUser);
  });

  it('should load sessions', async () => {
    const mockSessions = [
      {
        session_id: '1',
        device: 'Chrome on Windows',
        location: '北京市',
        created_at: Date.now(),
        is_current: true,
      },
    ];

    const { profileApi } = await import('./api/profile');
    vi.mocked(profileApi.getSessions).mockResolvedValue(mockSessions);

    await profileStore.getState().loadSessions();
    expect(profileStore.getState().sessions).toEqual(mockSessions);
  });

  it('should revoke session', async () => {
    const mockSessions = [
      { session_id: '1', device: 'Chrome', location: '北京', created_at: Date.now(), is_current: true },
      { session_id: '2', device: 'Safari', location: '北京', created_at: Date.now(), is_current: false },
    ];

    profileStore.setState({ sessions: mockSessions });

    const { profileApi } = await import('./api/profile');
    vi.mocked(profileApi.revokeSession).mockResolvedValue({ success: true });

    await profileStore.getState().revokeSession('2');
    expect(profileStore.getState().sessions).toHaveLength(1);
    expect(profileStore.getState().sessions[0].session_id).toBe('1');
  });

  it('should clear error', () => {
    profileStore.setState({ error: 'Some error' });
    profileStore.getState().clearError();
    expect(profileStore.getState().error).toBeNull();
  });
});
