#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""


import abc
from typing import Any


class Singleton(abc.ABCMeta, type):
    """当前类的职责定义。"""

    _instances = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """执行调用逻辑。"""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractSingleton(abc.ABC, metaclass=Singleton):
    """当前类的职责定义。"""

    pass
