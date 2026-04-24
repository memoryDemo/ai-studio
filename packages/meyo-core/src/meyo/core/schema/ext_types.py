"""扩展类型定义，补充接口结构和配置解析中需要的特殊字段类型。"""


from typing_extensions import Literal, Required, TypedDict


class ExtAudioURL(TypedDict, total=False):
    url: Required[str]
    """音频文件地址。"""

    detail: Required[Literal["wav", "mp3"]]
    """编码后音频数据的格式。"""


class ExtChatCompletionContentPartInputAudioParam(TypedDict, total=False):
    audio_url: Required[ExtAudioURL]

    type: Required[Literal["audio_url"]]
    """内容片段类型固定为音频地址。"""


class ExtVideoURL(TypedDict, total=False):
    url: Required[str]
    """视频文件地址。"""

    detail: Required[Literal["mp4", "avi"]]
    """编码后视频数据的格式。"""


class ExtChatCompletionContentPartInputVideoParam(TypedDict, total=False):
    video_url: Required[ExtVideoURL]

    type: Required[Literal["video_url"]]
    """内容片段类型固定为视频地址。"""


class ExtFileURL(TypedDict, total=False):
    url: Required[str]
    """字段说明。"""


class ExtChatCompletionContentPartInputFileParam(TypedDict, total=False):
    file_url: Required[ExtFileURL]
    type: Required[Literal["file_url"]]
    """内容片段类型固定为文件地址。"""
