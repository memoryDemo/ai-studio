---
title: 新增一个 Chat 场景(chat_mode)
---

# Playbook：新增一个 Agent 场景 / Scene

## 1. 什么时候用这份 playbook

你的需求命中下面任意一条：

- 要一种新的运行场景
- 要一种和现有默认主链不同的 prompt / context / tool 组合
- 你已经确认“只扩展 `RunRequest.metadata` 不够了”，需要正式的场景分发层

**当前状态说明：**

`AI Studio` 当前仓库**还没有正式的 `scene/` 目录和 `chat_mode` 契约**。

所以这份文档现在是一个**预置 playbook**：

- 你可以拿它做设计和目录预案
- 但如果仓库里还没有 `scene/` 主链，不要硬套成“今天就必须这样实现”

**不适用的情况：**

- 你只是想先区分 2 种 prompt 或上下文 → 先用 `RunRequest.metadata["scene"]` 做显式分支
- 你只是想加一个 HTTP 接口 → 看 [`add-new-api-endpoint.md`](./add-new-api-endpoint.md)
- 你只是想加一个新的 runtime adapter → 先改 `ext`

## 2. 主干定位

```text
[4] Scene 分发
     └── packages/ai-studio-app/src/ai_studio_app/scene/

[5] Serve 服务域
     └── packages/ai-studio-serve/src/ai_studio_serve/

[3] Ext 实现层
     └── packages/ai-studio-ext/src/ai_studio_ext/
```

## 3. 改动清单

### 步骤 1：先判断是不是真的需要“正式 Scene”

如果只是下面这些需求：

- 换一个系统提示词
- 多加一段知识上下文
- 多挂一个工具

当前更推荐先走轻量方式：

```python
RunRequest(
    thread_id="...",
    input="...",
    metadata={"scene": "research"},
)
```

只有当你已经确认：

- 场景需要独立 prompt 组装
- 场景需要独立上下文策略
- 场景需要独立 tool / render / policy

才建议进入正式 `scene/` 目录设计。

### 步骤 2：新建场景目录

当 `scene/` 主链建立后，建议目录至少是：

```text
packages/ai-studio-app/src/ai_studio_app/scene/my_new_scene/
├── __init__.py
├── chat.py
├── config.py
└── prompt.py
```

最小模板可以是：

```python
class MyNewSceneHandler:
    scene_code = "my_new_scene"
```

### 步骤 3：场景分发只应该发生在 `app`

不要在 `serve` 或 `ext` 层偷偷做场景分发。

场景属于：

- runtime / orchestration
- prompt selection
- context assembly

所以它天然是 `app` 层职责。

### 步骤 4：如果场景需要新的服务能力，回到 `serve` 和 `ext`

如果一个新场景需要新的业务能力：

- 在 `serve` 层加新的 service
- 在 `ext` 层补新的 adapter / gateway
- `scene` 本身只做分发和组装

不要在场景实现里直接写死：

- 数据访问
- 向量检索
- 工具调用
- 文件 I/O

### 步骤 5：当前阶段的最低限度验证

```bash
python -m compileall packages
```

如果你已经正式补了 `scene/` 主链，再验证：

```bash
uv run pytest
```

## 4. 验证

至少确认：

- 新场景没有把数据访问直接写进 `app`
- `scene` 只做分发和组装
- 新场景需要的服务能力已经沉到底层 `serve` / `ext`

## 5. 影响面说明

- 新场景是否引入新的对外契约
- 新场景是否需要新的 `serve` 服务
- 新场景是否需要新的 `ext` adapter
- 当前是否已经到了值得建立正式 `scene/` 目录的阶段
