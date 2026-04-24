"""核心通用类型定义，支撑模型接口、接口结构和存储接口复用。"""


from typing import Iterable, Optional, TypeAlias, Union

from typing_extensions import Literal, Required, TypedDict

from .ext_types import (
    ExtChatCompletionContentPartInputAudioParam,
    ExtChatCompletionContentPartInputFileParam,
    ExtChatCompletionContentPartInputVideoParam,
)


class ChatCompletionContentPartTextParam(TypedDict, total=False):
    text: Required[str]
    """字段说明。"""

    type: Required[Literal["text"]]
    """字段说明。"""


class ImageURL(TypedDict, total=False):
    url: Required[str]
    """字段说明。"""

    detail: Literal["auto", "low", "high"]
    """字段说明。"""


class ChatCompletionContentPartImageParam(TypedDict, total=False):
    image_url: Required[ImageURL]

    type: Required[Literal["image_url"]]
    """字段说明。"""


class InputAudio(TypedDict, total=False):
    data: Required[str]
    """编码后音频数据的格式。"""

    format: Required[Literal["wav", "mp3"]]
    """编码后音频数据的格式。"""


class ChatCompletionContentPartInputAudioParam(TypedDict, total=False):
    input_audio: Required[InputAudio]

    type: Required[Literal["input_audio"]]
    """字段说明。"""


class Function(TypedDict, total=False):
    arguments: Required[str]
    """字段说明。"""

    name: Required[str]
    """字段说明。"""


class FunctionCall(TypedDict, total=False):
    arguments: Required[str]
    """字段说明。"""

    name: Required[str]
    """字段说明。"""


class ChatCompletionMessageToolCallParam(TypedDict, total=False):
    id: Required[str]
    """字段说明。"""

    function: Required[Function]
    """字段说明。"""

    type: Required[Literal["function"]]
    """字段说明。"""


class Audio(TypedDict, total=False):
    id: Required[str]
    """字段说明。"""


class ChatCompletionContentPartRefusalParam(TypedDict, total=False):
    refusal: Required[str]
    """字段说明。"""

    type: Required[Literal["refusal"]]
    """字段说明。"""


ChatCompletionContentPartParam: TypeAlias = Union[
    ChatCompletionContentPartTextParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartInputAudioParam,
    ExtChatCompletionContentPartInputAudioParam,
    ExtChatCompletionContentPartInputVideoParam,
    ExtChatCompletionContentPartInputFileParam,
]
ContentArrayOfContentPart: TypeAlias = Union[
    ChatCompletionContentPartTextParam, ChatCompletionContentPartRefusalParam
]


class ChatCompletionSystemMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ChatCompletionContentPartTextParam]]]
    """字段说明。"""

    role: Required[Literal["system"]]
    """字段说明。"""

    name: str
    """字段说明。"""


class ChatCompletionUserMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ChatCompletionContentPartParam]]]
    """字段说明。"""

    role: Required[Literal["user"]]
    """字段说明。"""

    name: str
    """字段说明。"""


class ChatCompletionAssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]
    """字段说明。"""

    audio: Optional[Audio]
    """字段说明。"""

    content: Union[str, Iterable[ContentArrayOfContentPart], None]
    """字段说明。"""

    function_call: Optional[FunctionCall]
    """字段说明。"""

    name: str
    """字段说明。"""

    refusal: Optional[str]
    """字段说明。"""

    tool_calls: Iterable[ChatCompletionMessageToolCallParam]
    """字段说明。"""


class ChatCompletionToolMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ChatCompletionContentPartTextParam]]]
    """字段说明。"""

    role: Required[Literal["tool"]]
    """字段说明。"""

    tool_call_id: Required[str]
    """字段说明。"""


class ChatCompletionFunctionMessageParam(TypedDict, total=False):
    content: Required[Optional[str]]
    """字段说明。"""

    name: Required[str]
    """字段说明。"""

    role: Required[Literal["function"]]
    """字段说明。"""


# 历史调试代码，当前不启用。
OpenAIChatCompletionMessageParam: TypeAlias = Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionFunctionMessageParam,
]

ChatCompletionMessageParam = OpenAIChatCompletionMessageParam
