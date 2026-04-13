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
  user_id: string;
  username: string;
  nickname?: string;
  email?: string;
  phone?: string;
  avatar_url?: string;
  created_at?: string;
}
