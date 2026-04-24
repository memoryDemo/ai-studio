"""后端模型服务运行链路模块，负责补齐当前目录对应的基础能力。"""
import copy
import logging

import click

# 代码说明。
logging.basicConfig(
    level=logging.WARNING,
    encoding="utf-8",
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("meyo_cli")


@click.group()
@click.option(
    "--log-level",
    required=False,
    type=str,
    default="warn",
    help="Log level",
)
@click.version_option(package_name="meyo")
def cli(log_level: str) -> None:
    """执行当前函数对应的业务逻辑。"""
    logger.setLevel(logging.getLevelName(log_level.upper()))


def add_command_alias(command, name: str, hidden: bool = False, parent_group=None) -> None:
    """执行当前函数对应的业务逻辑。"""
    if not parent_group:
        parent_group = cli
    new_command = copy.deepcopy(command)
    new_command.hidden = hidden
    parent_group.add_command(new_command, name=name)


@click.group(invoke_without_command=True)
@click.pass_context
def start(ctx) -> None:
    """初始化并启动相关能力。"""
    if ctx.invoked_subcommand is None:
        cmd = start.commands.get("web") or start.commands.get("webserver")
        if cmd:
            ctx.invoke(cmd)
        else:
            click.echo(ctx.get_help())


cli.add_command(start)


# 代码说明。
try:
    # 代码说明。
    from meyo_app.cli import start_webserver

    add_command_alias(start_webserver, name="webserver", parent_group=start)
    add_command_alias(start_webserver, name="web", parent_group=start)
except ImportError as exc:
    # 代码说明。
    start_webserver = None
    logging.warning(
        "Integrating meyo webserver command line tool failed: %s",
        exc,
    )


def main() -> int:
    """执行当前函数对应的业务逻辑。"""
    return cli()


if __name__ == "__main__":
    main()
