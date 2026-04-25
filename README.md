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
| `apps/meyo-chatbot` | 客户聊天前端，基于 Open WebUI，包含 SvelteKit 前端和 Open WebUI FastAPI 后端 |
| `apps/meyo-studio-flow` | 可视化 Agent / Workflow 编排平台，基于 Langflow，作为 Meyo 的低代码工作流实验台 |
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

## Meyo Chatbot 客户前端

`apps/meyo-chatbot` 是独立的 Open WebUI 应用，不直接 import `packages/meyo-*`。它包含：

- `src/`：SvelteKit 前端
- `backend/open_webui/`：Open WebUI FastAPI 后端
- `backend/open_webui/routers/openai.py`：OpenAI-compatible provider 代理
- `backend/data/`：默认本地数据目录，未配置外部数据库时会使用 SQLite

推荐接入链路：

```text
浏览器 -> apps/meyo-chatbot 前端 -> apps/meyo-chatbot 后端 /openai -> Meyo /api/v1 -> model provider
```

先启动 Meyo 后端：

```bash
uv run meyo start webserver --config meyo.toml
```

然后配置 Meyo Chatbot 连接 Meyo 的模型接口：

```bash
cd apps/meyo-chatbot

export ENABLE_OPENAI_API=true
export ENABLE_OLLAMA_API=false
export OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1
export OPENAI_API_KEY=
```

如果 Meyo 在 `[service.model.api]` 配置了 `api_keys`，这里的 `OPENAI_API_KEY` 必须填对应 key；如果未配置，开发环境可以留空。

首次本地启动 Meyo Chatbot：

```bash
cd apps/meyo-chatbot

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
cd apps/meyo-chatbot
source .venv/bin/activate

export ENABLE_OPENAI_API=true
export ENABLE_OLLAMA_API=false
export OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1

open-webui dev --host 0.0.0.0 --port 8080
```

另开一个终端：

```bash
cd apps/meyo-chatbot
npm run dev
```

在 Docker Compose 或容器网络里，`OPENAI_API_BASE_URL` 不要写 `127.0.0.1`，应写 Meyo 服务名，例如：

```bash
export OPENAI_API_BASE_URL=http://meyo-api:5670/api/v1
```

## Meyo Studio Flow 工作流编排平台

`apps/meyo-studio-flow` 是独立的 Langflow 源码副本，不直接 import `packages/meyo-*`，也不进入根 `uv workspace`。它从本地 Langflow 仓库复制而来，并排除了 `.git`、虚拟环境、`node_modules`、构建产物、缓存、文档资源和 IDE 本地配置。

Langflow 的主要用途是：

- 用可视化画布搭建 AI agent / workflow
- 组合 LLM、Prompt、工具、向量数据库、检索和多 agent 流程
- 在 Playground 里调试流程
- 把流程发布为 API 或 MCP server，供外部系统调用

放进 Meyo 的定位是“工作流实验台”和“可视化编排层”：Meyo 负责沉淀平台级 runtime、memory、knowledge、tool mesh 和治理边界；Langflow 用来快速搭流程、验证节点组合、把成熟流程再接回 Meyo 的 API / MCP / 工具体系。

### 启动 Langflow

Langflow 是独立源码项目，启动时要进入它自己的目录。首次启动前建议先准备本地 `.env`。当前 `apps/meyo-studio-flow/.env.example` 已经填了本地启动所需的布尔、端口和缓存默认值，不要把这些 typed 配置留成空字符串。

```bash
cd apps/meyo-studio-flow

cp .env.example .env
```

然后启动 Langflow：

```bash
make run_cli open_browser=false
```

`make run_cli` 会安装后端依赖、安装前端依赖、构建前端，然后通过 `uv run langflow run` 启动服务。首次运行会比较慢，后续会复用缓存。

默认访问：

```text
http://127.0.0.1:7860
```

如果 `7860` 端口被占用，可以换端口：

```bash
make run_cli open_browser=false port=7861
```

如果要让 Langflow 调 Meyo 当前的 OpenAI-compatible 模型服务，另开一个终端启动 Meyo：

```bash
cd <repo-root>
uv run meyo start webserver --config meyo.toml
```

然后在 Langflow 的模型组件里使用：

```text
OpenAI API Base URL: http://127.0.0.1:5670/api/v1
OpenAI API Key: 按 configs/meyo.toml 的 service.model.api.api_keys 配置填写；开发环境未配置时可留空
```

为了不改 Langflow 原生 provider，Meyo Studio Flow 额外新增了独立的 `Meyo` 组件分类，里面提供两个自定义模型组件：`Meyo Language Model` 和 `Meyo Embedding Model`。可以在 `apps/meyo-studio-flow/.env` 里配置默认值：

```env
MEYO_OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1
MEYO_LANGUAGE_MODEL_NAME=Pro/zai-org/GLM-5.1
MEYO_EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-8B
MEYO_OPENAI_API_KEY=
```

已有 Flow 里的旧节点不会自动改值，需要手动更新节点字段或重新拖一个新的 Meyo 节点。
