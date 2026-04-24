"""应用层模块，负责后端启动装配和服务入口组织。"""
from typing import Optional

import click


@click.command(name="webserver")
@click.option(
    "-c",
    "--config",
    type=str,
    required=False,
    default=None,
    help="TOML 配置文件路径；可直接传 meyo.toml，默认读取 configs/meyo.toml。",
)
def start_webserver(config: Optional[str]) -> None:
    """初始化并启动相关能力。"""
    # 延迟导入真正的启动函数，确保命令被调用时才加载服务相关依赖。
    from meyo_app.meyo_server import run_webserver

    # 将命令行传入的配置路径交给服务启动层统一解析。
    run_webserver(config)
