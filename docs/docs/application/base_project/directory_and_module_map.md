---
title: 目录结构与模块职责
---

# 目录结构与模块职责

如果第一次看 `Meyo`，最容易误判的地方不是目录太多，而是会下意识拿它和 `Umber Studio` 当前体量做一一对应。

实际上，`Meyo` 现在还是一个**更早期、更干净的骨架仓库**。

## 顶层目录

```text
meyo/
├── docs/                  # Docusaurus 文档站
├── packages/              # Python workspace 子包
│   ├── meyo-core/
│   ├── meyo-ext/
│   ├── meyo-client/
│   ├── meyo-serve/
│   ├── meyo-app/
│   ├── meyo-sandbox/
│   └── meyo-accelerator/
├── configs/               # 本地启动配置
├── tests/                 # 测试目录
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

#### `packages/meyo-core`

职责：

- 放主包版本
- 放 CLI 总入口
- 放核心 optional dependencies

当前重点文件：

- `src/meyo/__init__.py`
- `src/meyo/_version.py`
- `src/meyo/cli/cli_scripts.py`

#### `packages/meyo-ext`

职责：

- 放具体实现
- 放 runtime adapter
- 放基础扩展能力

当前重点文件：

- `src/meyo_ext/__init__.py`

#### `packages/meyo-serve`

职责：

- 放应用服务层
- 负责把 runtime 变成更稳定的服务能力

当前重点文件：

- `src/meyo_serve/__init__.py`

#### `packages/meyo-app`

职责：

- 放启动与装配
- 承接 FastAPI、CLI、配置加载

当前重点文件：

- `src/meyo_app/_cli.py`
- `src/meyo_app/cli.py`
- `src/meyo_app/config.py`
- `src/meyo_app/meyo_server.py`
- `src/meyo_app/static/web/index.html`

#### `packages/meyo-client`

职责：

- 预留给未来的 SDK / 外部调用边界

#### `packages/meyo-sandbox`

职责：

- 预留给未来的受控执行与沙箱能力

#### `packages/meyo-accelerator`

职责：

- 放可选 GPU / 推理加速依赖的安装壳
- 把 GPU、推理加速、平台相关依赖从主包依赖里隔离出去

### `tests/`

当前还是占位目录，用来预留测试结构。

## 当前刻意没有的目录

下面这些目录在 `Umber Studio` 很重要，但在 `Meyo` 当前阶段**故意还没建**：

- `web/`
- `docker/`
- `scripts/`
- `openapi/`
- `scene/`

原因不是这些不需要，而是项目还在“先固化边界，再逐步实现”的阶段。

## 推荐阅读顺序

如果你想快速理解当前仓库，建议按下面顺序读目录：

1. 根 `pyproject.toml`
2. `packages/meyo-core`
3. `packages/meyo-ext`
4. `packages/meyo-serve`
5. `packages/meyo-app`
6. `docs/docs/application/base_project/`

## 一句话收口

当前 `Meyo` 的目录结构不是“大而全”，而是：

**先把 package 分层立住，再沿着 `core -> ext/serve -> app` 这条线逐步长真实系统。**
