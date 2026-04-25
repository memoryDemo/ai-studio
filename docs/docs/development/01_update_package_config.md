# 补 package 配置和启动壳
> 把 `uv init` 生成的默认壳，整理成真正可跑的 workspace 项目

上一节只做了目录和分层。这一节开始把配置接起来。

## 1. 先处理根项目冲突

`uv init` 生成的根项目默认也叫 `meyo`，但 `core` 包我们也要命名成 `meyo`。

这会导致 `uv sync --all-packages` 报重名冲突。

所以先把根 `pyproject.toml` 改成：

```toml
[project]
name = "meyo-mono"
```

根项目只是 workspace 容器，不参与真正的 CLI 命名。

## 2. 删除默认入口

`uv init` 默认会生成两类入口：

1. 根目录 `main.py`
2. 每个 package 里的默认 `[project.scripts]`

这些先删掉，只保留一个真正的总入口。

要删的东西：

```python
# /main.py
def main():
    print("Hello from Meyo!")
```

以及各 package 默认生成的：

```toml
[project.scripts]
meyo-* = "xxx:main"
```

## 3. 把本地包声明成 workspace source

根 `pyproject.toml` 里补上：

```toml
[tool.uv.sources]
meyo = { workspace = true }
meyo-accelerator = { workspace = true }
meyo-app = { workspace = true }
meyo-client = { workspace = true }
meyo-ext = { workspace = true }
meyo-sandbox = { workspace = true }
meyo-serve = { workspace = true }
```

这样 `uv` 才会优先使用本地 workspace 里的包，而不是去外面找。

## 4. 补 package 依赖

按当前技术栈，依赖分两类看：

- 包之间的依赖：谁依赖谁
- 第三方依赖：FastAPI、LangGraph、数据库驱动这些装在哪里

这里参考 `Umber Studio` 的做法：

- `core` 包名直接叫 `meyo`
- `core` 默认依赖保持轻量
- Web、Runtime、DB、观测这类依赖通过 optional extras 打开
- `app` 作为最终装配层，一次性选择需要的 extras

`meyo-core`

```toml
dependencies = [
    "pydantic>=2.6,<3.0",
]

[project.optional-dependencies]
cli = [
    "click>=8.1.0,<9.0.0",
    "rich>=13.0,<15.0",
    "tomlkit>=0.13,<1.0",
]
client = [
    "httpx>=0.24,<1.0",
    "tenacity>=8.0,<10.0",
]
simple_framework = [
    "aiofiles>=24.0,<25.0",
    "fastapi>=0.136,<0.137",
    "gunicorn>=23.0,<24.0",
    "pydantic-settings>=2.0,<3.0",
    "python-multipart>=0.0.20,<1.0",
    "uvicorn[standard]>=0.46,<0.47",
]
runtime = [
    "langchain-core>=1.0,<2.0",
    "langgraph>=1.0,<2.0",
]
framework = [
    "alembic>=1.13,<2.0",
    "jsonschema>=4.0,<5.0",
    "SQLAlchemy>=2.0,<3.0",
]
proxy_openai = [
    "httpx[socks]>=0.24,<1.0",
    "openai>=1.59,<3.0",
    "tiktoken>=0.8,<1.0",
]
tool = [
    "mcp>=1.0,<2.0",
]
observability = [
    "langfuse>=3.0,<4.0",
    "opentelemetry-api>=1.28,<2.0",
    "opentelemetry-exporter-otlp>=1.28,<2.0",
    "opentelemetry-instrumentation-fastapi>=0.50b0,<1.0",
    "opentelemetry-sdk>=1.28,<2.0",
    "prometheus-client>=0.20,<1.0",
    "structlog>=24.0,<26.0",
]
```

`meyo-ext`

```toml
dependencies = [
    "meyo",
]

[project.optional-dependencies]
storage_postgres = [
    "asyncpg>=0.29,<1.0",
    "psycopg[binary,pool]>=3.2,<4.0",
]
storage_redis = [
    "redis>=5.0,<8.0",
]
storage_milvus = [
    "pymilvus>=2.4,<3.0",
]
storage_neo4j = [
    "neo4j>=5.0,<7.0",
]
file_s3 = [
    "boto3>=1.34,<2.0",
    "minio>=7.0,<8.0",
]
```

