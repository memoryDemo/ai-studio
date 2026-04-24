"""链路追踪工具模块，负责模型服务请求的追踪初始化、记录和中间件集成。"""

from __future__ import annotations

import json
import secrets
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from meyo.component import BaseComponent, ComponentType, SystemApp

MEYO_TRACER_SPAN_ID = "Meyo-Trace-Span-Id"
MEYO_TRACER_SPAN_ID_COMPAT = "Umber-Studio-Trace-Span-Id"

# 代码说明。
_TRACE_ID_MAX_VALUE = 2**128 - 1
_SPAN_ID_MAX_VALUE = 2**64 - 1
INVALID_SPAN_ID = 0x0000000000000000
INVALID_TRACE_ID = 0x00000000000000000000000000000000


class SpanType(str, Enum):
    BASE = "base"
    RUN = "run"
    CHAT = "chat"
    AGENT = "agent"


class SpanTypeRunName(str, Enum):
    WEBSERVER = "Webserver"
    WORKER_MANAGER = "WorkerManager"
    MODEL_WORKER = "ModelWorker"
    EMBEDDING_MODEL = "EmbeddingModel"

    @staticmethod
    def values():
        return [item.value for item in SpanTypeRunName]


class Span:
    """当前类的职责定义。"""

    def __init__(
        self,
        trace_id: str,
        span_id: str,
        span_type: SpanType = None,
        parent_span_id: str = None,
        operation_name: str = None,
        metadata: Dict = None,
        end_caller: Callable[[Span], None] = None,
    ):
        if not span_type:
            span_type = SpanType.BASE
        self.span_type = span_type
        # 代码说明。
        self.trace_id = trace_id
        # 代码说明。
        self.span_id = span_id
        # 代码说明。
        self.parent_span_id = parent_span_id
        # 代码说明。
        self.operation_name = operation_name
        # 代码说明。
        self.start_time = datetime.now()
        # 代码说明。
        self.end_time = None
        # 整理元数据。
        self.metadata = metadata or {}
        self._end_callers = []
        if end_caller:
            self._end_callers.append(end_caller)

    def end(self, **kwargs):
        """执行当前函数对应的业务逻辑。"""
        self.end_time = datetime.now()
        if "metadata" in kwargs:
            self.metadata = kwargs.get("metadata")
        for caller in self._end_callers:
            caller(self)

    def add_end_caller(self, end_caller: Callable[[Span], None]):
        if end_caller:
            self._end_callers.append(end_caller)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
        return False

    def to_dict(self) -> Dict:
        return {
            "span_type": self.span_type.value,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "start_time": (
                None
                if not self.start_time
                else self.start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            ),
            "end_time": (
                None
                if not self.end_time
                else self.end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            ),
            "metadata": _clean_for_json(self.metadata) if self.metadata else None,
        }

    def copy(self) -> Span:
        """执行当前函数对应的业务逻辑。"""
        metadata = self.metadata.copy() if self.metadata else None
        span = Span(
            self.trace_id,
            self.span_id,
            self.span_type,
            self.parent_span_id,
            self.operation_name,
            metadata=metadata,
        )
        span.start_time = self.start_time
        span.end_time = self.end_time
        return span


class SpanStorageType(str, Enum):
    ON_CREATE = "on_create"
    ON_END = "on_end"
    ON_CREATE_END = "on_create_end"


class SpanStorage(BaseComponent, ABC):
    """存储能力实现。"""

    name = ComponentType.TRACER_SPAN_STORAGE.value

    def init_app(self, system_app: SystemApp):
        """初始化并启动相关能力。"""
        pass

    @abstractmethod
    def append_span(self, span: Span):
        """执行当前函数对应的业务逻辑。"""

    def append_span_batch(self, spans: List[Span]):
        """执行当前函数对应的业务逻辑。"""
        for span in spans:
            self.append_span(span)


