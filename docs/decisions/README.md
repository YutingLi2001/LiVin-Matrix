# 架构决策记录 (Architecture Decision Records)

## 概述

本目录包含LiVin-Matrix项目的重大技术决策记录。每个ADR都遵循标准格式，记录决策的背景、考量因素、替代方案和最终结果。

## ADR编号规则

- ADR编号从001开始，按时间顺序递增
- 格式：`XXX-decision-title.md`
- 示例：`001-startup-standardization.md`

## ADR状态定义

- **提议 (Proposed)**: 决策正在讨论中
- **已采纳 (Accepted)**: 决策已通过并开始实施
- **已实施 (Implemented)**: 决策已完全落地
- **已弃用 (Deprecated)**: 决策已过时但仍保留记录
- **已替代 (Superseded)**: 被新的ADR替代

## 决策记录清单

| 编号 | 标题 | 状态 | 日期 |
|------|------|------|------|
| 001 | [启动方式标准化](001-startup-standardization.md) | 已实施 | 2025-08-05 |
| 002 | [Auth0迁移至GitHub OAuth](002-auth0-to-github-migration.md) | 已实施 | 2025-08-02 |
| 003 | [密钥管理演进策略](003-secrets-management.md) | 待创建 | 2025-08-04 |

## 使用指南

1. 创建新ADR时，使用`template.md`作为起始模板
2. 确保每个决策都有清晰的背景和理由
3. 记录所有考虑过的替代方案
4. 定期审查和更新ADR状态

## 相关文档

- [ADR模板](template.md)
- [架构文档](../architecture/)
- [任务文档](../tasks/)
- [实施记录](../stories/)
