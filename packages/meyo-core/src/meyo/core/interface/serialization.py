"""序列化接口定义，统一复杂对象在模型服务链路中的转换方式。"""


from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional, Type


class Serializable(ABC):
    """当前类的职责定义。"""

    _serializer: Optional["Serializer"] = None

    @abstractmethod
    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""

    def serialize(self) -> bytes:
        """执行当前函数对应的业务逻辑。"""
        if self._serializer is None:
            raise ValueError(
                "Serializer is not set. Please set the serializer before serialization."
            )
        return self._serializer.serialize(self)

    def set_serializer(self, serializer: "Serializer") -> None:
        """设置对应数据。"""
        self._serializer = serializer


class Serializer(ABC):
    """当前类的职责定义。"""

    @abstractmethod
    def serialize(self, obj: Serializable) -> bytes:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def deserialize(self, data: bytes, cls: Type[Serializable]) -> Serializable:
        """执行当前函数对应的业务逻辑。"""
