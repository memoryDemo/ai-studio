---
title: 部署流程
---

# 部署流程

这篇是 Meyo `dev.yml` 的完整部署流程。目标是：拿到一台新的 Linux 服务器后，可以按步骤部署出和 117 环境一致的 dev 栈。

本文默认：

- 服务器用 root 部署。
- 代码部署到 `/root/docker/meyo`。
- Compose 文件是 `/root/docker/meyo/dev.yml`。
- 对外只暴露 `14000` 作为 Chatbot 和 Studio Flow 入口。
- 中间件端口使用 `14001` 到 `14010`。

:::warning
流程里的 `.env` 只展示变量名和占位值。真实 API key、数据库密码、对象存储密码必须从安全渠道传到服务器，不要提交到 Git。
:::

## 1. 目标拓扑

部署完成后，对外访问：

| 功能 | URL |
|---|---|
| Chatbot / Open WebUI | `http://<server-ip>:14000/` |
| Studio Flow / Langflow | `http://<server-ip>:14000/studio/` |

容器拓扑：

| 服务 | 容器名 | 宿主机端口 |
|---|---|---|
| Meyo + Chatbot + Studio Flow + Nginx | `meyo-stack` | `14000` |
| PostgreSQL | `meyo-postgres` | `14001` |
| Redis Stack | `meyo-redis-stack` | `14002`, `14003` |
| Neo4j | `meyo-neo4j` | `14004`, `14005` |
| Etcd | `meyo-etcd` | `14006` |
| MinIO | `meyo-minio` | `14007`, `14008` |
| Milvus | `meyo-milvus` | `14009`, `14010` |

`meyo-stack` 内部进程：

| 进程 | 容器内地址 |
|---|---|
| Meyo API | `127.0.0.1:5670` |
| Chatbot / Open WebUI | `127.0.0.1:8080` |
| Studio Flow / Langflow | `127.0.0.1:7860` |
| Nginx | `0.0.0.0:80` |

## 2. 服务器准备

### 2.1 基础条件

新服务器需要满足：

- Linux x86_64。
- 能访问 Docker 镜像源、npm 镜像源、PyPI 镜像源。
- 防火墙或安全组放开 `14000`。
- 如果需要外部调试中间件，再按需放开 `14001` 到 `14010`；生产或公网环境不建议直接暴露中间件端口。
- 有足够磁盘空间构建镜像，建议至少 40GB 可用空间。

### 2.2 安装基础工具

Debian / Ubuntu：

```shell
apt-get update
apt-get install -y ca-certificates curl gnupg git rsync lsof netcat-openbsd
```

### 2.3 安装 Docker 和 Compose 插件

Debian 示例：

```shell
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian ${VERSION_CODENAME} stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Ubuntu 服务器把上面的 Docker 源路径从 `linux/debian` 改成 `linux/ubuntu`。

验证：

```shell
docker version
docker compose version
docker run --rm hello-world
```

## 3. 上传代码

在本地仓库根目录执行。117 环境示例：

```shell
export SERVER=117.72.36.99
export KEY=/Users/memory/Downloads/nutritionist.pem
export REMOTE_DIR=/root/docker/meyo

ssh -i "$KEY" -o StrictHostKeyChecking=no root@$SERVER "mkdir -p $REMOTE_DIR"

rsync -az --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude 'apps/meyo-chatbot/backend/open_webui/data' \
  -e "ssh -i $KEY -o StrictHostKeyChecking=no" \
  ./ root@$SERVER:$REMOTE_DIR/
```

如果是在服务器上直接拉代码，也可以：

```shell
mkdir -p /root/docker
cd /root/docker
git clone <repo-url> meyo
cd /root/docker/meyo
```

## 4. 准备运行时环境变量

需要两个 env 文件：

| 文件 | 用途 |
|---|---|
| `/root/docker/meyo/.env` | Meyo 后端、模型 provider、中间件通用变量 |
| `/root/docker/meyo/apps/meyo-chatbot/.env` | Chatbot / Open WebUI 运行变量 |

从本地上传：

```shell
scp -i "$KEY" .env root@$SERVER:/root/docker/meyo/.env
scp -i "$KEY" apps/meyo-chatbot/.env root@$SERVER:/root/docker/meyo/apps/meyo-chatbot/.env

ssh -i "$KEY" root@$SERVER \
  'chmod 600 /root/docker/meyo/.env /root/docker/meyo/apps/meyo-chatbot/.env'