`meyo-client`

```toml
dependencies = [
    "meyo[client,cli]",
    "meyo-ext",
]
```

`meyo-serve`

```toml
dependencies = [
    "meyo-ext",
]
```

`meyo-sandbox`

```toml
dependencies = []
```

`meyo-accelerator`

```toml
dependencies = []
```

`meyo-app`

```toml
dependencies = [
    "meyo",
    "meyo-accelerator",
    "meyo-client",
    "meyo-ext",
    "meyo-sandbox",
    "meyo-serve",
]

[project.optional-dependencies]
base = [
    "meyo[cli,client,framework,runtime,simple_framework,tool]",
]
siliconflow = [
    "meyo[proxy_openai]",
]
pg_milvus_neo4j = [
    "meyo-ext[storage_postgres,storage_milvus,storage_neo4j]",
]
```

这里的重点是：

- `FastAPI / Uvicorn` 不直接写在 `app`，而是从 `meyo[simple_framework]` 打开
- `LangGraph` 从 `meyo[runtime]` 打开
- `OpenAI / tiktoken` 从 `meyo[proxy_openai]` 打开，SiliconFlow LLM 也复用这一组
- `MCP` 从 `meyo[tool]` 打开
- `PostgreSQL / Milvus / Neo4j` 从 `meyo-ext[...]` 按需打开

## 5. 只保留一个 CLI 入口

真正的 CLI 入口放在 `core` 包：

```toml
[project.scripts]
meyo = "meyo.cli.cli_scripts:main"
```

文件位置：

- `packages/meyo-core/src/meyo/cli/cli_scripts.py`

这一层只做两件事：

- 注册 `meyo`
- 挂 `start` 子命令

## 6. app 层补启动壳

`app` 包里补 4 个文件：

- `packages/meyo-app/src/meyo_app/_cli.py`
- `packages/meyo-app/src/meyo_app/cli.py`
- `packages/meyo-app/src/meyo_app/meyo_server.py`
- `packages/meyo-app/src/meyo_app/config.py`

职责分别是：

- `_cli.py`：定义 `webserver` 命令
- `cli.py`：对外公开导出 `start_webserver`
- `meyo_server.py`：真正执行启动逻辑
- `config.py`：解析 `--config` 和读取 TOML

当前这版最小链路是：

```text
uv run meyo start webserver --config meyo.toml
-> pyproject.toml [project.scripts]
-> meyo.cli.cli_scripts:main
-> meyo_app.cli.start_webserver
-> meyo_app.meyo_server.run_webserver
```

## 7. 配置文件解析规则

当前 `config.py` 的规则是：

- 传真实绝对路径，直接用
- 传 `meyo.toml`，回退到 `configs/meyo.toml`
- 传 `/meyo.toml` 这类伪绝对路径，也回退到 `configs/meyo.toml`
- 不传时，默认找 `configs/meyo.toml`

所以这两种写法都可以：

```shell
uv run meyo start webserver --config meyo.toml
uv run meyo start webserver --config /meyo.toml
```

## 8. 同步依赖并启动

因为根项目本身不承载业务依赖，统一用：

```shell
uv sync --all-packages \
  --extra "base" \
  --extra "siliconflow"
```

先看 CLI 有没有挂上：

```shell
uv run meyo --help
```

再启动：

```shell
uv run meyo start webserver --config meyo.toml
```

当前这版会启动一个最小 FastAPI WebServer。

```text
http://0.0.0.0:5670
```

可以用下面三个地址确认链路：

```shell
curl http://127.0.0.1:5670/
curl http://127.0.0.1:5670/api/healthz
curl http://127.0.0.1:5670/api/hello
```

## 9. 到这里得到什么

做完这一步，项目已经从：

- 根 `main.py`
- 每个包各自一个默认入口

变成：

- 一个统一的 workspace
- 一个统一的 CLI 入口
- 一个最小可跑的 FastAPI WebServer
- 一套按技术栈分层的核心依赖

后面再继续往里补业务代码就行。
