/**
 * ChatInput Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { Send } from 'lucide-react-native';
import { ChatInput } from './ChatInput';

// Mock lucide-react-native icons
jest.mock('lucide-react-native', () => ({
  Send: ({ size, color, strokeWidth }: { size: number; color: string; strokeWidth: number }) => null,
}));

describe('ChatInput Component', () => {
  describe('Rendering', () => {
    it('should render with default placeholder', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} />);

      expect(screen.getByPlaceholderText('输入消息...')).toBeTruthy();
    });

    it('should render disabled placeholder when disabled', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} disabled />);

      expect(screen.getByPlaceholderText('等待回复中...')).toBeTruthy();
    });
  });

  describe('User Interaction', () => {
    it('should update input value when text changes', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} />);

      const input = screen.getByPlaceholderText('输入消息...');
      fireEvent.changeText(input, 'Hello World');

      expect(input.props.value).toBe('Hello World');
    });

    it('should not call onSend when input is empty', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} />);

      const input = screen.getByPlaceholderText('输入消息...');
      fireEvent.changeText(input, '');

      expect(mockOnSend).not.toHaveBeenCalled();
    });

    it('should not call onSend when disabled', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} disabled />);

      const input = screen.getByPlaceholderText('等待回复中...');
      fireEvent.changeText(input, 'Test message');

      expect(mockOnSend).not.toHaveBeenCalled();
    });
  });

  describe('Disabled State', () => {
    it('should disable TextInput when disabled is true', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} disabled />);

      const input = screen.getByPlaceholderText('等待回复中...');
      expect(input.props.editable).toBe(false);
    });

    it('should enable TextInput when disabled is false', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} disabled={false} />);

      const input = screen.getByPlaceholderText('输入消息...');
      expect(input.props.editable).toBe(true);
    });
  });

  describe('Placeholder', () => {
    it('should show "输入消息..." when not disabled', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} />);

      expect(screen.getByPlaceholderText('输入消息...')).toBeTruthy();
    });

    it('should show "等待回复中..." when disabled', () => {
      const mockOnSend = jest.fn();
      render(<ChatInput onSend={mockOnSend} disabled />);

      expect(screen.getByPlaceholderText('等待回复中...')).toBeTruthy();
    });
  });
});
