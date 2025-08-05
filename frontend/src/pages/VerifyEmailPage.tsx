import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const VerifyEmailPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { verifyEmail, clearError, state } = useAuth();
  const { error } = state;

  const [verificationStatus, setVerificationStatus] = useState<
    'verifying' | 'success' | 'error' | 'invalid'
  >('verifying');
  const [message, setMessage] = useState('');

  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setVerificationStatus('invalid');
      return;
    }

    const performVerification = async () => {
      try {
        clearError();
        const response = await verifyEmail({ token });
        setMessage(response.message);
        setVerificationStatus('success');

        // 延迟跳转到登录页面
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } catch (error: any) {
        console.error('Email verification failed:', error);
        setMessage(error.error_description || '邮箱验证失败');
        setVerificationStatus('error');
      }
    };

    performVerification();
  }, [token, verifyEmail, clearError, navigate]);

  // 正在验证
  if (verificationStatus === 'verifying') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
        <div className="card-cyber max-w-md w-full mx-4">
          <div className="text-center">
            <div className="mb-4">
              <svg
                className="animate-spin mx-auto h-16 w-16 text-purple-400"
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
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-purple-400 mb-4">正在验证邮箱</h1>
            <p className="text-gray-300">请稍候，我们正在验证您的邮箱地址...</p>
          </div>
        </div>
      </div>
    );
  }

  // 验证成功
  if (verificationStatus === 'success') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
        <div className="card-cyber max-w-md w-full mx-4">
          <div className="text-center">
            <div className="mb-4">
              <svg
                className="mx-auto h-16 w-16 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-green-400 mb-4">邮箱验证成功！</h1>
            <p className="text-gray-300 mb-2">{message || '您的邮箱已成功验证，账户已激活。'}</p>
            <p className="text-gray-400 text-sm mb-6">3秒后将自动跳转到登录页面...</p>
            <div className="space-y-3">
              <Link to="/login" className="btn-primary w-full inline-block text-center">
                立即登录
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 验证失败
  if (verificationStatus === 'error') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
        <div className="card-cyber max-w-md w-full mx-4">
          <div className="text-center">
            <div className="mb-4">
              <svg
                className="mx-auto h-16 w-16 text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-red-400 mb-4">验证失败</h1>
            <p className="text-gray-300 mb-6">
              {message || error || '邮箱验证失败，验证链接可能已过期或无效。'}
            </p>
            <div className="space-y-3">
              <Link to="/login" className="btn-primary w-full inline-block text-center">
                返回登录
              </Link>
              <Link
                to="/register"
                className="w-full py-2 text-purple-400 hover:text-purple-300 text-sm transition-colors inline-block text-center"
              >
                重新注册
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 无效令牌
  return (
    <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
      <div className="card-cyber max-w-md w-full mx-4">
        <div className="text-center">
          <div className="mb-4">
            <svg
              className="mx-auto h-16 w-16 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-red-400 mb-4">验证链接无效</h1>
          <p className="text-gray-300 mb-6">
            验证链接格式不正确或缺少必要参数。请确保您访问的是完整的验证链接。
          </p>
          <div className="space-y-3">
            <Link to="/login" className="btn-primary w-full inline-block text-center">
              返回登录
            </Link>
            <Link
              to="/register"
              className="w-full py-2 text-purple-400 hover:text-purple-300 text-sm transition-colors inline-block text-center"
            >
              重新注册
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmailPage;
