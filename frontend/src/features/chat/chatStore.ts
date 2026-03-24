// src/features/chat/chatStore.ts
import { create } from 'zustand';
import { type Dialog } from '../../api/dialog';

export interface ToolEvent {
  id: string;
  status: 'START' | 'END' | 'ERROR';
  title: string;
  message: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  events: ToolEvent[];
  createdAt: Date;
}

interface ChatState {
  currentDialogId: string | null;
  currentKnowledgeIds: string[];
  enableRag: boolean;
  messages: ChatMessage[];
  isStreaming: boolean;
  toolEvents: ToolEvent[];
  dialogs: Dialog[];
}

interface ChatActions {
  setCurrentDialogId: (id: string | null) => void;
  setCurrentKnowledgeIds: (ids: string[]) => void;
  setEnableRag: (enabled: boolean) => void;
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
  loadDialog: (dialogId: string, dbMessages: any[]) => void;
}

type ChatStore = ChatState & ChatActions;

export const chatStore = create<ChatStore>((set) => ({
  currentDialogId: null,
  currentKnowledgeIds: [],
  enableRag: true,
  messages: [],
  isStreaming: false,
  toolEvents: [],
  dialogs: [],

  setCurrentDialogId: (id) => set({ currentDialogId: id }),

  setCurrentKnowledgeIds: (ids) => set({ currentKnowledgeIds: ids }),

  setEnableRag: (enabled) => set({ enableRag: enabled }),

  toggleRag: () => set((state) => ({ enableRag: !state.enableRag })),

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  updateStreamingMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      if (messages.length === 0) return state;

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
          message: event.message,
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
        const events = [...lastMsg.events ?? []];
        const existingIdx = events.findIndex((e) => e.id === event.id);
        if (existingIdx >= 0) {
          events[existingIdx] = {
            ...events[existingIdx],
            status: event.status,
            message: event.message,
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
          dialogs: state.dialogs.map((d) => (d.id === dialog.id ? { ...d, ...dialog } : d)),
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
        const parsed = JSON.parse(m.events) as ToolEvent[];
        // Merge events with same id (same as addToolEvent logic)
        for (const event of parsed) {
          const existingIdx = events.findIndex((e) => e.id === event.id);
          if (existingIdx >= 0) {
            events[existingIdx] = { ...events[existingIdx], ...event };
          } else {
            events.push(event);
          }
        }
      }
      return {
        id: m.id,
        role: m.role as 'user' | 'assistant',
        content: m.content,
        events,
        createdAt: new Date(m.created_at),
      };
    });
    set({ currentDialogId: dialogId, messages, toolEvents: [] });
  },
}));