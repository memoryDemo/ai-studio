---
title: 部署常见问题
---

# 部署常见问题

这篇记录 Meyo `dev.yml` 部署到 117 环境时实际遇到的问题、原因、处理方式和验证方法。

117 环境基线：

| 项 | 值 |
|---|---|
| 服务器 | `117.72.36.99` |
| 部署目录 | `/root/docker/meyo` |
| Compose 文件 | `/root/docker/meyo/dev.yml` |
| Compose 项目名 | `meyo` |
| Chatbot / Open WebUI | `http://117.72.36.99:14000/` |
| Studio Flow / Langflow | `http://117.72.36.99:14000/studio/` |
| 对外入口 | 宿主机 `14000` -> `meyo-stack:80` |

:::warning
不要把真实 `.env`、API key、数据库密码、对象存储密码写进文档或提交到仓库。本文只记录配置项名称和处理原则。
:::

## 1. 端口和服务怎么判断

`meyo-stack` 里同时跑 Meyo API、Chatbot、Studio Flow 和 Nginx：

| 组件 | 容器内地址 | 宿主机访问 |
|---|---|---|
| Nginx 入口 | `0.0.0.0:80` | `http://117.72.36.99:14000/` |
| Meyo API | `127.0.0.1:5670` | 不直接暴露 |
| Chatbot / Open WebUI | `127.0.0.1:8080` | `http://117.72.36.99:14000/` |
| Studio Flow / Langflow | `127.0.0.1:7860` | `http://117.72.36.99:14000/studio/` |

中间件容器和宿主机端口：

| 容器 | 宿主机端口 |
|---|---|
| `meyo-postgres` | `14001` |
| `meyo-redis-stack` | `14002`, `14003` |
| `meyo-neo4j` | `14004`, `14005` |
| `meyo-etcd` | `14006` |
| `meyo-minio` | `14007`, `14008` |
| `meyo-milvus` | `14009`, `14010` |
| `meyo-stack` | `14000` |

判断部署成功不能只看容器是否 running，至少要同时满足：

- `docker compose -f dev.yml ps` 显示核心服务 healthy。
- `http://117.72.36.99:14000/` 返回 `200`。
- `http://117.72.36.99:14000/studio/` 返回 `200`。
- `meyo-stack` 内部 `http://127.0.0.1:5670/api/v1/models` 能返回模型列表。
- 通过 Meyo API 调 embedding 能返回 `200`。

## 2. 构建和启动类问题

### 2.1 `vite.config.mts` 报 TS1259

表现：

```text
TS1259: Module "path" can only be default-imported using the esModuleInterop flag
```

位置：

```text
apps/meyo-studio-flow/src/frontend/vite.config.mts
```

原因：

`node:path` / `path` 在 TypeScript 类型里是 `export =` 模块。项目没有打开 `esModuleInterop` 时，不能写默认导入。

处理：

```ts
import * as path from "node:path";
```

验证：

```shell
docker compose -f dev.yml build meyo-stack
```

### 2.2 历史旧栈名称和新栈名称混用

表现：

- 新部署里还出现历史旧服务名、旧容器名或旧 volume 名。
- 新栈和旧栈同时占用相同宿主机端口。
- 用户访问时不确定命中的是旧服务还是新服务。

原因：

Compose service、container、volume、environment name 没有统一切到 `meyo-*`。

处理：

- 新 `dev.yml` 使用 `meyo-postgres`、`meyo-redis-stack`、`meyo-milvus`、`meyo-stack` 等名称。
- 迁移 117 时，先停止历史旧栈，再启动 Meyo 新栈。
- 新服务统一从 `/root/docker/meyo/dev.yml` 启动。

验证：

```shell
docker ps -a --format '{{.Names}}' | grep -E '^meyo-'
docker ps -a --format '{{.Names}}' | grep -E '^umber-studio-' || true
```

第二条命令没有输出，说明历史旧容器已经不再运行。

