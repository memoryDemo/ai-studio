"""
meyo_app 的内部 CLI 定义模块。

说明：
- 本模块定义 Web 服务启动命令 `start_webserver`；
- 该命令由 `click` 装饰后可被上层 CLI 组挂载为子命令；
- 通过 `--config` 可选参数传入 TOML 配置文件路径。
"""
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
    """
    启动 Meyo Web 服务。

    参数:
        config: TOML 配置文件路径。为 ``None`` 时，服务端按默认配置查找/加载配置。

    实现说明:
        这里采用函数内导入 `run_webserver`，可减少模块导入阶段的耦合与启动开销，
        也能避免某些场景下的循环导入问题。
    """
    # 延迟导入真正的启动函数，确保命令被调用时才加载服务相关依赖。
    from meyo_app.meyo_server import run_webserver

    # 将 CLI 参数透传给服务启动入口。
    run_webserver(config)
