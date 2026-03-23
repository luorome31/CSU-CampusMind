import { describe, it, expect, beforeEach } from 'vitest';
import { chatStore, type ChatMessage, type ToolEvent } from './chatStore';

describe('chatStore', () => {
  beforeEach(() => {
    chatStore.setState({
      currentDialogId: null,
      currentKnowledgeIds: [],
      messages: [],
      isStreaming: false,
      toolEvents: [],
    });
  });

  describe('initial state', () => {
    it('has null currentDialogId', () => {
      expect(chatStore.getState().currentDialogId).toBeNull();
    });

    it('has empty currentKnowledgeIds', () => {
      expect(chatStore.getState().currentKnowledgeIds).toEqual([]);
    });

    it('has empty messages', () => {
      expect(chatStore.getState().messages).toEqual([]);
    });

    it('has isStreaming false', () => {
      expect(chatStore.getState().isStreaming).toBe(false);
    });

    it('has empty toolEvents', () => {
      expect(chatStore.getState().toolEvents).toEqual([]);
    });
  });

  describe('setCurrentDialogId', () => {
    it('sets the current dialog ID', () => {
      chatStore.getState().setCurrentDialogId('dialog-123');
      expect(chatStore.getState().currentDialogId).toBe('dialog-123');
    });

    it('can set to null', () => {
      chatStore.setState({ currentDialogId: 'dialog-123' });
      chatStore.getState().setCurrentDialogId(null);
      expect(chatStore.getState().currentDialogId).toBeNull();
    });
  });

  describe('setCurrentKnowledgeIds', () => {
    it('sets the knowledge IDs', () => {
      chatStore.getState().setCurrentKnowledgeIds(['kb-1', 'kb-2']);
      expect(chatStore.getState().currentKnowledgeIds).toEqual(['kb-1', 'kb-2']);
    });

    it('can set to empty array', () => {
      chatStore.setState({ currentKnowledgeIds: ['kb-1'] });
      chatStore.getState().setCurrentKnowledgeIds([]);
      expect(chatStore.getState().currentKnowledgeIds).toEqual([]);
    });
  });

  describe('addMessage', () => {
    it('adds a message to the messages array', () => {
      const message: ChatMessage = {
        id: 'msg-1',
        role: 'user',
        content: 'Hello',
        events: [],
        createdAt: new Date(),
      };

      chatStore.getState().addMessage(message);
      expect(chatStore.getState().messages).toHaveLength(1);
      expect(chatStore.getState().messages[0]).toEqual(message);
    });

    it('appends to existing messages', () => {
      const message1: ChatMessage = {
        id: 'msg-1',
        role: 'user',
        content: 'First',
        events: [],
        createdAt: new Date(),
      };
      const message2: ChatMessage = {
        id: 'msg-2',
        role: 'assistant',
        content: 'Second',
        events: [],
        createdAt: new Date(),
      };

      chatStore.getState().addMessage(message1);
      chatStore.getState().addMessage(message2);

      expect(chatStore.getState().messages).toHaveLength(2);
    });
  });

  describe('updateStreamingMessage', () => {
    it('updates the content of the last assistant message', () => {
      const userMsg: ChatMessage = {
        id: 'msg-1',
        role: 'user',
        content: 'Hello',
        events: [],
        createdAt: new Date(),
      };
      const assistantMsg: ChatMessage = {
        id: 'msg-2',
        role: 'assistant',
        content: 'Hi',
        events: [],
        createdAt: new Date(),
      };

      chatStore.setState({ messages: [userMsg, assistantMsg] });
      chatStore.getState().updateStreamingMessage('Hi there!');

      expect(chatStore.getState().messages[1].content).toBe('Hi there!');
    });

    it('does nothing if there are no messages', () => {
      chatStore.getState().updateStreamingMessage('Hello');
      expect(chatStore.getState().messages).toHaveLength(0);
    });

    it('does nothing if last message is not assistant', () => {
      const userMsg: ChatMessage = {
        id: 'msg-1',
        role: 'user',
        content: 'Hello',
        events: [],
        createdAt: new Date(),
      };

      chatStore.setState({ messages: [userMsg] });
      chatStore.getState().updateStreamingMessage('Hello there');

      expect(chatStore.getState().messages[0].content).toBe('Hello');
    });
  });

  describe('addToolEvent', () => {
    it('adds a tool event to the toolEvents array', () => {
      const event: ToolEvent = {
        id: 'event-1',
        status: 'START',
        title: 'Query JWC',
        message: 'Starting...',
      };

      chatStore.getState().addToolEvent(event);
      expect(chatStore.getState().toolEvents).toHaveLength(1);
      expect(chatStore.getState().toolEvents[0]).toEqual(event);
    });
  });

  describe('finishStreaming', () => {
    it('sets isStreaming to false', () => {
      chatStore.setState({ isStreaming: true });
      chatStore.getState().finishStreaming();
      expect(chatStore.getState().isStreaming).toBe(false);
    });
  });

  describe('clearMessages', () => {
    it('clears all messages', () => {
      const message: ChatMessage = {
        id: 'msg-1',
        role: 'user',
        content: 'Hello',
        events: [],
        createdAt: new Date(),
      };

      chatStore.setState({ messages: [message] });
      chatStore.getState().clearMessages();

      expect(chatStore.getState().messages).toHaveLength(0);
    });

    it('clears all toolEvents', () => {
      const event: ToolEvent = {
        id: 'event-1',
        status: 'START',
        title: 'Query JWC',
        message: 'Starting...',
      };

      chatStore.setState({ toolEvents: [event] });
      chatStore.getState().clearMessages();

      expect(chatStore.getState().toolEvents).toHaveLength(0);
    });

    it('sets currentDialogId to null', () => {
      chatStore.setState({ currentDialogId: 'dialog-123' });
      chatStore.getState().clearMessages();

      expect(chatStore.getState().currentDialogId).toBeNull();
    });
  });

  describe('setToolEvents', () => {
    it('replaces toolEvents array', () => {
      const events: ToolEvent[] = [
        { id: 'event-1', status: 'START', title: 'Query 1', message: 'Starting...' },
        { id: 'event-2', status: 'END', title: 'Query 2', message: 'Done' },
      ];

      chatStore.getState().setToolEvents(events);
      expect(chatStore.getState().toolEvents).toEqual(events);
    });
  });

  describe('dialog management', () => {
    const mockDialogs = [
      { id: 'd1', title: 'Dialog 1', updated_at: '2024-01-01T00:00:00Z' },
      { id: 'd2', title: 'Dialog 2', updated_at: '2024-01-01T01:00:00Z' },
    ];

    it('sets dialogs', () => {
      chatStore.getState().setDialogs(mockDialogs);
      expect(chatStore.getState().dialogs).toEqual(mockDialogs);
    });

    it('updates dialog title', () => {
      chatStore.setState({ dialogs: mockDialogs });
      chatStore.getState().updateDialogTitle('d1', 'New Title');
      expect(chatStore.getState().dialogs[0].title).toBe('New Title');
    });

    it('removes dialog', () => {
      chatStore.setState({ dialogs: mockDialogs, currentDialogId: 'd1' });
      chatStore.getState().removeDialog('d1');
      expect(chatStore.getState().dialogs).toHaveLength(1);
      expect(chatStore.getState().currentDialogId).toBeNull();
    });

    it('loads dialog messages', () => {
      const dbMessages = [
        { id: 'm1', role: 'user', content: 'Hello', created_at: '2024-01-01T00:00:00Z' },
      ];
      chatStore.getState().loadDialog('d1', dbMessages);
      expect(chatStore.getState().currentDialogId).toBe('d1');
      expect(chatStore.getState().messages).toHaveLength(1);
      expect(chatStore.getState().messages[0].content).toBe('Hello');
    });
  });
});
