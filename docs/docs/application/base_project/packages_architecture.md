---
title: Packages 架构与包间分层设计
---

# Packages 架构与包间分层设计

本文档解释 `AI Studio` 的 `packages/` 目录当前是怎么设计的：

- 每个包负责什么
- 包之间的依赖方向是什么
- 新代码应该写到哪里

## 一句话先记住

`AI Studio` 当前采用的是一个 **uv workspace 风格的 Python monorepo**，由 8 个子包组成，其中 `accelerator` 层包含 2 个可选附属包；整体目标仍然是复用 `Umber Studio` 的分层思想，但保持更低复杂度。

核心设计哲学是：

> 稳定协议放内层，具体实现放外层，系统启动和装配永远放最外层。

## 当前 8 个包

| 包 | 目录名 | pyproject `name` | Python import 命名空间 |
|---|---|---|---|
| core | `packages/ai-studio-core/` | `ai-studio-core` | `ai_studio_core` |
| ext | `packages/ai-studio-ext/` | `ai-studio-ext` | `ai_studio_ext` |
| serve | `packages/ai-studio-serve/` | `ai-studio-serve` | `ai_studio_serve` |
| app | `packages/ai-studio-app/` | `ai-studio-app` | `ai_studio_app` |
| client | `packages/ai-studio-client/` | `ai-studio-client` | `ai_studio_client` |
| sandbox | `packages/ai-studio-sandbox/` | `ai-studio-sandbox` | `ai_studio_sandbox` |
| acc-auto | `packages/ai-studio-accelerator/ai-studio-acc-auto/` | `ai-studio-acc-auto` | `ai_studio_acc_auto` |
| acc-flash-attn | `packages/ai-studio-accelerator/ai-studio-acc-flash-attn/` | `ai-studio-acc-flash-attn` | `ai_studio_acc_flash_attn` |

## 每个包的职责

### `ai-studio-core`

定义“是什么”：

- contracts
- gateway 协议
- runtime 协议
- 输入输出模型

### `ai-studio-ext`

定义“用什么实现”：

- runtime adapter
- gateway adapter
- 基础扩展实现

当前它承载的是：

- `EchoAgentRuntime`
- `NoopMemoryGateway`
- `NoopKnowledgeGateway`
- `NoopToolGateway`

### `ai-studio-serve`

定义“怎么把底层能力组织成稳定服务”：

- application service
- use-case 编排

### `ai-studio-app`

定义“怎么启动和装配系统”：

- bootstrap
- 未来的 FastAPI 入口
- 未来的 CLI 入口

### `ai-studio-client`

定义“怎么给外部消费者调”：

- 未来 Python SDK
- 未来 HTTP client 封装

### `ai-studio-sandbox`

定义“怎么隔离执行”：

- 代码执行
- shell 执行
- 工具副作用隔离

### `ai-studio-accelerator`

定义“怎么挂可选推理加速依赖”：

- PyTorch / torchaudio / torchvision 的安装矩阵
- `vllm` / `mlx` / quantization 这类可选依赖组
- `flash-attn` 这种需要单独壳处理的附属包

## 包之间的依赖方向

当前目标依赖方向是：

```text
ai-studio-core <- ai-studio-ext / ai-studio-client / ai-studio-sandbox / ai-studio-serve <- ai-studio-app
ai-studio-acc-auto <- ai-studio-app
```

这意味着：

1. `core` 不依赖任何上层包
2. `ext` / `client` / `sandbox` / `serve` 都不能依赖 `app`
3. `app` 是最外层，只负责装配

### 当前实际依赖声明

目前根 `pyproject.toml` 和各子包 `pyproject.toml` 已经表达了一个更保守的版本：

- `ext -> core`
- `client -> core`
- `sandbox -> core`
- `serve -> core`
- `app -> core/ext/client/serve/sandbox/acc-auto`

其中 `acc-flash-attn` 不直接被 `app` 依赖，而是通过 `ai-studio-acc-auto[flash_attn]` 这类可选 extra 间接挂入。

这里故意没有把 `serve -> ext` 直接写死，因为当前仓库还没长到需要那层耦合的程度。

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

`AI Studio` 现在学的是 `Umber Studio` 的这几件事：

- package 分层方式
- 单向依赖方向
- `core / ext / serve / app / client / sandbox / accelerator` 的职责划分

但暂时**不学**这些东西：

- 同等规模的历史包袱
- 已经存在的业务域复杂度
- 过早的目录膨胀

## 一句话收口

当前 `AI Studio` 的 packages 架构，不是要一夜之间复制 `Umber Studio`，而是：

**先把正确的包边界立住，再按这个边界慢慢长功能。**
