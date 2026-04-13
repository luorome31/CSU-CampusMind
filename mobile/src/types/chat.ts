/**
 * Chat 模块类型定义
 */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  citations?: Citation[];
}

export interface Citation {
  index: number;
  document_id: string;
  text: string;
  score: number;
}

export interface Dialog {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

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

export interface ThinkingBlock {
  id: string;
  content: string;
  reasoning?: string;
}

export interface StreamChunk {
  type: 'message' | 'thinking' | 'tool_event' | 'citation' | 'done' | 'error';
  data: unknown;
}
