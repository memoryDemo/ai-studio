"""大语言模型基础接口和消息输出定义，是对话与补全能力的核心抽象。"""


import collections
import copy
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import (
    Any,
    AsyncIterator,
    Coroutine,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from cachetools import TTLCache

from meyo._private.pydantic import BaseModel, model_to_dict
from meyo.core.interface.media import MediaContent, MediaContentType, MediaObject
from meyo.core.interface.message import ModelMessage, ModelMessageRoleType
from meyo.util import BaseParameters
from meyo.util.annotations import PublicAPI
from meyo.util.model_utils import GPUInfo

logger = logging.getLogger(__name__)


@dataclass
@PublicAPI(stability="beta")
class ModelInferenceMetrics:
    """模型能力抽象或实现。"""

    collect_index: Optional[int] = 0

    start_time_ms: Optional[int] = None
    """字段说明。"""

    end_time_ms: Optional[int] = None
    """字段说明。"""

    current_time_ms: Optional[int] = None
    """字段说明。"""

    first_token_time_ms: Optional[int] = None
    """字段说明。"""

    first_completion_time_ms: Optional[int] = None
    """字段说明。"""

    first_completion_tokens: Optional[int] = None
    """字段说明。"""

    prompt_tokens: Optional[int] = None
    """字段说明。"""

    completion_tokens: Optional[int] = None
    """字段说明。"""

    total_tokens: Optional[int] = None
    """字段说明。"""

    speed_per_second: Optional[float] = None
    """字段说明。"""

    prefill_tokens_per_second: Optional[float] = None
    """字段说明。"""

    decode_tokens_per_second: Optional[float] = None
    """字段说明。"""

    current_gpu_infos: Optional[List[GPUInfo]] = None
    """字段说明。"""

    avg_gpu_infos: Optional[List[GPUInfo]] = None
    """字段说明。"""

    @staticmethod
    def create_metrics(
        last_metrics: Optional["ModelInferenceMetrics"] = None,
    ) -> "ModelInferenceMetrics":
        """创建对象实例。"""
        start_time_ms = last_metrics.start_time_ms if last_metrics else None
        first_token_time_ms = last_metrics.first_token_time_ms if last_metrics else None
        first_completion_time_ms = (
            last_metrics.first_completion_time_ms if last_metrics else None
        )
        first_completion_tokens = (
            last_metrics.first_completion_tokens if last_metrics else None
        )
        prompt_tokens = last_metrics.prompt_tokens if last_metrics else None
        completion_tokens = last_metrics.completion_tokens if last_metrics else None
        total_tokens = last_metrics.total_tokens if last_metrics else None
        speed_per_second = last_metrics.speed_per_second if last_metrics else None
        prefill_tokens_per_second = (
            last_metrics.prefill_tokens_per_second if last_metrics else None
        )
        decode_tokens_per_second = (
            last_metrics.decode_tokens_per_second if last_metrics else None
        )
        current_gpu_infos = last_metrics.current_gpu_infos if last_metrics else None
        avg_gpu_infos = last_metrics.avg_gpu_infos if last_metrics else None

        if not start_time_ms:
            start_time_ms = time.time_ns() // 1_000_000
        current_time_ms = time.time_ns() // 1_000_000
        end_time_ms = current_time_ms

        return ModelInferenceMetrics(
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            current_time_ms=current_time_ms,
            first_token_time_ms=first_token_time_ms,
            first_completion_time_ms=first_completion_time_ms,
            first_completion_tokens=first_completion_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            speed_per_second=speed_per_second,
            prefill_tokens_per_second=prefill_tokens_per_second,
            decode_tokens_per_second=decode_tokens_per_second,
            current_gpu_infos=current_gpu_infos,
            avg_gpu_infos=avg_gpu_infos,
        )

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        return asdict(self)

    def to_printable_string(self) -> str:
        """转换为目标数据结构。"""
        lines = []

        # 代码说明。
        first_token_latency = None
        if self.first_token_time_ms is not None and self.start_time_ms is not None:
            first_token_latency = (
                self.first_token_time_ms - self.start_time_ms
            ) / 1000.0

        # 添加对应数据。
        lines.append("=== Model Inference Metrics ===")

        # 代码说明。
        lines.append("\n▶ Latency:")
        if first_token_latency is not None:
            lines.append(f"  • First Token Latency: {first_token_latency:.3f}s")
        else:
            lines.append("  • First Token Latency: N/A")

        # 代码说明。
        lines.append("\n▶ Speed:")
        if self.prefill_tokens_per_second is not None:
            lines.append(
                f"  • Prefill Speed: {self.prefill_tokens_per_second:.2f} tokens/s"
            )
        else:
            lines.append("  • Prefill Speed: N/A")

        if self.decode_tokens_per_second is not None:
            lines.append(
                f"  • Decode Speed: {self.decode_tokens_per_second:.2f} tokens/s"
            )
        else:
            lines.append("  • Decode Speed: N/A")

        # 代码说明。
        lines.append("\n▶ Tokens:")
        if self.prompt_tokens is not None:
            lines.append(f"  • Prompt Tokens: {self.prompt_tokens}")
        else:
            lines.append("  • Prompt Tokens: N/A")

        if self.completion_tokens is not None:
            lines.append(f"  • Completion Tokens: {self.completion_tokens}")
        else:
            lines.append("  • Completion Tokens: N/A")

        if self.total_tokens is not None:
            lines.append(f"  • Total Tokens: {self.total_tokens}")

        return "\n".join(lines)


@dataclass
@PublicAPI(stability="beta")
class ModelRequestContext:
    """接口数据结构定义。"""

    stream: bool = False
    """字段说明。"""

    cache_enable: bool = False
    """字段说明。"""

    user_name: Optional[str] = None
    """字段说明。"""

    sys_code: Optional[str] = None
    """字段说明。"""

    conv_uid: Optional[str] = None
    """字段说明。"""

    span_id: Optional[str] = None
    """字段说明。"""

    chat_mode: Optional[str] = None
    """字段说明。"""

    chat_param: Optional[str] = None
    """字段说明。"""

    extra: Optional[Dict[str, Any]] = field(default_factory=dict)
    """字段说明。"""

    request_id: Optional[str] = None
    """字段说明。"""

    is_reasoning_model: Optional[bool] = False
    """字段说明。"""


@dataclass
@PublicAPI(stability="beta")
class ModelOutput:
    """模型能力抽象或实现。"""

    content: Union[MediaContent, List[MediaContent]]
    """字段说明。"""
    error_code: int
    """字段说明。"""
    incremental: bool = False
    model_context: Optional[Dict] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    metrics: Optional[ModelInferenceMetrics] = None
    """字段说明。"""

    def __init__(
        self,
        error_code: int,
        text: Optional[str] = None,
        content: Optional[
            Union[
                MediaContent, List[MediaContent], Dict[str, Any], List[Dict[str, Any]]
            ]
        ] = None,
        **kwargs,
    ):
        if text is not None and content is not None:
            raise ValueError("Cannot pass both text and content")
        elif text is not None:
            self.content = MediaContent.build_text(text)
        elif content is not None:
            self.content = MediaContent.parse_content(content)
        else:
            raise ValueError("Must pass either text or content")
        self.error_code = error_code
        for k, v in kwargs.items():
            if k in [
                "incremental",
                "model_context",
                "finish_reason",
                "usage",
                "metrics",
            ]:
                setattr(self, k, v)

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        text = self.gen_text_with_thinking()
        return {
            "error_code": self.error_code,
            "text": text,
            "incremental": self.incremental,
            "model_context": self.model_context,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "metrics": self.metrics,
        }

    @property
    def success(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return self.error_code == 0

    @property
    def has_text(self) -> bool:
        """校验条件并返回判断结果。"""
        if isinstance(self.content, MediaContent):
            return self.content.type == MediaContentType.TEXT
        elif isinstance(self.content, list):
            return any(c.type == MediaContentType.TEXT for c in self.content)
        return False

    @property
    def text(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        if isinstance(self.content, MediaContent):
            return self.content.get_text()
        elif isinstance(self.content, list) and all(
            isinstance(c, MediaContent) for c in self.content
        ):
            return MediaContent.last_text(self.content)
        raise ValueError("The content is not text")

    @property
    def has_thinking(self) -> bool:
        """校验条件并返回判断结果。"""
        if isinstance(self.content, MediaContent):
            return self.content.type == MediaContentType.THINKING
        elif isinstance(self.content, list) and self.content:
            return any(c.type == MediaContentType.THINKING for c in self.content)
        else:
            return False

    @property
    def thinking_text(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        if not self.content:
            return None
        if isinstance(self.content, MediaContent):
            if self.content.type == MediaContentType.THINKING:
                return self.content.get_thinking()
            return None
        elif isinstance(self.content, list) and all(
            isinstance(c, MediaContent) for c in self.content
        ):
            # 代码说明。
            thinking_content = [
                c for c in self.content if c.type == MediaContentType.THINKING
            ]
            if not thinking_content:
                return None
            # 返回对应结果。
            return thinking_content[-1].get_thinking()
        return None

    def gen_text_with_thinking(self, new_text: Optional[str] = None) -> str:
        from meyo.vis.tags.vis_thinking import VisThinking

        msg = ""
        if self.has_thinking:
            msg = self.thinking_text or ""
            msg = VisThinking().sync_display(content=msg)
            msg += "\n"
        if new_text:
            msg += new_text
        elif self.has_text:
            msg += self.text or ""
        return msg

    @text.setter
    def text(self, value: str):
        """执行当前函数对应的业务逻辑。"""
        if not isinstance(value, str):
            raise ValueError("text must be a string")
        # 代码说明。
        self.content = MediaContent(
            type="text",
            object=MediaObject(data=value, format="text"),
        )

    @classmethod
    def build_thinking(cls, thinking: str, error_code: int = 0) -> "ModelOutput":
        """构建目标对象。"""
        return cls(
            error_code=error_code,
            content=MediaContent.build_thinking(thinking),
        )

    @classmethod
    def build(
        cls,
        text: Optional[str] = None,
        thinking: Optional[str] = None,
        error_code: int = 0,
        usage: Optional[Dict[str, Any]] = None,
        finish_reason: Optional[str] = None,
        is_reasoning_model: bool = False,
        metrics: Optional[ModelInferenceMetrics] = None,
    ) -> "ModelOutput":
        if thinking and text:
            # 代码说明。
            content = [
                # 代码说明。
                MediaContent.build_thinking(thinking),
                MediaContent.build_text(text),
            ]
        elif text:
            # 代码说明。
            content = MediaContent.build_text(text)
        elif is_reasoning_model or thinking:
            # 代码说明。
            # 代码说明。
            content = MediaContent.build_thinking(thinking)
        else:
            content = MediaContent.build_text("")

        return cls(
            error_code=error_code,
            content=content,
            usage=usage,
            finish_reason=finish_reason,
            metrics=metrics,
        )

    @property
    def error_message(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self.text if self.has_text else "Unknown error"


_ModelMessageType = Union[List[ModelMessage], List[Dict[str, Any]]]


@dataclass
@PublicAPI(stability="beta")
class ModelRequest:
    """接口数据结构定义。"""

    model: str
    """字段说明。"""

    messages: _ModelMessageType
    """字段说明。"""

    temperature: Optional[float] = None
    """字段说明。"""

    top_p: Optional[float] = None
    """字段说明。"""

    max_new_tokens: Optional[int] = None
    """字段说明。"""

    stop: Optional[Union[str, List[str]]] = None
    """字段说明。"""
    stop_token_ids: Optional[List[int]] = None
    """字段说明。"""
    context_len: Optional[int] = None
    """字段说明。"""
    echo: Optional[bool] = False
    """字段说明。"""
    span_id: Optional[str] = None
    """字段说明。"""

    context: Optional[ModelRequestContext] = field(
        default_factory=lambda: ModelRequestContext()
    )
    """字段说明。"""

    @property
    def stream(self) -> bool:
        """生成模型输出。"""
        return bool(self.context and self.context.stream)

    def copy(self) -> "ModelRequest":
        """执行当前函数对应的业务逻辑。"""
        new_request = copy.deepcopy(self)
        # 代码说明。
        new_request.messages = new_request.get_messages()
        return new_request

    def to_dict(self) -> Dict[str, Any]:
        """转换为目标数据结构。"""
        new_reqeust = copy.deepcopy(self)
        new_messages = []
        for message in new_reqeust.messages:
            if isinstance(message, dict):
                new_messages.append(message)
            else:
                new_messages.append(message.dict())
        new_reqeust.messages = new_messages
        # 代码说明。
        return {k: v for k, v in asdict(new_reqeust).items() if v is not None}

    def to_trace_metadata(self) -> Dict[str, Any]:
        """转换为目标数据结构。"""
        metadata = self.to_dict()
        metadata["prompt"] = self.messages_to_string()
        return metadata

    def get_messages(self) -> List[ModelMessage]:
        """获取对应数据。"""
        messages = []
        for message in self.messages:
            if isinstance(message, dict):
                messages.append(ModelMessage(**message))
            else:
                messages.append(message)
        return messages

    def get_single_user_message(self) -> Optional[ModelMessage]:
        """获取对应数据。"""
        messages = self.get_messages()
        if len(messages) != 1 and messages[0].role != ModelMessageRoleType.HUMAN:
            raise ValueError("The messages is not a single user message")
        return messages[0]

    @staticmethod
    def build_request(
        model: str,
        messages: List[ModelMessage],
        context: Optional[Union[ModelRequestContext, Dict[str, Any], BaseModel]] = None,
        stream: bool = False,
        echo: bool = False,
        **kwargs,
    ):
        """构建目标对象。"""
        if not context:
            context = ModelRequestContext(stream=stream)
        elif not isinstance(context, ModelRequestContext):
            context_dict = None
            if isinstance(context, dict):
                context_dict = context
            elif isinstance(context, BaseModel):
                context_dict = model_to_dict(context)
            if context_dict and "stream" not in context_dict:
                context_dict["stream"] = stream
            if context_dict:
                context = ModelRequestContext(**context_dict)
            else:
                context = ModelRequestContext(stream=stream)
        return ModelRequest(
            model=model,
            messages=messages,
            context=context,
            echo=echo,
            **kwargs,
        )

    @staticmethod
    def _build(model: str, prompt: str, **kwargs):
        return ModelRequest(
            model=model,
            messages=[ModelMessage(role=ModelMessageRoleType.HUMAN, content=prompt)],
            **kwargs,
        )

    def to_common_messages(
        self, support_system_role: bool = True
    ) -> List[Dict[str, Any]]:
        """转换为目标数据结构。"""
        messages = [
            m if isinstance(m, ModelMessage) else ModelMessage(**m)
            for m in self.messages
        ]
        return ModelMessage.to_common_messages(
            messages, support_system_role=support_system_role
        )

    def messages_to_string(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return ModelMessage.messages_to_string(self.get_messages())

    def split_messages(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        """执行当前函数对应的业务逻辑。"""
        messages = self.get_messages()
        common_messages = []
        system_messages = []
        for message in messages:
            if message.role == ModelMessageRoleType.HUMAN:
                common_messages.append({"role": "user", "content": message.content})
            elif message.role == ModelMessageRoleType.SYSTEM:
                system_messages.append(message.content)
            elif message.role == ModelMessageRoleType.AI:
                common_messages.append(
                    {"role": "assistant", "content": message.content}
                )
            else:
                pass
        return common_messages, system_messages


@dataclass
class ModelExtraMedata(BaseParameters):
    """模型能力抽象或实现。"""

    prompt_roles: List[str] = field(
        default_factory=lambda: [
            ModelMessageRoleType.SYSTEM,
            ModelMessageRoleType.HUMAN,
            ModelMessageRoleType.AI,
        ],
        metadata={"help": "The roles of the prompt"},
    )

    prompt_sep: Optional[str] = field(
        default="\n",
        metadata={"help": "The separator of the prompt between multiple rounds"},
    )

    # 代码说明。
    # 代码说明。
    prompt_chat_template: Optional[str] = field(
        default=None,
        metadata={
            "help": "The chat template, see: "
            "https://huggingface.co/docs/transformers/main/en/chat_templating"
        },
    )

    @property
    def support_system_message(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return ModelMessageRoleType.SYSTEM in self.prompt_roles


@dataclass
@PublicAPI(stability="beta")
class ModelMetadata(BaseParameters):
    """模型能力抽象或实现。"""

    model: Union[str, List[str]] = field(
        metadata={"help": "Model name"},
    )
    label: Optional[str] = field(
        default=None,
        metadata={"help": "Model label"},
    )
    context_length: Optional[int] = field(
        default=None,
        metadata={"help": "Context length of model"},
    )
    max_output_length: Optional[int] = field(
        default=None,
        metadata={"help": "Max output length of model"},
    )
    description: Optional[str] = field(
        default=None,
        metadata={"help": "Model description"},
    )
    link: Optional[str] = field(
        default=None,
        metadata={"help": "Model link"},
    )
    chat_model: Optional[bool] = field(
        default=True,
        metadata={"help": "Whether the model is a chat model"},
    )
    function_calling: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether the model is a function calling model"},
    )
    metadata: Optional[Dict[str, Any]] = field(
        default_factory=dict,
        metadata={"help": "Model metadata"},
    )
    ext_metadata: Optional[ModelExtraMedata] = field(
        default_factory=ModelExtraMedata,
        metadata={"help": "Model extra metadata"},
    )

    @classmethod
    def from_dict(
        cls, data: dict, ignore_extra_fields: bool = False
    ) -> "ModelMetadata":
        """根据输入参数创建对象。"""
        if "ext_metadata" in data:
            data["ext_metadata"] = ModelExtraMedata(**data["ext_metadata"])
        return cls(**data)


class MessageConverter(ABC):
    """接口数据结构定义。"""

    @abstractmethod
    def convert(
        self,
        messages: List[ModelMessage],
        model_metadata: Optional[ModelMetadata] = None,
    ) -> List[ModelMessage]:
        """转换为目标数据结构。"""


class DefaultMessageConverter(MessageConverter):
    """接口数据结构定义。"""

    def __init__(self, prompt_sep: Optional[str] = None):
        """初始化实例。"""
        self._prompt_sep = prompt_sep

    def convert(
        self,
        messages: List[ModelMessage],
        model_metadata: Optional[ModelMetadata] = None,
    ) -> List[ModelMessage]:
        """转换为目标数据结构。"""
        # 代码说明。
        messages = list(filter(lambda m: m.pass_to_model, messages))
        # 代码说明。
        messages = self.move_last_user_message_to_end(messages)

        if not model_metadata or not model_metadata.ext_metadata:
            logger.warning("No model metadata, skip message system message conversion")
            return messages
        if not model_metadata.ext_metadata.support_system_message:
            # 转换数据格式。
            return self.convert_to_no_system_message(messages, model_metadata)
        return messages

    def convert_to_no_system_message(
        self,
        messages: List[ModelMessage],
        model_metadata: Optional[ModelMetadata] = None,
    ) -> List[ModelMessage]:
        """转换为目标数据结构。"""
        if not model_metadata or not model_metadata.ext_metadata:
            logger.warning("No model metadata, skip message conversion")
            return messages
        ext_metadata = model_metadata.ext_metadata
        system_messages = []
        result_messages = []
        for message in messages:
            if message.role == ModelMessageRoleType.SYSTEM:
                # 代码说明。
                # 代码说明。
                system_messages.append(message)
            elif message.role in [
                ModelMessageRoleType.HUMAN,
                ModelMessageRoleType.AI,
            ]:
                result_messages.append(message)
        prompt_sep = self._prompt_sep or ext_metadata.prompt_sep or "\n"
        system_message_str = None
        if len(system_messages) > 1:
            logger.warning("Your system messages have more than one message")
            system_message_str = prompt_sep.join([m.content for m in system_messages])
        elif len(system_messages) == 1:
            system_message_str = system_messages[0].content

        if system_message_str and result_messages:
            # 代码说明。
            # 代码说明。
            result_messages[-1].content = (
                system_message_str + prompt_sep + result_messages[-1].content
            )
        return result_messages

    def move_last_user_message_to_end(
        self, messages: List[ModelMessage]
    ) -> List[ModelMessage]:
        """执行当前函数对应的业务逻辑。"""
        last_user_input_index = None
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == ModelMessageRoleType.HUMAN:
                last_user_input_index = i
                break
        if last_user_input_index is not None:
            last_user_input = messages.pop(last_user_input_index)
            messages.append(last_user_input)
        return messages


@PublicAPI(stability="beta")
class LLMClient(ABC):
    """外部服务连接和调用实现。"""

    # 整理元数据。
    _MODEL_CACHE_ = TTLCache(maxsize=100, ttl=60)

    @property
    def cache(self) -> collections.abc.MutableMapping:
        """执行当前函数对应的业务逻辑。"""
        return self._MODEL_CACHE_

    @abstractmethod
    async def generate(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> ModelOutput:
        """生成模型输出。"""

    @abstractmethod
    async def generate_stream(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> AsyncIterator[ModelOutput]:
        """生成模型输出。"""

    @abstractmethod
    async def models(self) -> List[ModelMetadata]:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def count_token(self, model: str, prompt: str) -> int:
        """执行当前函数对应的业务逻辑。"""

    async def covert_message(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> ModelRequest:
        """执行当前函数对应的业务逻辑。"""
        if not message_converter:
            return request
        new_request = request.copy()
        model_metadata = await self.get_model_metadata(request.model)
        new_messages = message_converter.convert(request.get_messages(), model_metadata)
        new_request.messages = new_messages
        return new_request

    async def cached_models(self) -> List[ModelMetadata]:
        """执行当前函数对应的业务逻辑。"""
        key = "____$llm_client_models$____"
        if key not in self.cache:
            models = await self.models()
            self.cache[key] = models
            for model in models:
                model_metadata_key = (
                    f"____$llm_client_models_metadata_{model.model}$____"
                )
                self.cache[model_metadata_key] = model
        return self.cache[key]

    async def get_model_metadata(self, model: str) -> ModelMetadata:
        """获取对应数据。"""
        model_metadata_key = f"____$llm_client_models_metadata_{model}$____"
        if model_metadata_key not in self.cache:
            await self.cached_models()
        model_metadata = self.cache.get(model_metadata_key)
        if not model_metadata:
            raise ValueError(f"Model {model} not found")
        return model_metadata

    def __call__(
        self, *args, **kwargs
    ) -> Coroutine[Any, Any, ModelOutput] | ModelOutput:
        """执行调用逻辑。"""
        import asyncio

        from meyo.util import get_or_create_event_loop

        try:
            # 检查条件是否满足。
            loop = asyncio.get_running_loop()
            # 代码说明。
            if loop.is_running():
                # 代码说明。
                # 返回对应结果。
                return self.async_call(*args, **kwargs)
            else:
                loop = get_or_create_event_loop()
                return loop.run_until_complete(self.async_call(*args, **kwargs))
        except RuntimeError:
            # 代码说明。
            loop = get_or_create_event_loop()
            return loop.run_until_complete(self.async_call(*args, **kwargs))

    async def async_call(self, *args, **kwargs) -> ModelOutput:
        """执行调用逻辑。"""
        req = self._build_call_request(*args, **kwargs)
        return await self.generate(req)

    async def async_call_stream(self, *args, **kwargs) -> AsyncIterator[ModelOutput]:
        """执行调用逻辑。"""
        req = self._build_call_request(*args, **kwargs)
        async for output in self.generate_stream(req):  # type: ignore
            yield output

    def _build_call_request(self, *args, **kwargs) -> ModelRequest:
        """执行调用逻辑。"""
        messages = kwargs.get("messages")
        model = kwargs.get("model")

        if messages:
            del kwargs["messages"]
            model_messages = ModelMessage.from_openai_messages(messages)
        else:
            model_messages = [ModelMessage.build_human_message(args[0])]

        if not model:
            if hasattr(self, "default_model"):
                model = getattr(self, "default_model")
            else:
                raise ValueError("The default model is not set")

        if "model" in kwargs:
            del kwargs["model"]

        return ModelRequest.build_request(model, model_messages, **kwargs)
