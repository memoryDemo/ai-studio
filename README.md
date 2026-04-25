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

当前仓库采用 Meyo 自己的多 package 分层，规模先保持克制。

应用项目放在 `apps/` 下，核心 Python 能力放在 `packages/` 下。

| App | 职责 |
|---|---|
| `apps/chatbot` | 客户聊天前端，基于 Open WebUI，包含 SvelteKit 前端和 Open WebUI FastAPI 后端 |
| `apps/docs-site` | Docusaurus 文档站 |

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

文档工作区位于 [apps/docs-site](./apps/docs-site)，使用 Docusaurus。

核心文档：

- [基座项目总览](./apps/docs-site/docs/application/base_project/index.md)
- [Meyo 企业级 AgentOS 架构设计文档](./apps/docs-site/docs/application/base_project/architecture_design.md)
- [Meyo 功能设计](./apps/docs-site/docs/application/base_project/functional_design.md)
- [Meyo 技术栈](./apps/docs-site/docs/application/base_project/technology_stack.md)
- [Meyo Memory OS 设计](./apps/docs-site/docs/application/base_project/memory_os_design.md)
- [从零开始上手 uv 与 package 加载链路](./apps/docs-site/docs/application/base_project/from_zero_to_running.md)

## 最小启动

先按当前后端组合同步 workspace。默认配置使用 SiliconFlow，如果本地要跑 PostgreSQL + Milvus + Neo4j：

```bash
uv sync --all-packages \
  --extra "base" \
  --extra "siliconflow" \
  --extra "pg_milvus_neo4j"
```

查看 CLI：

```bash
uv run meyo --help
uv run meyo start --help
```

启动当前最小 WebServer：

```bash
uv run meyo start webserver --config meyo.toml
```

`--config meyo.toml` 会映射到：

```text
configs/meyo.toml
```

访问：

```bash
curl http://127.0.0.1:5670/
curl http://127.0.0.1:5670/api/healthz
curl http://127.0.0.1:5670/api/hello
```

模型 OpenAI-compatible 接口：

```bash
curl http://127.0.0.1:5670/api/v1/models
```

## Chatbot 客户前端

`apps/chatbot` 是独立的 Open WebUI 应用，不直接 import `packages/meyo-*`。它包含：

- `src/`：SvelteKit 前端
- `backend/open_webui/`：Open WebUI FastAPI 后端
- `backend/open_webui/routers/openai.py`：OpenAI-compatible provider 代理
- `backend/data/`：默认本地数据目录，未配置外部数据库时会使用 SQLite

推荐接入链路：

```text
浏览器 -> apps/chatbot 前端 -> apps/chatbot 后端 /openai -> Meyo /api/v1 -> model provider
```

先启动 Meyo 后端：

```bash
uv run meyo start webserver --config meyo.toml
```

然后配置 chatbot 连接 Meyo 的模型接口：

```bash
cd apps/chatbot

export ENABLE_OPENAI_API=true
export ENABLE_OLLAMA_API=false
export OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1
export OPENAI_API_KEY=
```

如果 Meyo 在 `[service.model.api]` 配置了 `api_keys`，这里的 `OPENAI_API_KEY` 必须填对应 key；如果未配置，开发环境可以留空。

首次本地启动 chatbot：

```bash
cd apps/chatbot

npm install
npm run build

python -m venv .venv
source .venv/bin/activate
pip install -e .

open-webui serve --host 0.0.0.0 --port 8080
```

访问：

```text
http://127.0.0.1:8080
```

前后端分离开发时，后端跑在 `8080`，前端跑在 Vite 默认端口：

```bash
cd apps/chatbot
source .venv/bin/activate

export ENABLE_OPENAI_API=true
export ENABLE_OLLAMA_API=false
export OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1

open-webui dev --host 0.0.0.0 --port 8080
```

另开一个终端：

```bash
cd apps/chatbot
npm run dev
```

在 Docker Compose 或容器网络里，`OPENAI_API_BASE_URL` 不要写 `127.0.0.1`，应写 Meyo 服务名，例如：

```bash
export OPENAI_API_BASE_URL=http://meyo-api:5670/api/v1
```
