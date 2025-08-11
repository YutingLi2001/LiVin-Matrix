# ADR-004: 文档架构重构

## 状态
提议 - 2025-08-07

## 背景
项目当前的文档架构基于BMAD-METHOD生成，存在严重的可维护性问题：

### 核心问题
- **信息冗余严重**: 同一信息在多个层次重复表达 (architecture/ + tasks/, epics/ + stories/)
- **维护成本过高**: 需求变更时必须同步更新多个文档，容易造成信息不一致
- **实际使用率极低**: 开发者99%时间只使用stories，其他文档成为"僵尸文档"
- **文档层级混乱**: 缺乏清晰的职责边界，存在功能重叠的文件夹

### 具体案例
**规划层冲突**:
- `architecture/` 和 `tasks/` 包含相同的系统设计信息，只是组织方式不同
- `frontend-spec.md` 和 `frontend-tasks/` 重复描述前端实现规划

**执行层冲突**:
- `epics/` 和 `stories/` 都在描述具体执行任务，但粒度不同，造成选择困惑

## 决策
采用三层文档架构，每层只保留一个Single Source of Truth：

### 架构原则
1. **分层职责清晰**: 战略层→规划层→执行层，各层职责边界明确
2. **单一真相源**: 每层只保留一个权威信息源，避免重复和冲突
3. **🎯 线性执行流** (核心原则): 执行层必须是线性的，按严格的时间顺序组织，支持跨技术栈的依赖关系，避免在多个文件夹间跳转
4. **就近原则**: 操作指导类文档放置在使用频率最高的位置
5. **Top-Down重构**: 从战略层开始，自上而下进行架构重构

### 具体架构设计

#### 核心三层结构
```
docs/
├── strategy/           # 战略层 - 项目愿景和长期方向
├── planning/           # 规划层 - 功能分解和架构设计
└── execution/          # 执行层 - 具体开发任务
    └── stories/        # 线性开发流水线
```

#### 辅助文档分类
```
docs/
├── decisions/          # ADR决策记录 (项目治理)
├── journal/            # 开发日志和历史记录
└── archive/            # 已废弃的历史文档
```

#### 操作指导文档
```
项目根目录/
├── HUMAN-TASKS.md      # 人类开发者备忘录
├── SECURITY-SETUP.md   # 安全配置指导
└── README.md           # 项目概述
```

### 层级职责定义

#### 战略层 (Strategy)
- **目标**: 项目愿景和长期方向
- **内容**: 高层次目标、核心价值主张、技术选型原则
- **特点**: 避免具体实施细节，保持抽象和灵活性，变更频率低
- **文件特点**: 保持现有文件名，减少修改工作量

#### 规划层 (Planning) - 按技术门类组织
- **目标**: 纯技术规范和架构设计
- **内容**: 技术选型rationale、架构设计原理、接口契约定义
- **特点**: 解释"为什么这样设计"，不包含执行步骤或checkboxes
- **门类划分**:
  - **应用架构**: 前端+后端+数据库技术规范
  - **基础设施架构**: AWS、容器、网络规划（如AWS规划、成本策略）
  - **安全架构**: 认证、密钥管理、权限策略（如Docker Secrets策略原理）
  - **部署架构**: CI/CD、环境配置、发布策略
  - **集成架构**: API设计、数据流、服务通信

#### 执行层 (Execution) - 线性组织
- **目标**: 具体开发任务和实施细节
- **内容**: Stories按严格线性顺序组织，支持跨技术栈依赖
- **重组策略**: 暂不执行，等现有Epic完成端到端测试后再处理
- **未来组织方式**:
  ```
  stories/
  ├── 1.1-project-setup/
  ├── 1.2-database-design/
  ├── 1.3-auth-backend-api/     # 后端认证API
  ├── 1.4-auth-frontend-ui/     # 前端登录界面 (依赖1.3)
  ├── 1.5-dashboard-api/        # 仪表盘后端
  └── 1.6-dashboard-ui/         # 仪表盘前端 (依赖1.5)
  ```

## 重构迁移策略 (Top-Down方法)

### 🎯 核心理念：自上而下重构
从战略层开始，确保每一层都为下一层提供清晰的指导，最终形成完全线性的执行流水线。

### 第一阶段：战略层重构 (Strategy) - 1天
- **保持文件名**: `prd.md`, `architecture.md`, `frontend-spec.md`
- **轻量修改**: prd和frontend-spec只需少量修改去掉实现细节
- **重点工作**: 从`docs/architecture/`文件夹中浓缩精炼出核心架构原则
- **为规划层提供指导框架**

