/**
 * ToolGroup Component Tests
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { ToolGroup } from './ToolGroup';
import type { ToolEvent } from '../../../types/chat';

// Mock lucide-react-native icons
jest.mock('lucide-react-native', () => ({
  Wrench: () => null,
  ChevronDown: () => null,
  ChevronRight: () => null,
  ChevronUp: () => null,
  CheckCircle2: () => null,
  XCircle: () => null,
  RefreshCw: () => null,
}));

describe('ToolGroup Component', () => {
  const createMockEvent = (overrides: Partial<ToolEvent> = {}): ToolEvent => ({
    id: `event-${Math.random()}`,
    type: 'tool_call',
    name: 'TestTool',
    status: 'START',
    timestamp: '2024-01-01T00:00:00Z',
    ...overrides,
  });

  describe('Collapsed State (Default)', () => {
    it('should render header with label', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'END' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('调用工具')).toBeTruthy();
    });

    it('should show status text when collapsed', () => {
      const events = [createMockEvent({ status: 'END' })];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('1 个工具成功')).toBeTruthy();
    });

    it('should render nothing when events is empty', () => {
      render(<ToolGroup events={[]} />);

      expect(screen.queryByText('调用工具')).toBeNull();
    });
  });

  describe('Expanded State', () => {
    it('should expand when header is pressed', () => {
      const events = [createMockEvent({ name: 'LibrarySearch' })];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('调用工具'));

      expect(screen.getByText('LibrarySearch')).toBeTruthy();
    });

    it('should show all tool events when expanded', () => {
      const events = [
        createMockEvent({ id: '1', name: 'JWCSchedule' }),
        createMockEvent({ id: '2', name: 'LibrarySearch' }),
        createMockEvent({ id: '3', name: 'CareerInfo' }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('调用工具'));

      expect(screen.getByText('JWCSchedule')).toBeTruthy();
      expect(screen.getByText('LibrarySearch')).toBeTruthy();
      expect(screen.getByText('CareerInfo')).toBeTruthy();
    });

    it('should show status text for each tool when expanded', () => {
      const events = [createMockEvent({ status: 'START' })];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('调用工具'));

      expect(screen.getByText('进行中')).toBeTruthy();
    });
  });

  describe('Status Display', () => {
    it('should show correct count during progress', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'START' }),
        createMockEvent({ id: '3', status: 'START' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('调用工具 (1/3)')).toBeTruthy();
    });

    it('should show success message when all tools succeed', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'END' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('2 个工具成功')).toBeTruthy();
    });

    it('should show failure count when some tools fail', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'ERROR' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('1 个工具失败')).toBeTruthy();
    });
  });

  describe('Tool Details', () => {
    it('should show tool content when expanded', () => {
      const events = [
        createMockEvent({
          id: '1',
          input: { query: '图书馆' },
        }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('调用工具'));

      expect(screen.getByText(/"query": "图书馆"/)).toBeTruthy();
    });
  });

  describe('Toggle Behavior', () => {
    it('should collapse when header is pressed again', () => {
      const events = [createMockEvent({ name: 'TestTool' })];

      render(<ToolGroup events={events} />);

      // Expand
      fireEvent.press(screen.getByText('调用工具'));
      expect(screen.getByText('TestTool')).toBeTruthy();

      // Collapse
      fireEvent.press(screen.getByText('调用工具'));
      expect(screen.queryByText('TestTool')).toBeNull();
    });
  });
});
