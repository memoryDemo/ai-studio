import copy
import logging

import click

logging.basicConfig(
    level=logging.WARNING,
    encoding="utf-8",
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("ai_studio_cli")


@click.group()
@click.option(
    "--log-level",
    required=False,
    type=str,
    default="warn",
    help="Log level",
)
@click.version_option(package_name="ai-studio")
def cli(log_level: str) -> None:
    logger.setLevel(logging.getLevelName(log_level.upper()))


def add_command_alias(command, name: str, hidden: bool = False, parent_group=None) -> None:
    if not parent_group:
        parent_group = cli
    new_command = copy.deepcopy(command)
    new_command.hidden = hidden
    parent_group.add_command(new_command, name=name)


@click.group(invoke_without_command=True)
@click.pass_context
def start(ctx) -> None:
    """Start specific server."""
    if ctx.invoked_subcommand is None:
        cmd = start.commands.get("web") or start.commands.get("webserver")
        if cmd:
            ctx.invoke(cmd)
        else:
            click.echo(ctx.get_help())


cli.add_command(start)


try:
    from ai_studio_app._cli import start_webserver

    add_command_alias(start_webserver, name="webserver", parent_group=start)
    add_command_alias(start_webserver, name="web", parent_group=start)
except ImportError as exc:
    logging.warning(
        "Integrating ai-studio webserver command line tool failed: %s",
        exc,
    )


def main() -> int:
    return cli()


if __name__ == "__main__":
    main()
