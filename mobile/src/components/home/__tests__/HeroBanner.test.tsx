// mobile/src/components/home/__tests__/HeroBanner.test.tsx
import React from 'react';
import { render } from '@testing-library/react-native';
import { HeroBanner } from '../HeroBanner';

// Mock navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({ navigate: jest.fn() }),
}));

// Mock Card component
jest.mock('../../ui/Card', () => ({
  Card: ({ children, style }: any) => {
    const { View } = require('react-native');
    return <View style={style}>{children}</View>;
  },
}));

describe('HeroBanner', () => {
  it('should render brand title', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText('CampusMind')).toBeTruthy();
  });

  it('should render correct subtitle', () => {
    const { getByText } = render(<HeroBanner />);
    expect(getByText(/基于 RAG 与 Tool-calling 的智能校园助手/)).toBeTruthy();
  });

  it('should navigate to ChatsTab with undefined dialogId when "新建对话" is pressed', () => {
    const mockNavigate = jest.fn();
    jest.spyOn(require('@react-navigation/native'), 'useNavigation').mockReturnValue({ navigate: mockNavigate });

    const { getByText } = render(<HeroBanner />);
    const button = getByText('新建对话');

    const { fireEvent } = require('@testing-library/react-native');
    fireEvent.press(button);

    expect(mockNavigate).toHaveBeenCalledWith('ChatsTab', {
      screen: 'Chats',
      params: { dialogId: undefined },
    });
  });
});
