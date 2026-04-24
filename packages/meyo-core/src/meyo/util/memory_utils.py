"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

from typing import Any

from pympler import asizeof


def _get_object_bytes(obj: Any) -> int:
    """执行当前函数对应的业务逻辑。"""
    return asizeof.asizeof(obj)
