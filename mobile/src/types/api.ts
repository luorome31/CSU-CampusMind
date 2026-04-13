/**
 * 全局 API 类型定义
 */

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

export interface LoginResponse {
  token: string;
  user_id: string;
  session_id: string;
  expires_in: number;
}

export interface User {
  id: string;
  username: string;
  display_name?: string;
  email?: string;
  phone?: string;
  avatar_url?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}
