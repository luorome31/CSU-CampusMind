/**
 * ChatStore Tests
 */
import { renderHook, act } from '@testing-library/react-native';
import { useChatStore } from '../chatStore';
import type { ToolEvent, ChatMessage } from '../chatStore';

const createMsg = (overrides: Partial<ChatMessage> = {}): ChatMessage => ({
  id: 'msg-1',
  role: 'user',
  content: 'Hello',
  createdAt: new Date(),
  events: [],
  ...overrides,
});

const createToolEvent = (overrides: Partial<ToolEvent> = {}): ToolEvent => ({
  id: 'tool-1',
  type: 'tool_call',
  name: 'test_tool',
  status: 'START',
  timestamp: new Date().toISOString(),
  ...overrides,
});

describe('useChatStore', () => {
  beforeEach(() => {
    useChatStore.setState({
      currentDialogId: null,
      currentKnowledgeIds: [],
      enableRag: true,
      messages: [],
      isStreaming: false,
      toolEvents: [],
      dialogs: [],
    });
  });

  describe('initial state', () => {
    it('should have correct initial values', () => {
      const { result } = renderHook(() => useChatStore());
      expect(result.current.currentDialogId).toBeNull();
      expect(result.current.currentKnowledgeIds).toEqual([]);
      expect(result.current.enableRag).toBe(true);
      expect(result.current.messages).toEqual([]);
      expect(result.current.isStreaming).toBe(false);
      expect(result.current.toolEvents).toEqual([]);
      expect(result.current.dialogs).toEqual([]);
    });
  });

  describe('setCurrentDialogId', () => {
    it('should set current dialog id', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setCurrentDialogId('dialog-123');
      });
      expect(result.current.currentDialogId).toBe('dialog-123');
    });

    it('should set to null', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setCurrentDialogId('dialog-123');
        result.current.setCurrentDialogId(null);
      });
      expect(result.current.currentDialogId).toBeNull();
    });
  });

  describe('setCurrentKnowledgeIds', () => {
    it('should set knowledge ids', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setCurrentKnowledgeIds(['kb-1', 'kb-2']);
      });
      expect(result.current.currentKnowledgeIds).toEqual(['kb-1', 'kb-2']);
    });
  });

  describe('setEnableRag / toggleRag', () => {
    it('should set enableRag', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setEnableRag(false);
      });
      expect(result.current.enableRag).toBe(false);
    });

    it('should toggle enableRag', () => {
      const { result } = renderHook(() => useChatStore());
      expect(result.current.enableRag).toBe(true);
      act(() => {
        result.current.toggleRag();
      });
      expect(result.current.enableRag).toBe(false);
      act(() => {
        result.current.toggleRag();
      });
      expect(result.current.enableRag).toBe(true);
    });
  });

  describe('addMessage', () => {
    it('should append message to messages array', () => {
      const { result } = renderHook(() => useChatStore());
      const msg = createMsg({ id: 'msg-1', content: 'Hello' });
      act(() => {
        result.current.addMessage(msg);
      });
      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].id).toBe('msg-1');
    });

    it('should keep existing messages', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addMessage(createMsg({ id: 'msg-1' }));
        result.current.addMessage(createMsg({ id: 'msg-2' }));
      });
      expect(result.current.messages).toHaveLength(2);
    });
  });

  describe('updateStreamingMessage', () => {
    it('should update last assistant message content', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addMessage(createMsg({ id: 'msg-1', role: 'user', content: 'Hello' }));
        result.current.addMessage(createMsg({ id: 'msg-2', role: 'assistant', content: '' }));
      });
      act(() => {
        result.current.updateStreamingMessage('Streaming response...');
      });
      expect(result.current.messages[1].content).toBe('Streaming response...');
    });

    it('should not update if no messages', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.updateStreamingMessage('test');
      });
      expect(result.current.messages).toHaveLength(0);
    });

    it('should not update if last message is not assistant', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addMessage(createMsg({ id: 'msg-1', role: 'user', content: 'Hello' }));
      });
      act(() => {
        result.current.updateStreamingMessage('Should not update');
      });
      expect(result.current.messages[0].content).toBe('Hello');
    });
  });

  describe('addToolEvent', () => {
    it('should add tool event to global toolEvents', () => {
      const { result } = renderHook(() => useChatStore());
      const event = createToolEvent({ id: 'tool-1', name: 'jwc查询' });
      act(() => {
        result.current.addToolEvent(event);
      });
      expect(result.current.toolEvents).toHaveLength(1);
      expect(result.current.toolEvents[0].id).toBe('tool-1');
    });

    it('should update existing tool event by id', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addToolEvent(createToolEvent({ id: 'tool-1', status: 'START' }));
      });
      act(() => {
        result.current.addToolEvent(createToolEvent({ id: 'tool-1', status: 'END', output: { result: 'ok' } }));
      });
      expect(result.current.toolEvents).toHaveLength(1);
      expect(result.current.toolEvents[0].status).toBe('END');
      expect(result.current.toolEvents[0].output).toEqual({ result: 'ok' });
    });

    it('should also update last assistant message events', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addMessage(createMsg({ id: 'msg-1', role: 'assistant', events: [] }));
        result.current.addToolEvent(createToolEvent({ id: 'tool-1' }));
      });
      expect(result.current.messages[0].events).toHaveLength(1);
      expect(result.current.messages[0].events[0].id).toBe('tool-1');
    });
  });

  describe('finishStreaming', () => {
    it('should set isStreaming to false', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        useChatStore.setState({ isStreaming: true });
      });
      act(() => {
        result.current.finishStreaming();
      });
      expect(result.current.isStreaming).toBe(false);
    });
  });

  describe('clearMessages', () => {
    it('should clear messages, toolEvents and reset currentDialogId', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addMessage(createMsg({ id: 'msg-1' }));
        result.current.addToolEvent(createToolEvent({ id: 'tool-1' }));
        result.current.setCurrentDialogId('dialog-123');
      });
      act(() => {
        result.current.clearMessages();
      });
      expect(result.current.messages).toEqual([]);
      expect(result.current.toolEvents).toEqual([]);
      expect(result.current.currentDialogId).toBeNull();
    });
  });

  describe('setToolEvents', () => {
    it('should replace all tool events', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addToolEvent(createToolEvent({ id: 'tool-1' }));
      });
      act(() => {
        result.current.setToolEvents([createToolEvent({ id: 'tool-2' })]);
      });
      expect(result.current.toolEvents).toHaveLength(1);
      expect(result.current.toolEvents[0].id).toBe('tool-2');
    });
  });

  describe('setDialogs', () => {
    it('should replace dialogs', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setDialogs([{ id: 'd1', title: 'Dialog 1', updated_at: '2024-01-01' }]);
      });
      expect(result.current.dialogs).toHaveLength(1);
    });
  });

  describe('updateDialogTitle', () => {
    it('should update dialog title', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setDialogs([
          { id: 'd1', title: 'Old Title', updated_at: '2024-01-01' },
        ]);
      });
      act(() => {
        result.current.updateDialogTitle('d1', 'New Title');
      });
      expect(result.current.dialogs[0].title).toBe('New Title');
    });

    it('should do nothing if dialogId is null', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setDialogs([{ id: 'd1', title: 'Old', updated_at: '2024-01-01' }]);
      });
      act(() => {
        result.current.updateDialogTitle(null, 'New');
      });
      expect(result.current.dialogs[0].title).toBe('Old');
    });
  });

  describe('removeDialog', () => {
    it('should remove dialog from list', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setDialogs([
          { id: 'd1', title: 'Dialog 1', updated_at: '2024-01-01' },
          { id: 'd2', title: 'Dialog 2', updated_at: '2024-01-01' },
        ]);
      });
      act(() => {
        result.current.removeDialog('d1');
      });
      expect(result.current.dialogs).toHaveLength(1);
      expect(result.current.dialogs[0].id).toBe('d2');
    });

    it('should reset currentDialogId if removed dialog was active', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setDialogs([{ id: 'd1', title: 'Dialog 1', updated_at: '2024-01-01' }]);
        result.current.setCurrentDialogId('d1');
      });
      act(() => {
        result.current.removeDialog('d1');
      });
      expect(result.current.currentDialogId).toBeNull();
    });
  });

  describe('upsertDialog', () => {
    it('should add new dialog to top of list', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.upsertDialog({ id: 'd1', title: 'Dialog 1', updated_at: '2024-01-01' });
      });
      expect(result.current.dialogs).toHaveLength(1);
      expect(result.current.dialogs[0].id).toBe('d1');
    });

    it('should update existing dialog', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.setDialogs([{ id: 'd1', title: 'Old', updated_at: '2024-01-01' }]);
        result.current.upsertDialog({ id: 'd1', title: 'Updated', updated_at: '2024-01-02' });
      });
      expect(result.current.dialogs).toHaveLength(1);
      expect(result.current.dialogs[0].title).toBe('Updated');
    });
  });

  describe('loadDialog', () => {
    it('should load messages and set currentDialogId', () => {
      const { result } = renderHook(() => useChatStore());
      const dbMessages = [
        {
          id: 'msg-1',
          role: 'user',
          content: 'Hello',
          created_at: '2024-01-01T10:00:00Z',
          events: null,
        },
        {
          id: 'msg-2',
          role: 'assistant',
          content: 'Hi there',
          created_at: '2024-01-01T10:01:00Z',
          events: null,
        },
      ];
      act(() => {
        result.current.loadDialog('dialog-123', dbMessages);
      });
      expect(result.current.currentDialogId).toBe('dialog-123');
      expect(result.current.messages).toHaveLength(2);
      expect(result.current.messages[0].content).toBe('Hello');
      expect(result.current.messages[0].createdAt).toBeInstanceOf(Date);
    });

    it('should parse and merge tool events from db', () => {
      const { result } = renderHook(() => useChatStore());
      const dbMessages = [
        {
          id: 'msg-1',
          role: 'assistant',
          content: 'Using tools',
          created_at: '2024-01-01T10:00:00Z',
          events: JSON.stringify([
            { id: 'tool-1', status: 'START', type: 'tool_call', name: 'jwc', timestamp: '2024-01-01T10:00:00Z' },
            { id: 'tool-1', status: 'END', type: 'tool_result', name: 'jwc', output: { data: 'grade' }, timestamp: '2024-01-01T10:00:01Z' },
          ]),
        },
      ];
      act(() => {
        result.current.loadDialog('dialog-123', dbMessages);
      });
      // Should merge events with same id
      expect(result.current.messages[0].events).toHaveLength(1);
      expect(result.current.messages[0].events[0].status).toBe('END');
      expect(result.current.messages[0].events[0].output).toEqual({ data: 'grade' });
    });

    it('should clear toolEvents on load', () => {
      const { result } = renderHook(() => useChatStore());
      act(() => {
        result.current.addToolEvent(createToolEvent({ id: 'old-tool' }));
      });
      act(() => {
        result.current.loadDialog('dialog-123', []);
      });
      expect(result.current.toolEvents).toHaveLength(0);
    });
  });
});