```

如果是新服务器手工创建，最小示例：

```shell
cd /root/docker/meyo
cat > .env <<'EOF'
MEYO_LANG=zh
MEYO_LOG_LEVEL=INFO
MEYO_ENCRYPT_KEY=<replace-with-long-random-secret>

SILICONFLOW_API_KEY=<replace-with-siliconflow-api-key>
MEYO_LANGUAGE_MODEL_NAME=Pro/zai-org/GLM-5.1
MEYO_EMBEDDING_MODEL_NAME=Qwen/Qwen3-Embedding-8B
MEYO_RERANKER_MODEL_NAME=BAAI/bge-reranker-v2-m3
EOF

mkdir -p apps/meyo-chatbot
cat > apps/meyo-chatbot/.env <<'EOF'
ENABLE_OPENAI_API=true
ENABLE_OLLAMA_API=false
OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1
OPENAI_API_KEY=<replace-with-runtime-api-key-or-placeholder>

RAG_EMBEDDING_ENGINE=openai
RAG_OPENAI_API_BASE_URL=http://127.0.0.1:5670/api/v1
RAG_OPENAI_API_KEY=<replace-with-runtime-api-key-or-placeholder>
RAG_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-8B
RAG_EMBEDDING_MODEL_AUTO_UPDATE=false
RAG_RERANKING_MODEL_AUTO_UPDATE=false
OFFLINE_MODE=true
EOF

chmod 600 .env apps/meyo-chatbot/.env
```

说明：

- Chatbot RAG embedding 必须走 `http://127.0.0.1:5670/api/v1`，也就是 Meyo API。
- 这样 Open WebUI 不会在启动时去 HuggingFace 下载 `sentence-transformers/all-MiniLM-L6-v2`。
- Meyo API 再根据 `SILICONFLOW_API_KEY` 和模型配置调用硅基流动。
- `.env` 不在镜像 build context 里，必须作为运行时文件放到远程目录。

## 5. 检查 Compose 配置

在服务器执行：

```shell
cd /root/docker/meyo
docker compose -f dev.yml config --quiet
```

确认关键变量已经进入 `meyo-stack`：

```shell
docker compose -f dev.yml config | grep -E 'SILICONFLOW|RAG_|MEYO_|OPENAI|LANGFLOW_STORE'
```

输出里应该能看到变量名和值。检查时不要把真实 key 复制到聊天、文档或工单里。

确认没有历史旧容器名：

```shell
docker compose -f dev.yml config | grep -E 'container_name:|image:|ports:'
```

服务名、容器名应该统一是 `meyo-*`。

## 6. 如果服务器上有历史旧栈

如果这台机器以前跑过旧栈，先停掉旧 Compose 项目，避免端口和数据目录冲突。

117 环境的历史路径示例：

```shell
cd /root/docker/umber_studio
docker compose -f docker-compose.local-pg-milvus.yml down
```

确认旧容器不再运行：

```shell
docker ps -a --format '{{.Names}}' | grep -E '^umber-studio-' || true
```

没有输出即可。

## 7. 构建业务镜像

在服务器执行：

```shell
cd /root/docker/meyo
docker compose -f dev.yml build meyo-stack
```

如果服务器的 BuildKit 或网络有问题，可以用 classic builder 重新试：

```shell
DOCKER_BUILDKIT=0 docker compose -f dev.yml build meyo-stack
```

117 环境为了提高成功率，Dockerfile 已经做过这些处理：

- 不依赖 `docker/dockerfile:1.7` syntax image。
- 不依赖 BuildKit cache mount。
- 不从 `ghcr.io/astral-sh/uv` 拉 uv 基础镜像。
- apt、pip、uv、npm 使用国内镜像。
- `uv.lock` 的 `files.pythonhosted.org` 直链在构建时改到镜像源。
- PyTorch 固定 CPU wheel。
- 跳过 Cypress binary 和 ONNXRuntime CUDA 下载。

## 8. 启动服务

首次启动全部服务：

```shell
cd /root/docker/meyo
docker compose -f dev.yml up -d
```

如果只是改了 Meyo、Chatbot、Studio Flow、Dockerfile 或 `meyo-stack` 环境变量，中间件不用动，只重建业务容器：

```shell
cd /root/docker/meyo
docker compose -f dev.yml build meyo-stack
docker compose -f dev.yml up -d --no-deps --force-recreate meyo-stack
```

查看状态：

```shell
docker compose -f dev.yml ps
```

## 9. 等待入口真正可用

`meyo-stack` healthy 不等于 Chatbot 和 Studio Flow 都已经可访问。必须检查 `/` 和 `/studio/`。

在服务器执行：

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

注意：

