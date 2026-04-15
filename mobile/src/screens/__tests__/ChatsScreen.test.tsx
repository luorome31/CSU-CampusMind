import React from 'react';
import { render, waitFor } from '@testing-library/react-native';

// 1. Mock EVERYTHING navigation related at the very top
jest.mock('@react-navigation/native', () => ({
  useFocusEffect: jest.fn(),
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
    setOptions: jest.fn(),
  }),
  useIsFocused: () => true,
  useRoute: () => ({ params: {} }),
}));

// 2. Mock the store
jest.mock('../../features/chat/chatStore', () => {
  const mockStore = {
    currentKnowledgeIds: [],
    loadDialog: jest.fn(),
    clearMessages: jest.fn(),
    setIsLoadingHistory: jest.fn(),
    isLoadingHistory: false,
    messages: [],
    isStreaming: false,
  };
  return {
    useChatStore: jest.fn((selector) => selector(mockStore)),
  };
});

// 3. Mock other hooks
jest.mock('../../features/chat/useChatStream', () => ({
  useChatStream: () => ({
    sendMessage: jest.fn(),
    isStreaming: false,
    messages: [],
  }),
}));

// 4. Mock API
jest.mock('../../api/dialog', () => ({
  getDialogMessages: jest.fn().mockResolvedValue([]),
}));

// 5. Mock Safe Area
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaView: ({ children }: any) => children,
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));

// 6. Mock sub-components
jest.mock('../../components/chat/MessageList', () => ({ MessageList: () => null }));
jest.mock('../../components/chat/ChatInput', () => ({ ChatInput: () => null }));
jest.mock('../../components/chat/EmptyState', () => ({ EmptyState: () => null }));

import { ChatsScreen } from '../ChatsScreen';

describe('ChatsScreen (Simple)', () => {
  it('renders header', async () => {
    const mockNavigation = { navigate: jest.fn() };
    const mockRoute = { params: {} };
    const { getByText } = render(
      <ChatsScreen navigation={mockNavigation as any} route={mockRoute as any} />
    );
    expect(getByText('CampusMind')).toBeTruthy();
  });
});
