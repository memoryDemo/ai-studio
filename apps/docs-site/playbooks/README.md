---
title: Playbooks 索引
---

# Meyo Playbooks — 填空式操作手册

## 这是什么

这个目录下每一份文档都是一份**填空题**：告诉你改哪几个文件、先后顺序是什么、最少要做哪些验证。

目标是：

- 在 `Meyo` 还处于骨架期时，先把常见改动方式标准化
- 避免一边写代码一边临时改边界
- 把从 `Umber Studio` 学到的方法论迁过来，但不照抄它的现状

## 现有 Playbook

| # | 场景 | Playbook |
|---|---|---|
| 1 | 新增一个 HTTP 接口 | [add-new-api-endpoint.md](./add-new-api-endpoint.md) |
| 2 | 新增一个 Agent 场景 / Scene | [add-new-scene.md](./add-new-scene.md) |

接下来建议补的：

- `add-new-runtime-adapter.md`
- `add-new-memory-backend.md`
- `add-new-runs-endpoint.md`

## 怎么使用

1. 找到最接近你需求的 playbook。
2. **从头到尾读一遍**，不要跳读。
3. 按“改动清单”一步步做。
4. 做完后把“验证结果”和“影响面说明”一起记录下来。

## 如果找不到对应的 playbook

说明这是一个还没被标准化的改动类型。先回到架构文档确认边界，再动手。

原因通常只有两种：

- 当前仓库还没长到那一层
- 这个改动方式还没被沉淀成团队资产

## 写新 Playbook 的统一格式

所有 playbook 统一 5 段：

1. **什么时候用这份 playbook**
2. **主干定位**
3. **改动清单**
4. **验证**
5. **影响面说明**
