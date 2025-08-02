/**
 * 认证相关的React Hooks
 */

import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import { AuthState, User } from '../types/auth';

/**
 * 使用认证上下文的Hook
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

/**
 * 获取认证状态的Hook
 */
export const useAuthState = (): AuthState => {
  const { state } = useAuth();
  return state;
};

/**
 * 获取当前用户的Hook
 */
export const useCurrentUser = (): User | null => {
  const { state } = useAuth();
  return state.user;
};

/**
 * 检查是否已认证的Hook
 */
export const useIsAuthenticated = (): boolean => {
  const { state } = useAuth();
  return state.isAuthenticated;
};

/**
 * 检查是否正在加载的Hook
 */
export const useIsLoading = (): boolean => {
  const { state } = useAuth();
  return state.isLoading;
};

/**
 * 获取认证错误的Hook
 */
export const useAuthError = (): string | null => {
  const { state } = useAuth();
  return state.error;
};

/**
 * 认证操作的Hook
 */
export const useAuthActions = () => {
  const { login, logout, refreshToken, clearError, checkAuthStatus } = useAuth();
  
  return {
    login,
    logout,
    refreshToken,
    clearError,
    checkAuthStatus,
  };
};