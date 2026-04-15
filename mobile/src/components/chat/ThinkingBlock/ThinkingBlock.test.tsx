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
  ChevronUp: () => null,
}));

// Mock react-native-markdown-display
jest.mock('react-native-markdown-display', () => {
  const { Text } = require('react-native');
  return {
    __esModule: true,
    default: ({ children }: { children: string }) => (
      <Text testID="markdown-content">{children}</Text>
    ),
  };
});

describe('ThinkingBlock Component', () => {
  describe('Collapsed State (Default)', () => {
    it('should render header with step count', () => {
      const thinking = ['Step 1 thought', 'Step 2 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('思考')).toBeTruthy();
      expect(screen.getByText('(2 步)')).toBeTruthy();
    });

    it('should show step count when collapsed', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('(1 步)')).toBeTruthy();
    });

    it('should not show step content when collapsed', () => {
      const thinking = ['Step 1 thought', 'Step 2 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.queryByTestId('markdown-content')).toBeNull();
    });

    it('should render nothing when thinking is empty', () => {
      render(<ThinkingBlock thinking={[]} />);

      // Should not render any thinking-related content
      expect(screen.queryByText('思考')).toBeNull();
    });
  });

  describe('Expanded State', () => {
    it('should expand when header is pressed', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('思考'));

      expect(screen.getByTestId('markdown-content')).toBeTruthy();
    });

    it('should show all thinking steps when expanded', () => {
      const thinking = ['First thought', 'Second thought', 'Third thought'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('思考'));

      const steps = screen.getAllByTestId('markdown-content');
      expect(steps).toHaveLength(3);
    });

    it('should render markdown content for each step', () => {
      const thinking = ['# Header\nContent here'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('思考'));

      expect(screen.getByTestId('markdown-content')).toBeTruthy();
    });
  });

  describe('Toggle Behavior', () => {
    it('should collapse when header is pressed again', () => {
      const thinking = ['Step 1 thought'];

      render(<ThinkingBlock thinking={thinking} />);

      // Expand
      fireEvent.press(screen.getByText('思考'));
      expect(screen.getByTestId('markdown-content')).toBeTruthy();

      // Collapse
      fireEvent.press(screen.getByText('思考'));
      expect(screen.queryByTestId('markdown-content')).toBeNull();
    });
  });

  describe('Edge Cases', () => {
    it('should handle single step', () => {
      const thinking = ['Only one step'];

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('(1 步)')).toBeTruthy();

      fireEvent.press(screen.getByText('思考'));

      expect(screen.getByTestId('markdown-content')).toBeTruthy();
    });

    it('should handle many steps', () => {
      const thinking = Array.from({ length: 10 }, (_, i) => `Step ${i + 1}`);

      render(<ThinkingBlock thinking={thinking} />);

      expect(screen.getByText('(10 步)')).toBeTruthy();

      fireEvent.press(screen.getByText('思考'));

      const steps = screen.getAllByTestId('markdown-content');
      expect(steps).toHaveLength(10);
    });

    it('should handle empty string steps', () => {
      const thinking = ['Valid step', '', 'Another valid step'];

      render(<ThinkingBlock thinking={thinking} />);

      fireEvent.press(screen.getByText('思考'));

      const steps = screen.getAllByTestId('markdown-content');
      expect(steps).toHaveLength(3);
    });
  });
});
