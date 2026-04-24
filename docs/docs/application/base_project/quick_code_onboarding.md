---
title: 快速上手：当前工程骨架与最短阅读路径
---

# 快速上手：当前工程骨架与最短阅读路径

这篇文档只解决两个问题：

1. 第一次接手 `Meyo`，应该按什么顺序看代码。
2. 当前仓库还没长成完整产品时，怎么验证你改的东西没有跑偏。

目标不是把全仓库讲完，而是给你一条**最短阅读路径**。

如果你是第一次接触：

- `uv`
- Python workspace / monorepo
- 多 package 分层

建议先读：

- [从零开始上手：uv、Workspace 与包加载链路](./from_zero_to_running.md)

## 先建立正确认知

`Meyo` 当前还是一个 **package skeleton + 最小 WebServer** 阶段的项目。

这意味着：

- 已经有清晰的架构文档
- 已经有 `core / ext / client / serve / app / sandbox / accelerator` 的包边界
- 已经有统一 CLI、配置加载、最小 FastAPI WebServer 和静态首页
- 但**还没有**完整的 OpenAPI 路由、Scene 分发和前端工作台

所以第一次看代码时，不要先找：

- `openapi/`
- `scene/`
- `web/`
- `configs/`

因为这些在当前仓库里还没有落下来。

你现在真正应该先理解的是：

`workspace 配置 -> core CLI -> app 配置与 WebServer -> ext/serve 预留层 -> accelerator 可选依赖层 -> docs 设计基线`

## 当前最短阅读路径

建议按下面顺序阅读。

### 1. 根工作区配置

先看：

- `<repo-root>/pyproject.toml`

你重点关注：

- `project.dependencies`
- `tool.uv.workspace`
- `tool.uv.sources`
- `dependency-groups`
- 当前有哪些 package
- 根仓库默认的开发工具约束

### 2. `meyo-core`

再看：

- `packages/meyo-core/pyproject.toml`
- `packages/meyo-core/src/meyo/__init__.py`
- `packages/meyo-core/src/meyo/cli/cli_scripts.py`

这一层定义的是：

- 主包名 `meyo`
- CLI 命令 `meyo`
- `start webserver` 子命令挂载方式
- 核心 optional dependencies

### 3. `meyo-ext`

再看：

- `packages/meyo-app/src/meyo_app/_cli.py`
- `packages/meyo-app/src/meyo_app/cli.py`
- `packages/meyo-app/src/meyo_app/config.py`
- `packages/meyo-app/src/meyo_app/meyo_server.py`
- `packages/meyo-app/src/meyo_app/static/web/index.html`

这一层当前负责：

- 接收 CLI 参数
- 解析 `configs/my/dev.toml`
- 创建 FastAPI app
- 挂载最小静态页

### 4. `meyo-serve`

再看：

- `packages/meyo-ext/pyproject.toml`
- `packages/meyo-ext/src/meyo_ext/__init__.py`

这一层现在主要表达依赖边界：

- 具体外部系统驱动放这里
- PG / Redis / Milvus / Neo4j / S3 通过 extras 打开

### 4. `meyo-serve`

再看：

- `packages/meyo-serve/pyproject.toml`
- `packages/meyo-serve/src/meyo_serve/__init__.py`

这一层现在还很薄，后续负责应用服务编排。

### 5. `meyo-client`

再看：

- `packages/meyo-client/pyproject.toml`
- `packages/meyo-client/src/meyo_client/__init__.py`

这一层预留给未来 SDK / API client。

### 6. `meyo-accelerator`

最后补看：

- `packages/meyo-accelerator/pyproject.toml`
- `packages/meyo-accelerator/src/meyo_accelerator/__init__.py`

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
cd <repo-root>/docs
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

当前 `Meyo` 的最短阅读路径，不是：

`前端页面 -> 某个 API -> 某个业务函数`

而是：

`workspace -> core CLI -> app webserver -> ext/serve/client boundaries -> accelerator deps -> docs truth`
