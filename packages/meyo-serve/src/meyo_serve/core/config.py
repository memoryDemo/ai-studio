"""服务层通用配置定义，描述服务模块启动所需的基础参数。"""

from dataclasses import dataclass, field
from functools import cache
from typing import List, Optional, Type

from meyo.component import AppConfig, SystemApp
from meyo.util import BaseParameters, RegisterParameters
from meyo.util.i18n_utils import _


@dataclass
class BaseServeConfig(BaseParameters, RegisterParameters):
    """配置参数定义。"""

    __type__ = "___serve_type_placeholder___"
    __cfg_type__ = "serve"

    api_keys: Optional[str] = field(
        default=None,
        metadata={"help": _("API keys for the endpoint, if None, allow all")},
    )

    @classmethod
    def from_app_config(cls, config: AppConfig, config_prefix: str):
        """根据输入参数创建对象。"""
        global_prefix = "meyo.app.global."
        global_dict = config.get_all_by_prefix(global_prefix)
        config_dict = config.get_all_by_prefix(config_prefix)
        if isinstance(config_dict, BaseServeConfig):
            # 创建新的配置对象。
            if not config_dict.api_keys:
                config_dict.api_keys = global_dict.get("api_keys")
            return config_dict

        # 移除配置前缀。
        config_dict = {
            k[len(config_prefix) :]: v
            for k, v in config_dict.items()
            if k.startswith(config_prefix)
        }
        for k, v in global_dict.items():
            if k not in config_dict and k[len(global_prefix) :] in cls().__dict__:
                config_dict[k[len(global_prefix) :]] = v
        return cls(**config_dict)


@dataclass
class BaseGPTsAppMemoryConfig(BaseParameters, RegisterParameters):
    __type__ = "___memory_placeholder___"
    __cfg_type__ = "memory"


@dataclass
class BufferWindowGPTsAppMemoryConfig(BaseGPTsAppMemoryConfig):
    """配置参数定义。"""

    __type__ = "window"
    keep_start_rounds: int = field(
        default=0,
        metadata={"help": _("The number of start rounds to keep in memory")},
    )
    keep_end_rounds: int = field(
        default=0,
        metadata={"help": _("The number of end rounds to keep in memory")},
    )


@dataclass
class TokenBufferGPTsAppMemoryConfig(BaseGPTsAppMemoryConfig):
    """配置参数定义。"""

    __type__ = "token"
    max_token_limit: int = field(
        default=100 * 1024,
        metadata={"help": _("The max token limit. Default is 100k")},
    )


@dataclass
class GPTsAppCommonConfig(BaseParameters, RegisterParameters):
    __type_field__ = "name"
    __cfg_type__ = "app"

    top_k: Optional[int] = field(
        default=None,
        metadata={"help": _("The top k for LLM generation")},
    )
    top_p: Optional[float] = field(
        default=None,
        metadata={"help": _("The top p for LLM generation")},
    )
    temperature: Optional[float] = field(
        default=None,
        metadata={"help": _("The temperature for LLM generation")},
    )
    max_new_tokens: Optional[int] = field(
        default=None,
        metadata={"help": _("The max new tokens for LLM generation")},
    )
    name: Optional[str] = field(
        default=None, metadata={"help": _("The name of your app")}
    )
    memory: Optional[BaseGPTsAppMemoryConfig] = field(
        default=None, metadata={"help": _("The memory configuration")}
    )


@dataclass
class GPTsAppConfig(BaseParameters):
    """配置参数定义。"""

    __cfg_type__ = "app"

    name: str = "app"

    top_k: Optional[int] = field(
        default=None,
        metadata={"help": _("The top k for LLM generation")},
    )
    top_p: Optional[float] = field(
        default=None,
        metadata={"help": _("The top p for LLM generation")},
    )
    temperature: Optional[float] = field(
        default=None,
        metadata={"help": _("The temperature for LLM generation")},
    )
    max_new_tokens: Optional[int] = field(
        default=None,
        metadata={"help": _("The max new tokens for LLM generation")},
    )
    name: Optional[str] = field(
        default=None, metadata={"help": _("The name of your app")}
    )
    memory: Optional[BaseGPTsAppMemoryConfig] = field(
        default=None, metadata={"help": _("The memory configuration")}
    )

    configs: List[GPTsAppCommonConfig] = field(
        default_factory=list,
        metadata={"help": _("The configs for specific app")},
    )


@cache
def parse_config(
    system_app: SystemApp,
    config_name: str,
    type_class: Optional[Type[GPTsAppCommonConfig]],
):
    from meyo_app.config import ApplicationConfig

    app_config = system_app.config.get_typed("app_config", ApplicationConfig)
    # 对话场景的全局配置。
    config = app_config.app

    for custom_config in config.configs:
        if custom_config.name == config_name:
            return custom_config

    if type_class is not None:
        return type_class.from_dict(config.to_dict(), ignore_extra_fields=True)

    return config
