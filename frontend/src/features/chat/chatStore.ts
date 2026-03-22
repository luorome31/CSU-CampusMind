// src/features/chat/chatStore.ts
import { create } from 'zustand';

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
  messages: ChatMessage[];
  isStreaming: boolean;
  toolEvents: ToolEvent[];
}

interface ChatActions {
  setCurrentDialogId: (id: string | null) => void;
  setCurrentKnowledgeIds: (ids: string[]) => void;
  addMessage: (msg: ChatMessage) => void;
  updateStreamingMessage: (content: string) => void;
  addToolEvent: (event: ToolEvent) => void;
  finishStreaming: () => void;
  clearMessages: () => void;
  setToolEvents: (events: ToolEvent[]) => void;
}

type ChatStore = ChatState & ChatActions;

export const chatStore = create<ChatStore>((set) => ({
  currentDialogId: null,
  currentKnowledgeIds: [],
  messages: [],
  isStreaming: false,
  toolEvents: [],

  setCurrentDialogId: (id) => set({ currentDialogId: id }),

  setCurrentKnowledgeIds: (ids) => set({ currentKnowledgeIds: ids }),

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
      // Update last assistant message's events if exists
      if (messages.length > 0 && messages[messages.length - 1].role === 'assistant') {
        messages[messages.length - 1] = {
          ...messages[messages.length - 1],
          events: [...messages[messages.length - 1].events, event],
        };
      }
      return {
        toolEvents: [...state.toolEvents, event],
        messages,
      };
    }),

  finishStreaming: () => set({ isStreaming: false }),

  clearMessages: () => set({ messages: [], toolEvents: [], currentDialogId: null }),

  setToolEvents: (events) => set({ toolEvents: events }),
}));