"""
AI Studio 应用配置加载与解析工具。

本模块负责：
- 解析配置文件路径（支持绝对路径、相对路径与 `configs/` 下回退查找）；
- 读取 TOML 配置并构造强类型配置对象；
- 对配置中的 `${env:VAR}` / `${env:VAR:-default}` 占位符做环境变量替换。
"""
import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# 匹配环境变量占位符：
# - ${env:NAME}
# - ${env:NAME:-default_value}
_ENV_PATTERN = re.compile(r"\$\{env:([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
# 未显式传入配置路径时的默认配置文件（相对仓库根目录）
_DEFAULT_CONFIG = Path("configs/my/dev.toml")


@dataclass(slots=True)
class WebServerConfig:
    """Web 服务核心配置。"""

    # 监听地址（默认仅本机可访问）
    host: str = "127.0.0.1"
    # 监听端口
    port: int = 8000


@dataclass(slots=True)
class AppConfig:
    """应用配置聚合对象。"""

    # 实际命中的配置文件绝对路径
    path: Path
    # 结构化后的 Web 服务配置
    web: WebServerConfig
    # 完整配置字典（已完成环境变量解析）
    raw: dict[str, Any]


def resolve_config_path(
    config_value: Optional[str],
    repo_root: Optional[Path] = None,
    cwd: Optional[Path] = None,
) -> Path:
    """
    根据用户输入解析配置文件路径。

    解析顺序：
    1) `config_value` 为空：尝试 `<repo_root>/configs/my/dev.toml`；
    2) 若为存在的绝对路径，直接返回；
    3) 按当前工作目录 `cwd` 解析相对路径；
    4) 回退到 `<repo_root>/configs/<relative_path>`；
    5) 均失败则抛出 `FileNotFoundError`。
    """
    # 允许调用方覆盖 repo_root / cwd，便于测试或特殊运行环境注入。
    repo_root = (repo_root or _default_repo_root()).resolve()
    cwd = (cwd or Path.cwd()).resolve()
    configs_root = repo_root / "configs"

    if not config_value:
        # 未传参时走默认配置文件。
        default_path = (repo_root / _DEFAULT_CONFIG).resolve()
        if default_path.exists():
            return default_path
        raise FileNotFoundError("No config file provided and configs/my/dev.toml was not found.")

    raw = Path(config_value)
    if raw.is_absolute() and raw.exists():
        return raw.resolve()

    # 优先按当前工作目录解析。
    direct = (cwd / raw).resolve()
    if direct.exists():
        return direct

    # 将可能的绝对/相对前缀去掉后，拼到 configs 目录下作为回退路径。
    relative = raw.as_posix().lstrip("/") if raw.is_absolute() else raw.as_posix().lstrip("./")
    fallback = (configs_root / relative).resolve()
    if fallback.exists():
        return fallback

    raise FileNotFoundError(f"Config file not found: {config_value}")


def load_app_config(
    config_value: Optional[str],
    repo_root: Optional[Path] = None,
    cwd: Optional[Path] = None,
) -> AppConfig:
    """
    加载并解析应用配置。

    流程：
    - 先解析最终配置文件路径；
    - 读取 TOML 并做环境变量替换；
    - 从 `service.web` 提取 Web 配置并填充默认值；
    - 返回 `AppConfig`（含路径、结构化 web 配置与完整原始配置）。
    """
    path = resolve_config_path(config_value, repo_root=repo_root, cwd=cwd)
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    resolved = _resolve_env(raw)
    # 只抽取当前启动阶段所需的 web 子配置，其它内容保留在 raw 里供后续使用。
    web = resolved.get("service", {}).get("web", {})

    return AppConfig(
        path=path,
        web=WebServerConfig(
            host=str(web.get("host", "127.0.0.1")),
            port=int(str(web.get("port", 8000))),
        ),
        raw=resolved,
    )


def _default_repo_root() -> Path:
    """推断仓库根目录（基于当前文件相对层级回溯）。"""
    return Path(__file__).resolve().parents[4]


def _resolve_env(value: Any) -> Any:
    """
    递归解析配置中的环境变量占位符。

    支持类型：
    - dict: 递归处理 value；
    - list: 递归处理元素；
    - str: 执行 `${env:VAR}` / `${env:VAR:-default}` 替换；
    - 其它类型：原样返回。
    """
    if isinstance(value, dict):
        return {k: _resolve_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env(v) for v in value]
    if isinstance(value, str):
        # 未设置环境变量时，使用 `:-` 后的默认值；若默认值也缺失，则替换为空字符串。
        return _ENV_PATTERN.sub(
            lambda match: os.environ.get(match.group(1), match.group(2) or ""),
            value,
        )
    return value