### 第二阶段：规划层整合 (Planning) - 2天
#### 2.1 内容重复/互补关系分析
- **Tasks/** vs **Architecture/**: 高度重复(80%)，tasks为执行导向，architecture为技术规范
- **Frontend-tasks/** vs **Tasks/06-frontend**: 互补关系，frontend-tasks是详细分解
- **Architecture/内部冗余**: 编号文件与独立文件重复

#### 2.2 按技术门类重组
- **合并策略**: 提取纯技术规范，去除执行清单和checkboxes
- **门类文件**:
  - `application-architecture.md`: 前端+后端+数据库技术规范
  - `infrastructure-architecture.md`: AWS规划、容器、网络（如AWS选型rationale、成本策略）
  - `security-architecture.md`: Docker Secrets策略原理、认证架构、威胁模型
  - `deployment-architecture.md`: CI/CD策略、环境配置原理
  - `integration-architecture.md`: API设计、数据流、服务通信
- **删除原有文件夹**: `architecture/`, `tasks/`, `frontend-tasks/`

### 第三阶段：执行层线性重组 - 暂不执行
- **推迟原因**: 等现有Epic完成端到端测试后再处理
- **避免干扰**: 不影响当前开发进度
- **未来计划**: 重新排序为严格线性执行顺序，合并frontend-tasks内容

### 第四阶段：辅助文档归类 + 操作手册策略 - 1天
#### 4.1 辅助文档归类
- 历史文档 → `docs/archive/`
- 开发日志 → `docs/journal/` (移入`developmentjournal.md`)
- 在根目录创建 `HUMAN-TASKS.md` 人类备忘录

#### 4.2 取消操作手册策略
- **删除**: `SECURITY-SETUP.md`, `AWS-SETUP.md`等操作手册
- **rationale**:
  - 开发速度快(一周翻天覆地)，手册更新滞后产生误导
  - AI Agent能处理常识操作，复杂场景手册也说不清
  - 维护多套文档成本过高
- **替代方案**: AI Agent实时查询规划文档，Stories包含关键操作要点

## 替代方案

**保持现状** - 被拒绝：维护成本过高，信息不一致风险大

**激进精简(只保留stories)** - 被拒绝：丢失架构层面的整体视角

**按技术栈分割** - 被拒绝：无法体现跨栈的依赖关系和执行顺序

## 预期结果

### 维护效率显著提升
- **消除重复**: 单一真相源原则避免80%的信息重复
- **同步成本降低**: 需求变更时只需更新单一文档
- **文档职责清晰**: 按技术门类组织，消除"信息应该放哪里"的困惑
- **减少维护负担**: 取消操作手册避免多套文档的同步问题

### 开发体验显著改善
- **架构理解清晰**: 规划层提供纯技术规范和设计rationale
- **执行流程优化**: 未来线性stories组织支持顺序执行，减少跨文件夹跳转
- **AI协作高效**: 规划文档为AI Agent提供准确的架构指导
- **人类任务管理**: HUMAN-TASKS.md专门管理需要外部操作的琐事

### 架构治理规范化
- **分层职责明确**: 战略-规划-执行三层架构各司其职
- **技术决策可追溯**: 规划层记录技术选型的完整rationale
- **扩展性良好**: 按技术门类组织便于未来添加新的架构领域
- **风险控制**: Top-Down重构确保架构一致性，分阶段执行降低风险

## 成功指标
- 文档维护时间减少70%以上
- 新开发者理解项目架构时间从数天缩短到数小时
- AI Agent查询架构信息准确率达到95%以上
- 技术决策争议减少，有明确的权威参考源

## 执行计划 (简版)

### 阶段1：战略层 (1天)
1. 创建 `docs/strategy/`
2. 轻度修改 `prd.md` 和 `frontend-spec.md`
3. 从 `architecture/` 浓缩出精炼的 `architecture.md`
4. 移动到 `strategy/` 文件夹

### 阶段2：规划层 (2天)
1. 创建 `docs/planning/`
2. 读完 `tasks/`, `architecture/`, `frontend-tasks/` 所有文件
3. 提取纯技术规范，去掉执行步骤
4. 写5个门类文件：
   - `application-architecture.md` (前后端数据库)
   - `infrastructure-architecture.md` (AWS容器网络)
   - `security-architecture.md` (Docker Secrets认证)
   - `deployment-architecture.md` (CI/CD环境)
   - `integration-architecture.md` (API数据流)
5. 删除 `architecture/`, `tasks/`, `frontend-tasks/`

### 阶段3：执行层
**跳过** - 等Epic完成后再处理

### 阶段4：收尾 (1天)
1. 创建 `docs/journal/`，移入 `developmentjournal.md`
2. 创建 `docs/archive/`，移入废弃文档
3. 根目录创建 `HUMAN-TASKS.md`
4. 删除 `SECURITY-SETUP.md` 等操作手册

**总耗时：4天，核心在阶段2的门类文件编写**
