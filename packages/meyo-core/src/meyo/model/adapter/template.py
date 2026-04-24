"""模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

if TYPE_CHECKING:
    pass


class PromptType(str, Enum):
    """枚举类型定义。"""

    FSCHAT: str = "fschat"
    MEYO: str = "meyo"


class ConversationAdapter(ABC):
    """当前类的职责定义。"""

    @property
    def prompt_type(self) -> PromptType:
        return PromptType.FSCHAT

    @property
    @abstractmethod
    def roles(self) -> Tuple[str]:
        """执行当前函数对应的业务逻辑。"""

    @property
    def sep(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        return "\n"

    @property
    def stop_str(self) -> Optional[Union[str, List[str]]]:
        """关闭或停止资源。"""
        return None

    @property
    def stop_token_ids(self) -> Optional[List[int]]:
        """关闭或停止资源。"""
        return None

    @abstractmethod
    def get_prompt(self) -> str:
        """获取对应数据。"""

    @abstractmethod
    def set_system_message(self, system_message: str) -> None:
        """设置对应数据。"""

    @abstractmethod
    def append_message(self, role: str, message: str) -> None:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def update_last_message(self, message: str) -> None:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def copy(self) -> "ConversationAdapter":
        """执行当前函数对应的业务逻辑。"""


class ConversationAdapterFactory(ABC):
    """当前类的职责定义。"""

    def get_by_name(
        self,
        template_name: str,
        prompt_template_type: Optional[PromptType] = PromptType.FSCHAT,
    ) -> ConversationAdapter:
        """获取对应数据。"""
        raise NotImplementedError()

    def get_by_model(self, model_name: str, model_path: str) -> ConversationAdapter:
        """获取对应数据。"""
        raise NotImplementedError()


def get_conv_template(name: str) -> ConversationAdapter:
    """获取对应数据。"""
    from fastchat.conversation import get_conv_template

    from meyo.model.adapter.fschat_adapter import FschatConversationAdapter

    conv_template = get_conv_template(name)
    return FschatConversationAdapter(conv_template)
