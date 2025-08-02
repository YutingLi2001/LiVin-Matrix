/**
 * 受保护路由组件
 */

import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import LoginButton from './LoginButton';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireAuth?: boolean;
  showLoginButton?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback,
  requireAuth = true,
  showLoginButton = true,
}) => {
  const { state } = useAuth();

  // 如果不需要认证，直接渲染子组件
  if (!requireAuth) {
    return <>{children}</>;
  }

  // 加载状态
  if (state.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <svg
            className="animate-spin h-8 w-8 text-blue-600 mx-auto"
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
          <p className="mt-4 text-lg text-gray-600">正在验证用户身份...</p>
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
            <svg
              className="h-12 w-12 text-red-600 mx-auto"
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
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              认证错误
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              {state.error}
            </p>
            {showLoginButton && (
              <div className="mt-6">
                <LoginButton className="w-full" />
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 未认证状态
  if (!state.isAuthenticated) {
    // 如果提供了自定义的fallback，使用它
    if (fallback) {
      return <>{fallback}</>;
    }

    // 默认的未认证页面
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <svg
              className="h-12 w-12 text-gray-400 mx-auto"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 15v2m-6 0h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              需要登录
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              请先登录以访问此页面
            </p>
            {showLoginButton && (
              <div className="mt-6">
                <LoginButton className="w-full" />
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // 已认证，渲染子组件
  return <>{children}</>;
};

export default ProtectedRoute;