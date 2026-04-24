"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import asyncio
import inspect
from functools import wraps
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Union,
    _UnionGenericAlias,
    get_args,
    get_origin,
    get_type_hints,
)

from typeguard import check_type
from typing_extensions import Annotated, Doc, _AnnotatedAlias

TYPE_TO_STRING = {
    int: "integer",
    str: "string",
    float: "number",
    bool: "boolean",
    Any: "any",
    List: "array",
    list: "array",
    dict: "object",
    Dict: "object",
}
FORMAT_TYPE_STRING = {
    "int": "integer",
    "str": "string",
    "float": "number",
    "bool": "boolean",
    "list": "array",
    "dict": "object",
}

TYPE_STRING_TO_TYPE = {
    "integer": int,
    "int": int,
    "string": str,
    "str": str,
    "float": float,
    "boolean": bool,
    "bool": bool,
    "any": Any,
    "array": list,
    "list": list,
    "object": dict,
}


def format_type_string(type_str: str) -> str:
    """执行当前函数对应的业务逻辑。"""
    return FORMAT_TYPE_STRING.get(type_str, type_str)


def _is_typing(obj):
    from typing import _Final  # type: ignore

    return isinstance(obj, _Final)


def _is_instance_of_generic_type(obj, generic_type):
    """执行当前函数对应的业务逻辑。"""
    if generic_type is Any:
        return True  # 用于兼容新旧模型参数设计。

    origin = get_origin(generic_type)
    if origin is None:
        return isinstance(obj, generic_type)  # 代码说明。

    args = get_args(generic_type)
    if not args:
        return isinstance(obj, origin)

    # 检查条件是否满足。
    if not _is_typing(origin):
        return isinstance(obj, origin)

    objs = [obj for _ in range(len(args))]

    # 检查条件是否满足。
    for sub_obj, arg in zip(objs, args):
        # 检查条件是否满足。
        if arg is not Any:
            if _is_typing(arg):
                sub_args = get_args(arg)
                if (
                    sub_args
                    and not _is_typing(sub_args[0])
                    and not isinstance(sub_obj, sub_args[0])
                ):
                    return False
            elif not isinstance(sub_obj, arg):
                return False
    return True


def _check_type(obj, t) -> bool:
    try:
        check_type(obj, t)
        return True
    except Exception:
        return False


def _get_orders(obj, arg_types):
    try:
        orders = [i for i, t in enumerate(arg_types) if _check_type(obj, t)]
        return orders[0] if orders else int(1e8)
    except Exception:
        return int(1e8)


def _sort_args(func, args, kwargs):
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    arg_types = [
        type_hints[param_name]
        for param_name in sig.parameters
        if param_name != "return" and param_name != "self"
    ]

    if "self" in sig.parameters:
        self_arg = [args[0]]
        other_args = args[1:]
    else:
        self_arg = []
        other_args = args

    sorted_args = sorted(
        other_args,
        key=lambda x: _get_orders(x, arg_types),
    )
    return (*self_arg, *sorted_args), kwargs


def rearrange_args_by_type(func):
    """执行当前函数对应的业务逻辑。"""

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        sorted_args, sorted_kwargs = _sort_args(func, args, kwargs)
        return func(*sorted_args, **sorted_kwargs)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        sorted_args, sorted_kwargs = _sort_args(func, args, kwargs)
        return await func(*sorted_args, **sorted_kwargs)

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def type_to_string(obj: Any, default_type: str = "unknown") -> Tuple[str, List[str]]:
    """执行当前函数对应的业务逻辑。"""
    # 检查条件是否满足。
    if obj is type(None) or obj is None:
        return "null", []

    # 获取对应数据。
    origin = getattr(obj, "__origin__", None)
    if origin:
        if _is_typing(origin) and not isinstance(obj, _UnionGenericAlias):
            obj = origin
            origin = origin.__origin__
        elif _is_typing(origin) and isinstance(obj, _UnionGenericAlias):
            # 代码说明。
            return type_to_string(obj.__args__[0], default_type)
        # 代码说明。
        if origin is Union and hasattr(obj, "__args__"):
            subtypes = ", ".join(
                type_to_string(t, default_type)[0]
                for t in obj.__args__
                if t is not type(None)
            )
            # 历史调试代码，当前不启用。
            return subtypes, []
        elif origin is list or origin is List:
            subtypes = list(type_to_string(t, default_type)[0] for t in obj.__args__)
            # 历史调试代码，当前不启用。
            return "array", subtypes
        elif origin in [dict, Dict]:
            # 代码说明。
            # 代码说明。
            # 历史调试代码，当前不启用。
            return "object", []
        # 代码说明。
        elif origin is tuple:
            subtypes = list(type_to_string(t, default_type)[0] for t in obj.__args__)
            return "array", subtypes
        elif origin is Annotated:
            subtypes = list(type_to_string(t, default_type)[0] for t in obj.__args__)
            return subtypes[0], []
        elif origin is _UnionGenericAlias:
            subtypes = list(type_to_string(t, default_type)[0] for t in obj.__args__)
            return subtypes, []
    elif obj is list:
        return "array", []
    elif obj is dict:
        return "object", []
    elif obj is tuple:
        return "array", []
    elif hasattr(obj, "__args__"):
        subtypes = ", ".join(
            type_to_string(t, default_type)[0]
            for t in obj.__args__
            if t is not type(None)
        )
        return subtypes, []

    if obj in TYPE_TO_STRING:
        return TYPE_TO_STRING[obj], []

    if default_type == "unknown" and hasattr(obj, "__name__"):
        return obj.__name__, []
    return default_type, []


def parse_param_description(name: str, obj: Any) -> str:
    default_type_title = name.replace("_", " ").title()
    if isinstance(obj, _AnnotatedAlias):
        metadata = obj.__metadata__
        docs = [arg for arg in metadata if isinstance(arg, Doc)]
        doc_str = docs[0].documentation if docs else default_type_title
    else:
        doc_str = default_type_title
    return doc_str
