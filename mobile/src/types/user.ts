/**
 * User/Profile 模块类型定义
 */

export interface UsageStats {
  dialog_count: number;
  message_count: number;
  knowledge_base_count: number;
  joined_at: string;
}

export interface Session {
  id: string;
  device?: string;
  location?: string;
  ip_address?: string;
  last_active_at: string;
  is_current: boolean;
}
