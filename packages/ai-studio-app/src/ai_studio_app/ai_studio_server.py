from typing import Optional

from ai_studio_app.config import load_app_config


def run_webserver(config_file: Optional[str] = None) -> None:
    load_app_config(config_file)
    print("Hello from ai-studio!")
