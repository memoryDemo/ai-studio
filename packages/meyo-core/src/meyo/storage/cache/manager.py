"""缓存存储基础模块，为模型服务和后续业务缓存提供统一实现入口。"""


import logging
from abc import ABC, abstractmethod
from concurrent.futures import Executor
from dataclasses import dataclass, field
from typing import Optional, Type, cast

from meyo.component import BaseComponent, ComponentType, SystemApp
from meyo.core import CacheConfig, CacheKey, CacheValue, Serializable, Serializer
from meyo.core.interface.cache import K, V
from meyo.util.executor_utils import ExecutorFactory, blocking_func_to_async
from meyo.util.i18n_utils import _
from meyo.util.parameter_utils import BaseParameters

from .storage.base import CacheStorage

logger = logging.getLogger(__name__)


@dataclass
class ModelCacheParameters(BaseParameters):
    """配置参数定义。"""

    __cfg_type__ = "utils"

    enable_model_cache: bool = field(
        default=True,
        metadata={
            "help": _("Whether to enable model cache, default is True"),
        },
    )
    storage_type: str = field(
        default="memory",
        metadata={
            "help": _("The storage type, default is memory"),
        },
    )
    max_memory_mb: int = field(
        default=256,
        metadata={
            "help": _("The max memory in MB, default is 256"),
        },
    )
    persist_dir: str = field(
        default="model_cache",
        metadata={
            "help": _("The persist directory, default is model_cache"),
        },
    )


class CacheManager(BaseComponent, ABC):
    """模型服务运行组件定义。"""

    name = ComponentType.MODEL_CACHE_MANAGER

    def __init__(self, system_app: SystemApp | None = None):
        """初始化实例。"""
        super().__init__(system_app)

    def init_app(self, system_app: SystemApp):
        """初始化并启动相关能力。"""
        self.system_app = system_app

    @abstractmethod
    async def set(
        self,
        key: CacheKey[K],
        value: CacheValue[V],
        cache_config: Optional[CacheConfig] = None,
    ):
        """设置对应数据。"""

    @abstractmethod
    async def get(
        self,
        key: CacheKey[K],
        cls: Type[Serializable],
        cache_config: Optional[CacheConfig] = None,
    ) -> Optional[CacheValue[V]]:
        """获取对应数据。"""

    @property
    @abstractmethod
    def serializer(self) -> Serializer:
        """执行当前函数对应的业务逻辑。"""


class LocalCacheManager(CacheManager):
    """模型服务运行组件定义。"""

    def __init__(
        self, system_app: SystemApp, serializer: Serializer, storage: CacheStorage
    ) -> None:
        """初始化实例。"""
        super().__init__(system_app)
        self._serializer = serializer
        self._storage = storage

    @property
    def executor(self) -> Executor:
        """执行当前函数对应的业务逻辑。"""
        return self.system_app.get_component(  # type: ignore
            ComponentType.EXECUTOR_DEFAULT, ExecutorFactory
        ).create()

    async def set(
        self,
        key: CacheKey[K],
        value: CacheValue[V],
        cache_config: Optional[CacheConfig] = None,
    ):
        """设置对应数据。"""
        if self._storage.support_async():
            await self._storage.aset(key, value, cache_config)
        else:
            await blocking_func_to_async(
                self.executor, self._storage.set, key, value, cache_config
            )

    async def get(
        self,
        key: CacheKey[K],
        cls: Type[Serializable],
        cache_config: Optional[CacheConfig] = None,
    ) -> Optional[CacheValue[V]]:
        """获取对应数据。"""
        if self._storage.support_async():
            item_bytes = await self._storage.aget(key, cache_config)
        else:
            item_bytes = await blocking_func_to_async(
                self.executor, self._storage.get, key, cache_config
            )
        if not item_bytes:
            return None
        return cast(
            CacheValue[V], self._serializer.deserialize(item_bytes.value_data, cls)
        )

    @property
    def serializer(self) -> Serializer:
        """执行当前函数对应的业务逻辑。"""
        return self._serializer


def initialize_cache(
    system_app: SystemApp, storage_type: str, max_memory_mb: int, persist_dir: str
):
    """初始化并启动相关能力。"""
    from meyo.util.serialization.json_serialization import JsonSerializer

    from .storage.base import MemoryCacheStorage

    if storage_type == "disk":
        try:
            from .storage.disk.disk_storage import DiskCacheStorage

            cache_storage: CacheStorage = DiskCacheStorage(
                persist_dir, mem_table_buffer_mb=max_memory_mb
            )
        except ImportError as e:
            logger.warning(
                f"Can't import DiskCacheStorage, use MemoryCacheStorage, import error "
                f"message: {str(e)}"
            )
            cache_storage = MemoryCacheStorage(max_memory_mb=max_memory_mb)
    else:
        cache_storage = MemoryCacheStorage(max_memory_mb=max_memory_mb)
    system_app.register(
        LocalCacheManager, serializer=JsonSerializer(), storage=cache_storage
    )
