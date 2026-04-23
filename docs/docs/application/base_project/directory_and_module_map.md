---
title: 目录结构与模块职责
---

# 目录结构与模块职责

如果第一次看 `AI Studio`，最容易误判的地方不是目录太多，而是会下意识拿它和 `Umber Studio` 当前体量做一一对应。

实际上，`AI Studio` 现在还是一个**更早期、更干净的骨架仓库**。

## 顶层目录

```text
ai-studio/
├── docs/                  # Docusaurus 文档站
├── packages/              # Python workspace 子包
│   ├── ai-studio-core/
│   ├── ai-studio-ext/
│   ├── ai-studio-client/
│   ├── ai-studio-serve/
│   ├── ai-studio-app/
│   └── ai-studio-sandbox/
├── tests/                 # 预留测试目录
├── pyproject.toml         # uv workspace 根配置
├── README.md              # 项目说明
└── .editorconfig          # 编码风格
```

## 关键目录怎么读

### `docs/`

文档工作区，当前已经是仓库里最完整的一层。

主要承载：

- 架构设计文档
- 技术栈文档
- Memory OS 文档
- 开发指南与 playbooks

### `packages/`

这是仓库当前最重要的代码目录。

#### `packages/ai-studio-core`

职责：

- 放稳定 contracts
- 放 gateway 协议
- 放运行时输入输出模型

当前重点文件：

- `contracts/models.py`
- `contracts/gateways.py`
- `contracts/runtime.py`

#### `packages/ai-studio-ext`

职责：

- 放具体实现
- 放 runtime adapter
- 放基础扩展能力

当前重点文件：

- `runtime/echo_runtime.py`
- `gateways/noop_gateways.py`

#### `packages/ai-studio-serve`

职责：

- 放应用服务层
- 负责把 runtime 变成更稳定的服务能力

当前重点文件：

- `run_service.py`

#### `packages/ai-studio-app`

职责：

- 放启动与装配
- 未来承接 FastAPI、CLI、配置加载

当前重点文件：

- `bootstrap.py`

#### `packages/ai-studio-client`

职责：

- 预留给未来的 SDK / 外部调用边界

#### `packages/ai-studio-sandbox`

职责：

- 预留给未来的受控执行与沙箱能力

### `tests/`

当前还是占位目录，用来预留测试结构。

## 当前刻意没有的目录

下面这些目录在 `Umber Studio` 很重要，但在 `AI Studio` 当前阶段**故意还没建**：

- `web/`
- `configs/`
- `docker/`
- `scripts/`
- `openapi/`
- `scene/`

原因不是这些不需要，而是项目还在“先固化边界，再逐步实现”的阶段。

## 推荐阅读顺序

如果你想快速理解当前仓库，建议按下面顺序读目录：

1. 根 `pyproject.toml`
2. `packages/ai-studio-core`
3. `packages/ai-studio-ext`
4. `packages/ai-studio-serve`
5. `packages/ai-studio-app`
6. `docs/docs/application/base_project/`

## 一句话收口

当前 `AI Studio` 的目录结构不是“大而全”，而是：

**先把 package 分层立住，再沿着 `core -> ext/serve -> app` 这条线逐步长真实系统。**
