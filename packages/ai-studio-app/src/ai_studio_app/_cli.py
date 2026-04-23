from typing import Optional

import click


@click.command(name="webserver")
@click.option(
    "-c",
    "--config",
    type=str,
    required=False,
    default=None,
    help="Path to a TOML config file.",
)
def start_webserver(config: Optional[str]) -> None:
    from ai_studio_app.ai_studio_server import run_webserver

    run_webserver(config)