### 2.3 `docker/dockerfile:1.7` 或 BuildKit 语法导致远程构建失败

表现：

- 远程服务器拉不到 `docker/dockerfile:1.7`。
- `RUN --mount=type=cache` 这类 BuildKit 语法在当前构建环境不可用。

原因：

117 环境网络和 Docker 构建器能力不稳定，BuildKit-only 语法增加了失败点。

处理：

- 移除 Dockerfile 顶部 `# syntax=docker/dockerfile:1.7`。
- 去掉 BuildKit cache mount，改成普通 `RUN`。
- 必要时用 classic builder 验证：

```shell
DOCKER_BUILDKIT=0 docker compose -f dev.yml build meyo-stack
```

验证：

```shell
docker compose -f dev.yml build meyo-stack
```

### 2.4 `ghcr.io/astral-sh/uv` 拉取失败

表现：

构建早期卡在或失败在拉取 `ghcr.io/astral-sh/uv`。

原因：

远程服务器访问 GitHub Container Registry 不稳定。

处理：

- 改用 `python:<version>-slim-bookworm` 作为 base image。
- 在镜像内通过 pip 安装 `uv`。
- pip 使用国内镜像源。

验证：

```shell
docker compose -f dev.yml build meyo-stack
```

### 2.5 apt / PyPI 下载慢或不可达

表现：

- `apt-get update` 长时间无响应。
- `pip install` / `uv sync` 访问 `pypi.org` 或 `files.pythonhosted.org` 超时。

原因：

服务器到海外包源网络不稳定。

处理：

- Debian apt 源切到清华源。
- pip / uv index 切到清华源。
- 仍然在 `uv.lock` 里出现 `files.pythonhosted.org` 的包，需要在构建阶段把 lockfile 里的直链替换到清华源。

验证：

```shell
docker compose -f dev.yml build meyo-stack
```

### 2.6 PyTorch 拉取 CUDA 大包

表现：

构建时下载大量 CUDA 相关 wheel，速度慢、体积大，容易失败。

原因：

默认 PyPI 解析可能选择 CUDA 版本的 PyTorch 依赖。

处理：

在 Dockerfile 中固定 CPU wheel，例如：

```text
torch==2.9.1+cpu
torchvision==0.24.1+cpu
torchaudio==2.9.1+cpu
```

并使用 PyTorch CPU wheel 镜像。

验证：

```shell
docker compose -f dev.yml build meyo-stack
```

### 2.7 npm、Cypress、ONNXRuntime 额外下载导致构建失败

表现：

- npm install 卡住。
- Cypress 二进制下载失败。
- ONNXRuntime CUDA 包下载失败。

原因：

前端依赖安装会触发额外二进制下载，远程网络不稳定时容易失败。

处理：

- npm registry 使用国内镜像。
- 设置 `CYPRESS_INSTALL_BINARY=0`。
- 设置 `ONNXRUNTIME_NODE_INSTALL_CUDA=skip`。

验证：

```shell
docker compose -f dev.yml build meyo-stack
```

### 2.8 Docker build context 带入密钥和运行时数据

表现：

- 构建上下文非常大。
- `.env`、sqlite、Open WebUI data 这类运行时文件可能被打进镜像上下文。

原因：

`.dockerignore` 没有覆盖 monorepo 中的密钥文件、运行时数据库和缓存目录。

处理：

`.dockerignore` 需要排除：

```text
.env
.env.*
**/.env*
apps/meyo-chatbot/backend/open_webui/data
apps/docs-site
*.sqlite
*.db
```

并保留 `.env.example` 这类示例文件。

验证：

```shell
docker compose -f dev.yml build meyo-stack
```

构建日志里的 context size 应明显下降，且镜像内不应包含真实密钥。

## 3. 环境变量和配置类问题

### 3.1 远程目录缺少 `.env`

表现：

