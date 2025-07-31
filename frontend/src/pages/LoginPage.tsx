
import React from 'react';

const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center cyber-grid-bg">
      <div className="card-cyber max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-purple-500 neon-glow mb-2">
            LiVin Matrix
          </h1>
          <p className="text-gray-300">
            生活数据相关性分析平台
          </p>
        </div>
        
        <form className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
              邮箱地址
            </label>
            <input
              type="email"
              id="email"
              className="input-cyber w-full"
              placeholder="请输入邮箱地址"
            />
          </div>
          
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-white mb-2">
              密码
            </label>
            <input
              type="password"
              id="password"
              className="input-cyber w-full"
              placeholder="请输入密码"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-purple-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-300">
                记住我
              </label>
            </div>
            
            <div className="text-sm">
              <a href="#" className="font-medium text-purple-500 hover:text-purple-400">
                忘记密码？
              </a>
            </div>
          </div>
          
          <div>
            <button
              type="submit"
              className="btn-primary w-full"
            >
              登录
            </button>
          </div>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-300">
            还没有账户？{' '}
            <a href="#" className="font-medium text-purple-500 hover:text-purple-400">
              立即注册
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;