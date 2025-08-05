import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ResetPasswordPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const { resetPassword, clearError, state } = useAuth();
  const { isLoading, error } = state;

  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: '',
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [resetSuccess, setResetSuccess] = useState(false);
  const [invalidToken, setInvalidToken] = useState(false);

  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setInvalidToken(true);
    }
  }, [token]);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // 密码验证
    if (!formData.newPassword) {
      errors.newPassword = '请输入新密码';
    } else if (formData.newPassword.length < 8) {
      errors.newPassword = '密码至少需要8位字符';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.newPassword)) {
      errors.newPassword = '密码需包含大小写字母和数字';
    }

    // 确认密码验证
    if (!formData.confirmPassword) {
      errors.confirmPassword = '请确认新密码';
    } else if (formData.newPassword !== formData.confirmPassword) {
      errors.confirmPassword = '两次输入的密码不一致';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    // 清除对应字段的错误
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setInvalidToken(true);
      return;
    }

    if (!validateForm()) {
      return;
    }

    try {
      clearError();

      await resetPassword({
        token,
        new_password: formData.newPassword,
      });

      setResetSuccess(true);
    } catch (error) {
      console.error('Password reset failed:', error);
    }
  };

  // 无效令牌页面
  if (invalidToken) {
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
            <h1 className="text-2xl font-bold text-red-400 mb-4">链接无效或已过期</h1>
            <p className="text-gray-300 mb-6">密码重置链接可能已过期或无效。请重新申请密码重置。</p>
            <div className="space-y-3">
              <Link to="/forgot-password" className="btn-primary w-full inline-block text-center">
                重新申请密码重置
              </Link>
              <Link
                to="/login"
                className="w-full py-2 text-purple-400 hover:text-purple-300 text-sm transition-colors inline-block text-center"
              >
                返回登录页面
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 重置成功页面
  if (resetSuccess) {
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
            <h1 className="text-2xl font-bold text-green-400 mb-4">密码重置成功！</h1>
            <p className="text-gray-300 mb-6">
              您的密码已成功重置。现在可以使用新密码登录您的账户。
            </p>
            <Link to="/login" className="btn-primary w-full inline-block text-center">
              立即登录
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 重置密码表单
  return (
    <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
      <div className="card-cyber max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1
            className="text-3xl font-bold mb-2"
            style={{ color: '#8b5cf6', textShadow: '0 0 10px #8b5cf6' }}
          >
            重置密码
          </h1>
          <p style={{ color: '#e5e5e5' }}>请输入您的新密码</p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-lg">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 新密码 */}
          <div>
            <label
              htmlFor="newPassword"
              className="block text-sm font-medium mb-2"
              style={{ color: '#e5e5e5' }}
            >
              新密码 *
            </label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                formErrors.newPassword ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="至少8位，包含大小写字母和数字"
              required
              disabled={isLoading}
            />
            {formErrors.newPassword && (
              <p className="mt-1 text-sm text-red-400">{formErrors.newPassword}</p>
            )}
          </div>

          {/* 确认新密码 */}
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium mb-2"
              style={{ color: '#e5e5e5' }}
            >
              确认新密码 *
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                formErrors.confirmPassword ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="再次输入新密码"
              required
              disabled={isLoading}
            />
            {formErrors.confirmPassword && (
              <p className="mt-1 text-sm text-red-400">{formErrors.confirmPassword}</p>
            )}
          </div>

          {/* 提交按钮 */}
          <button
            type="submit"
            className="btn-primary w-full"
            disabled={isLoading || !formData.newPassword || !formData.confirmPassword}
          >
            {isLoading ? '重置中...' : '重置密码'}
          </button>
        </form>

        {/* 密码要求提示 */}
        <div className="mt-4 p-3 bg-gray-800/50 rounded-lg">
          <p className="text-xs text-gray-400 mb-2">密码要求：</p>
          <ul className="text-xs text-gray-400 space-y-1">
            <li>• 至少8位字符</li>
            <li>• 包含大写字母</li>
            <li>• 包含小写字母</li>
            <li>• 包含数字</li>
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

export default ResetPasswordPage;
