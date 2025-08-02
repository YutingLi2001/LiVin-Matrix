import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginButtonProps {
  className?: string;
  children?: React.ReactNode;
}

const LoginButton: React.FC<LoginButtonProps> = ({
  className = 'bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors',
  children = '登录',
}) => {
  const { loginWithRedirect, isLoading } = useAuth();

  const handleLogin = () => {
    loginWithRedirect();
  };

  return (
    <button
      onClick={handleLogin}
      disabled={isLoading}
      className={`${className} ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {isLoading ? '登录中...' : children}
    </button>
  );
};

export default LoginButton;
