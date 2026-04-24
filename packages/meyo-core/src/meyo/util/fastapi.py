"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""


import importlib.metadata as metadata
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, List, Optional

from fastapi import FastAPI
from fastapi.routing import APIRouter

_FASTAPI_VERSION = metadata.version("fastapi")


class PriorityAPIRouter(APIRouter):
    """当前类的职责定义。"""

    def __init__(self, *args, **kwargs):
        """初始化实例。"""
        super().__init__(*args, **kwargs)
        self.route_priority: Dict[str, int] = {}

    def add_api_route(
        self, path: str, endpoint: Callable, *, priority: int = 0, **kwargs: Any
    ):
        """执行当前函数对应的业务逻辑。"""
        super().add_api_route(path, endpoint, **kwargs)
        self.route_priority[path] = priority
        # 代码说明。
        self.sort_routes_by_priority()

    def sort_routes_by_priority(self):
        """执行当前函数对应的业务逻辑。"""

        def my_func(route):
            if route.path in ["", "/"]:
                return -100
            return self.route_priority.get(route.path, 0)

        self.routes.sort(key=my_func, reverse=True)


_HAS_STARTUP = False
_HAS_SHUTDOWN = False
_GLOBAL_STARTUP_HANDLERS: List[Callable] = []

_GLOBAL_SHUTDOWN_HANDLERS: List[Callable] = []


def register_event_handler(app: FastAPI, event: str, handler: Callable):
    """注册对象。"""
    if _FASTAPI_VERSION >= "0.109.1":
        # 参考链接。
        if event == "startup":
            if _HAS_STARTUP:
                raise ValueError(
                    "FastAPI app already started. Cannot add startup handler."
                )
            _GLOBAL_STARTUP_HANDLERS.append(handler)
        elif event == "shutdown":
            if _HAS_SHUTDOWN:
                raise ValueError(
                    "FastAPI app already shutdown. Cannot add shutdown handler."
                )
            _GLOBAL_SHUTDOWN_HANDLERS.append(handler)
        else:
            raise ValueError(f"Invalid event: {event}")
    else:
        if event == "startup":
            app.add_event_handler("startup", handler)
        elif event == "shutdown":
            app.add_event_handler("shutdown", handler)
        else:
            raise ValueError(f"Invalid event: {event}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 代码说明。
    global _HAS_STARTUP, _HAS_SHUTDOWN
    for handler in _GLOBAL_STARTUP_HANDLERS:
        await handler()
    _HAS_STARTUP = True
    yield
    # 代码说明。
    for handler in _GLOBAL_SHUTDOWN_HANDLERS:
        await handler()
    _HAS_SHUTDOWN = True


def create_app(*args, **kwargs) -> FastAPI:
    """创建对象实例。"""
    _sp = None
    if _FASTAPI_VERSION >= "0.109.1":
        if "lifespan" not in kwargs:
            kwargs["lifespan"] = lifespan
        _sp = kwargs["lifespan"]
    app = FastAPI(*args, **kwargs)
    if _sp:
        app.__meyo_custom_lifespan = _sp
    return app


def replace_router(app: FastAPI, router: Optional[APIRouter] = None):
    """执行当前函数对应的业务逻辑。"""
    if not router:
        router = PriorityAPIRouter()
    if _FASTAPI_VERSION >= "0.109.1":
        if hasattr(app, "__meyo_custom_lifespan"):
            _sp = getattr(app, "__meyo_custom_lifespan")
            router.lifespan_context = _sp

    app.router = router
    app.setup()
    return app
