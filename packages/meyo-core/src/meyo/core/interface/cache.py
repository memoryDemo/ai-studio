"""缓存接口定义，约束模型服务和后续业务缓存实现的基础协议。"""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from meyo.core.interface.serialization import Serializable

K = TypeVar("K")
V = TypeVar("V")


class RetrievalPolicy(str, Enum):
    """枚举类型定义。"""

    EXACT_MATCH = "exact_match"
    SIMILARITY_MATCH = "similarity_match"


class CachePolicy(str, Enum):
    """枚举类型定义。"""

    LRU = "lru"
    FIFO = "fifo"


@dataclass
class CacheConfig:
    """配置参数定义。"""

    retrieval_policy: Optional[RetrievalPolicy] = RetrievalPolicy.EXACT_MATCH
    cache_policy: Optional[CachePolicy] = CachePolicy.LRU


class CacheKey(Serializable, ABC, Generic[K]):
    """当前类的职责定义。"""

    @abstractmethod
    def __hash__(self) -> int:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def get_hash_bytes(self) -> bytes:
        """获取对应数据。"""

    @abstractmethod
    def get_value(self) -> K:
        """获取对应数据。"""


class CacheValue(Serializable, ABC, Generic[V]):
    """当前类的职责定义。"""

    @abstractmethod
    def get_value(self) -> V:
        """获取对应数据。"""


class CacheClient(ABC, Generic[K, V]):
    """外部服务连接和调用实现。"""

    @abstractmethod
    async def get(
        self, key: CacheKey[K], cache_config: Optional[CacheConfig] = None
    ) -> Optional[CacheValue[V]]:
        """获取对应数据。"""

    @abstractmethod
    async def set(
        self,
        key: CacheKey[K],
        value: CacheValue[V],
        cache_config: Optional[CacheConfig] = None,
    ) -> None:
        """设置对应数据。"""

    @abstractmethod
    async def exists(
        self, key: CacheKey[K], cache_config: Optional[CacheConfig] = None
    ) -> bool:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def new_key(self, **kwargs) -> CacheKey[K]:
        """创建对象实例。"""

    @abstractmethod
    def new_value(self, **kwargs) -> CacheValue[K]:
        """创建对象实例。"""
