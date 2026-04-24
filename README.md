# Meyo

Meyo 是一个私有化的 `LangGraph-first` AgentOS 框架壳。

名字来自 `张梦瑶` 的音感变体：从 `Mengyao` 收敛成更短、更像框架名的 `Meyo`。它不追求公开营销感，目标是作为这个项目长期使用的私有化框架品牌。

## 定位

Meyo 目标是为上层 AI 应用提供统一的：

- agent runtime
- knowledge / skill
- memory OS
- tool mesh
- observability

当前阶段先把 `uv workspace + 多 package + CLI + WebServer` 的壳搭稳，再逐步补业务能力。

## 项目分层

当前仓库采用向 `Umber Studio` 对齐的多 package 分层，但规模先保持克制。

| Package | Python import | 职责 |
|---|---|---|
| `packages/meyo-core` | `meyo` | 主包、CLI 总入口、核心 extras |
| `packages/meyo-ext` | `meyo_ext` | 外部系统适配，PG / Redis / Milvus / Neo4j / S3 |
| `packages/meyo-client` | `meyo_client` | SDK / API client 边界 |
| `packages/meyo-serve` | `meyo_serve` | 服务层与应用服务编排 |
| `packages/meyo-app` | `meyo_app` | 启动、配置、FastAPI WebServer 装配 |
| `packages/meyo-sandbox` | `meyo_sandbox` | 受控执行与沙箱能力边界 |
| `packages/meyo-accelerator` | `meyo_accelerator` | 可选加速能力边界 |

依赖方向：

```text
meyo <- meyo-ext / meyo-client / meyo-serve <- meyo-app
```

`meyo-app` 作为最终装配层，会同时依赖 `meyo-sandbox` 和 `meyo-accelerator`。

## 文档

文档工作区位于 [docs](./docs)，使用 Docusaurus。

核心文档：

- [基座项目总览](./docs/docs/application/base_project/index.md)
- [Meyo 企业级 AgentOS 架构设计文档](./docs/docs/application/base_project/architecture_design.md)
- [Meyo 功能设计](./docs/docs/application/base_project/functional_design.md)
- [Meyo 技术栈](./docs/docs/application/base_project/technology_stack.md)
- [Meyo Memory OS 设计](./docs/docs/application/base_project/memory_os_design.md)
- [从零开始上手 uv 与 package 加载链路](./docs/docs/application/base_project/from_zero_to_running.md)

## 最小启动

先同步 workspace：

```bash
uv sync --all-packages
```

查看 CLI：

```bash
uv run meyo --help
uv run meyo start --help
```

启动当前最小 WebServer：

```bash
uv run meyo start webserver --config /my/dev.toml
```

`--config /my/dev.toml` 会映射到：

```text
configs/my/dev.toml
```

访问：

```bash
curl http://127.0.0.1:5670/
curl http://127.0.0.1:5670/api/healthz
curl http://127.0.0.1:5670/api/hello
```
