/**
 * User/Profile 模块类型定义
 */

export interface UsageStats {
  conversation_count: number;
  message_count: number;
  knowledge_base_count: number;
  join_date: string;
}

export interface Session {
  session_id: string;
  device?: string;
  location?: string;
  created_at: string;
  is_current: boolean;
}