`docker compose config` 里 `SILICONFLOW_API_KEY`、模型配置或 Open WebUI 配置为空。

原因：

`.dockerignore` 正确排除了 `.env`，但部署时忘记把运行时 `.env` 单独传到 `/root/docker/meyo`。

处理：

- 根目录 `.env` 放到 `/root/docker/meyo/.env`。
- Chatbot 专用 env 放到 `/root/docker/meyo/apps/meyo-chatbot/.env`。
- `dev.yml` 里给 `meyo-stack` 配置：

```yaml
env_file:
  - .env
  - apps/meyo-chatbot/.env
```

验证：

```shell
cd /root/docker/meyo
docker compose -f dev.yml config --quiet
docker compose -f dev.yml config | grep -E 'SILICONFLOW|RAG_|MEYO_|OPENAI|LANGFLOW_STORE'
```

检查输出时要确认变量存在，但不要把真实 key 粘贴到聊天、日志或文档。

### 3.2 Chatbot RAG 默认拉 HuggingFace 模型

表现：

Open WebUI 启动时尝试下载：

```text
sentence-transformers/all-MiniLM-L6-v2
```

随后因为容器网络访问 HuggingFace 不通，服务没有正常接起来。

原因：

Open WebUI RAG 默认 embedding 使用本地 sentence-transformers 模型。当前 Meyo 架构里，embedding 应该走 Meyo 的 OpenAI-compatible API，由 Meyo 再调用硅基流动。

处理：

`dev.yml` / Chatbot env 需要明确：

```yaml
RAG_EMBEDDING_ENGINE: ${RAG_EMBEDDING_ENGINE:-openai}
RAG_OPENAI_API_BASE_URL: ${RAG_OPENAI_API_BASE_URL:-http://127.0.0.1:5670/api/v1}
RAG_EMBEDDING_MODEL: ${RAG_EMBEDDING_MODEL:-Qwen/Qwen3-Embedding-8B}
RAG_EMBEDDING_MODEL_AUTO_UPDATE: ${RAG_EMBEDDING_MODEL_AUTO_UPDATE:-false}
RAG_RERANKING_MODEL_AUTO_UPDATE: ${RAG_RERANKING_MODEL_AUTO_UPDATE:-false}
OFFLINE_MODE: ${OFFLINE_MODE:-true}
```

注意：这不是绕过 Meyo，而是让 Chatbot 的 RAG embedding 调 Meyo API；Meyo 再按自己的 provider 配置调用硅基流动。

验证：

```shell
docker exec meyo-stack curl -sS --max-time 10 \
  http://127.0.0.1:5670/api/v1/models | head -c 1200

cat <<'JSON' | docker exec -i meyo-stack sh -lc \
  'curl -sS --max-time 30 -X POST http://127.0.0.1:5670/api/v1/embeddings \
  -H "Content-Type: application/json" -d @- -o /tmp/embed.json \
  -w "embedding_http:%{http_code} bytes:%{size_download}\n"; head -c 160 /tmp/embed.json; echo'
{"model":"Qwen/Qwen3-Embedding-8B","input":"hello"}
JSON
```

117 上最终验证返回 `embedding_http:200`。

### 3.3 `MEYO_LOG_LEVEL=info` 导致启动失败

表现：

```text
ValueError: Unknown level: 'info'
```

原因：

日志初始化逻辑只接受标准大写级别。

处理：

把 env 改成：

```text
MEYO_LOG_LEVEL=INFO
```

或在 `dev.yml` 默认值里使用：

```yaml
MEYO_LOG_LEVEL: ${MEYO_LOG_LEVEL:-INFO}
```

验证：

```shell
docker logs meyo-stack --tail=200 | grep -i 'unknown level' || true
```

### 3.4 pg + Milvus 配置缺少 `controller_addr`

表现：

`meyo-stack` 启动失败，日志里出现：

```text
AttributeError: 'ModelControllerParameters' object has no attribute 'controller_addr'
```

