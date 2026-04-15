// mobile/src/components/home/__tests__/HistoryList.test.tsx
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { HistoryList } from '../HistoryList';
import type { Dialog } from '../../../api/dialog';

const mockNavigate = jest.fn();

jest.mock('@react-navigation/native', () => ({
  ...jest.requireActual('@react-navigation/native'),
  useNavigation: () => ({ navigate: mockNavigate }),
}));

const mockDialogs: Dialog[] = [
  { id: '1', title: 'Test Dialog', updated_at: new Date().toISOString() },
];

describe('HistoryList', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it('should render empty state when no dialogs', () => {
    const { getByText } = render(<HistoryList dialogs={[]} />);
    expect(getByText('暂无对话记录')).toBeTruthy();
  });

  it('should render dialog items', () => {
    const { getByText } = render(<HistoryList dialogs={mockDialogs} />);
    expect(getByText('Test Dialog')).toBeTruthy();
  });

  it('should navigate to ChatDetail when pressing dialog', () => {
    const { getByText } = render(<HistoryList dialogs={mockDialogs} />);
    fireEvent.press(getByText('Test Dialog'));
    expect(mockNavigate).toHaveBeenCalledWith('ChatsTab', {
      screen: 'Chats',
      params: { dialogId: '1' },
    });
  });
});
