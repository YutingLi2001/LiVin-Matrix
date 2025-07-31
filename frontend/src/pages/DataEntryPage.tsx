
import React from 'react';

const DataEntryPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-primary cyber-grid-bg">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-primary-500 neon-glow mb-4">
            数据录入
          </h1>
          <p className="text-text-secondary text-lg">
            记录您今天的生活数据，构建个人生活矩阵
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 睡眠数据 */}
          <div className="card-cyber">
            <h3 className="text-xl font-semibold text-text-primary mb-4 flex items-center">
              <span className="w-3 h-3 bg-neon-cyan rounded-full mr-3"></span>
              睡眠数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  睡眠质量 (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  className="w-full h-2 bg-bg-tertiary rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  睡眠时长 (小时)
                </label>
                <input
                  type="number"
                  className="input-cyber w-full"
                  placeholder="8"
                />
              </div>
            </div>
          </div>
          
          {/* 饮食数据 */}
          <div className="card-cyber">
            <h3 className="text-xl font-semibold text-text-primary mb-4 flex items-center">
              <span className="w-3 h-3 bg-neon-green rounded-full mr-3"></span>
              饮食数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  饮食质量 (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  className="w-full h-2 bg-bg-tertiary rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  用餐次数
                </label>
                <input
                  type="number"
                  className="input-cyber w-full"
                  placeholder="3"
                />
              </div>
            </div>
          </div>
          
          {/* 运动数据 */}
          <div className="card-cyber">
            <h3 className="text-xl font-semibold text-text-primary mb-4 flex items-center">
              <span className="w-3 h-3 bg-neon-orange rounded-full mr-3"></span>
              运动数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  运动强度 (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  className="w-full h-2 bg-bg-tertiary rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  运动时长 (分钟)
                </label>
                <input
                  type="number"
                  className="input-cyber w-full"
                  placeholder="30"
                />
              </div>
            </div>
          </div>
          
          {/* 心情数据 */}
          <div className="card-cyber">
            <h3 className="text-xl font-semibold text-text-primary mb-4 flex items-center">
              <span className="w-3 h-3 bg-neon-pink rounded-full mr-3"></span>
              心情数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  心情指数 (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  className="w-full h-2 bg-bg-tertiary rounded-lg appearance-none cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">
                  压力水平 (1-10)
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  className="w-full h-2 bg-bg-tertiary rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          </div>
        </div>
        
        {/* 提交按钮 */}
        <div className="mt-8 text-center">
          <button className="btn-primary px-12 py-3 text-lg">
            保存今日数据
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataEntryPage;