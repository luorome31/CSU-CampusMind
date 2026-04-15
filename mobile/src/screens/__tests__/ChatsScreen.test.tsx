// mobile/src/screens/__tests__/ChatsScreen.test.tsx
import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import { ChatsScreen } from '../ChatsScreen';

// Mock sub-components using exact relative paths from the current file
jest.mock('../../components/chat/MessageList', () => ({
  MessageList: () => null,
}));
jest.mock('../../components/chat/ChatInput', () => ({
  ChatInput: () => null,
}));
jest.mock('../../components/chat/EmptyState', () => ({
  EmptyState: () => null,
}));

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

// Mock safe area insets
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => {
    const { View } = require('react-native');
    return <View>{children}</View>;
  },
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));

// Mock navigation
const mockNavigation = {
  goBack: jest.fn(),
  navigate: jest.fn(),
  setOptions: jest.fn(),
};

describe('ChatsScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render header correctly', async () => {
    const { getAllByText } = render(<ChatsScreen navigation={mockNavigation as any} />);

    await waitFor(() => {
      expect(getAllByText('CampusMind').length).toBeGreaterThan(0);
    });
  });
});
