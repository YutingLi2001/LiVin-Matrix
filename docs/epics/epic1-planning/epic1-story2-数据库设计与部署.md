# E1S2: 数据库设计与部署

## 任务概述

**任务ID**: E1S2
**任务标题**: 数据库设计与部署
**所属Epic**: Epic 1 - 基础架构与用户认证
**预估时间**: 4天
**优先级**: 高

## 任务目标

作为系统架构师，我希望设计并部署核心数据库schema，以便后续功能基于稳定的数据结构开发。建立支持6个维度数据的完整数据库结构，包含用户管理和数据记录的所有表。

## 详细的验收标准

### 1. PostgreSQL数据库在本地和AWS RDS环境成功部署
- [ ] 本地Docker环境中PostgreSQL服务正常运行
- [ ] AWS RDS PostgreSQL实例创建并配置完成
- [ ] 数据库连接配置支持开发/生产环境切换
- [ ] 数据库备份策略配置（RDS自动备份）
- [ ] 数据库监控和告警设置

### 2. 用户表（users）和核心数据表（user_daily_records）创建完成
- [ ] `users`表包含：id, auth0_user_id, email, username, created_at, updated_at
- [ ] `user_daily_records`表包含所有6个维度的数据字段
- [ ] 表间关系正确建立（外键约束）
- [ ] 数据完整性约束设置（非空、唯一性等）
- [ ] 索引优化配置（查询性能）

### 3. 运动训练记录表（workout_sessions）支持分时段记录
- [ ] `workout_sessions`表支持多个训练记录
- [ ] 包含字段：id, user_daily_record_id, workout_type, start_time, end_time, intensity, feeling
- [ ] 支持力量训练和有氧训练两种类型
- [ ] 训练时长自动计算功能
- [ ] 数据验证确保时间逻辑正确

### 4. 支持6个维度的所有数据字段（基于最终确定的数据结构）
- [ ] **睡眠维度**: sleep_start_time, sleep_end_time, sleep_quality, wake_clarity
- [ ] **饮食维度**: calories, protein, fat, carbohydrates
- [ ] **运动维度**: total_workout_duration, daily_steps
- [ ] **情绪维度**: overall_mood, stress_level, anxiety_level, energy_level
- [ ] **工作效率维度**: deep_work_hours, active_breaks, focus_quality, task_completion, work_satisfaction, work_environment
- [ ] **社交维度**: initiated_social, responded_social, interpersonal_satisfaction, solitude_satisfaction

### 5. Alembic迁移脚本配置完成，支持数据库版本控制
- [ ] Alembic初始化配置文件
- [ ] 初始迁移脚本创建所有表结构
- [ ] 迁移脚本可以正确执行和回滚
- [ ] 版本控制策略建立（命名规范）
- [ ] 生产环境迁移流程文档

## 技术实现要点

### 数据库表结构设计

#### 用户表 (users)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    auth0_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 每日记录主表 (user_daily_records)
```sql
CREATE TABLE user_daily_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,

    -- 睡眠维度
    sleep_start_time TIME,
    sleep_end_time TIME,
    sleep_quality INTEGER CHECK (sleep_quality >= 1 AND sleep_quality <= 10),
    wake_clarity INTEGER CHECK (wake_clarity >= 1 AND wake_clarity <= 10),

    -- 饮食维度
    calories INTEGER CHECK (calories >= 0 AND calories <= 5000),
    protein INTEGER CHECK (protein >= 0 AND protein <= 500),
    fat INTEGER CHECK (fat >= 0 AND fat <= 500),
    carbohydrates INTEGER CHECK (carbohydrates >= 0 AND carbohydrates <= 1000),

    -- 运动维度
    total_workout_duration INTEGER DEFAULT 0, -- 分钟
    daily_steps DECIMAL(4,1) CHECK (daily_steps >= 0), -- 千步

    -- 情绪维度
    overall_mood INTEGER CHECK (overall_mood >= 1 AND overall_mood <= 10),
    stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
    anxiety_level INTEGER CHECK (anxiety_level >= 1 AND anxiety_level <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),

    -- 工作效率维度
    deep_work_hours DECIMAL(3,1) CHECK (deep_work_hours >= 0 AND deep_work_hours <= 24),
    active_breaks INTEGER CHECK (active_breaks >= 0),
    focus_quality INTEGER CHECK (focus_quality >= 1 AND focus_quality <= 10),
    task_completion INTEGER CHECK (task_completion >= 1 AND task_completion <= 10),
    work_satisfaction INTEGER CHECK (work_satisfaction >= 1 AND work_satisfaction <= 10),
    work_environment VARCHAR(20) CHECK (work_environment IN ('home', 'office', 'cafe', 'mixed')),

    -- 社交维度
    initiated_social INTEGER CHECK (initiated_social >= 0),
    responded_social INTEGER CHECK (responded_social >= 0),
    interpersonal_satisfaction INTEGER CHECK (interpersonal_satisfaction >= 1 AND interpersonal_satisfaction <= 10),
    solitude_satisfaction INTEGER CHECK (solitude_satisfaction >= 1 AND solitude_satisfaction <= 10),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, record_date)
);
```

