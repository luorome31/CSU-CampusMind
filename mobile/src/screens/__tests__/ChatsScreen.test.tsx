// mobile/src/screens/__tests__/ChatsScreen.test.tsx
import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { ChatsScreen } from '../ChatsScreen';

// Mock the chat store
jest.mock('../../features/chat/chatStore', () => ({
  useChatStore: jest.fn().mockReturnValue({
    currentKnowledgeIds: [],
  }),
}));

// Mock the useChatStream hook
jest.mock('../../features/chat/useChatStream', () => ({
  useChatStream: jest.fn().mockReturnValue({
    sendMessage: jest.fn(),
    cancelStream: jest.fn(),
    isStreaming: false,
    messages: [],
    toolEvents: [],
  }),
}));

function renderWithNavigation(ui: React.ReactElement) {
  return render(<NavigationContainer>{ui}</NavigationContainer>);
}

describe('ChatsScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render EmptyState when no messages', async () => {
    const { getByTestId, getByText } = renderWithNavigation(<ChatsScreen />);

    await waitFor(() => {
      expect(getByTestId('empty-state-avatar')).toBeTruthy();
      expect(getByTestId('empty-state-title')).toBeTruthy();
      expect(getByText('CampusMind')).toBeTruthy();
    });
  });

  it('should render EmptyState subtitle correctly', async () => {
    const { getByTestId } = renderWithNavigation(<ChatsScreen />);

    await waitFor(() => {
      expect(getByTestId('empty-state-subtitle')).toBeTruthy();
    });
  });

  it('should render ChatInput component', async () => {
    const { getByPlaceholderText } = renderWithNavigation(<ChatsScreen />);

    await waitFor(() => {
      expect(getByPlaceholderText('输入消息...')).toBeTruthy();
    });
  });
});
