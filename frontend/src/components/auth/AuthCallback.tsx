/**
 * GitHub OAuth回调处理组件
 */

import React, { useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';

interface AuthCallbackProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

const AuthCallback: React.FC<AuthCallbackProps> = ({ onSuccess, onError }) => {
  const { state } = useAuth();

  useEffect(() => {
    // 认证成功后的处理
    if (state.isAuthenticated && state.user && !state.isLoading) {
      console.log('OAuth callback successful, user authenticated:', state.user);
      onSuccess?.();
    }

    // 认证失败后的处理
    if (state.error && !state.isLoading) {
      console.error('OAuth callback failed:', state.error);
      onError?.(state.error);
    }
  }, [state.isAuthenticated, state.user, state.error, state.isLoading, onSuccess, onError]);

  // 加载状态
  if (state.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 flex items-center justify-center">
              <svg
                className="animate-spin h-8 w-8 text-blue-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">正在登录...</h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              正在处理GitHub OAuth认证，请稍候
            </p>
          </div>
        </div>
      </div>
    );
  }

  // 错误状态
  if (state.error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 flex items-center justify-center">
              <svg
                className="h-8 w-8 text-red-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
            </div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">登录失败</h2>
            <p className="mt-2 text-center text-sm text-gray-600">{state.error}</p>
            <div className="mt-6">
              <button
                onClick={() => (window.location.href = '/')}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                返回首页
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 成功状态（通常不会显示，因为会重定向）
  if (state.isAuthenticated && state.user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-12 w-12 flex items-center justify-center">
              <svg
                className="h-8 w-8 text-green-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">登录成功</h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              欢迎回来，{state.user.name || state.user.github_username}！
            </p>
            <p className="mt-1 text-center text-xs text-gray-500">正在跳转...</p>
          </div>
        </div>
      </div>
    );
  }

  // 默认状态（不应该到达这里）
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <p className="text-gray-600">处理认证回调中...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
