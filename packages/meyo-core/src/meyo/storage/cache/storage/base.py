"""缓存存储基础模块，为模型服务和后续业务缓存提供统一实现入口。"""


import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

import msgpack

from meyo.core.interface.cache import (
    CacheConfig,
    CacheKey,
    CachePolicy,
    CacheValue,
    K,
    RetrievalPolicy,
    V,
)
from meyo.util.memory_utils import _get_object_bytes

logger = logging.getLogger(__name__)


@dataclass
class StorageItem:
    """存储能力实现。"""

    length: int  # 代码说明。
    key_hash: bytes  # 代码说明。
    key_data: bytes  # 代码说明。
    value_data: bytes  # 代码说明。

    @staticmethod
    def build_from(
        key_hash: bytes, key_data: bytes, value_data: bytes
    ) -> "StorageItem":
        """构建目标对象。"""
        length = (
            32
            + _get_object_bytes(key_hash)
            + _get_object_bytes(key_data)
            + _get_object_bytes(value_data)
        )
        return StorageItem(
            length=length, key_hash=key_hash, key_data=key_data, value_data=value_data
        )

    @staticmethod
    def build_from_kv(key: CacheKey[K], value: CacheValue[V]) -> "StorageItem":
        """构建目标对象。"""
        key_hash = key.get_hash_bytes()
        key_data = key.serialize()
        value_data = value.serialize()
        return StorageItem.build_from(key_hash, key_data, value_data)

    def serialize(self) -> bytes:
        """执行当前函数对应的业务逻辑。"""
        obj = {
            "length": self.length,
            "key_hash": msgpack.ExtType(1, self.key_hash),
            "key_data": msgpack.ExtType(2, self.key_data),
            "value_data": msgpack.ExtType(3, self.value_data),
        }
        return msgpack.packb(obj)

    @staticmethod
    def deserialize(data: bytes) -> "StorageItem":
        """执行当前函数对应的业务逻辑。"""
        obj = msgpack.unpackb(data)
        key_hash = obj["key_hash"].data
        key_data = obj["key_data"].data
        value_data = obj["value_data"].data

        return StorageItem(
            length=obj["length"],
            key_hash=key_hash,
            key_data=key_data,
            value_data=value_data,
        )


class CacheStorage(ABC):
    """存储能力实现。"""

    @abstractmethod
    def check_config(
        self,
        cache_config: Optional[CacheConfig] = None,
        raise_error: Optional[bool] = True,
    ) -> bool:
        """校验条件并返回判断结果。"""

    def support_async(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return False

    @abstractmethod
    def get(
        self, key: CacheKey[K], cache_config: Optional[CacheConfig] = None
    ) -> Optional[StorageItem]:
        """获取对应数据。"""

    async def aget(
        self, key: CacheKey[K], cache_config: Optional[CacheConfig] = None
    ) -> Optional[StorageItem]:
        """执行当前函数对应的业务逻辑。"""
        raise NotImplementedError

    @abstractmethod
    def set(
        self,
        key: CacheKey[K],
        value: CacheValue[V],
        cache_config: Optional[CacheConfig] = None,
    ) -> None:
        """设置对应数据。"""

    async def aset(
        self,
        key: CacheKey[K],
        value: CacheValue[V],
        cache_config: Optional[CacheConfig] = None,
    ) -> None:
        """执行当前函数对应的业务逻辑。"""
        raise NotImplementedError


class MemoryCacheStorage(CacheStorage):
    """存储能力实现。"""

    def __init__(self, max_memory_mb: int = 256):
        """初始化实例。"""
        self.cache: OrderedDict = OrderedDict()
        self.max_memory = max_memory_mb * 1024 * 1024
        self.current_memory_usage = 0

    def check_config(
        self,
        cache_config: Optional[CacheConfig] = None,
        raise_error: Optional[bool] = True,
    ) -> bool:
        """校验条件并返回判断结果。"""
        if (
            cache_config
            and cache_config.retrieval_policy != RetrievalPolicy.EXACT_MATCH
        ):
            if raise_error:
                raise ValueError(
                    "MemoryCacheStorage only supports 'EXACT_MATCH' retrieval policy"
                )
            return False
        return True

    def get(
        self, key: CacheKey[K], cache_config: Optional[CacheConfig] = None
    ) -> Optional[StorageItem]:
        """获取对应数据。"""
        self.check_config(cache_config, raise_error=True)
        # 代码说明。
        key_hash = hash(key)
        item: Optional[StorageItem] = self.cache.get(key_hash)
        logger.debug(f"MemoryCacheStorage get key {key}, hash {key_hash}, item: {item}")

        if not item:
            return None
        # 代码说明。
        self.cache.move_to_end(key_hash)
        return item

    def set(
        self,
        key: CacheKey[K],
        value: CacheValue[V],
        cache_config: Optional[CacheConfig] = None,
    ) -> None:
        """设置对应数据。"""
        key_hash = hash(key)
        item = StorageItem.build_from_kv(key, value)
        # 代码说明。
        new_entry_size = _get_object_bytes(item)
        # 代码说明。
        while self.current_memory_usage + new_entry_size > self.max_memory:
            self._apply_cache_policy(cache_config)

        # 代码说明。
        self.cache[key_hash] = item
        self.current_memory_usage += new_entry_size
        logger.debug(f"MemoryCacheStorage set key {key}, hash {key_hash}, item: {item}")

    def exists(
        self, key: CacheKey[K], cache_config: Optional[CacheConfig] = None
    ) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return self.get(key, cache_config) is not None

    def _apply_cache_policy(self, cache_config: Optional[CacheConfig] = None):
        # 代码说明。
        if cache_config and cache_config.cache_policy == CachePolicy.FIFO:
            self.cache.popitem(last=False)
        else:  # 默认配置说明。
            self.cache.popitem(last=True)
