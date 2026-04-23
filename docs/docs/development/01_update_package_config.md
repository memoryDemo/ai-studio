# 补 package 配置和启动壳
> 把 `uv init` 生成的默认壳，整理成真正可跑的 workspace 项目

上一节只做了目录和分层。这一节开始把配置接起来。

## 1. 先处理根项目冲突

`uv init` 生成的根项目默认也叫 `ai-studio`，但 `core` 包我们也要命名成 `ai-studio`。

这会导致 `uv sync --all-packages` 报重名冲突。

所以先把根 `pyproject.toml` 改成：

```toml
[project]
name = "ai-studio-mono"
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
    print("Hello from ai-studio!")
```

以及各 package 默认生成的：

```toml
[project.scripts]
ai-studio-* = "xxx:main"
```

## 3. 把本地包声明成 workspace source

根 `pyproject.toml` 里补上：

```toml
[tool.uv.sources]
ai-studio = { workspace = true }
ai-studio-accelerator = { workspace = true }
ai-studio-app = { workspace = true }
ai-studio-client = { workspace = true }
ai-studio-ext = { workspace = true }
ai-studio-sandbox = { workspace = true }
ai-studio-serve = { workspace = true }
```

这样 `uv` 才会优先使用本地 workspace 里的包，而不是去外面找。

## 4. 补 package 依赖

按当前这版最小壳，依赖关系是：

`ai-studio-core`

```toml
dependencies = [
    "click>=8.1.0,<9.0.0",
]
```

`ai-studio-ext`

```toml
dependencies = [
    "ai-studio",
]
```

`ai-studio-client`

```toml
dependencies = [
    "ai-studio",
    "ai-studio-ext",
]
```

`ai-studio-serve`

```toml
dependencies = [
    "ai-studio-ext",
]
```

`ai-studio-sandbox`

```toml
dependencies = []
```

`ai-studio-accelerator`

```toml
dependencies = []
```

`ai-studio-app`

```toml
dependencies = [
    "ai-studio",
    "ai-studio-accelerator",
    "ai-studio-client",
    "ai-studio-ext",
    "ai-studio-sandbox",
    "ai-studio-serve",
]
```

## 5. 只保留一个 CLI 入口

真正的 CLI 入口放在 `core` 包：

```toml
[project.scripts]
ai-studio = "ai_studio.cli.cli_scripts:main"
```

文件位置：

- `packages/ai-studio-core/src/ai_studio/cli/cli_scripts.py`

这一层只做两件事：

- 注册 `ai-studio`
- 挂 `start` 子命令

## 6. app 层补启动壳

`app` 包里补 4 个文件：

- `packages/ai-studio-app/src/ai_studio_app/_cli.py`
- `packages/ai-studio-app/src/ai_studio_app/cli.py`
- `packages/ai-studio-app/src/ai_studio_app/ai_studio_server.py`
- `packages/ai-studio-app/src/ai_studio_app/config.py`

职责分别是：

- `_cli.py`：定义 `webserver` 命令
- `cli.py`：对外公开导出 `start_webserver`
- `ai_studio_server.py`：真正执行启动逻辑
- `config.py`：解析 `--config` 和读取 TOML

当前这版最小链路是：

```text
uv run ai-studio start webserver --config /my/dev.toml
-> pyproject.toml [project.scripts]
-> ai_studio.cli.cli_scripts:main
-> ai_studio_app.cli.start_webserver
-> ai_studio_app.ai_studio_server.run_webserver
```

## 7. 配置文件解析规则

当前 `config.py` 的规则是：

- 传真实绝对路径，直接用
- 传 `my/dev.toml`，回退到 `configs/my/dev.toml`
- 传 `/my/dev.toml`，也回退到 `configs/my/dev.toml`
- 不传时，默认找 `configs/my/dev.toml`

所以这两种写法都可以：

```shell
uv run ai-studio start webserver --config configs/my/dev.toml
uv run ai-studio start webserver --config /my/dev.toml
```

## 8. 同步依赖并启动

因为根项目本身不承载业务依赖，统一用：

```shell
uv sync --all-packages
```

先看 CLI 有没有挂上：

```shell
uv run ai-studio --help
```

再启动：

```shell
uv run ai-studio start webserver --config /my/dev.toml
```

当前这版最小壳的输出是：

```text
Hello from ai-studio!
```

## 9. 到这里得到什么

做完这一步，项目已经从：

- 根 `main.py`
- 每个包各自一个默认入口

变成：

- 一个统一的 workspace
- 一个统一的 CLI 入口
- 一个最小可跑的启动链路

后面再继续往里补业务代码就行。
