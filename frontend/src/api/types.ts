export interface User {
  user_id: string;
  username: string;
  // Add other user fields as needed from backend response
}

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
  expires_in: number;
}
