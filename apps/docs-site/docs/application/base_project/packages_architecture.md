---
title: Packages 架构与包间分层设计
---

# Packages 架构与包间分层设计

本文档解释 `Meyo` 的 `packages/` 目录当前是怎么设计的：

- 每个包负责什么
- 包之间的依赖方向是什么
- 新代码应该写到哪里

如果你还不熟 `uv workspace`、`pyproject.toml`、或者“依赖关系”和“加载链路”的区别，先看：

- [从零开始上手：uv、Workspace 与包加载链路](./from_zero_to_running.md)

## 一句话先记住

`Meyo` 当前采用的是一个 **uv workspace 风格的 Python monorepo**，由 7 个子包组成；整体目标仍然是复用 `Umber Studio` 的分层思想，但保持更低复杂度。

核心设计哲学是：

> 稳定协议放内层，具体实现放外层，系统启动和装配永远放最外层。

## 当前 7 个包

| 包 | 目录名 | pyproject `name` | Python import 命名空间 |
|---|---|---|---|
| core | `packages/meyo-core/` | `meyo` | `meyo` |
| ext | `packages/meyo-ext/` | `meyo-ext` | `meyo_ext` |
| serve | `packages/meyo-serve/` | `meyo-serve` | `meyo_serve` |
| app | `packages/meyo-app/` | `meyo-app` | `meyo_app` |
| client | `packages/meyo-client/` | `meyo-client` | `meyo_client` |
| sandbox | `packages/meyo-sandbox/` | `meyo-sandbox` | `meyo_sandbox` |
| accelerator | `packages/meyo-accelerator/` | `meyo-accelerator` | `meyo_accelerator` |

## 每个包的职责

### `meyo-core`

定义主包和稳定入口：

- `meyo` CLI
- 版本号
- core optional dependencies
- 未来的 contracts / gateway / runtime 协议

### `meyo-ext`

定义“用什么实现”，当前先承接外部系统依赖：

- PostgreSQL / Redis
- Milvus / Neo4j
- S3 / MinIO
- 未来 runtime adapter / gateway adapter

### `meyo-serve`

定义“怎么把底层能力组织成稳定服务”：

- application service
- use-case 编排

### `meyo-app`

定义“怎么启动和装配系统”：

- CLI webserver 子命令
- 配置加载
- FastAPI 入口
- 静态首页

### `meyo-client`

定义“怎么给外部消费者调”：

- 未来 Python SDK
- 未来 HTTP client 封装

### `meyo-sandbox`

定义“怎么隔离执行”：

- 代码执行
- shell 执行
- 工具副作用隔离

### `meyo-accelerator`

定义“怎么挂可选推理加速依赖”：

- 当前还是空壳
- 后续放 GPU、推理加速或平台相关依赖
- 避免这些重依赖污染主包

## 包之间的依赖方向

当前目标依赖方向是：

```text
meyo <- meyo-ext / meyo-client / meyo-serve <- meyo-app
```

这意味着：

1. `core` 不依赖任何上层包
2. `ext` / `client` / `sandbox` / `serve` 都不能依赖 `app`
3. `app` 是最外层，只负责装配
4. `sandbox` 和 `accelerator` 是侧向能力，由 `app` 最终选择是否装配

### 当前实际依赖声明

目前根 `pyproject.toml` 和各子包 `pyproject.toml` 已经表达了一个更保守的版本：

- `ext -> meyo`
- `client -> meyo/ext`
- `serve -> ext`
- `app -> meyo/ext/client/serve/sandbox/accelerator`

## 新代码应该写到哪里

| 你要加的东西 | 应该写到哪里 |
|---|---|
| 稳定输入输出模型 | `core` |
| 新的 gateway 协议 | `core` |
| LangGraph runtime adapter | `ext` |
| Milvus / Neo4j / PG 的实现适配 | `ext` |
| 面向业务的应用服务 | `serve` |
| FastAPI router / CLI / 启动装配 | `app` |
| 对外 SDK | `client` |
| Python / Shell / Tool 的隔离执行器 | `sandbox` |
| 可选推理加速依赖矩阵 | `accelerator` |

## 当前最重要的边界规则

### 规则 1：`core` 不写业务 I/O

`core` 可以有：

- dataclass
- protocol
- typed models

`core` 不应该有：

- FastAPI 路由
- 数据库连接
- 真正的向量检索实现
- HTTP client 细节

### 规则 2：`ext` 只放实现，不定义系统真相

例如：

- `MemoryGateway` 的协议在 `core`
- `PostgresMemoryGateway` 或 `Mem0MemoryGateway` 未来应在 `ext`

### 规则 3：`serve` 面向 use case，不面向底层细节

`serve` 的职责不是“替代 runtime”，而是把底层能力变成稳定的应用服务。

### 规则 4：`app` 只做装配，不承载协议定义

以后即使加上 FastAPI，`app` 也应该：

- 调 `serve`
- 组装 `ext`
- 使用 `core`

而不是重新定义 contracts。

## 和 Umber Studio 的关系

`Meyo` 现在学的是 `Umber Studio` 的这几件事：

- package 分层方式
- 单向依赖方向
- `core / ext / serve / app / client / sandbox / accelerator` 的职责划分

但暂时**不学**这些东西：

- 同等规模的历史包袱
- 已经存在的业务域复杂度
- 过早的目录膨胀

## 一句话收口

当前 `Meyo` 的 packages 架构，不是要一夜之间复制 `Umber Studio`，而是：

**先把正确的包边界立住，再按这个边界慢慢长功能。**
