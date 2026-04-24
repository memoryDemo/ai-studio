"""后端应用启动装配，负责创建服务应用、初始化模型服务并挂载路由。"""

import logging
import os
import sys
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from meyo._version import version
from meyo.component import SystemApp
from meyo.configs.model_config import LOGDIR, STATIC_MESSAGE_IMG_PATH
from meyo.model.cluster.apiserver.api import initialize_apiserver
from meyo.model.cluster.worker.manager import initialize_worker_manager_in_client
from meyo.util.fastapi import create_app, replace_router
from meyo.util.i18n_utils import _, set_default_language
from meyo.util.utils import (
    logging_str_to_uvicorn_level,
    setup_http_service_logging,
    setup_logging,
)
from meyo_app.config import ApplicationConfig, ServiceWebParameters, SystemParameters

logger = logging.getLogger(__name__)
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_PATH)

app = create_app(
    title=_("Meyo Open API"),
    description=_("Meyo Open API"),
    version=version,
    openapi_tags=[],
)
replace_router(app)

system_app = SystemApp(app)


def mount_routers(app: FastAPI):
    """执行当前函数对应的业务逻辑。"""
    # 当前只挂载模型服务接口，业务路由后续按能力逐步补充。


def mount_static_files(app: FastAPI, param: ApplicationConfig):
    package_dir = os.path.dirname(os.path.abspath(__file__))
    static_file_path = os.path.join(package_dir, "static", "web")

    os.makedirs(STATIC_MESSAGE_IMG_PATH, exist_ok=True)
    app.mount(
        "/images",
        StaticFiles(directory=STATIC_MESSAGE_IMG_PATH, html=True),
        name="static2",
    )

    # 当前没有内置前端应用，只保留静态目录作为占位入口。
    app.mount("/", StaticFiles(directory=static_file_path, html=True), name="static")


def initialize_app(param: ApplicationConfig, args: List[str] = None):
    """初始化并启动相关能力。"""
    web_config = param.service.web
    log_config = web_config.log or param.log
    setup_logging(
        "meyo",
        log_config,
        default_logger_filename=os.path.join(LOGDIR, "meyo_webserver.log"),
    )

    mount_routers(app)

    binding_port = web_config.port
    binding_host = web_config.host
    controller_addr = (
        web_config.controller_addr
        or param.service.model.worker.controller_addr
        or f"http://127.0.0.1:{binding_port}"
    )
    if not param.service.model.worker.controller_addr:
        param.service.model.worker.controller_addr = controller_addr
    if not param.service.model.api.controller_addr:
        param.service.model.api.controller_addr = controller_addr
    elif param.service.model.api.controller_addr == "http://127.0.0.1:8000":
        param.service.model.api.controller_addr = controller_addr

    if not web_config.light:
        logger.info("Model Unified Deployment Mode, run all services in the same process")
        initialize_worker_manager_in_client(
            worker_params=param.service.model.worker,
            models_config=param.models,
            app=app,
            binding_port=binding_port,
            binding_host=binding_host,
            start_listener=None,
            system_app=system_app,
        )
    else:
        param.models.llms = []
        param.models.rerankers = []
        param.models.embeddings = []
        initialize_worker_manager_in_client(
            worker_params=param.service.model.worker,
            models_config=param.models,
            app=app,
            run_locally=False,
            controller_addr=controller_addr,
            binding_port=binding_port,
            binding_host=binding_host,
            start_listener=None,
            system_app=system_app,
        )

    initialize_apiserver(
        param.service.model.api,
        sys_trace=web_config.trace or param.trace,
        sys_log=log_config,
        app=app,
        system_app=system_app,
    )
    mount_static_files(app, param)
    system_app.before_start()
    return param


def run_uvicorn(param: ServiceWebParameters):
    import uvicorn

    setup_http_service_logging()

    cors_app = CORSMiddleware(
        app=app,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    log_level = "info"
    if param.log:
        log_level = logging_str_to_uvicorn_level(param.log.level)
    uvicorn.run(
        cors_app,
        host=param.host,
        port=param.port,
        log_level=log_level,
    )


def run_webserver(config_file: str):
    param = load_config(config_file)
    system_app.config.configs["app_config"] = param
    param = initialize_app(param)
    run_uvicorn(param.service.web)


def scan_configs():
    from meyo.model import scan_model_providers

    scan_model_providers()


def load_config(config_file: str = None) -> ApplicationConfig:
    from meyo._private.config import Config
    from meyo.configs.model_config import ROOT_PATH as MEYO_ROOT_PATH
    from meyo.util.configure import ConfigurationManager

    if config_file is None:
        config_file = os.path.join(MEYO_ROOT_PATH, "configs", "meyo.toml")
    else:
        config_file = _resolve_config_file(config_file, MEYO_ROOT_PATH)

    _load_env_files(MEYO_ROOT_PATH, config_file)

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    logger.info(f"Loading configuration from: {config_file}")
    cfg = ConfigurationManager.from_file(config_file)
    sys_config = cfg.parse_config(SystemParameters, prefix="system")
    set_default_language(sys_config.language)
    _CFG = Config()
    _CFG.LANGUAGE = sys_config.language

    scan_configs()

    app_config = cfg.parse_config(ApplicationConfig, hook_section="hooks")
    return app_config


def _resolve_config_file(config_file: str, root_path: str) -> str:
    """解析配置文件路径。"""
    candidates = []
    if os.path.isabs(config_file):
        candidates.append(config_file)
        normalized = config_file.lstrip(os.sep)
        candidates.append(os.path.join(root_path, normalized))
        candidates.append(os.path.join(root_path, "configs", normalized))
    else:
        candidates.append(os.path.join(root_path, config_file))
        candidates.append(os.path.join(root_path, "configs", config_file))

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0]


def _load_env_files(root_path: str, config_file: str) -> None:
    """加载本地环境变量文件。"""
    env_files = [
        os.path.join(root_path, ".env"),
        os.path.join(os.path.dirname(config_file), ".env"),
    ]
    for env_file in dict.fromkeys(env_files):
        _load_env_file(env_file)


def _load_env_file(env_file: str) -> None:
    """加载单个环境变量文件。"""
    if not os.path.exists(env_file):
        return
    with open(env_file, "r", encoding="utf-8") as fp:
        for raw_line in fp:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not key or key in os.environ:
                continue
            value = value.strip().strip("'").strip('"')
            os.environ[key] = value


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="Meyo Webserver")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=None,
        help=(
            "Path to the TOML configuration file. "
            "Default: configs/meyo.toml. "
            "Relative names are resolved under configs/."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    _args = parse_args()
    _config_file = _args.config
    run_webserver(_config_file)
