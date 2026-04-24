"""模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。"""

from __future__ import annotations

import logging
import sys
import time
from collections import OrderedDict
from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from meyo.core.interface.message import BaseMessage, ModelMessage

logger = logging.getLogger(__name__)


class ProxyTokenizerWrapper:
    def __init__(self) -> None:
        self._support_encoding = True
        self._encoding_model = None

    def count_token(
        self,
        messages: Union[str, BaseMessage, ModelMessage, List[ModelMessage]],
        model_name: Optional[str] = None,
    ) -> int:
        """执行当前函数对应的业务逻辑。"""
        if not self._support_encoding:
            logger.warning(
                "model does not support encoding model, can't count token, returning -1"
            )
            return -1
        encoding = self._get_or_create_encoding_model(model_name)
        cnt = 0
        if isinstance(messages, str):
            cnt = len(encoding.encode(messages, disallowed_special=()))
        elif isinstance(messages, BaseMessage):
            cnt = len(encoding.encode(messages.content, disallowed_special=()))
        elif isinstance(messages, ModelMessage):
            cnt = len(encoding.encode(messages.content, disallowed_special=()))
        elif isinstance(messages, list):
            for message in messages:
                cnt += len(encoding.encode(message.content, disallowed_special=()))
        else:
            logger.warning(
                "unsupported type of messages, can't count token, returning -1"
            )
            return -1
        return cnt

    def _get_or_create_encoding_model(self, model_name: Optional[str] = None):
        """执行当前函数对应的业务逻辑。"""
        if self._encoding_model:
            return self._encoding_model
        try:
            import tiktoken

            logger.info(
                "tiktoken installed, using it to count tokens, tiktoken will download "
                "tokenizer from network, also you can download it and put it in the "
                "directory of environment variable TIKTOKEN_CACHE_DIR"
            )
        except ImportError:
            self._support_encoding = False
            logger.warning("tiktoken not installed, cannot count tokens, returning -1")
            return -1
        try:
            if not model_name:
                model_name = "gpt-3.5-turbo"
            self._encoding_model = tiktoken.model.encoding_for_model(model_name)
        except KeyError:
            logger.warning(
                f"{model_name}'s tokenizer not found, using cl100k_base encoding."
            )
            self._encoding_model = tiktoken.get_encoding("cl100k_base")
        return self._encoding_model


class LRUTokenCache:
    """当前类的职责定义。"""

    def __init__(self, max_size: int = 1000, max_memory_mb: float = 100):
        """初始化实例。"""
        # 检查条件是否满足。
        self.max_size = max(1, max_size)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024  # 转换数据格式。
        self.cache = OrderedDict()  # 代码说明。
        self.current_memory = 0  # 代码说明。

    def get(self, key):
        """获取对应数据。"""
        if key not in self.cache:
            return None

        # 获取对应数据。
        value, size, _ = self.cache[key]
        current_time = time.time()

        # 代码说明。
        self.cache.move_to_end(key)
        # 代码说明。
        self.cache[key] = (value, size, current_time)

        return value

    def put(self, key, value):
        """执行当前函数对应的业务逻辑。"""
        # 代码说明。
        size_estimate = sys.getsizeof(key) + sys.getsizeof(value)
        current_time = time.time()

        # 代码说明。
        if key in self.cache:
            _, old_size, _ = self.cache[key]
            self.current_memory -= old_size
            # 代码说明。
            self.cache.move_to_end(key)

        # 删除对应数据。
        # 代码说明。
        while (
            self.current_memory + size_estimate > self.max_memory_bytes
            and self.cache
            and len(self.cache) > 0
        ):
            # 代码说明。
            if len(self.cache) == 1 and key in self.cache:
                # 代码说明。
                # 代码说明。
                break

            oldest_key, (_, oldest_size, _) = next(iter(self.cache.items()))
            if oldest_key == key:
                # 代码说明。
                # 代码说明。
                self.cache.move_to_end(oldest_key)
                if len(self.cache) <= 1:
                    break
                oldest_key, (_, oldest_size, _) = next(iter(self.cache.items()))

            self.cache.pop(oldest_key)  # 代码说明。
            self.current_memory -= oldest_size
            logger.debug(
                f"LRU cache: Removed token count entry '{oldest_key}' due to memory "
                "limit"
            )

        # 代码说明。
        if len(self.cache) >= self.max_size and key not in self.cache:
            # 检查条件是否满足。
            if self.cache:
                oldest_key, (_, oldest_size, _) = next(iter(self.cache.items()))
                self.cache.pop(oldest_key)
                self.current_memory -= oldest_size
                logger.debug(
                    f"LRU cache: Removed token count entry '{oldest_key}' due to count "
                    "limit"
                )

        # 添加对应数据。
        self.cache[key] = (value, size_estimate, current_time)
        self.current_memory += size_estimate

    def clear(self):
        """执行当前函数对应的业务逻辑。"""
        self.cache.clear()
        self.current_memory = 0

    def __len__(self):
        """执行当前函数对应的业务逻辑。"""
        return len(self.cache)
