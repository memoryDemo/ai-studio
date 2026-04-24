"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import os
from functools import cache
from typing import Any, Dict, Optional, Type, TypeVar, cast

T = TypeVar("T")


class AppConfig:
    def __init__(self, configs: Optional[Dict[str, Any]] = None) -> None:
        self.configs = configs or {}

    def set(self, key: str, value: Any, overwrite: bool = False) -> None:
        """设置对应数据。"""
        if key in self.configs and not overwrite:
            raise KeyError(f"Config key {key} already exists")
        self.configs[key] = value

    def get(self, key, default: Optional[Any] = None) -> Any:
        """获取对应数据。"""
        return self.configs.get(key, default)

    def get_typed(
        self, key: str, type_class: Type[T], default: Optional[T] = None
    ) -> T:
        """获取对应数据。"""
        value = self.configs.get(key, default)
        if value is None:
            return cast(T, value)

        # 按期望类型处理配置值。
        if isinstance(value, type_class):
            return value

        # 按期望类型处理配置值。
        try:
            if type_class is bool and isinstance(value, str):
                # 处理布尔字符串。
                return cast(T, value.lower() in ("true", "yes", "1", "y"))
            # 按期望类型处理配置值。
            return type_class(value)
        except (ValueError, TypeError):
            raise TypeError(
                f"Cannot convert config value '{value}' to type {type_class.__name__}"
            )

    @cache
    def get_all_by_prefix(self, prefix) -> Dict[str, Any]:
        """获取对应数据。"""
        return {k: v for k, v in self.configs.items() if k.startswith(prefix)}

    def get_current_lang(self, default: Optional[str] = None) -> str:
        """获取对应数据。"""
        env_lang = (
            "zh"
            if os.getenv("LANG") and cast(str, os.getenv("LANG")).startswith("zh")
            else default
        )
        return self.get("meyo.app.global.language", env_lang)
