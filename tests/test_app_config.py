from pathlib import Path

from ai_studio_app.config import load_app_config, resolve_config_path


def test_resolve_config_path_maps_slash_prefixed_values_into_configs_root(tmp_path: Path):
    repo_root = tmp_path / "repo"
    config_path = repo_root / "configs" / "my" / "dev.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("[service.web]\nport = 14000\n", encoding="utf-8")

    resolved = resolve_config_path("/my/dev.toml", repo_root=repo_root, cwd=repo_root)

    assert resolved == config_path.resolve()


def test_resolve_config_path_falls_back_to_configs_root_for_relative_paths(tmp_path: Path):
    repo_root = tmp_path / "repo"
    config_path = repo_root / "configs" / "my" / "dev.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text("[service.web]\nport = 14000\n", encoding="utf-8")

    resolved = resolve_config_path("my/dev.toml", repo_root=repo_root, cwd=repo_root)

    assert resolved == config_path.resolve()


def test_load_app_config_expands_env_placeholders(tmp_path: Path, monkeypatch):
    repo_root = tmp_path / "repo"
    config_path = repo_root / "configs" / "my" / "dev.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        "\n".join(
            [
                "[service.web]",
                'host = "${env:AI_STUDIO_HOST:-0.0.0.0}"',
                'port = "${env:AI_STUDIO_PORT:-14000}"',
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("AI_STUDIO_HOST", "127.0.0.1")
    monkeypatch.setenv("AI_STUDIO_PORT", "18080")

    loaded = load_app_config("/my/dev.toml", repo_root=repo_root, cwd=repo_root)

    assert loaded.path == config_path.resolve()
    assert loaded.web.host == "127.0.0.1"
    assert loaded.web.port == 18080
