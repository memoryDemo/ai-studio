"""
Meyo 命令行入口与「启动」子命令的装配。

本模块提供：
- 根 CLI 组及日志等级选项；
- `start` 子命令组：默认不带子命令时等价于 `start web`；
- 在可选依赖 `meyo_app` 可用时，将 Web 服务启动入口注册为 `web` / `webserver` 别名。

若未安装 `meyo_app`，仅会记录警告，不影响其它 CLI 能力。
"""
import copy
import logging

import click

# 为 CLI 设置默认的日志格式与等级（具体等级由根命令 --log-level 再覆盖）
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
    """根命令组：处理全局 --log-level，并作为所有子命令的父组。"""
    logger.setLevel(logging.getLevelName(log_level.upper()))


def add_command_alias(command, name: str, hidden: bool = False, parent_group=None) -> None:
    """
    将已有 Click 命令以指定名称注册到父组，实现命令别名（如 web 与 webserver 指向同一实现）。

    通过深拷贝原命令对象，避免同一 Command 实例被多次 add_command 时产生状态冲突。

    参数:
        command: 已装饰好的 Click 命令（Command 对象）。
        name: 在父组下暴露的子命令名。
        hidden: 为 True 时通常不在 --help 中列出该别名（取决于 Click 版本与用法）。
        parent_group: 挂载的 Click Group；未指定时使用本模块的顶层 ``cli``。
    """
    if not parent_group:
        parent_group = cli
    new_command = copy.deepcopy(command)
    new_command.hidden = hidden
    parent_group.add_command(new_command, name=name)


@click.group(invoke_without_command=True)
@click.pass_context
def start(ctx) -> None:
    """
    「启动」子命令组；允许不带子命令直接调用本组（invoke_without_command=True）。

    当用户只输入 ``meyo start`` 且未写 web/webserver 时，自动回退为启动 Web 服务
   （优先 ``web``，否则 ``webserver``）；若均不存在则仅打印本组帮助。
    """
    if ctx.invoked_subcommand is None:
        cmd = start.commands.get("web") or start.commands.get("webserver")
        if cmd:
            ctx.invoke(cmd)
        else:
            click.echo(ctx.get_help())


cli.add_command(start)


# 可选集成：从 meyo_app 拉取 Web 服务 CLI，失败则降级（不阻塞核心包安装与使用）
try:
    # 通过公开模块导入，避免直接访问受保护成员 `_cli`。
    from meyo_app.cli import start_webserver

    add_command_alias(start_webserver, name="webserver", parent_group=start)
    add_command_alias(start_webserver, name="web", parent_group=start)
except ImportError as exc:
    # 兜底定义，避免静态检查器报「try 中定义的名称在 except 路径未定义」。
    start_webserver = None
    logging.warning(
        "Integrating meyo webserver command line tool failed: %s",
        exc,
    )


def main() -> int:
    """程序入口：执行 Click 主循环并返回其退出码。"""
    return cli()


if __name__ == "__main__":
    main()
