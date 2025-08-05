import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LogoutButton from '../components/auth/LogoutButton';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();
  const { user } = state;
  return (
    <div className="min-h-screen bg-bg-primary cyber-grid-bg">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h1
              className="text-4xl font-bold"
              style={{ color: '#8b5cf6', textShadow: '0 0 10px #8b5cf6' }}
            >
              数据仪表盘
            </h1>
            <div className="flex items-center space-x-4">
              {user && (
                <span className="text-sm" style={{ color: '#a3a3a3' }}>
                  欢迎回来，{user.name || user.email}
                </span>
              )}
              <button onClick={() => navigate('/data-entry')} className="btn-secondary">
                数据录入
              </button>
              <LogoutButton className="btn-secondary" />
            </div>
          </div>
          <p className="text-lg" style={{ color: '#e5e5e5' }}>
            欢迎来到 LiVin Matrix，您的生活数据分析中心
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* 数据录入卡片 */}
          <div className="card-cyber">
            <div className="flex items-center justify-between mb-4">
              <h3
                className="text-xl font-semibold"
                style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
              >
                数据录入
              </h3>
              <div className="w-8 h-8 bg-neon-green rounded-full flex items-center justify-center">
                <span className="text-bg-primary font-bold">+</span>
              </div>
            </div>
            <p className="mb-4" style={{ color: '#e5e5e5' }}>
              记录您的睡眠、饮食、运动和情绪数据
            </p>
            <button onClick={() => navigate('/data-entry')} className="btn-primary w-full">
              开始录入
            </button>
          </div>

          {/* 相关性矩阵卡片 */}
          <div className="card-cyber">
            <div className="flex items-center justify-between mb-4">
              <h3
                className="text-xl font-semibold"
                style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
              >
                相关性矩阵
              </h3>
              <div className="w-8 h-8 bg-neon-cyan rounded-full flex items-center justify-center">
                <span className="text-bg-primary font-bold">#</span>
              </div>
            </div>
            <p className="mb-4" style={{ color: '#e5e5e5' }}>
              查看生活维度之间的相关性热力图
            </p>
            <button className="btn-secondary w-full">查看矩阵</button>
          </div>

          {/* 趋势分析卡片 */}
          <div className="card-cyber">
            <div className="flex items-center justify-between mb-4">
              <h3
                className="text-xl font-semibold"
                style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
              >
                趋势分析
              </h3>
              <div className="w-8 h-8 bg-neon-pink rounded-full flex items-center justify-center">
                <span className="text-bg-primary font-bold">📈</span>
              </div>
            </div>
            <p className="mb-4" style={{ color: '#e5e5e5' }}>
              分析您的生活数据时间趋势
            </p>
            <button className="btn-secondary w-full">查看趋势</button>
          </div>
        </div>

        {/* 近期活动 */}
        <div className="card-cyber">
          <h3
            className="text-xl font-semibold mb-4"
            style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
          >
            近期活动
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-neon-green rounded-full mr-3"></div>
                <span style={{ color: '#e5e5e5' }}>今日睡眠数据已记录</span>
              </div>
              <span className="text-sm" style={{ color: '#a3a3a3' }}>
                2分钟前
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-neon-cyan rounded-full mr-3"></div>
                <span style={{ color: '#e5e5e5' }}>相关性矩阵已更新</span>
              </div>
              <span className="text-sm" style={{ color: '#a3a3a3' }}>
                1小时前
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-neon-pink rounded-full mr-3"></div>
                <span style={{ color: '#e5e5e5' }}>运动数据已同步</span>
              </div>
              <span className="text-sm" style={{ color: '#a3a3a3' }}>
                3小时前
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
