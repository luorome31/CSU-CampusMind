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
      createChatStream.mockReturnValue({ abort: jest.fn() });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Hello', []);
      });

      const messages = useChatStore.getState().messages;
      expect(messages).toHaveLength(2);
      expect(messages[0].role).toBe('user');
      expect(messages[0].content).toBe('Hello');
      expect(messages[1].role).toBe('assistant');
    });

    it('should set isStreaming to true during stream and handle callbacks', async () => {
      let callbacks: any;
      createChatStream.mockImplementation((msg: string, opt: any, cb: any) => {
        callbacks = cb;
        return { abort: jest.fn() };
      });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Hello', []);
      });

      expect(useChatStore.getState().isStreaming).toBe(true);

      await act(async () => {
        callbacks.onChunk('Hi');
        callbacks.onEvent('response_chunk', { data: { chunk: 'Hi' } });
      });

      expect(useChatStore.getState().messages[1].content).toBe('Hi');

      await act(async () => {
        callbacks.onDone();
      });

      expect(useChatStore.getState().isStreaming).toBe(false);
    });

    it('should handle response_chunk events', async () => {
      let callbacks: any;
      createChatStream.mockImplementation((msg: string, opt: any, cb: any) => {
        callbacks = cb;
        return { abort: jest.fn() };
      });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Hello', []);
      });

      await act(async () => {
        callbacks.onEvent('response_chunk', { data: { chunk: 'Hello', accumulated: 'Hello' } });
        callbacks.onEvent('response_chunk', { data: { chunk: ' World', accumulated: 'Hello World' } });
      });

      const messages = useChatStore.getState().messages;
      expect(messages[1].content).toBe('Hello World');
    });

    it('should handle new_dialog event and create dialog', async () => {
      let callbacks: any;
      createChatStream.mockImplementation((msg: string, opt: any, cb: any) => {
        callbacks = cb;
        return { abort: jest.fn() };
      });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Hello', []);
      });

      await act(async () => {
        callbacks.onNewDialog('new-dialog-123');
      });

      expect(useChatStore.getState().currentDialogId).toBe('new-dialog-123');
      expect(useChatStore.getState().dialogs).toHaveLength(1);
      expect(useChatStore.getState().dialogs[0].id).toBe('new-dialog-123');
    });

    it('should handle title_update event', async () => {
      let callbacks: any;
      createChatStream.mockImplementation((msg: string, opt: any, cb: any) => {
        callbacks = cb;
        return { abort: jest.fn() };
      });

      // Set current dialog
      useChatStore.setState({ 
        currentDialogId: 'dialog-123',
        dialogs: [{ id: 'dialog-123', title: 'Old Title', updated_at: '' }]
      });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Hello', []);
      });

      await act(async () => {
        callbacks.onTitleUpdate('Updated Title');
      });

      const dialog = useChatStore.getState().dialogs.find((d) => d.id === 'dialog-123');
      expect(dialog?.title).toBe('Updated Title');
    });

    it('should handle event tool events', async () => {
      let callbacks: any;
      createChatStream.mockImplementation((msg: string, opt: any, cb: any) => {
        callbacks = cb;
        return { abort: jest.fn() };
      });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Hello', []);
      });

      await act(async () => {
        callbacks.onEvent('event', { data: { id: 'tool-1', status: 'START', title: 'JWC查询', message: '查询中' } });
      });

      const toolEvents = useChatStore.getState().toolEvents;
      expect(toolEvents).toHaveLength(1);
      expect(toolEvents[0].id).toBe('tool-1');
      expect(toolEvents[0].status).toBe('START');
    });

    it('should call createChatStream with correct options', async () => {
      createChatStream.mockReturnValue({ abort: jest.fn() });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Test message', ['kb-1', 'kb-2']);
      });

      expect(createChatStream).toHaveBeenCalledWith(
        'Test message',
        expect.objectContaining({
          knowledgeIds: ['kb-1', 'kb-2'],
          enableRag: true,
        }),
        expect.any(Object) // callbacks
      );
    });
  });

  describe('cancelStream', () => {
    it('should set isStreaming to false and call abort', async () => {
      const abort = jest.fn();
      createChatStream.mockReturnValue({ abort });
      useChatStore.setState({ isStreaming: true });

      const { result } = renderHook(() => useChatStream());

      await act(async () => {
        result.current.sendMessage('Hello', []);
      });

      act(() => {
        result.current.cancelStream();
      });

      expect(useChatStore.getState().isStreaming).toBe(false);
      expect(abort).toHaveBeenCalled();
    });
  });

  describe('return values', () => {
    it('should expose isStreaming, messages, toolEvents from store', async () => {
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
