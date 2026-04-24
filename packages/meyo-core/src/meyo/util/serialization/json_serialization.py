"""序列化工具模块，负责把模型服务中的复杂对象转换为可传输结构。
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Type

from meyo.model.resource import ResourceCategory, register_resource
from meyo.core.interface.serialization import Serializable, Serializer
from meyo.util.i18n_utils import _

JSON_ENCODING = "utf-8"


class JsonSerializable(Serializable, ABC):
    @abstractmethod
    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""

    def serialize(self) -> bytes:
        """执行当前函数对应的业务逻辑。"""
        return json.dumps(self.to_dict(), ensure_ascii=False).encode(JSON_ENCODING)


@register_resource(
    label=_("Json Serializer"),
    name="json_serializer",
    category=ResourceCategory.SERIALIZER,
    description=_("The serializer for serializing data with json format."),
)
class JsonSerializer(Serializer):
    """当前类的职责定义。"""

    def serialize(self, obj: Serializable) -> bytes:
        """执行当前函数对应的业务逻辑。"""
        return json.dumps(obj.to_dict(), ensure_ascii=False).encode(JSON_ENCODING)

    def deserialize(self, data: bytes, cls: Type[Serializable]) -> Serializable:
        """执行当前函数对应的业务逻辑。"""
        # 转换数据格式。
        json_data = json.loads(data.decode(JSON_ENCODING))
        # 代码说明。
        obj = cls(**json_data)
        obj.set_serializer(self)
        return obj
