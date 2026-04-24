"""模型资源注册兼容层，用于保留供应商参数注册入口并隔离非核心编排依赖。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeVar

TAGS_ORDER_HIGH = "higher-order"

T = TypeVar("T")


class ResourceCategory(str, Enum):
    """枚举类型定义。"""

    HTTP_BODY = "http_body"
    LLM_CLIENT = "llm_client"
    STORAGE = "storage"
    SERIALIZER = "serializer"
    COMMON = "common"
    PROMPT = "prompt"
    AGENT = "agent"
    EMBEDDINGS = "embeddings"
    RAG = "rag"
    VECTOR_STORE = "vector_store"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    FULL_TEXT = "full_text"
    DATABASE = "database"
    EXAMPLE = "example"


@dataclass(slots=True)
class Parameter:
    """配置参数定义。"""

    label: str
    name: str
    type: type
    optional: bool = True
    default: Any = None
    description: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def build_from(
        cls,
        label: str | None = None,
        name: str | None = None,
        type: type | None = None,
        **kwargs: Any,
    ) -> "Parameter":
        """构建目标对象。"""
        if label is not None:
            kwargs["label"] = label
        if name is not None:
            kwargs["name"] = name
        if type is not None:
            kwargs["type"] = type
        known = {
            "label",
            "name",
            "type",
            "optional",
            "default",
            "description",
        }
        init_kwargs = {key: value for key, value in kwargs.items() if key in known}
        init_kwargs["extra"] = {key: value for key, value in kwargs.items() if key not in known}
        return cls(**init_kwargs)


def auto_register_resource(*args: Any, **kwargs: Any) -> Callable[[T], T]:
    """执行当前函数对应的业务逻辑。"""

    def decorator(obj: T) -> T:
        return obj

    return decorator


def register_resource(*args: Any, **kwargs: Any) -> Callable[[T], T]:
    """注册对象。"""

    def decorator(obj: T) -> T:
        return obj

    return decorator
