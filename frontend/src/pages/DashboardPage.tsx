
import React from 'react';

const DashboardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-primary cyber-grid-bg">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-primary-500 neon-glow mb-4">
            数据仪表盘
          </h1>
          <p className="text-text-secondary text-lg">
            欢迎来到 LiVin Matrix，您的生活数据分析中心
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* 数据录入卡片 */}
          <div className="card-cyber">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-text-primary">数据录入</h3>
              <div className="w-8 h-8 bg-neon-green rounded-full flex items-center justify-center">
                <span className="text-bg-primary font-bold">+</span>
              </div>
            </div>
            <p className="text-text-secondary mb-4">
              记录您的睡眠、饮食、运动和情绪数据
            </p>
            <button className="btn-primary w-full">
              开始录入
            </button>
          </div>
          
          {/* 相关性矩阵卡片 */}
          <div className="card-cyber">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-text-primary">相关性矩阵</h3>
              <div className="w-8 h-8 bg-neon-cyan rounded-full flex items-center justify-center">
                <span className="text-bg-primary font-bold">#</span>
              </div>
            </div>
            <p className="text-text-secondary mb-4">
              查看生活维度之间的相关性热力图
            </p>
            <button className="btn-secondary w-full">
              查看矩阵
            </button>
          </div>
          
          {/* 趋势分析卡片 */}
          <div className="card-cyber">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-text-primary">趋势分析</h3>
              <div className="w-8 h-8 bg-neon-pink rounded-full flex items-center justify-center">
                <span className="text-bg-primary font-bold">📈</span>
              </div>
            </div>
            <p className="text-text-secondary mb-4">
              分析您的生活数据时间趋势
            </p>
            <button className="btn-secondary w-full">
              查看趋势
            </button>
          </div>
        </div>
        
        {/* 近期活动 */}
        <div className="card-cyber">
          <h3 className="text-xl font-semibold text-text-primary mb-4">近期活动</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-neon-green rounded-full mr-3"></div>
                <span className="text-text-primary">今日睡眠数据已记录</span>
              </div>
              <span className="text-text-tertiary text-sm">2分钟前</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-neon-cyan rounded-full mr-3"></div>
                <span className="text-text-primary">相关性矩阵已更新</span>
              </div>
              <span className="text-text-tertiary text-sm">1小时前</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-bg-tertiary rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-neon-pink rounded-full mr-3"></div>
                <span className="text-text-primary">运动数据已同步</span>
              </div>
              <span className="text-text-tertiary text-sm">3小时前</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;