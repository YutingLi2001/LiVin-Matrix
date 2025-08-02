import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface LogoutButtonProps {
  className?: string;
  children?: React.ReactNode;
}

const LogoutButton: React.FC<LogoutButtonProps> = ({
  className = 'bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700 transition-colors',
  children = '登出',
}) => {
  const { logout } = useAuth();

  const handleLogout = () => {
    logout({
      returnTo: window.location.origin,
    });
  };

  return (
    <button onClick={handleLogout} className={className}>
      {children}
    </button>
  );
};

export default LogoutButton;
