import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoginButton from '../components/auth/LoginButton';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, login, emailLogin, clearError } = useAuth();
  const { isAuthenticated, isLoading, error } = state;

  const [loginMode, setLoginMode] = useState<'github' | 'email'>('github');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleGitHubLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('GitHub login failed:', error);
    }
  };

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.email || !formData.password) {
      return;
    }

    try {
      await emailLogin({
        email: formData.email,
        password: formData.password,
      });
    } catch (error) {
      console.error('Email login failed:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const switchLoginMode = (mode: 'github' | 'email') => {
    setLoginMode(mode);
    clearError();
    setFormData({ email: '', password: '' });
  };

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

        {/* 登录方式选择器 */}
        <div className="mb-6">
          <div className="flex rounded-lg border border-gray-600 bg-gray-800">
            <button
              className={`flex-1 py-2 px-4 rounded-l-lg transition-colors ${
                loginMode === 'github'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => switchLoginMode('github')}
            >
              GitHub OAuth
            </button>
            <button
              className={`flex-1 py-2 px-4 rounded-r-lg transition-colors ${
                loginMode === 'email'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              onClick={() => switchLoginMode('email')}
            >
              邮箱密码
            </button>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-lg">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="text-center">
            <div className="text-lg" style={{ color: '#e5e5e5' }}>
              正在验证用户身份...
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {loginMode === 'github' ? (
              /* GitHub登录 */
              <div className="text-center">
                <p className="text-sm mb-4" style={{ color: '#a3a3a3' }}>
                  使用GitHub账号安全登录
                </p>
                <LoginButton
                  className="btn-primary w-full"
                  onClick={handleGitHubLogin}
                  disabled={isLoading}
                >
                  使用GitHub登录
                </LoginButton>
              </div>
            ) : (
              /* 邮箱登录 */
              <form onSubmit={handleEmailLogin} className="space-y-4">
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium mb-2"
                    style={{ color: '#e5e5e5' }}
                  >
                    邮箱地址
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="输入您的邮箱地址"
                    required
                  />
                </div>
                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium mb-2"
                    style={{ color: '#e5e5e5' }}
                  >
                    密码
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="输入您的密码"
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="btn-primary w-full"
                  disabled={isLoading || !formData.email || !formData.password}
                >
                  邮箱登录
                </button>
                <div className="text-center">
                  <Link
                    to="/forgot-password"
                    className="text-sm text-purple-400 hover:text-purple-300"
                  >
                    忘记密码？
                  </Link>
                </div>
              </form>
            )}
          </div>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm" style={{ color: '#a3a3a3' }}>
            还没有账户？{' '}
            <Link
              to="/register"
              className="font-medium hover:text-purple-400"
              style={{ color: '#8b5cf6' }}
            >
              立即注册
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