- zsh 里 `status` 是只读变量，脚本里用 `health`。
- `/studio/` 短时间 `502` 通常是 Langflow 还没启动完。
- 如果长时间不是 `200`，看 `docker logs meyo-stack`。

## 10. 验证中间件

PostgreSQL：

```shell
docker exec meyo-postgres pg_isready -U meyo -d meyo
```

Redis：

```shell
docker exec meyo-redis-stack redis-cli -a '<redis-password-from-dev-yml>' PING
```

MinIO：

```shell
docker exec meyo-minio curl -fsS http://127.0.0.1:9000/minio/health/live
```

Milvus：

```shell
docker exec meyo-milvus sh -lc 'nc -z 127.0.0.1 19530'
```

Compose 状态：

```shell
docker compose -f dev.yml ps
```

## 11. 验证 Meyo 模型服务

不要用未登录的 Open WebUI API 判断模型服务是否正常。`/api/models` 可能返回 `Not authenticated`，这是 Open WebUI 鉴权，不代表 Meyo API 异常。

用 `meyo-stack` 内部的 Meyo API 验证模型列表：

```shell
docker exec meyo-stack curl -sS --max-time 10 \
  http://127.0.0.1:5670/api/v1/models | head -c 1200
```

返回里应该能看到：

```text
Pro/zai-org/GLM-5.1
Qwen/Qwen3-Embedding-8B
BAAI/bge-reranker-v2-m3
```

验证 embedding：

```shell
cat <<'JSON' | docker exec -i meyo-stack sh -lc \
  'curl -sS --max-time 30 -X POST http://127.0.0.1:5670/api/v1/embeddings \
  -H "Content-Type: application/json" -d @- -o /tmp/embed.json \
  -w "embedding_http:%{http_code} bytes:%{size_download}\n"; head -c 160 /tmp/embed.json; echo'
{"model":"Qwen/Qwen3-Embedding-8B","input":"hello"}
JSON
```

期望：

```text
embedding_http:200
```

## 12. 验证公网入口

从本地或任意外部机器执行：

```shell
export SERVER=117.72.36.99

curl -sS -o /tmp/meyo_public_root -w 'public_root:%{http_code} bytes:%{size_download}\n' \
  --max-time 15 http://$SERVER:14000/

curl -sS -o /tmp/meyo_public_studio -w 'public_studio:%{http_code} bytes:%{size_download}\n' \
  --max-time 15 http://$SERVER:14000/studio/
```

期望两个都是 `200`。

浏览器访问：

- `http://117.72.36.99:14000/`
- `http://117.72.36.99:14000/studio/`

## 13. 常用运维命令

查看服务：

```shell
cd /root/docker/meyo
docker compose -f dev.yml ps
```

查看业务日志：

```shell
docker logs -f meyo-stack
```

只重启业务容器：

```shell
docker compose -f dev.yml up -d --no-deps --force-recreate meyo-stack
```

修改 `dev.yml` 或 env 后重新应用：

```shell
docker compose -f dev.yml config --quiet
docker compose -f dev.yml up -d --no-deps --force-recreate meyo-stack
```

修改 Dockerfile 或源码后重建：

```shell
docker compose -f dev.yml build meyo-stack
docker compose -f dev.yml up -d --no-deps --force-recreate meyo-stack
```

停止整套 dev 栈：

```shell
docker compose -f dev.yml down
```

查看端口占用：

```shell
lsof -iTCP -sTCP:LISTEN -P -n | grep -E '14000|14001|14002|14003|14004|14005|14006|14007|14008|14009|14010'
```

## 14. 部署完成检查清单

部署完成前逐项确认：

- `docker compose -f dev.yml config --quiet` 通过。
- `docker compose -f dev.yml ps` 中核心服务 healthy。
- 没有历史旧容器继续占用端口。
- `http://<server-ip>:14000/` 返回 `200`。
- `http://<server-ip>:14000/studio/` 返回 `200`。
- Postgres `pg_isready` 通过。
- Redis 返回 `PONG`。
- MinIO live health 通过。
- Milvus `19530` TCP 探测通过。
- Meyo `/api/v1/models` 返回 LLM、embedding、reranker。
- Meyo `/api/v1/embeddings` 用 `Qwen/Qwen3-Embedding-8B` 返回 `200`。
- Chatbot RAG env 指向 `http://127.0.0.1:5670/api/v1`，不会启动时拉 HuggingFace 本地模型。
- `docker logs meyo-stack --tail=300` 没有持续重启、`Unknown level`、`controller_addr` 或 Langflow 长时间卡住的错误。

