/**
 * GitHub OAuth认证上下文
 */

import React, { createContext, useReducer, useEffect, ReactNode } from 'react';
import {
  AuthState,
  User,
  EmailLoginRequest,
  EmailRegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  VerifyEmailRequest,
  EmailAuthResponse,
} from '../types/auth';
import { authService } from '../services/authService';

// 认证状态的动作类型
type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_AUTHENTICATED'; payload: { user: User; token: string } }
  | { type: 'SET_UNAUTHENTICATED' }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_USER'; payload: User };

// 认证上下文类型
interface AuthContextType {
  state: AuthState;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  clearError: () => void;
  checkAuthStatus: () => Promise<void>;
  // 邮箱认证方法
  emailLogin: (loginData: EmailLoginRequest) => Promise<void>;
  emailRegister: (registerData: EmailRegisterRequest) => Promise<EmailAuthResponse>;
  verifyEmail: (verifyData: VerifyEmailRequest) => Promise<EmailAuthResponse>;
  forgotPassword: (forgotData: ForgotPasswordRequest) => Promise<EmailAuthResponse>;
  resetPassword: (resetData: ResetPasswordRequest) => Promise<EmailAuthResponse>;
}

// 初始状态
const initialState: AuthState = {
  isAuthenticated: false,
  isLoading: true,
  user: null,
  token: null,
  error: null,
};

// 状态reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_AUTHENTICATED':
      return {
        ...state,
        isAuthenticated: true,
        isLoading: false,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };
    case 'SET_UNAUTHENTICATED':
      return {
        ...state,
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null,
        error: null,
      };
    case 'SET_ERROR':
      return {
        ...state,
        isLoading: false,
        error: action.payload,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    default:
      return state;
  }
};

