/**
 * ThinkingBlock Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { ThinkingBlock } from './ThinkingBlock';

// Mock lucide-react-native icons
jest.mock('lucide-react-native', () => ({
  Brain: () => null,
  ChevronDown: () => null,
  ChevronRight: () => null,
}));

// Mock react-native-markdown-display
jest.mock('react-native-markdown-display', () => {
  const { Text } = require('react-native');
  return {
    __esModule: true,
    default: ({ children, style }: { children: string; style: object }) => (
      <Text testID="markdown-content">{children}</Text>
    ),
  };
});

describe('ThinkingBlock Component', () => {
  describe('Collapsed State (Default)', () => {
    it('should render header with step count', () => {
      const thinking = ['Step 1 thought', 'Step 2 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('AI 思考过程')).toBeTruthy();
      expect(screen.getByText('(2步)')).toBeTruthy();
    });

    it('should show expand hint when collapsed', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('查看思考过程')).toBeTruthy();
    });

    it('should not show step content when collapsed', () => {
      const thinking = ['Step 1 thought', 'Step 2 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.queryByText('步骤 1')).toBeNull();
      expect(screen.queryByText('步骤 2')).toBeNull();
    });

    it('should render nothing when thinking is empty', () => {
      render(<ThinkingBlock thinking={[]} />);

      // Should not render any thinking-related content
      expect(screen.queryByText('AI 思考过程')).toBeNull();
      expect(screen.queryByText('查看思考过程')).toBeNull();
    });
  });

  describe('Expanded State', () => {
    it('should expand when header is pressed', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('查看思考过程'));

      expect(screen.getByText('步骤 1')).toBeTruthy();
    });

    it('should show all thinking steps when expanded', () => {
      const thinking = ['First thought', 'Second thought', 'Third thought'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('查看思考过程'));

      expect(screen.getByText('步骤 1')).toBeTruthy();
      expect(screen.getByText('步骤 2')).toBeTruthy();
      expect(screen.getByText('步骤 3')).toBeTruthy();
    });

    it('should render markdown content for each step', () => {
      const thinking = ['# Header\nContent here'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('查看思考过程'));

      expect(screen.getByTestId('markdown-content')).toBeTruthy();
    });

    it('should show collapse button when expanded', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('查看思考过程'));

      expect(screen.getByText('收起')).toBeTruthy();
    });
  });

  describe('Toggle Behavior', () => {
    it('should collapse when collapse button is pressed', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      // Expand
      fireEvent.press(screen.getByText('查看思考过程'));
      expect(screen.getByText('步骤 1')).toBeTruthy();

      // Collapse
      fireEvent.press(screen.getByText('收起'));
      expect(screen.queryByText('步骤 1')).toBeNull();
    });

    it('should re-expand when header is pressed after collapse', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      // Expand
      fireEvent.press(screen.getByText('查看思考过程'));
      expect(screen.getByText('步骤 1')).toBeTruthy();

      // Collapse
      fireEvent.press(screen.getByText('收起'));
      expect(screen.queryByText('步骤 1')).toBeNull();

      // Re-expand
      fireEvent.press(screen.getByText('查看思考过程'));
      expect(screen.getByText('步骤 1')).toBeTruthy();
    });
  });

  describe('Edge Cases', () => {
    it('should handle single step', () => {
      const thinking = ['Only one step'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('(1步)')).toBeTruthy();

      fireEvent.press(screen.getByText('查看思考过程'));

      expect(screen.getByText('步骤 1')).toBeTruthy();
    });

    it('should handle many steps', () => {
      const thinking = Array.from({ length: 10 }, (_, i) => `Step ${i + 1}`);

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('(10步)')).toBeTruthy();

      fireEvent.press(screen.getByText('查看思考过程'));

      expect(screen.getByText('步骤 1')).toBeTruthy();
      expect(screen.getByText('步骤 10')).toBeTruthy();
    });

    it('should handle empty string steps', () => {
      const thinking = ['Valid step', '', 'Another valid step'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('查看思考过程'));

      expect(screen.getByText('步骤 1')).toBeTruthy();
      expect(screen.getByText('步骤 2')).toBeTruthy();
      expect(screen.getByText('步骤 3')).toBeTruthy();
    });
  });
});