class Tracer(BaseComponent, ABC):
    """当前类的职责定义。"""

    name = ComponentType.TRACER.value

    def __init__(self, system_app: SystemApp | None = None):
        super().__init__(system_app)
        self.system_app = system_app  # 代码说明。

    def init_app(self, system_app: SystemApp):
        """初始化并启动相关能力。"""
        self.system_app = system_app

    @abstractmethod
    def append_span(self, span: Span):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def start_span(
        self,
        operation_name: str,
        parent_span_id: str = None,
        span_type: SpanType = None,
        metadata: Dict = None,
    ) -> Span:
        """初始化并启动相关能力。"""

    @abstractmethod
    def end_span(self, span: Span, **kwargs):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def get_current_span(self) -> Optional[Span]:
        """获取对应数据。"""

    @abstractmethod
    def _get_current_storage(self) -> SpanStorage:
        """执行当前函数对应的业务逻辑。"""

    def _new_uuid(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return str(uuid.uuid4())

    def _new_random_trace_id(self) -> str:
        """执行当前函数对应的业务逻辑。"""

        return _new_random_trace_id()

    def _new_random_span_id(self) -> str:
        """执行当前函数对应的业务逻辑。"""

        return _new_random_span_id()


def _new_random_trace_id() -> str:
    """执行当前函数对应的业务逻辑。"""
    # 代码说明。
    return secrets.token_hex(16)


def _is_valid_trace_id(trace_id: Union[str, int]) -> bool:
    if isinstance(trace_id, str):
        try:
            trace_id = int(trace_id, 16)
        except ValueError:
            return False
    return INVALID_TRACE_ID < int(trace_id) <= _TRACE_ID_MAX_VALUE


def _new_random_span_id() -> str:
    """执行当前函数对应的业务逻辑。"""

    # 代码说明。
    return secrets.token_hex(8)


def _is_valid_span_id(span_id: Union[str, int]) -> bool:
    if isinstance(span_id, str):
        try:
            span_id = int(span_id, 16)
        except ValueError:
            return False
    return INVALID_SPAN_ID < int(span_id) <= _SPAN_ID_MAX_VALUE


def _split_span_id(span_id: str) -> Tuple[int, int]:
    parent_span_id_parts = span_id.split(":")
    if len(parent_span_id_parts) != 2:
        return 0, 0
    trace_id, parent_span_id = parent_span_id_parts
    try:
        trace_id = int(trace_id, 16)
        span_id = int(parent_span_id, 16)
        return trace_id, span_id
    except ValueError:
        return 0, 0


@dataclass
class TracerContext:
    span_id: Optional[str] = None


def _clean_for_json(data: Optional[str, Any] = None):
    if data is None:
        return None
    if isinstance(data, dict):
        cleaned_dict = {}
        for key, value in data.items():
            # 代码说明。
            cleaned_value = _clean_for_json(value)
            if cleaned_value is not None:
                # 添加对应数据。
                try:
                    json.dumps({key: cleaned_value})
                    cleaned_dict[key] = cleaned_value
                except TypeError:
                    # 代码说明。
                    pass
        return cleaned_dict
    elif isinstance(data, list):
        cleaned_list = []
        for item in data:
            cleaned_item = _clean_for_json(item)
            if cleaned_item is not None:
                try:
                    json.dumps(cleaned_item)
                    cleaned_list.append(cleaned_item)
                except TypeError:
                    pass
        return cleaned_list
    else:
        try:
            json.dumps(data)
            return data
        except TypeError:
            return None


def _parse_span_id(body: Any) -> Optional[str]:
    from starlette.requests import Request

    from meyo._private.pydantic import BaseModel, model_to_dict

    span_id: Optional[str] = None
    if isinstance(body, Request):
        span_id = body.headers.get(MEYO_TRACER_SPAN_ID) or body.headers.get(
            MEYO_TRACER_SPAN_ID_COMPAT
        )
    elif isinstance(body, dict):
        span_id = (
            body.get(MEYO_TRACER_SPAN_ID)
            or body.get(MEYO_TRACER_SPAN_ID_COMPAT)
            or body.get("span_id")
        )
    elif isinstance(body, BaseModel):
        dict_body = model_to_dict(body)
        span_id = (
            dict_body.get(MEYO_TRACER_SPAN_ID)
            or dict_body.get(MEYO_TRACER_SPAN_ID_COMPAT)
            or dict_body.get("span_id")
        )
    if not span_id:
        return None
    else:
        int_trace_id, int_span_id = _split_span_id(span_id)
        if not int_trace_id:
            return None
        if _is_valid_span_id(int_span_id) and _is_valid_trace_id(int_trace_id):
            return span_id
        else:
            return span_id
