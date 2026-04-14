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
}));

describe('ToolGroup Component', () => {
  const createMockEvent = (overrides: Partial<ToolEvent> = {}): ToolEvent => ({
    id: 'event-1',
    type: 'tool_call',
    name: 'TestTool',
    status: 'START',
    timestamp: '2024-01-01T00:00:00Z',
    ...overrides,
  });

  describe('Collapsed State (Default)', () => {
    it('should render header with tool count', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'END' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('工具调用')).toBeTruthy();
    });

    it('should show expand hint when collapsed', () => {
      const events = [createMockEvent({ status: 'END' })];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('查看详情')).toBeTruthy();
    });

    it('should not show tool details when collapsed', () => {
      const events = [createMockEvent({ name: 'BookSearch' })];

      render(<ToolGroup events={events} />);

      expect(screen.queryByText('BookSearch')).toBeNull();
    });

    it('should render nothing when events is empty', () => {
      render(<ToolGroup events={[]} />);

      expect(screen.queryByText('工具调用')).toBeNull();
      expect(screen.queryByText('查看详情')).toBeNull();
    });
  });

  describe('Expanded State', () => {
    it('should expand when expand hint is pressed', () => {
      const events = [createMockEvent({ name: 'LibrarySearch' })];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('LibrarySearch')).toBeTruthy();
    });

    it('should show all tool events when expanded', () => {
      const events = [
        createMockEvent({ id: '1', name: 'JWCSchedule' }),
        createMockEvent({ id: '2', name: 'LibrarySearch' }),
        createMockEvent({ id: '3', name: 'CareerInfo' }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('JWCSchedule')).toBeTruthy();
      expect(screen.getByText('LibrarySearch')).toBeTruthy();
      expect(screen.getByText('CareerInfo')).toBeTruthy();
    });

    it('should show collapse button when expanded', () => {
      const events = [createMockEvent()];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('收起')).toBeTruthy();
    });

    it('should show status icon for each tool', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'ERROR' }),
        createMockEvent({ id: '3', status: 'START' }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('成功')).toBeTruthy();
      expect(screen.getByText('失败')).toBeTruthy();
      expect(screen.getByText('进行中')).toBeTruthy();
    });
  });

  describe('Status Display', () => {
    it('should show "正在准备工具..." when no events', () => {
      render(<ToolGroup events={[]} />);

      // Component renders nothing when events is empty
      expect(screen.queryByText('正在准备工具...')).toBeNull();
    });

    it('should show correct count during progress', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'START' }),
        createMockEvent({ id: '3', status: 'START' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('正在调用工具 (1/3)...')).toBeTruthy();
    });

    it('should show success message when all tools succeed', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'END' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('成功调用了 2 个工具')).toBeTruthy();
    });

    it('should show failure count when some tools fail', () => {
      const events = [
        createMockEvent({ id: '1', status: 'END' }),
        createMockEvent({ id: '2', status: 'ERROR' }),
      ];

      render(<ToolGroup events={events} />);

      expect(screen.getByText('调用了 2 个工具 (1 个失败)')).toBeTruthy();
    });
  });

  describe('Tool Details', () => {
    it('should show input when provided', () => {
      const events = [
        createMockEvent({
          id: '1',
          input: { query: '图书馆', type: 'book' },
        }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('输入:')).toBeTruthy();
    });

    it('should show output when provided', () => {
      const events = [
        createMockEvent({
          id: '1',
          output: { books: [{ title: '测试书籍' }] },
        }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('输出:')).toBeTruthy();
    });

    it('should show error when provided', () => {
      const events = [
        createMockEvent({
          id: '1',
          status: 'ERROR',
          error: 'Network timeout',
        }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('错误:')).toBeTruthy();
      expect(screen.getByText('Network timeout')).toBeTruthy();
    });

    it('should not show input/output sections when empty', () => {
      const events = [
        createMockEvent({
          id: '1',
          input: {},
          output: {},
        }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.queryByText('输入:')).toBeNull();
      expect(screen.queryByText('输出:')).toBeNull();
    });
  });

  describe('Toggle Behavior', () => {
    it('should collapse when collapse button is pressed', () => {
      const events = [createMockEvent({ name: 'TestTool' })];

      render(<ToolGroup events={events} />);

      // Expand
      fireEvent.press(screen.getByText('查看详情'));
      expect(screen.getByText('TestTool')).toBeTruthy();

      // Collapse
      fireEvent.press(screen.getByText('收起'));
      expect(screen.queryByText('TestTool')).toBeNull();
    });

    it('should re-expand when expand hint is pressed after collapse', () => {
      const events = [createMockEvent({ name: 'TestTool' })];

      render(<ToolGroup events={events} />);

      // Expand
      fireEvent.press(screen.getByText('查看详情'));
      expect(screen.getByText('TestTool')).toBeTruthy();

      // Collapse
      fireEvent.press(screen.getByText('收起'));
      expect(screen.queryByText('TestTool')).toBeNull();

      // Re-expand
      fireEvent.press(screen.getByText('查看详情'));
      expect(screen.getByText('TestTool')).toBeTruthy();
    });
  });

  describe('Edge Cases', () => {
    it('should handle single tool', () => {
      const events = [createMockEvent({ id: '1', name: 'OnlyTool' })];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('OnlyTool')).toBeTruthy();
    });

    it('should handle many tools', () => {
      const events = Array.from({ length: 10 }, (_, i) =>
        createMockEvent({ id: String(i), name: `Tool${i + 1}` })
      );

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('Tool1')).toBeTruthy();
      expect(screen.getByText('Tool10')).toBeTruthy();
    });

    it('should handle events with no input/output/error', () => {
      const events = [
        createMockEvent({
          id: '1',
          input: undefined,
          output: undefined,
          error: undefined,
        }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      // Just shows the tool with status
      expect(screen.getByText('TestTool')).toBeTruthy();
      expect(screen.getByText('进行中')).toBeTruthy();
    });

    it('should handle tool name with special characters', () => {
      const events = [
        createMockEvent({ name: 'JWC_Grade_Lookup_v2' }),
      ];

      render(<ToolGroup events={events} />);

      fireEvent.press(screen.getByText('查看详情'));

      expect(screen.getByText('JWC_Grade_Lookup_v2')).toBeTruthy();
    });
  });
});
