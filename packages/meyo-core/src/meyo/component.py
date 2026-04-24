"""系统组件和应用上下文定义，用于在模型服务启动时共享运行时对象。"""


from __future__ import annotations

import asyncio
import atexit
import logging
import sys
import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional, Type, TypeVar, Union

from meyo.util import AppConfig
from meyo.util.annotations import PublicAPI

# 运行时检查类型标注。
if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


class LifeCycle:
    """当前类的职责定义。"""

    def on_init(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    def after_init(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    async def async_on_init(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    def before_start(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    async def async_before_start(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    def after_start(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    async def async_after_start(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    def before_stop(self):
        """执行当前函数对应的业务逻辑。"""
        pass

    async def async_before_stop(self):
        """执行当前函数对应的业务逻辑。"""
        pass


class ComponentType(str, Enum):
    WORKER_MANAGER = "meyo_worker_manager"
    WORKER_MANAGER_FACTORY = "meyo_worker_manager_factory"
    MODEL_CONTROLLER = "meyo_model_controller"
    MODEL_REGISTRY = "meyo_model_registry"
    MODEL_API_SERVER = "meyo_model_api_server"
    MODEL_CACHE_MANAGER = "meyo_model_cache_manager"
    PLUGIN_HUB = "meyo_plugin_hub"
    MULTI_AGENTS = "meyo_multi_agents"
    EXECUTOR_DEFAULT = "meyo_thread_pool_default"
    TRACER = "meyo_tracer"
    TRACER_SPAN_STORAGE = "meyo_tracer_span_storage"
    RAG_GRAPH_DEFAULT = "meyo_rag_engine_default"
    AWEL_TRIGGER_MANAGER = "meyo_awel_trigger_manager"
    AWEL_DAG_MANAGER = "meyo_awel_dag_manager"
    UNIFIED_METADATA_DB_MANAGER_FACTORY = "meyo_unified_metadata_db_manager_factory"
    CONNECTOR_MANAGER = "meyo_connector_manager"
    RAG_STORAGE_MANAGER = "meyo_rag_storage_manager"
    AGENT_MANAGER = "meyo_agent_manager"
    RESOURCE_MANAGER = "meyo_resource_manager"
    SKILL_MANAGER = "meyo_skill_manager"
    VARIABLES_PROVIDER = "meyo_variables_provider"
    FILE_STORAGE_CLIENT = "meyo_file_storage_client"
    BENCHMARK_DATA_MANAGER = "meyo_benchmark_data_manager"


_EMPTY_DEFAULT_COMPONENT = "_EMPTY_DEFAULT_COMPONENT"


@PublicAPI(stability="beta")
class BaseComponent(LifeCycle, ABC):
    """当前类的职责定义。"""

    name = "base_meyo_component"

    def __init__(self, system_app: Optional[SystemApp] = None):
        if system_app is not None:
            self.init_app(system_app)

    @abstractmethod
    def init_app(self, system_app: SystemApp):
        """初始化并启动相关能力。"""

    @classmethod
    def get_instance(
        cls: Type[T],
        system_app: SystemApp,
        default_component=_EMPTY_DEFAULT_COMPONENT,
        or_register_component: Optional[Type[T]] = None,
        *args,
        **kwargs,
    ) -> T:
        """获取对应数据。"""
        # 检查关键字参数冲突。
        if "default_component" in kwargs:
            raise ValueError(
                "default_component argument given in both fixed and **kwargs"
            )
        if "or_register_component" in kwargs:
            raise ValueError(
                "or_register_component argument given in both fixed and **kwargs"
            )
        kwargs["default_component"] = default_component
        kwargs["or_register_component"] = or_register_component
        return system_app.get_component(
            cls.name,
            cls,
            *args,
            **kwargs,
        )


T = TypeVar("T", bound=BaseComponent)


@PublicAPI(stability="beta")
class SystemApp(LifeCycle):
    """当前类的职责定义。"""

    def __init__(
        self,
        asgi_app: Optional["FastAPI"] = None,
        app_config: Optional[AppConfig] = None,
    ) -> None:
        self.components: Dict[
            str, BaseComponent
        ] = {}  # 用于保存已注册组件。
        self._asgi_app = asgi_app
        self._app_config = app_config or AppConfig()
        self._stop_event = threading.Event()
        self._stop_event.clear()
        self._build()

    @property
    def app(self) -> Optional["FastAPI"]:
        """执行当前函数对应的业务逻辑。"""
        return self._asgi_app

    @property
    def config(self) -> AppConfig:
        """执行当前函数对应的业务逻辑。"""
        return self._app_config

    def register(self, component: Type[T], *args, **kwargs) -> T:
        """注册对象。"""
        instance = component(self, *args, **kwargs)
        self.register_instance(instance)
        return instance

    def register_instance(self, instance: T) -> T:
        """注册对象。"""
        name = instance.name
        if isinstance(name, ComponentType):
            name = name.value
        if name in self.components:
            raise RuntimeError(
                f"Componse name {name} already exists: {self.components[name]}"
            )
        logger.info(f"Register component with name {name} and instance: {instance}")
        self.components[name] = instance
        instance.init_app(self)
        return instance

    def get_component(
        self,
        name: Union[str, ComponentType],
        component_type: Type,
        default_component=_EMPTY_DEFAULT_COMPONENT,
        or_register_component: Optional[Type[T]] = None,
        *args,
        **kwargs,
    ) -> T:
        """获取对应数据。"""
        if isinstance(name, ComponentType):
            name = name.value
        component = self.components.get(name)
        if not component:
            if or_register_component:
                return self.register(or_register_component, *args, **kwargs)
            if default_component != _EMPTY_DEFAULT_COMPONENT:
                return default_component
            raise ValueError(f"No component found with name {name}")
        if not isinstance(component, component_type):
            raise TypeError(f"Component {name} is not of type {component_type}")
        return component

    def on_init(self):
        """执行当前函数对应的业务逻辑。"""
        copied_view = {k: v for k, v in self.components.items()}
        for _, v in copied_view.items():
            v.on_init()

    def after_init(self):
        """执行当前函数对应的业务逻辑。"""
        copied_view = {k: v for k, v in self.components.items()}
        for _, v in copied_view.items():
            v.after_init()

    async def async_on_init(self):
        """执行当前函数对应的业务逻辑。"""

        copied_view = {k: v for k, v in self.components.items()}
        tasks = [v.async_on_init() for _, v in copied_view.items()]
        await asyncio.gather(*tasks)

    def before_start(self):
        """执行当前函数对应的业务逻辑。"""
        copied_view = {k: v for k, v in self.components.items()}
        for _, v in copied_view.items():
            v.before_start()

    async def async_before_start(self):
        """执行当前函数对应的业务逻辑。"""
        copied_view = {k: v for k, v in self.components.items()}
        tasks = [v.async_before_start() for _, v in copied_view.items()]
        await asyncio.gather(*tasks)

    def after_start(self):
        """执行当前函数对应的业务逻辑。"""
        copied_view = {k: v for k, v in self.components.items()}
        for _, v in copied_view.items():
            v.after_start()

    async def async_after_start(self):
        """执行当前函数对应的业务逻辑。"""
        copied_view = {k: v for k, v in self.components.items()}
        tasks = [v.async_after_start() for _, v in copied_view.items()]
        await asyncio.gather(*tasks)

    def before_stop(self):
        """执行当前函数对应的业务逻辑。"""
        if self._stop_event.is_set():
            return

        copied_view = {k: v for k, v in self.components.items()}
        for _, v in copied_view.items():
            try:
                v.before_stop()
            except Exception:
                pass
        self._stop_event.set()

    async def async_before_stop(self):
        """执行当前函数对应的业务逻辑。"""
        copied_view = {k: v for k, v in self.components.items()}
        tasks = [v.async_before_stop() for _, v in copied_view.items()]
        await asyncio.gather(*tasks)

    def _build(self):
        """执行当前函数对应的业务逻辑。"""
        if not self.app:
            self._register_exit_handler()
            return
        from meyo.util.fastapi import register_event_handler

        async def startup_event():
            """初始化并启动相关能力。"""

            async def _startup_func():
                try:
                    await self.async_after_start()
                except Exception as e:
                    logger.error(f"Error starting system app: {e}")
                    sys.exit(1)

            asyncio.create_task(_startup_func())
            self.after_start()

        async def shutdown_event():
            """执行当前函数对应的业务逻辑。"""
            await self.async_before_stop()
            self.before_stop()

        register_event_handler(self.app, "startup", startup_event)
        register_event_handler(self.app, "shutdown", shutdown_event)

    def _register_exit_handler(self):
        """执行当前函数对应的业务逻辑。"""
        atexit.register(self.before_stop)
