---
title: 快速上手：当前工程骨架与最短阅读路径
---

# 快速上手：当前工程骨架与最短阅读路径

这篇文档只解决两个问题：

1. 第一次接手 `AI Studio`，应该按什么顺序看代码。
2. 当前仓库还没长成完整产品时，怎么验证你改的东西没有跑偏。

目标不是把全仓库讲完，而是给你一条**最短阅读路径**。

如果你是第一次接触：

- `uv`
- Python workspace / monorepo
- 多 package 分层

建议先读：

- [从零开始上手：uv、Workspace 与包加载链路](./from_zero_to_running.md)

## 先建立正确认知

`AI Studio` 当前还是一个 **docs-first + package skeleton** 阶段的项目。

这意味着：

- 已经有清晰的架构文档
- 已经有 `core / ext / client / serve / app / sandbox / accelerator` 的包边界
- 已经有最小 contracts、最小 runtime 示例和最小 wiring
- 但**还没有**完整的 FastAPI WebServer、OpenAPI 路由、Scene 分发和前端工作台

所以第一次看代码时，不要先找：

- `openapi/`
- `scene/`
- `web/`
- `configs/`

因为这些在当前仓库里还没有落下来。

你现在真正应该先理解的是：

`workspace 配置 -> core contracts -> ext 实现 -> serve 编排 -> app 装配 -> accelerator 可选依赖层 -> docs 设计基线`

## 当前最短阅读路径

建议按下面顺序阅读。

### 1. 根工作区配置

先看：

- `/Users/memory/CodeRepository/PycharmProjects/ai-studio/pyproject.toml`

你重点关注：

- `project.dependencies`
- `tool.uv.workspace`
- `tool.uv.sources`
- `dependency-groups`
- 当前有哪些 package
- 根仓库默认的开发工具约束

### 2. `ai-studio-core`

再看：

- `packages/ai-studio-core/src/ai_studio_core/contracts/models.py`
- `packages/ai-studio-core/src/ai_studio_core/contracts/gateways.py`
- `packages/ai-studio-core/src/ai_studio_core/contracts/runtime.py`

这一层定义的是：

- `RunRequest`
- `RunContext`
- `RunResult`
- `MemoryGateway`
- `KnowledgeGateway`
- `ToolGateway`
- `AgentRuntime`

### 3. `ai-studio-ext`

再看：

- `packages/ai-studio-ext/src/ai_studio_ext/runtime/echo_runtime.py`
- `packages/ai-studio-ext/src/ai_studio_ext/gateways/noop_gateways.py`

这一层当前还很薄，但已经表达了一个关键方向：

- `core` 只定义协议
- `ext` 放具体实现

### 4. `ai-studio-serve`

再看：

- `packages/ai-studio-serve/src/ai_studio_serve/run_service.py`

这一层现在的目标很清楚：

- `serve` 负责应用服务编排
- `serve` 调 runtime，但不负责系统启动

### 5. `ai-studio-app`

最后看：

- `packages/ai-studio-app/src/ai_studio_app/bootstrap.py`

这一层目前只做一件事：

- 把 `ext` 和 `serve` 装配成一个可用的 `RunService`

### 6. `ai-studio-accelerator`

最后补看：

- `packages/ai-studio-accelerator/ai-studio-acc-auto/pyproject.toml`
- `packages/ai-studio-accelerator/ai-studio-acc-flash-attn/pyproject.toml`

这一层不承载业务代码，主要负责：

- 维持可选推理加速依赖矩阵
- 把高风险或高平台耦合的安装策略从主业务包里隔离出来

## 当前最有效的验证方式

### 验证 1：代码最小语法检查

在仓库根目录执行：

```bash
python -m compileall packages
```

### 验证 2：文档站构建

在 docs 工作区执行：

```bash
cd /Users/memory/CodeRepository/PycharmProjects/ai-studio/docs
bun install
bun run build
```

## 当前推荐的开发顺序

如果你要从“文档基线”继续往“可运行骨架”推进，建议按下面顺序做：

1. 补 `app` 层的 FastAPI 入口
2. 补 `/runs` 最小接口
3. 把 `RunService` 真实挂进 API
4. 把 `EchoAgentRuntime` 替换成真实 LangGraph adapter
5. 再补 `MemoryGateway`、`KnowledgeGateway`、`ToolGateway` 的真实实现

## 一句话收口

当前 `AI Studio` 的最短阅读路径，不是：

`前端页面 -> 某个 API -> 某个业务函数`

而是：

`workspace -> core contracts -> ext impl -> serve service -> app bootstrap -> accelerator deps -> docs truth`
