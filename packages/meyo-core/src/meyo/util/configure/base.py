"""配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。"""


import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


class _MISSING_TYPE:
    pass


_MISSING = _MISSING_TYPE()


class ConfigCategory(str, Enum):
    """配置参数定义。"""

    AGENT = "agent"


class ProviderType(str, Enum):
    """枚举类型定义。"""

    ENV = "env"
    PROMPT_MANAGER = "prompt_manager"


class ConfigProvider(ABC):
    """配置参数定义。"""

    name: ProviderType

    @abstractmethod
    def query(self, key: str, **kwargs) -> Any:
        """执行查询并返回结果。"""


class EnvironmentConfigProvider(ConfigProvider):
    """配置参数定义。"""

    name: ProviderType = ProviderType.ENV

    def query(self, key: str, **kwargs) -> Any:
        import os

        return os.environ.get(key, None)


class PromptManagerConfigProvider(ConfigProvider):
    """配置参数定义。"""

    name: ProviderType = ProviderType.PROMPT_MANAGER

    def query(self, key: str, **kwargs) -> Any:
        from meyo._private.config import Config

        try:
            from meyo_serve.prompt.serve import Serve
        except ImportError:
            logger.debug("Prompt manager is not available.")
            return None

        cfg = Config()
        sys_app = cfg.SYSTEM_APP
        if not sys_app:
            return None
        prompt_serve = Serve.get_instance(sys_app)
        if not prompt_serve or not prompt_serve.prompt_manager:
            return None
        prompt_manager = prompt_serve.prompt_manager
        value = prompt_manager.prefer_query(key, **kwargs)
        if not value:
            return None
        # 返回对应结果。
        return value[0].to_prompt_template().template


class ConfigInfo:
    def __init__(
        self,
        default: Any,
        key: Optional[str] = None,
        provider: Optional[Union[str, ConfigProvider]] = None,
        is_list: bool = False,
        separator: str = "[LIST_SEP]",
        description: Optional[str] = None,
    ):
        self.default = default
        self.key = key
        self.provider = provider
        self.is_list = is_list
        self.separator = separator
        self.description = description

    def query(self, **kwargs) -> Any:
        if self.key is None:
            return self.default
        value: Any = None
        if isinstance(self.provider, ConfigProvider):
            value = self.provider.query(self.key, **kwargs)
        elif self.provider == ProviderType.ENV:
            value = EnvironmentConfigProvider().query(self.key, **kwargs)
        elif self.provider == ProviderType.PROMPT_MANAGER:
            value = PromptManagerConfigProvider().query(self.key, **kwargs)
        if value is None:
            value = self.default
        if value and self.is_list and isinstance(value, str):
            value = value.split(self.separator)
        return value


def DynConfig(
    default: Any = _MISSING,
    *,
    category: str | ConfigCategory | None = None,
    key: str | None = None,
    provider: str | ProviderType | ConfigProvider | None = None,
    is_list: bool = False,
    separator: str = "[LIST_SEP]",
    description: str | None = None,
) -> Any:
    """执行当前函数对应的业务逻辑。"""
    if provider is None and category == ConfigCategory.AGENT:
        provider = ProviderType.PROMPT_MANAGER
    if default == _MISSING and key is None:
        raise ValueError("Default value or key is required.")
    if default != _MISSING and isinstance(default, list):
        is_list = True
    return ConfigInfo(
        default=default,
        key=key,
        provider=provider,
        is_list=is_list,
        separator=separator,
        description=description,
    )
