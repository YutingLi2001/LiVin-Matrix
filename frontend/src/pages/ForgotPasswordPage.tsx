import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ForgotPasswordPage: React.FC = () => {
  const { forgotPassword, clearError, state } = useAuth();
  const { isLoading, error } = state;

  const [email, setEmail] = useState('');
  const [emailSent, setEmailSent] = useState(false);
  const [formError, setFormError] = useState('');

  const validateEmail = (email: string): boolean => {
    if (!email) {
      setFormError('请输入邮箱地址');
      return false;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setFormError('请输入有效的邮箱地址');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setFormError('');
    clearError();

    if (!validateEmail(email)) {
      return;
    }

    try {
      await forgotPassword({ email });
      setEmailSent(true);
    } catch (error) {
      console.error('Forgot password request failed:', error);
    }
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (formError) {
      setFormError('');
    }
  };

  if (emailSent) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
        <div className="card-cyber max-w-md w-full mx-4">
          <div className="text-center">
            <div className="mb-4">
              <svg
                className="mx-auto h-16 w-16 text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-blue-400 mb-4">邮件已发送</h1>
            <p className="text-gray-300 mb-2">
              我们已向 <span className="text-purple-400 font-medium">{email}</span>{' '}
              发送了密码重置邮件。
            </p>
            <p className="text-gray-400 text-sm mb-6">
              请查收邮件并点击其中的链接来重置您的密码。如果没有收到邮件，请检查垃圾邮箱。
            </p>
            <div className="space-y-3">
              <Link to="/login" className="btn-primary w-full inline-block text-center">
                返回登录
              </Link>
              <button
                onClick={() => {
                  setEmailSent(false);
                  setEmail('');
                }}
                className="w-full py-2 text-purple-400 hover:text-purple-300 text-sm transition-colors"
              >
                使用其他邮箱
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
      <div className="card-cyber max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: '#8b5cf6', textShadow: '0 0 10px #8b5cf6' }}
          >
            忘记密码
          </h1>
          <p style={{ color: '#e5e5e5' }}>输入您的邮箱地址，我们将发送密码重置链接</p>
        </div>

        {/* 错误提示 */}
        {(error || formError) && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-lg">
            <p className="text-red-300 text-sm">{error || formError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
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
              value={email}
              onChange={handleEmailChange}
              className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                error || formError ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="输入您注册时使用的邮箱地址"
              required
              disabled={isLoading}
            />
          </div>

          <button type="submit" className="btn-primary w-full" disabled={isLoading || !email}>
            {isLoading ? '发送中...' : '发送重置邮件'}
          </button>
        </form>

        {/* 帮助信息 */}
        <div className="mt-6 p-4 bg-gray-800/50 rounded-lg">
          <h3 className="text-sm font-medium text-gray-200 mb-2">找不到重置邮件？</h3>
          <ul className="text-xs text-gray-400 space-y-1">
            <li>• 检查垃圾邮箱或促销文件夹</li>
            <li>• 确认邮箱地址拼写正确</li>
            <li>• 等待几分钟，邮件可能需要一些时间送达</li>
            <li>• 如果仍未收到，请联系客服支持</li>
          </ul>
        </div>

        {/* 返回登录链接 */}
        <div className="mt-6 text-center">
          <Link
            to="/login"
            className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
          >
            ← 返回登录页面
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
