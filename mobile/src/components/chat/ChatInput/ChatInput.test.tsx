/**
 * ChatInput Component Tests
 */

import React from 'react';
import { render, fireEvent, screen, act } from '@testing-library/react-native';
import { ChatInput } from './ChatInput';

// Mock lucide-react-native icons
jest.mock('lucide-react-native', () => ({
  Send: () => null,
}));

// Mock safe area insets
jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
}));

describe('ChatInput Component', () => {
  const mockOnSend = jest.fn();

  beforeEach(() => {
    mockOnSend.mockClear();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Initial Rendering', () => {
    it('should render correctly', () => {
      render(<ChatInput onSend={mockOnSend} />);
      
      expect(screen.getByPlaceholderText('输入消息...')).toBeTruthy();
      expect(screen.getByTestId('chat-input')).toBeTruthy();
    });
  });

  describe('Input Behavior', () => {
    it('should update value on text change', () => {
      render(<ChatInput onSend={mockOnSend} />);
      const input = screen.getByPlaceholderText('输入消息...');

      act(() => {
        fireEvent.changeText(input, 'Hello World');
      });
      expect(input.props.value).toBe('Hello World');
    });

    it('should clear input on send', () => {
      render(<ChatInput onSend={mockOnSend} />);
      const input = screen.getByPlaceholderText('输入消息...');
      
      act(() => {
        fireEvent.changeText(input, 'Hello World');
      });
      
      const sendButton = screen.getByTestId('send-button');
      act(() => {
        fireEvent.press(sendButton);
        jest.runAllTimers();
      });

      expect(mockOnSend).toHaveBeenCalledWith('Hello World');
      expect(input.props.value).toBe('');
    });
  });

  describe('Disabled State', () => {
    it('should disable TextInput when disabled is true', () => {
      render(<ChatInput onSend={mockOnSend} disabled={true} />);
      const input = screen.getByPlaceholderText('等待回复中...');
      
      expect(input.props.editable).toBe(false);
    });
  });

  describe('Placeholder', () => {
    it('should show "输入消息..." when not disabled', () => {
      render(<ChatInput onSend={mockOnSend} disabled={false} />);
      expect(screen.getByPlaceholderText('输入消息...')).toBeTruthy();
    });

    it('should show "等待回复中..." when disabled', () => {
      render(<ChatInput onSend={mockOnSend} disabled={true} />);
      expect(screen.getByPlaceholderText('等待回复中...')).toBeTruthy();
    });
  });
});