// 创建上下文
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider组件的Props
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // 检查认证状态
  const checkAuthStatus = async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      // 检查本地存储的认证信息
      if (authService.isAuthenticated()) {
        const user = authService.getLocalUser();
        const token = authService.getLocalToken();

        if (user && token) {
          dispatch({
            type: 'SET_AUTHENTICATED',
            payload: { user, token },
          });

          // 如果需要刷新令牌，在后台刷新
          if (authService.shouldRefreshToken()) {
            try {
              await refreshToken();
            } catch (error) {
              console.warn('Background token refresh failed:', error);
            }
          }
        } else {
          dispatch({ type: 'SET_UNAUTHENTICATED' });
        }
      } else {
        dispatch({ type: 'SET_UNAUTHENTICATED' });
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
      dispatch({ type: 'SET_UNAUTHENTICATED' });
    }
  };

  // 处理GitHub OAuth回调
  const handleGitHubCallback = async (): Promise<void> => {
    try {
      const callbackData = authService.parseCallbackFromURL();

      if (callbackData) {
        // 立即清理URL参数，防止重复使用OAuth code
        authService.cleanupCallbackURL();

        dispatch({ type: 'SET_LOADING', payload: true });

        const authResponse = await authService.handleGitHubCallback(callbackData);

        dispatch({
          type: 'SET_AUTHENTICATED',
          payload: {
            user: authResponse.user,
            token: authResponse.access_token,
          },
        });
      }
    } catch (error: any) {
      console.error('GitHub callback handling failed:', error);
      dispatch({
        type: 'SET_ERROR',
        payload: error.error_description || 'GitHub登录失败',
      });
    }
  };

  // 登录
  const login = async (): Promise<void> => {
    try {
      dispatch({ type: 'CLEAR_ERROR' });
      await authService.initiateGitHubLogin();
    } catch (error: any) {
      console.error('Login initiation failed:', error);
      dispatch({
        type: 'SET_ERROR',
        payload: error.error_description || '登录失败',
      });
    }
  };

  // 登出
  const logout = async (): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      await authService.logout();
      dispatch({ type: 'SET_UNAUTHENTICATED' });
    } catch (error: any) {
      console.error('Logout failed:', error);
      // 即使服务器端登出失败，也要清除本地状态
      dispatch({ type: 'SET_UNAUTHENTICATED' });
    }
  };

  // 刷新令牌
  const refreshToken = async (): Promise<void> => {
    try {
      const authResponse = await authService.refreshToken();

      dispatch({
        type: 'SET_AUTHENTICATED',
        payload: {
          user: authResponse.user,
          token: authResponse.access_token,
        },
      });
    } catch (error: any) {
      console.error('Token refresh failed:', error);
      dispatch({ type: 'SET_UNAUTHENTICATED' });
      throw error;
    }
  };

  // 清除错误
  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  // 邮箱认证方法

  // 邮箱登录
  const emailLogin = async (loginData: EmailLoginRequest): Promise<void> => {
    try {
      dispatch({ type: 'CLEAR_ERROR' });
      dispatch({ type: 'SET_LOADING', payload: true });

      const authResponse = await authService.emailLogin(loginData);

      dispatch({
        type: 'SET_AUTHENTICATED',
        payload: {
          user: authResponse.user,
          token: authResponse.access_token,
        },
      });
    } catch (error: any) {
      console.error('Email login failed:', error);
      dispatch({
        type: 'SET_ERROR',
        payload: error.error_description || '邮箱登录失败',
      });
    }
  };

  // 邮箱注册
  const emailRegister = async (registerData: EmailRegisterRequest): Promise<EmailAuthResponse> => {
    try {
      dispatch({ type: 'CLEAR_ERROR' });
      dispatch({ type: 'SET_LOADING', payload: true });

      const response = await authService.emailRegister(registerData);

      dispatch({ type: 'SET_LOADING', payload: false });
      return response;
    } catch (error: any) {
      console.error('Email registration failed:', error);
      dispatch({
        type: 'SET_ERROR',
        payload: error.error_description || '邮箱注册失败',
      });
      throw error;
    }
  };

  // 验证邮箱
  const verifyEmail = async (verifyData: VerifyEmailRequest): Promise<EmailAuthResponse> => {
    try {
      dispatch({ type: 'CLEAR_ERROR' });
      dispatch({ type: 'SET_LOADING', payload: true });

      const response = await authService.verifyEmail(verifyData);

      dispatch({ type: 'SET_LOADING', payload: false });
      return response;
    } catch (error: any) {
      console.error('Email verification failed:', error);
      dispatch({
        type: 'SET_ERROR',
        payload: error.error_description || '邮箱验证失败',
      });
      throw error;
    }
  };

  // 申请密码重置
  const forgotPassword = async (forgotData: ForgotPasswordRequest): Promise<EmailAuthResponse> => {
    try {
      dispatch({ type: 'CLEAR_ERROR' });
      dispatch({ type: 'SET_LOADING', payload: true });

      const response = await authService.forgotPassword(forgotData);

      dispatch({ type: 'SET_LOADING', payload: false });
      return response;
    } catch (error: any) {
      console.error('Forgot password request failed:', error);
      dispatch({
        type: 'SET_ERROR',
        payload: error.error_description || '申请密码重置失败',
      });
      throw error;
    }
  };

  // 重置密码
  const resetPassword = async (resetData: ResetPasswordRequest): Promise<EmailAuthResponse> => {
    try {
      dispatch({ type: 'CLEAR_ERROR' });
      dispatch({ type: 'SET_LOADING', payload: true });

      const response = await authService.resetPassword(resetData);

      dispatch({ type: 'SET_LOADING', payload: false });
      return response;
    } catch (error: any) {
      console.error('Password reset failed:', error);
      dispatch({
        type: 'SET_ERROR',
        payload: error.error_description || '密码重置失败',
      });
      throw error;
    }
  };

  // 组件挂载时检查认证状态和处理回调
  useEffect(() => {
    let isExecuted = false;

    const initializeAuth = async () => {
      if (isExecuted) return;
      isExecuted = true;

      // 检查是否是OAuth回调
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('code')) {
        await handleGitHubCallback();
      } else {
        await checkAuthStatus();
      }
    };

    initializeAuth();
  }, []);

  // 设置令牌刷新定时器
  useEffect(() => {
    if (!state.isAuthenticated || !state.token) {
      return;
    }

    const checkTokenRefresh = () => {
      if (authService.shouldRefreshToken()) {
        refreshToken().catch(console.error);
      }
    };

    // 每5分钟检查一次是否需要刷新令牌
    const intervalId = setInterval(checkTokenRefresh, 5 * 60 * 1000);

    return () => clearInterval(intervalId);
  }, [state.isAuthenticated, state.token]);

  const value: AuthContextType = {
    state,
    login,
    logout,
    refreshToken,
    clearError,
    checkAuthStatus,
    emailLogin,
    emailRegister,
    verifyEmail,
    forgotPassword,
    resetPassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// useAuth hook
export const useAuth = (): AuthContextType => {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
