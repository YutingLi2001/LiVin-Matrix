-- LiVin Matrix 数据库初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表（示例）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建数据记录表（示例）
CREATE TABLE IF NOT EXISTS life_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sleep_quality INTEGER CHECK (sleep_quality >= 1 AND sleep_quality <= 10),
    sleep_hours DECIMAL(3,1),
    diet_quality INTEGER CHECK (diet_quality >= 1 AND diet_quality <= 10),
    meal_count INTEGER,
    exercise_intensity INTEGER CHECK (exercise_intensity >= 1 AND exercise_intensity <= 10),
    exercise_minutes INTEGER,
    mood_score INTEGER CHECK (mood_score >= 1 AND mood_score <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    work_efficiency INTEGER CHECK (work_efficiency >= 1 AND work_efficiency <= 10),
    social_activity INTEGER CHECK (social_activity >= 1 AND social_activity <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_life_data_user_date ON life_data(user_id, date);
CREATE INDEX IF NOT EXISTS idx_life_data_date ON life_data(date);

-- 插入示例数据（可选）
INSERT INTO users (email, username, full_name, hashed_password) 
VALUES ('demo@livin-matrix.com', 'demo', 'Demo User', '$2b$12$example_hashed_password') 
ON CONFLICT (email) DO NOTHING;