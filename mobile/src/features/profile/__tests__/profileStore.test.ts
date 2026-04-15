import { renderHook, act } from '@testing-library/react-native';
import { useProfileStore } from '../profileStore';

// Mock profileApi
jest.mock('../api/profile', () => ({
  profileApi: {
    getProfile: jest.fn(),
    updateProfile: jest.fn(),
    getStats: jest.fn(),
    getSessions: jest.fn(),
  },
}));

describe('useProfileStore', () => {
  beforeEach(() => {
    useProfileStore.setState({
      user: null,
      stats: null,
      sessions: [],
      isLoading: false,
      error: null,
    });
  });

  it('should have initial state', () => {
    const { result } = renderHook(() => useProfileStore());
    expect(result.current.user).toBeNull();
    expect(result.current.stats).toBeNull();
    expect(result.current.sessions).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should load profile successfully', async () => {
    const mockUser = { id: '1', username: 'testuser', display_name: 'Test User' };
    require('../api/profile').profileApi.getProfile.mockResolvedValue({ data: mockUser });

    const { result } = renderHook(() => useProfileStore());

    await act(async () => {
      await result.current.loadProfile();
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isLoading).toBe(false);
  });
});