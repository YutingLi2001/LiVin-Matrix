/**
 * 登出按钮组件
 */

import React from 'react';
import { useAuth } from '../../hooks/useAuth';

interface LogoutButtonProps {
  className?: string;
  children?: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  showIcon?: boolean;
  confirmLogout?: boolean;
}

const LogoutButton: React.FC<LogoutButtonProps> = ({
  className,
  children,
  variant = 'danger',
  size = 'medium',
  showIcon = false,
  confirmLogout = false,
}) => {
  const { state, logout } = useAuth();

  const handleLogout = async () => {
    if (confirmLogout) {
      const confirmed = window.confirm('确定要登出吗？');
      if (!confirmed) return;
    }

    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // 默认样式
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  // 尺寸样式
  const sizeStyles = {
    small: 'px-3 py-2 text-sm',
    medium: 'px-4 py-2.5 text-base',
    large: 'px-6 py-3 text-lg',
  };

  // 变体样式
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };

  const buttonClassName = className || `${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]}`;

  // 登出图标
  const LogoutIcon = () => (
    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
      />
    </svg>
  );

  return (
    <button
      onClick={handleLogout}
      disabled={state.isLoading}
      className={buttonClassName}
      type="button"
    >
      {showIcon && <LogoutIcon />}
      {state.isLoading ? (
        <>
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
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
          登出中...
        </>
      ) : (
        children || '登出'
      )}
    </button>
  );
};

export default LogoutButton;