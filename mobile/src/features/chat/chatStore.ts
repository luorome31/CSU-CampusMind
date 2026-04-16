/**
 * ChatStore - 聊天状态管理
 */
import { create } from 'zustand';
import type { Dialog } from '../../api/dialog';

/**
 * Tool event types matching mobile API
 */
export interface ToolEvent {
  id: string;
  type: 'tool_call' | 'tool_result' | 'tool_error';
  name: string;
  status: 'START' | 'END' | 'ERROR';
  input?: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  timestamp: string;
}

/**
 * Chat message type for store internal use
 * Note: events is internal for SSE streaming, distinct from citations in API response
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  events: ToolEvent[];
}

interface ChatState {
  currentDialogId: string | null;
  currentKnowledgeIds: string[];
  enableRag: boolean;
  messages: ChatMessage[];
  isStreaming: boolean;
  isLoadingHistory: boolean;
  toolEvents: ToolEvent[];
  dialogs: Dialog[];
}

interface ChatActions {
  setCurrentDialogId: (id: string | null) => void;
  setCurrentKnowledgeIds: (ids: string[]) => void;
  setEnableRag: (enabled: boolean) => void;
  setIsLoadingHistory: (loading: boolean) => void;
  toggleRag: () => void;
  addMessage: (msg: ChatMessage) => void;
  updateStreamingMessage: (content: string) => void;
  addToolEvent: (event: ToolEvent) => void;
  finishStreaming: () => void;
  clearMessages: () => void;
  setToolEvents: (events: ToolEvent[]) => void;
  setDialogs: (dialogs: Dialog[]) => void;
  updateDialogTitle: (dialogId: string | null, title: string) => void;
  removeDialog: (dialogId: string) => void;
  upsertDialog: (dialog: Dialog) => void;
  loadDialog: (dialogId: string, dbMessages: DbMessage[]) => void;
}

/**
 * Database message type for loading dialogs from persistence
 */
interface DbMessage {
  id: string;
  role: string;
  content: string;
  created_at: string;
  events?: string;
}

type ChatStore = ChatState & ChatActions;

export const useChatStore = create<ChatStore>((set) => ({
  currentDialogId: null,
  currentKnowledgeIds: [],
  enableRag: true,
  messages: [],
  isStreaming: false,
  isLoadingHistory: false,
  toolEvents: [],
  dialogs: [],

  setCurrentDialogId: (id) => set({ currentDialogId: id }),

  setCurrentKnowledgeIds: (ids) => set({ currentKnowledgeIds: ids }),

  setEnableRag: (enabled) => set({ enableRag: enabled }),

  setIsLoadingHistory: (loading) => set({ isLoadingHistory: loading }),

  toggleRag: () => set((state) => ({ enableRag: !state.enableRag })),

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  updateStreamingMessage: (content) =>
    set((state) => {
      if (state.messages.length === 0) return state;

      // Get copy BEFORE modifying
      const messages = [...state.messages];
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.role !== 'assistant') return state;

      messages[messages.length - 1] = {
        ...lastMsg,
        content,
      };
      return { messages };
    }),

  addToolEvent: (event) =>
    set((state) => {
      const messages = [...state.messages];
      const globalEvents = [...state.toolEvents];
      const globalIdx = globalEvents.findIndex((e) => e.id === event.id);
      if (globalIdx >= 0) {
        globalEvents[globalIdx] = {
          ...globalEvents[globalIdx],
          status: event.status,
          output: event.output,
          error: event.error,
        };
      } else {
        globalEvents.push(event);
      }

      // Also update last assistant message's events if exists
      if (
        messages.length > 0 &&
        messages[messages.length - 1].role === 'assistant'
      ) {
        const lastMsg = { ...messages[messages.length - 1] };
        const events = [...lastMsg.events];
        const existingIdx = events.findIndex((e) => e.id === event.id);
        if (existingIdx >= 0) {
          events[existingIdx] = {
            ...events[existingIdx],
            status: event.status,
            output: event.output,
            error: event.error,
          };
        } else {
          events.push(event);
        }
        lastMsg.events = events;
        messages[messages.length - 1] = lastMsg;
        return { toolEvents: globalEvents, messages };
      }

      return { toolEvents: globalEvents };
    }),

  finishStreaming: () => set({ isStreaming: false }),

  clearMessages: () =>
    set({ messages: [], toolEvents: [], currentDialogId: null }),

  setToolEvents: (events) => set({ toolEvents: events }),

  setDialogs: (dialogs) => set({ dialogs }),

  updateDialogTitle: (dialogId, title) =>
    set((state) => {
      if (!dialogId) return state;
      const updatedDialogs = state.dialogs.map((d) =>
        d.id === dialogId ? { ...d, title } : d
      );
      return { dialogs: updatedDialogs };
    }),

  removeDialog: (dialogId) =>
    set((state) => ({
      dialogs: state.dialogs.filter((d) => d.id !== dialogId),
      currentDialogId:
        state.currentDialogId === dialogId ? null : state.currentDialogId,
      messages: state.currentDialogId === dialogId ? [] : state.messages,
    })),

  upsertDialog: (dialog: Dialog) => {
    set((state) => {
      const exists = state.dialogs.some((d) => d.id === dialog.id);
      if (exists) {
        return {
          dialogs: state.dialogs.map((d) =>
            d.id === dialog.id ? { ...d, ...dialog } : d
          ),
        };
      }
      return {
        dialogs: [dialog, ...state.dialogs],
      };
    });
  },

  loadDialog: (dialogId, dbMessages) => {
    const messages: ChatMessage[] = dbMessages.map((m) => {
      let events: ToolEvent[] = [];
      if (m.events) {
        try {
          const rawEvents = JSON.parse(m.events) as any[];
          // Merge events with same id (same as addToolEvent logic)
          for (const raw of rawEvents) {
            const mapped: ToolEvent = {
              id: raw.id || `tool_${Date.now()}_${Math.random()}`,
              type: raw.type || 'tool_call',
              name: raw.name || raw.title || 'Unknown Tool',
              status: raw.status || 'START',
              timestamp: raw.timestamp || m.created_at,
            };

            // Parse message string into input/output where possible
            if (raw.message && typeof raw.message === 'string') {
              if (raw.status === 'START') {
                try {
                  mapped.input = JSON.parse(raw.message);
                } catch {
                  mapped.input = { content: raw.message };
                }
              } else if (raw.status === 'END') {
                mapped.output = { content: raw.message };
              }
            }

            // Prefer existing fields if they exist
            if (raw.input) mapped.input = raw.input;
            if (raw.output) mapped.output = raw.output;
            if (raw.error) mapped.error = raw.error;

            const existingIdx = events.findIndex((e) => e.id === mapped.id);
            if (existingIdx >= 0) {
              events[existingIdx] = { ...events[existingIdx], ...mapped };
            } else {
              events.push(mapped);
            }
          }
        } catch {
          // Handle malformed JSON gracefully
          events = [];
        }
      }
      return {
        id: m.id,
        role: m.role as 'user' | 'assistant' | 'system',
        content: m.content,
        events,
        created_at: m.created_at,
      };
    });
    set({ currentDialogId: dialogId, messages, toolEvents: [] });
  },
}));
