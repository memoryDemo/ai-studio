import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

_ENV_PATTERN = re.compile(r"\$\{env:([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
_DEFAULT_CONFIG = Path("configs/my/dev.toml")


@dataclass(slots=True)
class WebServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000


@dataclass(slots=True)
class AppConfig:
    path: Path
    web: WebServerConfig
    raw: dict[str, Any]


def resolve_config_path(
    config_value: Optional[str],
    repo_root: Optional[Path] = None,
    cwd: Optional[Path] = None,
) -> Path:
    repo_root = (repo_root or _default_repo_root()).resolve()
    cwd = (cwd or Path.cwd()).resolve()
    configs_root = repo_root / "configs"

    if not config_value:
        default_path = (repo_root / _DEFAULT_CONFIG).resolve()
        if default_path.exists():
            return default_path
        raise FileNotFoundError("No config file provided and configs/my/dev.toml was not found.")

    raw = Path(config_value)
    if raw.is_absolute() and raw.exists():
        return raw.resolve()

    direct = (cwd / raw).resolve()
    if direct.exists():
        return direct

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
    path = resolve_config_path(config_value, repo_root=repo_root, cwd=cwd)
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    resolved = _resolve_env(raw)
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
    return Path(__file__).resolve().parents[4]


def _resolve_env(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _resolve_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env(v) for v in value]
    if isinstance(value, str):
        return _ENV_PATTERN.sub(
            lambda match: os.environ.get(match.group(1), match.group(2) or ""),
            value,
        )
    return value