原因：

当前激活的 pg + Milvus 配置缺少模型 API controller 地址。

处理：

在 `configs/meyo-proxy-siliconflow-pg-milvus.toml` 中加入：

```toml
[service.model.api]
controller_addr = "http://127.0.0.1:5670"
```

验证：

```shell
docker compose -f dev.yml up -d --no-deps --force-recreate meyo-stack
docker logs meyo-stack --tail=200 | grep -i 'controller_addr' || true
```

### 3.5 embedding 模型名称不一致

表现：

- `.env` 或 `dev.yml` 里期望 `Qwen/Qwen3-Embedding-8B`。
- 实际配置文件里仍硬编码旧 embedding 名称。
- Chatbot RAG 和 Meyo provider 调用不一致。

原因：

`configs/meyo-proxy-siliconflow-pg-milvus.toml` 没有从环境变量读取模型名。

处理：

配置文件使用 env-driven 写法：

```toml
name = "${env:MEYO_EMBEDDING_MODEL_NAME:-Qwen/Qwen3-Embedding-8B}"
backend = "${env:MEYO_EMBEDDING_MODEL_NAME:-Qwen/Qwen3-Embedding-8B}"
```

同时 reranker 和 LLM 也保持 env-driven。

验证：

```shell
docker exec meyo-stack curl -sS --max-time 10 \
  http://127.0.0.1:5670/api/v1/models | grep -E 'Qwen/Qwen3-Embedding-8B|BAAI/bge-reranker-v2-m3|GLM'
```

### 3.6 Studio Flow 访问 `/studio/` 返回 502

表现：

`http://117.72.36.99:14000/studio/` 返回 `502`。

原因：

Nginx 已启动，但 `langflow` 进程还没有监听 `127.0.0.1:7860`。这通常是启动阶段的短暂状态。

处理：

不要只看 `meyo-stack` healthz。需要等待 `/studio/` 自己返回 `200`。

验证：

```shell
for i in $(seq 1 60); do
  health=$(docker inspect -f '{{.State.Health.Status}}' meyo-stack 2>/dev/null || true)
  root_code=$(curl -sS -o /tmp/meyo_root -w '%{http_code}' --max-time 4 http://127.0.0.1:14000/ 2>/dev/null || true)
  studio_code=$(curl -sS -o /tmp/meyo_studio -w '%{http_code}' --max-time 4 http://127.0.0.1:14000/studio/ 2>/dev/null || true)
  echo "attempt=$i health=$health root=$root_code studio=$studio_code"
  [ "$health" = "healthy" ] && [ "$root_code" = "200" ] && [ "$studio_code" = "200" ] && break
  sleep 5
done
```

### 3.7 Studio Flow 卡在 `Launching Langflow`

表现：

页面能打开，但一直停在 `Launching Langflow`。

原因：

Chatbot env 里有 `OPENAI_API_KEY` 等变量时，Langflow 可能尝试自动存储或校验 provider 环境变量，导致启动阶段阻塞或等待外部 provider。

处理：

在 `dev.yml` 或 env 中设置：

```yaml
LANGFLOW_STORE_ENVIRONMENT_VARIABLES: ${LANGFLOW_STORE_ENVIRONMENT_VARIABLES:-false}
```

Meyo 自己的 provider 配置仍然从 `MEYO_*` 和硅基流动相关变量读取，不依赖 Langflow 自动存储这些环境变量。

验证：

```shell
curl -sS -o /tmp/meyo_studio -w 'studio:%{http_code} bytes:%{size_download}\n' \
  --max-time 10 http://127.0.0.1:14000/studio/
docker logs meyo-stack --tail=300 | grep -i 'Launching Langflow' || true
```

### 3.8 未登录访问 Open WebUI API 返回 `Not authenticated`

表现：

直接请求：

```text
http://127.0.0.1:14000/api/models
```

可能返回：

