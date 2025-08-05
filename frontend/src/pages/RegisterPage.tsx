import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { state, emailRegister, clearError } = useAuth();
  const { isAuthenticated, isLoading, error } = state;

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [registrationSuccess, setRegistrationSuccess] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    // 邮箱验证
    if (!formData.email) {
      errors.email = '请输入邮箱地址';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = '请输入有效的邮箱地址';
    }

    // 密码验证
    if (!formData.password) {
      errors.password = '请输入密码';
    } else if (formData.password.length < 8) {
      errors.password = '密码至少需要8位字符';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = '密码需包含大小写字母和数字';
    }

    // 确认密码验证
    if (!formData.confirmPassword) {
      errors.confirmPassword = '请确认密码';
    } else if (formData.password !== formData.confirmPassword) {
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

    if (!validateForm()) {
      return;
    }

    try {
      clearError();

      await emailRegister({
        email: formData.email,
        password: formData.password,
        name: formData.name || undefined,
      });

      setRegistrationSuccess(true);
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  if (registrationSuccess) {
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
            <h1 className="text-2xl font-bold text-green-400 mb-4">注册成功！</h1>
            <p className="text-gray-300 mb-6">
              我们已经向您的邮箱发送了验证邮件。请查收邮件并点击验证链接来激活您的账户。
            </p>
            <div className="space-y-3">
              <Link to="/login" className="btn-primary w-full inline-block text-center">
                返回登录
              </Link>
              <p className="text-sm text-gray-400">没收到邮件？请检查垃圾邮箱，或联系客服</p>
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
            创建账户
          </h1>
          <p style={{ color: '#e5e5e5' }}>加入LiVin Matrix，开始您的数据分析之旅</p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-lg">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 邮箱 */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium mb-2"
              style={{ color: '#e5e5e5' }}
            >
              邮箱地址 *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                formErrors.email ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="输入您的邮箱地址"
              required
            />
            {formErrors.email && <p className="mt-1 text-sm text-red-400">{formErrors.email}</p>}
          </div>

          {/* 姓名 */}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium mb-2"
              style={{ color: '#e5e5e5' }}
            >
              姓名（可选）
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="输入您的姓名"
            />
          </div>

          {/* 密码 */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium mb-2"
              style={{ color: '#e5e5e5' }}
            >
              密码 *
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                formErrors.password ? 'border-red-500' : 'border-gray-600'
              }`}
              placeholder="至少8位，包含大小写字母和数字"
              required
            />
            {formErrors.password && (
              <p className="mt-1 text-sm text-red-400">{formErrors.password}</p>
            )}
          </div>

          {/* 确认密码 */}
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium mb-2"
              style={{ color: '#e5e5e5' }}
            >
              确认密码 *
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
              placeholder="再次输入密码"
              required
            />
            {formErrors.confirmPassword && (
              <p className="mt-1 text-sm text-red-400">{formErrors.confirmPassword}</p>
            )}
          </div>

          {/* 提交按钮 */}
          <button type="submit" className="btn-primary w-full" disabled={isLoading}>
            {isLoading ? '注册中...' : '创建账户'}
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

        {/* 登录链接 */}
        <div className="mt-6 text-center">
          <p className="text-sm" style={{ color: '#a3a3a3' }}>
            已有账户？{' '}
            <Link
              to="/login"
              className="font-medium hover:text-purple-400"
              style={{ color: '#8b5cf6' }}
            >
              立即登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
