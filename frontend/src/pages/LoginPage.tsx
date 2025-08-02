import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginButton from '../components/auth/LoginButton';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  return (
    <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
      <div className="card-cyber max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: '#8b5cf6', textShadow: '0 0 10px #8b5cf6' }}
          >
            LiVin Matrix
          </h1>
          <p style={{ color: '#e5e5e5' }}>生活数据相关性分析平台</p>
        </div>

        {isLoading ? (
          <div className="text-center">
            <div className="text-lg" style={{ color: '#e5e5e5' }}>
              正在验证用户身份...
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="text-center">
              <p className="text-sm mb-4" style={{ color: '#a3a3a3' }}>
                使用Auth0安全登录系统
              </p>
              <LoginButton className="btn-primary w-full">安全登录</LoginButton>
            </div>
          </div>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm" style={{ color: '#a3a3a3' }}>
            还没有账户？{' '}
            <a href="#" className="font-medium hover:text-purple-400" style={{ color: '#8b5cf6' }}>
              立即注册
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
