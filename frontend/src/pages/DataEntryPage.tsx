import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const DataEntryPage: React.FC = () => {
  const navigate = useNavigate();
  const [sleepQuality, setSleepQuality] = useState(5);
  const [dietQuality, setDietQuality] = useState(5);
  const [exerciseIntensity, setExerciseIntensity] = useState(5);
  const [moodIndex, setMoodIndex] = useState(5);
  const [stressLevel, setStressLevel] = useState(5);

  const handleKeyDown = (
    e: React.KeyboardEvent,
    value: number,
    setValue: (value: number) => void,
    min = 1,
    max = 10
  ) => {
    if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
      e.preventDefault();
      setValue(Math.max(min, value - 1));
    } else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
      e.preventDefault();
      setValue(Math.min(max, value + 1));
    }
  };
  return (
    <div className="min-h-screen bg-bg-primary cyber-grid-bg">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h1
              className="text-4xl font-bold"
              style={{ color: '#8b5cf6', textShadow: '0 0 10px #8b5cf6' }}
            >
              数据录入
            </h1>
            <div className="space-x-4">
              <button onClick={() => navigate('/dashboard')} className="btn-secondary">
                返回仪表盘
              </button>
              <button onClick={() => navigate('/login')} className="btn-secondary">
                退出登录
              </button>
            </div>
          </div>
          <p className="text-lg" style={{ color: '#e5e5e5' }}>
            记录您今天的生活数据，构建个人生活矩阵
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 睡眠数据 */}
          <div className="card-cyber">
            <h3
              className="text-xl font-semibold mb-4 flex items-center"
              style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
            >
              <span className="w-3 h-3 bg-neon-cyan rounded-full mr-3"></span>
              睡眠数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  睡眠质量 (1-10)
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={sleepQuality}
                    onChange={e => setSleepQuality(parseInt(e.target.value))}
                    onKeyDown={e => handleKeyDown(e, sleepQuality, setSleepQuality)}
                    className="slider-track"
                    style={
                      {
                        '--value-percent': `${((sleepQuality - 1) / 9) * 100}%`,
                      } as React.CSSProperties
                    }
                    tabIndex={0}
                  />
                  <div className="text-sm font-mono" style={{ color: '#e5e5e5' }}>
                    当前值: {sleepQuality}/10
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  睡眠时长 (小时)
                </label>
                <input type="number" className="input-cyber w-full" placeholder="8" />
              </div>
            </div>
          </div>

          {/* 饮食数据 */}
          <div className="card-cyber">
            <h3
              className="text-xl font-semibold mb-4 flex items-center"
              style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
            >
              <span className="w-3 h-3 bg-neon-green rounded-full mr-3"></span>
              饮食数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  饮食质量 (1-10)
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={dietQuality}
                    onChange={e => setDietQuality(parseInt(e.target.value))}
                    onKeyDown={e => handleKeyDown(e, dietQuality, setDietQuality)}
                    className="slider-track"
                    style={
                      {
                        '--value-percent': `${((dietQuality - 1) / 9) * 100}%`,
                      } as React.CSSProperties
                    }
                    tabIndex={0}
                  />
                  <div className="text-sm font-mono" style={{ color: '#e5e5e5' }}>
                    当前值: {dietQuality}/10
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  用餐次数
                </label>
                <input type="number" className="input-cyber w-full" placeholder="3" />
              </div>
            </div>
          </div>

          {/* 运动数据 */}
          <div className="card-cyber">
            <h3
              className="text-xl font-semibold mb-4 flex items-center"
              style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
            >
              <span className="w-3 h-3 bg-neon-orange rounded-full mr-3"></span>
              运动数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  运动强度 (1-10)
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={exerciseIntensity}
                    onChange={e => setExerciseIntensity(parseInt(e.target.value))}
                    onKeyDown={e => handleKeyDown(e, exerciseIntensity, setExerciseIntensity)}
                    className="slider-track"
                    style={
                      {
                        '--value-percent': `${((exerciseIntensity - 1) / 9) * 100}%`,
                      } as React.CSSProperties
                    }
                    tabIndex={0}
                  />
                  <div className="text-sm font-mono" style={{ color: '#e5e5e5' }}>
                    当前值: {exerciseIntensity}/10
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  运动时长 (分钟)
                </label>
                <input type="number" className="input-cyber w-full" placeholder="30" />
              </div>
            </div>
          </div>

          {/* 心情数据 */}
          <div className="card-cyber">
            <h3
              className="text-xl font-semibold mb-4 flex items-center"
              style={{ color: '#a78bfa', textShadow: '0 0 5px #a78bfa' }}
            >
              <span className="w-3 h-3 bg-neon-pink rounded-full mr-3"></span>
              心情数据
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  心情指数 (1-10)
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={moodIndex}
                    onChange={e => setMoodIndex(parseInt(e.target.value))}
                    onKeyDown={e => handleKeyDown(e, moodIndex, setMoodIndex)}
                    className="slider-track"
                    style={
                      {
                        '--value-percent': `${((moodIndex - 1) / 9) * 100}%`,
                      } as React.CSSProperties
                    }
                    tabIndex={0}
                  />
                  <div className="text-sm font-mono" style={{ color: '#e5e5e5' }}>
                    当前值: {moodIndex}/10
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: '#e5e5e5' }}>
                  压力水平 (1-10)
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={stressLevel}
                    onChange={e => setStressLevel(parseInt(e.target.value))}
                    onKeyDown={e => handleKeyDown(e, stressLevel, setStressLevel)}
                    className="slider-track"
                    style={
                      {
                        '--value-percent': `${((stressLevel - 1) / 9) * 100}%`,
                      } as React.CSSProperties
                    }
                    tabIndex={0}
                  />
                  <div className="text-sm font-mono" style={{ color: '#e5e5e5' }}>
                    当前值: {stressLevel}/10
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 提交按钮 */}
        <div className="mt-8 text-center">
          <button onClick={() => navigate('/dashboard')} className="btn-primary px-12 py-3 text-lg">
            保存今日数据
          </button>
        </div>
      </div>
    </div>
  );
};

export default DataEntryPage;
