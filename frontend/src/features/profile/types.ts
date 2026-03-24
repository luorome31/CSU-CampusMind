export interface User {
  id: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface UsageStats {
  conversation_count: number;
  message_count: number;
  knowledge_base_count: number;
  join_date: string;
}

export interface Session {
  session_id: string;
  device: string;
  location: string;
  created_at: number;
  is_current: boolean;
}

export interface UpdateProfileData {
  display_name?: string;
  email?: string;
  phone?: string;
}