#### 运动训练记录表 (workout_sessions)
```sql
CREATE TABLE workout_sessions (
    id SERIAL PRIMARY KEY,
    user_daily_record_id INTEGER REFERENCES user_daily_records(id) ON DELETE CASCADE,
    workout_type VARCHAR(20) NOT NULL CHECK (workout_type IN ('strength', 'cardio')),
    cardio_type VARCHAR(20) CHECK (cardio_type IN ('running', 'cycling', 'swimming', 'hiit', 'machine', 'other')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    intensity INTEGER NOT NULL CHECK (intensity >= 1 AND intensity <= 10),
    feeling INTEGER NOT NULL CHECK (feeling >= 1 AND feeling <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### SQLAlchemy模型配置
- 使用SQLAlchemy ORM定义模型类
- 配置关系映射（一对多、外键）
- 数据验证使用Pydantic模型
- 自动时间戳更新配置

### Alembic配置要点
- 环境配置支持异步数据库连接
- 迁移脚本自动生成和手动编辑
- 数据库升级和降级策略
- 生产环境迁移安全检查

## 依赖关系

**前置依赖**: E1S1 (项目基础架构搭建)
**后续任务**:
- E1S3 (Auth0用户认证集成) - 需要用户表结构
- E1S4 (基础API框架建立) - 需要数据库连接配置

## 预估时间分解

- **第1天**: 数据库表结构设计，本地PostgreSQL配置
- **第2天**: SQLAlchemy模型创建，Alembic配置
- **第3天**: AWS RDS部署，生产环境配置
- **第4天**: 数据完整性测试，迁移脚本验证

## 风险点和缓解策略

### 风险点
1. **AWS RDS费用超支**: 免费层配置可能不足
2. **数据库性能问题**: 复杂查询可能影响响应时间
3. **迁移脚本错误**: 生产环境数据丢失风险
4. **数据类型选择**: 后续需求变更导致结构调整

### 缓解策略
1. 严格使用RDS免费层配置，设置费用告警
2. 合理设计索引，预估查询性能，设置连接池
3. 迁移脚本充分测试，建立备份恢复流程
4. 预留扩展字段，使用JSONB存储可变数据

## 验证方法

### 功能验证
1. **数据库连接测试**: 本地和RDS环境连接成功
2. **表结构验证**: 所有表创建成功，约束生效
3. **数据插入测试**: 完整的6维度数据插入和查询
4. **迁移测试**: Alembic升级和降级操作正常

### 性能验证
- 单条记录插入时间 < 50ms
- 用户历史数据查询（30天）< 200ms
- 数据库连接池配置验证（10个并发连接）

### 数据完整性验证
- 外键约束正常工作
- 数据类型验证生效（评分1-10等）
- 唯一性约束防止重复数据

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 本地和AWS RDS数据库正常运行
- [ ] 所有表结构创建并测试通过
- [ ] Alembic迁移脚本可以正常执行
- [ ] 数据完整性约束全部生效
- [ ] 性能测试达到预期指标
- [ ] 数据库备份策略配置完成

## 相关文档

- [数据库设计文档](../数据库设计.md)
- [Alembic使用指南](../Alembic使用指南.md)
- [AWS RDS配置指南](../AWS-RDS配置指南.md)

---

**任务负责人**: [待分配]
**创建时间**: 2024年
**最后更新**: 2024年