```json
{"detail":"Not authenticated"}
```

原因：

这是 Open WebUI 自己的鉴权，不代表 Meyo 模型服务不可用。

处理：

- 浏览器里按 Open WebUI 登录态访问 Chatbot。
- 模型健康检查使用 Meyo 内部 API：

```shell
docker exec meyo-stack curl -sS --max-time 10 \
  http://127.0.0.1:5670/api/v1/models
```

验证：

返回里能看到 LLM、embedding、reranker 模型。

### 3.9 zsh 里 `status` 是只读变量

表现：

远程脚本里写：

```shell
status=...
```

在 zsh 下报错：

```text
read-only variable: status
```

原因：

`status` 是 zsh 的特殊只读变量。

处理：

健康检查脚本里不要用 `status`，改用：

```shell
health=$(docker inspect -f '{{.State.Health.Status}}' meyo-stack 2>/dev/null || true)
```

验证：

健康检查循环能正常输出 `health=healthy`。

## 4. 中间件类问题

### 4.1 重建业务栈时中间件不用动

表现：

修改 Dockerfile、Meyo 配置、Chatbot RAG env 后，担心是否需要重启 Postgres、Redis、Milvus、MinIO、Neo4j。

结论：

这类变更只影响 `meyo-stack`，中间件不用重建。推荐只重建和重启业务容器：

```shell
cd /root/docker/meyo
docker compose -f dev.yml build meyo-stack
docker compose -f dev.yml up -d --no-deps --force-recreate meyo-stack
```

验证：

```shell
docker compose -f dev.yml ps
```

中间件容器应保持 healthy，`meyo-stack` 重新变成 healthy。

### 4.2 中间件实际健康检查命令

不要只看端口。117 上使用过的最小探测如下：

```shell
docker exec meyo-postgres pg_isready -U meyo -d meyo

docker exec meyo-redis-stack redis-cli -a '<redis-password>' PING

docker exec meyo-minio curl -fsS http://127.0.0.1:9000/minio/health/live

docker exec meyo-milvus sh -lc 'nc -z 127.0.0.1 19530'
```

Redis 密码从 `dev.yml` 的 Redis 配置读取，不要写进文档。

## 5. 117 最终验收结果

117 环境最终验收时的关键结果：

| 检查项 | 结果 |
|---|---|
| `docker compose -f dev.yml ps` | 核心服务 healthy |
| `meyo-stack` image | `meyo-stack:dev` |
| Chatbot | `http://117.72.36.99:14000/` 返回 `200` |
| Studio Flow | `http://117.72.36.99:14000/studio/` 返回 `200` |
| Postgres | `pg_isready` OK |
| Redis | `PONG` |
| MinIO | live health OK |
| Milvus | TCP `19530` OK |
| Meyo 模型列表 | 返回 LLM、embedding、reranker |
| Meyo embedding | `Qwen/Qwen3-Embedding-8B` 返回 `200` |

验收命令：

```shell
curl -sS -o /tmp/meyo_public_root -w 'public_root:%{http_code} bytes:%{size_download}\n' \
  --max-time 15 http://117.72.36.99:14000/

curl -sS -o /tmp/meyo_public_studio -w 'public_studio:%{http_code} bytes:%{size_download}\n' \
  --max-time 15 http://117.72.36.99:14000/studio/

docker exec meyo-stack curl -sS --max-time 10 \
  http://127.0.0.1:5670/api/v1/models | head -c 1200

cat <<'JSON' | docker exec -i meyo-stack sh -lc \
  'curl -sS --max-time 30 -X POST http://127.0.0.1:5670/api/v1/embeddings \
  -H "Content-Type: application/json" -d @- -o /tmp/embed.json \
  -w "embedding_http:%{http_code} bytes:%{size_download}\n"; head -c 160 /tmp/embed.json; echo'
{"model":"Qwen/Qwen3-Embedding-8B","input":"hello"}
JSON
```

