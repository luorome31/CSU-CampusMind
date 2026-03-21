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

let messageIdCounter = 0;
function generateId(): string {
  return `msg_${Date.now()}_${++messageIdCounter}`;
}

export const chatStore = create<ChatStore>((set, get) => ({
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
    set((state) => ({
      toolEvents: [...state.toolEvents, event],
    })),

  finishStreaming: () => set({ isStreaming: false }),

  clearMessages: () => set({ messages: [], toolEvents: [], currentDialogId: null }),

  setToolEvents: (events) => set({ toolEvents: events }),
}));