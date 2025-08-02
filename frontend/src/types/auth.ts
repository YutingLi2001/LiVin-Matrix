/**
 * 认证相关类型定义
 */

export interface User {
  id: number;
  github_user_id: number;
  github_username: string;
  email: string;
  name?: string;
  avatar_url?: string;
  bio?: string;
  location?: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
  error: string | null;
}

export interface GitHubAuthURLResponse {
  auth_url: string;
  state: string;
}

export interface GitHubCallbackData {
  code: string;
  state?: string;
}

export interface AuthError {
  error: string;
  error_description: string;
  error_code?: number;
}

export interface TokenInfo {
  user_id: number;
  github_user_id: number;
  jti: string;
  exp: number;
  iat: number;
  type: string;
}