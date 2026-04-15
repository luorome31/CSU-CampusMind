import React from 'react';
import { render } from '@testing-library/react-native';
import { ProfileCard } from '../ProfileCard';

jest.mock('../../profileStore', () => ({
  useProfileStore: () => ({
    user: {
      id: '1',
      username: 'testuser',
      display_name: 'Test User',
      email: 'test@example.com',
      phone: '13800138000',
    },
    updateProfile: jest.fn(),
    isLoading: false,
  }),
}));

describe('ProfileCard', () => {
  it('should render user info correctly', () => {
    const { getByText } = render(<ProfileCard />);

    expect(getByText('Test User')).toBeTruthy();
    expect(getByText('testuser')).toBeTruthy();
    expect(getByText('test@example.com')).toBeTruthy();
  });

  it('should show edit hints for editable fields', () => {
    const { getAllByText } = render(<ProfileCard />);
    const editHints = getAllByText('点击编辑');
    // display_name, email, phone are editable; username is not
    expect(editHints.length).toBe(3);
  });
});
