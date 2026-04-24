"""模型消息结构定义，统一对话请求、响应和流式消息的数据格式。"""


from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple, Union, cast

from meyo._private.pydantic import BaseModel, Field, model_to_dict
from meyo.core.interface.media import MediaContent
from meyo.core.interface.storage import (
    InMemoryStorage,
    ResourceIdentifier,
    StorageInterface,
    StorageItem,
)

from ..schema.types import ChatCompletionMessageParam

MessageContentType = Union[str, List[MediaContent]]


class BaseMessage(BaseModel, ABC):
    """接口数据结构定义。"""

    content: MessageContentType
    index: int = 0
    round_index: int = 0
    """消息在会话中的轮次序号。"""
    additional_kwargs: dict = Field(default_factory=dict)

    @property
    @abstractmethod
    def type(self) -> str:
        """执行当前函数对应的业务逻辑。"""

    @property
    def pass_to_model(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return True

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        return {
            "type": self.type,
            "data": model_to_dict(self),
            "index": self.index,
            "round_index": self.round_index,
        }

    @staticmethod
    def messages_to_string(messages: List["BaseMessage"]) -> str:
        """执行当前函数对应的业务逻辑。"""
        return _messages_to_str(messages)

    @classmethod
    def parse_chat_completion_message(
        cls,
        message: Union[str, ChatCompletionMessageParam],
        role: str = "human",
        ignore_unknown_media: bool = False,
    ) -> "BaseMessage":
        """解析输入并返回标准结果。"""
        if not message:
            raise ValueError("The message is empty")
        if isinstance(message, str):
            content = message
        else:
            content = MediaContent.parse_chat_completion_message(
                message, ignore_unknown_media=ignore_unknown_media
            )
            if not isinstance(content, list):
                content = [content]
        if role == "human":
            return HumanMessage(content=content)
        elif role == "ai":
            return AIMessage(content=content)
        elif role == "system":
            return SystemMessage(content=content)
        elif role == "view":
            return ViewMessage(content=content)

    @property
    def last_text(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        if isinstance(self.content, list):
            return MediaContent.last_text(self.content)
        elif isinstance(self.content, str):
            return self.content
        raise ValueError("The content is not a string or list of MediaContent")

    def get_view_markdown_text(self, replace_url_func: Callable[[str], str]) -> str:
        if isinstance(self.content, str):
            return self.content
        elif isinstance(self.content, list):
            return MediaContent.get_view_markdown_text(self.content, replace_url_func)

    @property
    def has_media(self) -> bool:
        """校验条件并返回判断结果。"""
        return isinstance(self.content, list) and self.content


class HumanMessage(BaseMessage):
    """接口数据结构定义。"""

    example: bool = False

    @property
    def type(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return "human"


class AIMessage(BaseMessage):
    """接口数据结构定义。"""

    example: bool = False

    @property
    def type(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return "ai"


class ViewMessage(BaseMessage):
    """接口数据结构定义。"""

    example: bool = False

    @property
    def type(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return "view"

    @property
    def pass_to_model(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return False


class SystemMessage(BaseMessage):
    """接口数据结构定义。"""

    @property
    def type(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return "system"


class ModelMessageRoleType:
    """接口数据结构定义。"""

    SYSTEM = "system"
    HUMAN = "human"
    AI = "ai"
    VIEW = "view"


class ModelMessage(BaseModel):
    """接口数据结构定义。"""

    """兼容常见对话消息格式。"""
    role: str
    content: Union[str, List[MediaContent]]
    round_index: Optional[int] = 0

    @property
    def pass_to_model(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return self.role in [
            ModelMessageRoleType.SYSTEM,
            ModelMessageRoleType.HUMAN,
            ModelMessageRoleType.AI,
        ]

    @staticmethod
    def from_base_messages(messages: List[BaseMessage]) -> List["ModelMessage"]:
        """根据输入参数创建对象。"""
        result = []
        for message in messages:
            content, round_index = message.content, message.round_index
            if isinstance(message, HumanMessage):
                result.append(
                    ModelMessage(
                        role=ModelMessageRoleType.HUMAN,
                        content=content,
                        round_index=round_index,
                    )
                )
            elif isinstance(message, AIMessage):
                result.append(
                    ModelMessage(
                        role=ModelMessageRoleType.AI,
                        content=content,
                        round_index=round_index,
                    )
                )
            elif isinstance(message, SystemMessage):
                result.append(
                    ModelMessage(
                        role=ModelMessageRoleType.SYSTEM, content=message.content
                    )
                )
        return result

    @staticmethod
    def _parse_openai_system_message(
        message: ChatCompletionMessageParam,
    ) -> List[ModelMessage]:
        """执行当前函数对应的业务逻辑。"""
        content = message["content"]
        result = []
        if isinstance(content, str):
            result.append(
                ModelMessage(role=ModelMessageRoleType.SYSTEM, content=content)
            )
        elif isinstance(content, Iterable):
            for item in content:
                if isinstance(item, str):
                    result.append(
                        ModelMessage(role=ModelMessageRoleType.SYSTEM, content=item)
                    )
                elif isinstance(item, dict) and "type" in item:
                    type = item["type"]
                    if type == "text" and "text" in item:
                        result.append(
                            ModelMessage(
                                role=ModelMessageRoleType.SYSTEM, content=item["text"]
                            )
                        )
                    else:
                        raise ValueError(
                            f"Unknown message type: {item} of system message"
                        )
                else:
                    raise ValueError(f"Unknown message type: {item} of system message")
        else:
            raise ValueError(f"Unknown content type: {message} of system message")
        return result

    @staticmethod
    def _parse_openai_user_message(
        message: ChatCompletionMessageParam,
    ) -> List[ModelMessage]:
        """执行当前函数对应的业务逻辑。"""
        result = []
        content = message["content"]
        if isinstance(content, str):
            result.append(
                ModelMessage(role=ModelMessageRoleType.HUMAN, content=content)
            )
        elif isinstance(content, Iterable):
            for item in content:
                if isinstance(item, str):
                    result.append(
                        ModelMessage(role=ModelMessageRoleType.HUMAN, content=item)
                    )
                elif isinstance(item, dict) and "type" in item:
                    type = item["type"]
                    if type == "text" and "text" in item:
                        result.append(
                            ModelMessage(
                                role=ModelMessageRoleType.HUMAN, content=item["text"]
                            )
                        )
                    elif type == "image_url":
                        raise ValueError("Image message is not supported now")
                    elif type == "input_audio":
                        raise ValueError("Input audio message is not supported now")
                    else:
                        raise ValueError(
                            f"Unknown message type: {item} of human message"
                        )
                else:
                    raise ValueError(f"Unknown message type: {item} of humman message")
        else:
            raise ValueError(f"Unknown content type: {message} of humman message")
        return result

    @staticmethod
    def _parse_assistant_message(
        message: ChatCompletionMessageParam,
    ) -> List[ModelMessage]:
        """执行当前函数对应的业务逻辑。"""
        result = []
        content = message["content"]
        if isinstance(content, str):
            result.append(ModelMessage(role=ModelMessageRoleType.AI, content=content))
        elif isinstance(content, Iterable):
            for item in content:
                if isinstance(item, str):
                    result.append(
                        ModelMessage(role=ModelMessageRoleType.AI, content=item)
                    )
                elif isinstance(item, dict) and "type" in item:
                    type = item["type"]
                    if type == "text" and "text" in item:
                        result.append(
                            ModelMessage(
                                role=ModelMessageRoleType.AI, content=item["text"]
                            )
                        )
                    elif type == "refusal" and "refusal" in item:
                        result.append(
                            ModelMessage(
                                role=ModelMessageRoleType.AI, content=item["refusal"]
                            )
                        )
                    else:
                        raise ValueError(
                            f"Unknown message type: {item} of assistant message"
                        )
                else:
                    raise ValueError(
                        f"Unknown message type: {item} of assistant message"
                    )
        else:
            raise ValueError(f"Unknown content type: {message} of assistant message")
        return result

    @staticmethod
    def from_openai_messages(
        messages: Union[str, List[ChatCompletionMessageParam]],
    ) -> List["ModelMessage"]:
        """根据输入参数创建对象。"""
        if isinstance(messages, str):
            return [ModelMessage(role=ModelMessageRoleType.HUMAN, content=messages)]
        result = []
        for message in messages:
            msg_role = message["role"]
            if msg_role == "system":
                result.extend(ModelMessage._parse_openai_system_message(message))
            elif msg_role == "user":
                result.extend(ModelMessage._parse_openai_user_message(message))
            elif msg_role == "assistant":
                result.extend(ModelMessage._parse_assistant_message(message))
            elif msg_role == "function":
                raise ValueError(
                    "Function role is not supported in ModelMessage format"
                )
            elif msg_role == "tool":
                raise ValueError("Tool role is not supported in ModelMessage format")
            else:
                raise ValueError(f"Unknown role: {msg_role}")
        return result

    @staticmethod
    def to_common_messages(
        messages: List["ModelMessage"],
        convert_to_compatible_format: bool = False,
        support_system_role: bool = True,
        support_media_content: bool = True,
        type_mapping: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, str]]:
        """转换为目标数据结构。"""
        history = []
        # 添加对应数据。
        for message in messages:
            if message.role == ModelMessageRoleType.HUMAN:
                history.append(
                    MediaContent.to_chat_completion_message(
                        "user",
                        message.content,
                        support_media_content=support_media_content,
                        type_mapping=type_mapping,
                    )
                )
            elif message.role == ModelMessageRoleType.SYSTEM:
                if not support_system_role:
                    raise ValueError("Current model not support system role")
                # 代码说明。
                history.append(
                    MediaContent.to_chat_completion_message(
                        "system",
                        message.content,
                        support_media_content=support_media_content,
                        type_mapping=type_mapping,
                    )
                )
            elif message.role == ModelMessageRoleType.AI:
                history.append(
                    MediaContent.to_chat_completion_message(
                        "assistant",
                        message.content,
                        support_media_content=support_media_content,
                        type_mapping=type_mapping,
                    )
                )
            else:
                pass
        if convert_to_compatible_format:
            # 代码说明。
            last_user_input_index = None
            for i in range(len(history) - 1, -1, -1):
                if history[i]["role"] == "user":
                    last_user_input_index = i
                    break
            if last_user_input_index:
                last_user_input = history.pop(last_user_input_index)
                history.append(last_user_input)
        return history

    @staticmethod
    def to_dict_list(messages: List["ModelMessage"]) -> List[Dict[str, str]]:
        """转换为目标数据结构。"""
        return list(map(lambda m: model_to_dict(m), messages))

    @staticmethod
    def build_human_message(content: str) -> "ModelMessage":
        """构建目标对象。"""
        return ModelMessage(role=ModelMessageRoleType.HUMAN, content=content)

    @staticmethod
    def get_printable_message(messages: List["ModelMessage"]) -> str:
        """获取对应数据。"""
        str_msg = ""
        for message in messages:
            curr_message = (
                f"(Round {message.round_index}) {message.role}: {message.content} "
            )
            str_msg += curr_message.rstrip() + "\n"

        return str_msg

    @staticmethod
    def messages_to_string(
        messages: List["ModelMessage"],
        human_prefix: str = "Human",
        ai_prefix: str = "AI",
        system_prefix: str = "System",
    ) -> str:
        """执行当前函数对应的业务逻辑。"""
        return _messages_to_str(messages, human_prefix, ai_prefix, system_prefix)

    @staticmethod
    def parse_user_message(messages: List[ModelMessage]) -> str:
        """解析输入并返回标准结果。"""
        lass_user_message = None
        for message in messages[::-1]:
            if message.role == ModelMessageRoleType.HUMAN:
                lass_user_message = message.content
                break
        if not lass_user_message:
            raise ValueError("No user message")
        return lass_user_message


_SingleRoundMessage = List[BaseMessage]
_MultiRoundMessageMapper = Callable[[List[_SingleRoundMessage]], List[BaseMessage]]


def _message_to_dict(message: BaseMessage) -> Dict:
    return message.to_dict()


def _messages_to_dict(messages: List[BaseMessage]) -> List[Dict]:
    return [_message_to_dict(m) for m in messages]


def _messages_to_str(
    messages: Union[List[BaseMessage], List[ModelMessage]],
    human_prefix: str = "Human",
    ai_prefix: str = "AI",
    system_prefix: str = "System",
) -> str:
    """执行当前函数对应的业务逻辑。"""
    str_messages = []
    for message in messages:
        role = None
        if isinstance(message, HumanMessage):
            role = human_prefix
        elif isinstance(message, AIMessage):
            role = ai_prefix
        elif isinstance(message, SystemMessage):
            role = system_prefix
        elif isinstance(message, ViewMessage):
            pass
        elif isinstance(message, ModelMessage):
            role = message.role
        else:
            raise ValueError(f"Got unsupported message type: {message}")
        if role:
            str_messages.append(f"{role}: {message.content}")
    return "\n".join(str_messages)


def _message_from_dict(message: Dict) -> BaseMessage:
    _type = message["type"]
    if _type == "human":
        return HumanMessage(**message["data"])
    elif _type == "ai":
        return AIMessage(**message["data"])
    elif _type == "system":
        return SystemMessage(**message["data"])
    elif _type == "view":
        return ViewMessage(**message["data"])
    else:
        raise ValueError(f"Got unexpected type: {_type}")


def _messages_from_dict(messages: List[Dict]) -> List[BaseMessage]:
    return [_message_from_dict(m) for m in messages]


def parse_model_messages(
    messages: List[ModelMessage],
) -> Tuple[str, List[str], List[List[str]]]:
    """解析输入并返回标准结果。"""
    system_messages: List[str] = []
    history_messages: List[List[str]] = [[]]

    for message in messages[:-1]:
        if message.role == "human":
            history_messages[-1].append(message.content)
        elif message.role == "system":
            system_messages.append(message.content)
        elif message.role == "ai":
            history_messages[-1].append(message.content)
            history_messages.append([])
    if messages[-1].role != "human":
        raise ValueError("Hi! What do you want to talk about？")
    # 代码说明。
    history_messages = list(filter(lambda x: len(x) == 2, history_messages))
    user_prompt = messages[-1].content
    return user_prompt, system_messages, history_messages


class OnceConversation:
    """当前类的职责定义。"""

    def __init__(
        self,
        chat_mode: str,
        user_name: Optional[str] = None,
        sys_code: Optional[str] = None,
        summary: Optional[str] = None,
        app_code: Optional[str] = None,
        **kwargs,
    ):
        """初始化实例。"""
        self.chat_mode: str = chat_mode
        self.user_name: Optional[str] = user_name
        self.sys_code: Optional[str] = sys_code
        self.summary: Optional[str] = summary
        self.app_code: Optional[str] = app_code

        self.messages: List[BaseMessage] = kwargs.get("messages", [])
        self.start_date: str = kwargs.get("start_date", "")
        # 代码说明。
        # 代码说明。
        self.chat_order: int = int(kwargs.get("chat_order", 0))
        self.model_name: str = kwargs.get("model_name", "")
        self.param_type: str = kwargs.get("param_type", "")
        self.param_value: str = kwargs.get("param_value", "")
        self.cost: int = int(kwargs.get("cost", 0))
        self.tokens: int = int(kwargs.get("tokens", 0))
        self._message_index: int = int(kwargs.get("message_index", 0))

    def _append_message(self, message: BaseMessage) -> None:
        index = self._message_index
        self._message_index += 1
        message.index = index
        message.round_index = self.chat_order
        message.additional_kwargs["param_type"] = self.param_type
        message.additional_kwargs["param_value"] = self.param_value
        message.additional_kwargs["model_name"] = self.model_name
        self.messages.append(message)

    def start_new_round(self) -> None:
        """初始化并启动相关能力。"""
        self.chat_order += 1

    def end_current_round(self) -> None:
        """执行当前函数对应的业务逻辑。"""
        pass

    def add_user_message(
        self, message: MessageContentType, check_duplicate_type: Optional[bool] = False
    ) -> None:
        """执行当前函数对应的业务逻辑。"""
        if check_duplicate_type:
            has_message = any(
                isinstance(instance, HumanMessage) for instance in self.messages
            )
            if has_message:
                raise ValueError("Already Have Human message")
        self._append_message(HumanMessage(content=message))

    def add_ai_message(
        self, message: MessageContentType, update_if_exist: Optional[bool] = False
    ) -> None:
        """执行当前函数对应的业务逻辑。"""
        if not update_if_exist:
            self._append_message(AIMessage(content=message))
            return
        has_message = any(isinstance(instance, AIMessage) for instance in self.messages)
        if has_message:
            self._update_ai_message(message)
        else:
            self._append_message(AIMessage(content=message))

    def _update_ai_message(self, new_message: MessageContentType) -> None:
        """执行当前函数对应的业务逻辑。"""
        for item in self.messages:
            if item.type == "ai":
                item.content = new_message

    def add_view_message(self, message: MessageContentType) -> None:
        """执行当前函数对应的业务逻辑。"""
        self._append_message(ViewMessage(content=message))

    def add_system_message(self, message: MessageContentType) -> None:
        """执行当前函数对应的业务逻辑。"""
        self._append_message(SystemMessage(content=message))

    def set_start_time(self, datatime: datetime):
        """设置对应数据。"""
        dt_str = datatime.strftime("%Y-%m-%d %H:%M:%S")
        self.start_date = dt_str

    def clear(self) -> None:
        """执行当前函数对应的业务逻辑。"""
        self.messages.clear()

    def get_latest_user_message(self) -> Optional[HumanMessage]:
        """获取对应数据。"""
        for message in self.messages[::-1]:
            if isinstance(message, HumanMessage):
                return message
        return None

    def get_system_messages(self) -> List[SystemMessage]:
        """获取对应数据。"""
        return cast(
            List[SystemMessage],
            list(filter(lambda x: isinstance(x, SystemMessage), self.messages)),
        )

    def _to_dict(self) -> Dict:
        return _conversation_to_dict(self)

    def from_conversation(self, conversation: OnceConversation) -> None:
        """根据输入参数创建对象。"""
        self.chat_mode = conversation.chat_mode
        self.messages = conversation.messages
        self.start_date = conversation.start_date
        self.chat_order = conversation.chat_order
        if not self.model_name and conversation.model_name:
            self.model_name = conversation.model_name
        if not self.app_code and conversation.app_code:
            self.app_code = conversation.app_code
        if not self.param_type and conversation.param_type:
            self.param_type = conversation.param_type
        if not self.param_value and conversation.param_value:
            self.param_value = conversation.param_value
        self.cost = conversation.cost
        self.tokens = conversation.tokens
        self.user_name = conversation.user_name
        self.sys_code = conversation.sys_code
        self._message_index = conversation._message_index

    def get_messages_by_round(self, round_index: int) -> List[BaseMessage]:
        """获取对应数据。"""
        return list(filter(lambda x: x.round_index == round_index, self.messages))

    def get_latest_round(self) -> List[BaseMessage]:
        """获取对应数据。"""
        return self.get_messages_by_round(self.chat_order)

    def get_messages_with_round(self, round_count: int) -> List[BaseMessage]:
        """获取对应数据。"""
        latest_round_index = self.chat_order
        start_round_index = max(1, latest_round_index - round_count + 1)
        messages = []
        for round_index in range(start_round_index, latest_round_index + 1):
            messages.extend(self.get_messages_by_round(round_index))
        return messages

    def get_model_messages(self) -> List[ModelMessage]:
        """获取对应数据。"""
        messages = []
        for message in self.messages:
            if message.pass_to_model:
                messages.append(
                    ModelMessage(
                        role=message.type,
                        content=message.content,
                        round_index=message.round_index,
                    )
                )
        return messages

    def get_history_message(
        self, include_system_message: bool = False
    ) -> List[BaseMessage]:
        """获取对应数据。"""
        messages = []
        for message in self.messages:
            if (
                message.pass_to_model
                and include_system_message
                or message.type != "system"
            ):
                messages.append(message)
        return messages


class ConversationIdentifier(ResourceIdentifier):
    """当前类的职责定义。"""

    def __init__(self, conv_uid: str, identifier_type: str = "conversation"):
        """初始化实例。"""
        self.conv_uid = conv_uid
        self.identifier_type = identifier_type

    @property
    def str_identifier(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return f"{self.identifier_type}:{self.conv_uid}"  # noqa:

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        return {"conv_uid": self.conv_uid, "identifier_type": self.identifier_type}


class MessageIdentifier(ResourceIdentifier):
    """接口数据结构定义。"""

    identifier_split = "___"

    def __init__(self, conv_uid: str, index: int, identifier_type: str = "message"):
        """初始化实例。"""
        self.conv_uid = conv_uid
        self.index = index
        self.identifier_type = identifier_type

    @property
    def str_identifier(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return (
            f"{self.identifier_type}{self.identifier_split}{self.conv_uid}"
            f"{self.identifier_split}{self.index}"
        )

    @staticmethod
    def from_str_identifier(str_identifier: str) -> MessageIdentifier:
        """根据输入参数创建对象。"""
        parts = str_identifier.split(MessageIdentifier.identifier_split)
        if len(parts) != 3:
            raise ValueError(f"Invalid str identifier: {str_identifier}")
        return MessageIdentifier(parts[1], int(parts[2]))

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        return {
            "conv_uid": self.conv_uid,
            "index": self.index,
            "identifier_type": self.identifier_type,
        }


class MessageStorageItem(StorageItem):
    """接口数据结构定义。"""

    @property
    def identifier(self) -> MessageIdentifier:
        """执行当前函数对应的业务逻辑。"""
        return self._id

    def __init__(self, conv_uid: str, index: int, message_detail: Dict):
        """初始化实例。"""
        self.conv_uid = conv_uid
        self.index = index
        self.message_detail = message_detail
        self._id = MessageIdentifier(conv_uid, index)

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        return {
            "conv_uid": self.conv_uid,
            "index": self.index,
            "message_detail": self.message_detail,
        }

    def to_message(self) -> BaseMessage:
        """转换为目标数据结构。"""
        return _message_from_dict(self.message_detail)

    def merge(self, other: "StorageItem") -> None:
        """执行当前函数对应的业务逻辑。"""
        if not isinstance(other, MessageStorageItem):
            raise ValueError(f"Can not merge {other} to {self}")
        self.message_detail = other.message_detail


class StorageConversation(OnceConversation, StorageItem):
    """存储能力实现。"""

    @property
    def identifier(self) -> ConversationIdentifier:
        """执行当前函数对应的业务逻辑。"""
        return self._id

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        dict_data = self._to_dict()
        messages: Dict = dict_data.pop("messages")
        message_ids = []
        index = 0
        for message in messages:
            if "index" in message:
                message_idx = message["index"]
            else:
                message_idx = index
                index += 1
            message_ids.append(
                MessageIdentifier(self.conv_uid, message_idx).str_identifier
            )
        # 代码说明。
        dict_data["conv_uid"] = self.conv_uid
        dict_data["message_ids"] = message_ids
        dict_data["save_message_independent"] = self.save_message_independent
        return dict_data

    def merge(self, other: "StorageItem") -> None:
        """执行当前函数对应的业务逻辑。"""
        if not isinstance(other, StorageConversation):
            raise ValueError(f"Can not merge {other} to {self}")
        self.from_conversation(other)

    def __init__(
        self,
        conv_uid: str,
        chat_mode: str = "chat_normal",
        user_name: Optional[str] = None,
        sys_code: Optional[str] = None,
        message_ids: Optional[List[str]] = None,
        summary: Optional[str] = None,
        app_code: Optional[str] = None,
        save_message_independent: bool = True,
        conv_storage: Optional[StorageInterface] = None,
        message_storage: Optional[StorageInterface] = None,
        load_message: bool = True,
        **kwargs,
    ):
        """初始化实例。"""
        super().__init__(chat_mode, user_name, sys_code, summary, app_code, **kwargs)
        self.conv_uid = conv_uid
        self._message_ids = message_ids
        # 代码说明。
        # 代码说明。
        self._has_stored_message_index = (
            len(kwargs["messages"]) - 1 if "messages" in kwargs else -1
        )
        # 加载对应资源。
        self._load_message = load_message
        self.save_message_independent = save_message_independent
        self._id = ConversationIdentifier(conv_uid)
        if conv_storage is None:
            conv_storage = InMemoryStorage()
        if message_storage is None:
            message_storage = InMemoryStorage()
        self.conv_storage = conv_storage
        self.message_storage = message_storage
        # 加载对应资源。
        self.load_from_storage(self.conv_storage, self.message_storage)

    @property
    def message_ids(self) -> List[str]:
        """执行当前函数对应的业务逻辑。"""
        return self._message_ids if self._message_ids else []

    def end_current_round(self) -> None:
        """执行当前函数对应的业务逻辑。"""
        self.save_to_storage()

    def _get_message_items(self) -> List[MessageStorageItem]:
        return [
            MessageStorageItem(self.conv_uid, message.index, message.to_dict())
            for message in self.messages
        ]

    def save_to_storage(self) -> None:
        """保存数据或资源。"""
        # 代码说明。
        message_list = self._get_message_items()
        self._message_ids = [
            message.identifier.str_identifier for message in message_list
        ]
        messages_to_save = message_list[self._has_stored_message_index + 1 :]
        self._has_stored_message_index = len(message_list) - 1
        if self.save_message_independent:
            # 代码说明。
            self.message_storage.save_list(messages_to_save)
        # 代码说明。
        if self.summary is not None and len(self.summary) > 4000:
            self.summary = self.summary[0:4000]
        self.conv_storage.save_or_update(self)

    def load_from_storage(
        self, conv_storage: StorageInterface, message_storage: StorageInterface
    ) -> None:
        """加载数据或资源。"""
        # 加载对应资源。
        conversation: Optional[StorageConversation] = conv_storage.load(
            self._id, StorageConversation
        )
        if conversation is None:
            return
        message_ids = conversation._message_ids or []

        if self._load_message:
            # 加载对应资源。
            message_list = message_storage.load_list(
                [
                    MessageIdentifier.from_str_identifier(message_id)
                    for message_id in message_ids
                ],
                MessageStorageItem,
            )
            messages = [message.to_message() for message in message_list]
        else:
            messages = []
        real_messages = messages or conversation.messages
        conversation.messages = real_messages
        # 代码说明。
        # 代码说明。
        conversation._message_index = len(real_messages)
        conversation.chat_order = (
            max(m.round_index for m in real_messages) if real_messages else 0
        )
        self._append_additional_kwargs(conversation, real_messages)
        self._message_ids = message_ids
        self._has_stored_message_index = len(real_messages) - 1
        self.save_message_independent = conversation.save_message_independent
        self.from_conversation(conversation)

    def _append_additional_kwargs(
        self, conversation: StorageConversation, messages: List[BaseMessage]
    ) -> None:
        """执行当前函数对应的业务逻辑。"""
        param_type = ""
        param_value = ""
        for message in messages[::-1]:
            if message.additional_kwargs:
                param_type = message.additional_kwargs.get("param_type", "")
                param_value = message.additional_kwargs.get("param_value", "")
                break
        if not conversation.param_type:
            conversation.param_type = param_type
        if not conversation.param_value:
            conversation.param_value = param_value

    def delete(self) -> None:
        """删除对应数据。"""
        # 删除对应数据。
        message_list = self._get_message_items()
        message_ids = [message.identifier for message in message_list]
        self.message_storage.delete_list(message_ids)
        # 删除对应数据。
        self.conv_storage.delete(self.identifier)
        # 代码说明。
        self.from_conversation(
            StorageConversation(
                self.conv_uid,
                save_message_independent=self.save_message_independent,
                conv_storage=self.conv_storage,
                message_storage=self.message_storage,
            )
        )

    def clear(self) -> None:
        """执行当前函数对应的业务逻辑。"""
        from meyo_serve.agent.db import GptsConversationsDao, GptsMessagesDao

        # 代码说明。
        GptsMessagesDao().delete_chat_message(conv_id=self.conv_uid)
        GptsConversationsDao().delete_chat_message(conv_id=self.conv_uid)

        # 代码说明。
        message_list = self._get_message_items()
        message_ids = [message.identifier for message in message_list]
        self.message_storage.delete_list(message_ids)
        # 代码说明。
        self.conv_storage.delete(self.identifier)
        # 代码说明。
        self.from_conversation(
            StorageConversation(
                self.conv_uid,
                save_message_independent=self.save_message_independent,
                conv_storage=self.conv_storage,
                message_storage=self.message_storage,
            )
        )


def _conversation_to_dict(once: OnceConversation) -> Dict:
    start_str: str = ""
    if hasattr(once, "start_date") and once.start_date:
        if isinstance(once.start_date, datetime):
            start_str = once.start_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            start_str = once.start_date

    return {
        "chat_mode": once.chat_mode,
        "model_name": once.model_name,
        "chat_order": once.chat_order,
        "start_date": start_str,
        "cost": once.cost if once.cost else 0,
        "tokens": once.tokens if once.tokens else 0,
        "messages": _messages_to_dict(once.messages),
        "param_type": once.param_type,
        "param_value": once.param_value,
        "user_name": once.user_name,
        "sys_code": once.sys_code,
        "summary": once.summary if once.summary else "",
    }


def _conversations_to_dict(conversations: List[OnceConversation]) -> List[dict]:
    return [_conversation_to_dict(m) for m in conversations]


def _conversation_from_dict(once: dict) -> OnceConversation:
    conversation = OnceConversation(
        once.get("chat_mode", ""), once.get("user_name"), once.get("sys_code")
    )
    conversation.cost = once.get("cost", 0)
    conversation.chat_mode = once.get("chat_mode", "chat_normal")
    conversation.tokens = once.get("tokens", 0)
    conversation.start_date = once.get("start_date", "")
    conversation.chat_order = int(once.get("chat_order", 0))
    conversation.param_type = once.get("param_type", "")
    conversation.param_value = once.get("param_value", "")
    conversation.model_name = once.get("model_name", "proxyllm")
    print(once.get("messages"))
    conversation.messages = _messages_from_dict(once.get("messages", []))
    return conversation


def _split_messages_by_round(messages: List[BaseMessage]) -> List[List[BaseMessage]]:
    """执行当前函数对应的业务逻辑。"""
    messages_by_round: List[List[BaseMessage]] = []
    last_round_index = 0
    for message in messages:
        if not message.round_index:
            # 代码说明。
            raise ValueError("Message round_index is not set")
        if message.round_index > last_round_index:
            last_round_index = message.round_index
            messages_by_round.append([])
        messages_by_round[-1].append(message)
    return messages_by_round


def _append_view_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    """执行当前函数对应的业务逻辑。"""
    messages_by_round = _split_messages_by_round(messages)
    for current_round in messages_by_round:
        ai_message = None
        view_message = None
        for message in current_round:
            if message.type == "ai":
                ai_message = message
            elif message.type == "view":
                view_message = message
        if view_message:
            # 代码说明。
            continue
        if ai_message:
            view_message = ViewMessage(
                content=ai_message.content,
                index=ai_message.index,
                round_index=ai_message.round_index,
                additional_kwargs=(
                    ai_message.additional_kwargs.copy()
                    if ai_message.additional_kwargs
                    else {}
                ),
            )
            current_round.append(view_message)
    return sum(messages_by_round, [])
