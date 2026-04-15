import React from 'react';
import { render } from '@testing-library/react-native';
import { SessionList } from '../SessionList';

// Mock Date.now to get consistent time formatting
const mockNow = new Date('2024-01-15T12:00:00Z').getTime();

jest.mock('../../profileStore', () => ({
  useProfileStore: () => ({
    sessions: [
      {
        session_id: '1',
        device: 'iPhone 15',
        location: '上海',
        created_at: new Date(mockNow - 5 * 60 * 1000).toISOString(), // 5 minutes ago
        is_current: true,
      },
      {
        session_id: '2',
        device: 'Chrome',
        location: '北京',
        created_at: new Date(mockNow - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        is_current: false,
      },
    ],
  }),
}));

describe('SessionList', () => {
  it('should render sessions', () => {
    const { getByText } = render(<SessionList />);

    expect(getByText('iPhone 15')).toBeTruthy();
    expect(getByText('Chrome')).toBeTruthy();
  });

  it('should show current badge', () => {
    const { getByText } = render(<SessionList />);
    expect(getByText('当前')).toBeTruthy();
  });
});
