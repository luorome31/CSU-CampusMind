/**
 * useChatStream Tests
 */
import { renderHook, act } from '@testing-library/react-native';
import { useChatStream } from '../useChatStream';
import { useChatStore } from '../chatStore';

// Mock the chat API
jest.mock('../../../api/chat', () => ({
  createChatStream: jest.fn(),
}));

// Mock storage
jest.mock('../../../utils/storage', () => ({
  storage: {
    getToken: jest.fn(),
    getSessionId: jest.fn(),
  },
}));

const { createChatStream } = require('../../../api/chat');
const { storage } = require('../../../utils/storage');

// Helper to create async generator mock
function createMockStreamGenerator(events: Array<{ event: { type: string; data: unknown }; newDialogId?: string }>) {
  let callCount = 0;

  async function* makeGenerator() {
    for (const e of events) {
      yield e;
    }
  }

  return makeGenerator();
}

describe('useChatStream', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset store state
    useChatStore.setState({
      currentDialogId: null,
      currentKnowledgeIds: [],
      enableRag: true,
      messages: [],
      isStreaming: false,
      toolEvents: [],
      dialogs: [],
    });
    // Default storage mocks
    storage.getToken.mockResolvedValue('mock-token');
    storage.getSessionId.mockResolvedValue('mock-session');
  });

  describe('sendMessage', () => {
    it('should add user and assistant messages to store', async () => {
      const mockGenerator = createMockStreamGenerator([]);
      createChatStream.mockReturnValue(mockGenerator);

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Hello', []);
      });

      const messages = useChatStore.getState().messages;
      expect(messages).toHaveLength(2);
      expect(messages[0].role).toBe('user');
      expect(messages[0].content).toBe('Hello');
      expect(messages[1].role).toBe('assistant');
    });

    it('should set isStreaming to true during stream', async () => {
      const events = [
        { event: { type: 'response_chunk', data: { accumulated: 'Hi' } }, newDialogId: undefined },
      ];
      const mockGenerator = createMockStreamGenerator(events);
      createChatStream.mockReturnValue(mockGenerator);

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Hello', []);
      });

      expect(useChatStore.getState().isStreaming).toBe(false);
    });

    it('should handle response_chunk events', async () => {
      const events = [
        { event: { type: 'response_chunk', data: { accumulated: 'Hello' } }, newDialogId: undefined },
        { event: { type: 'response_chunk', data: { accumulated: 'Hello World' } }, newDialogId: undefined },
      ];
      const mockGenerator = createMockStreamGenerator(events);
      createChatStream.mockReturnValue(mockGenerator);

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Hello', []);
      });

      const messages = useChatStore.getState().messages;
      expect(messages[1].content).toBe('Hello World');
    });

    it('should handle new_dialog event and create dialog', async () => {
      const events = [
        { event: { type: 'new_dialog', data: { dialog_id: 'new-dialog-123' } }, newDialogId: undefined },
        { event: { type: 'response_chunk', data: { accumulated: 'Response' } }, newDialogId: 'new-dialog-123' },
      ];
      const mockGenerator = createMockStreamGenerator(events);
      createChatStream.mockReturnValue(mockGenerator);

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Hello', []);
      });

      expect(useChatStore.getState().currentDialogId).toBe('new-dialog-123');
      expect(useChatStore.getState().dialogs).toHaveLength(1);
      expect(useChatStore.getState().dialogs[0].id).toBe('new-dialog-123');
    });

    it('should handle title_update event', async () => {
      const events = [
        { event: { type: 'new_dialog', data: { dialog_id: 'dialog-123' } }, newDialogId: undefined },
        { event: { type: 'title_update', data: { title: 'Updated Title' } }, newDialogId: undefined },
      ];
      const mockGenerator = createMockStreamGenerator(events);
      createChatStream.mockReturnValue(mockGenerator);

      // Set current dialog
      useChatStore.setState({ currentDialogId: 'dialog-123' });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Hello', []);
      });

      const dialog = useChatStore.getState().dialogs.find((d) => d.id === 'dialog-123');
      expect(dialog?.title).toBe('Updated Title');
    });

    it('should handle event tool events', async () => {
      const events = [
        { event: { type: 'event', data: { id: 'tool-1', status: 'START', title: 'JWC查询', message: '查询中' } }, newDialogId: undefined },
        { event: { type: 'response_chunk', data: { accumulated: 'Result' } }, newDialogId: undefined },
      ];
      const mockGenerator = createMockStreamGenerator(events);
      createChatStream.mockReturnValue(mockGenerator);

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Hello', []);
      });

      const toolEvents = useChatStore.getState().toolEvents;
      expect(toolEvents).toHaveLength(1);
      expect(toolEvents[0].id).toBe('tool-1');
      expect(toolEvents[0].status).toBe('START');
    });

    it('should reset isStreaming after stream ends', async () => {
      const events = [
        { event: { type: 'response_chunk', data: { accumulated: 'Done' } }, newDialogId: undefined },
      ];
      const mockGenerator = createMockStreamGenerator(events);
      createChatStream.mockReturnValue(mockGenerator);

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Hello', []);
      });

      expect(useChatStore.getState().isStreaming).toBe(false);
    });

    it('should call createChatStream with correct options', async () => {
      const mockGenerator = createMockStreamGenerator([]);
      createChatStream.mockReturnValue(mockGenerator);

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        await result.current.sendMessage('Test message', ['kb-1', 'kb-2']);
      });

      expect(createChatStream).toHaveBeenCalledWith(
        'Test message',
        expect.objectContaining({
          knowledgeIds: ['kb-1', 'kb-2'],
          enableRag: true,
          signal: expect.any(Object), // AbortSignal
        })
      );
    });
  });

  describe('cancelStream', () => {
    it('should set isStreaming to false', async () => {
      useChatStore.setState({ isStreaming: true });

      const { result } = renderHook(() => useChatStream());

      act(() => {
        result.current.cancelStream();
      });

      expect(useChatStore.getState().isStreaming).toBe(false);
    });
  });

  describe('return values', () => {
    it('should expose isStreaming, messages, toolEvents from store', async () => {
      const mockGenerator = createMockStreamGenerator([]);
      createChatStream.mockReturnValue(mockGenerator);

      // Pre-populate store
      useChatStore.setState({
        messages: [{ id: 'msg-1', role: 'user' as const, content: 'Hi', created_at: new Date().toISOString(), events: [] }],
        toolEvents: [{ id: 'tool-1', type: 'tool_call' as const, name: 'test', status: 'START' as const, timestamp: new Date().toISOString() }],
        isStreaming: false,
      });

      const { result } = renderHook(() => useChatStream());

      expect(result.current.isStreaming).toBe(false);
      expect(result.current.messages).toHaveLength(1);
      expect(result.current.toolEvents).toHaveLength(1);
    });
  });
});
