"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import functools
import logging
import warnings
from typing import Optional

logger = logging.getLogger(__name__)


def PublicAPI(*args, **kwargs):
    """执行当前函数对应的业务逻辑。"""
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        return PublicAPI(stability="stable")(args[0])
    stability = None
    if "stability" in kwargs:
        stability = kwargs["stability"]
    if not stability:
        stability = "stable"
    assert stability in ["alpha", "beta", "stable"]

    def decorator(obj):
        if stability in ["alpha", "beta"]:
            _modify_docstring(
                obj,
                f"**PublicAPI ({stability}):** This API is in {stability} and "
                "may change before becoming stable.",
            )
            _modify_annotation(obj, stability)
        return obj

    return decorator


def DeveloperAPI(*args, **kwargs):
    """执行当前函数对应的业务逻辑。"""
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        return DeveloperAPI()(args[0])

    def decorator(obj):
        _modify_docstring(
            obj,
            "**DeveloperAPI:** This API is for advanced users and may change "
            "cross major versions.",
        )
        return obj

    return decorator


def mutable(func):
    """执行当前函数对应的业务逻辑。"""
    _modify_mutability(func, mutability=True)
    return func


def immutable(func):
    """执行当前函数对应的业务逻辑。"""
    _modify_mutability(func, mutability=False)
    return func


def Deprecated(
    reason: Optional[str] = None,
    version: Optional[str] = None,
    remove_version: Optional[str] = None,
    alternative: Optional[str] = None,
):
    """执行当前函数对应的业务逻辑。"""

    def decorator(obj):
        if isinstance(obj, type):
            categoria = "class"
            # 添加对应数据。
            original_new = obj.__new__

            def deprecated_new(cls, *args, **kwargs):
                msg = _build_message(
                    categoria,
                    obj.__name__,
                    reason,
                    version,
                    remove_version,
                    alternative,
                )
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                logger.warning(msg)  # 代码说明。
                if original_new is not object.__new__:
                    return original_new(cls, *args, **kwargs)
                return super(obj, cls).__new__(cls)

            obj.__new__ = staticmethod(deprecated_new)
        else:
            categoria = "function"

        msg = f"Call to deprecated {categoria} {obj.__name__}."
        if reason:
            msg += f" {reason}"
        if version:
            msg += f" Deprecated since version {version}."
        if remove_version:
            msg += f" Will be removed in version {remove_version}."
        if alternative:
            msg += f" Use {alternative} instead."

        if not isinstance(obj, type):

            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                logger.warning(msg)  # 代码说明。
                return obj(*args, **kwargs)

            return wrapper

        return obj

    def _build_message(categoria, name, reason, version, remove_version, alternative):
        msg = f"Call to deprecated {categoria} {name}."
        if reason:
            msg += f" {reason}"
        if version:
            msg += f" Deprecated since version {version}."
        if remove_version:
            msg += f" Will be removed in version {remove_version}."
        if alternative:
            msg += f" Use {alternative} instead."
        return msg

    # 代码说明。
    if callable(reason):
        # 代码说明。
        fn = reason
        reason = None
        return decorator(fn)

    # 代码说明。
    return decorator


def _modify_docstring(obj, message: Optional[str] = None):
    if not message:
        return
    if not obj.__doc__:
        obj.__doc__ = ""
    original_doc = obj.__doc__

    lines = original_doc.splitlines()

    min_indent = float("inf")
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            min_indent = min(min_indent, len(line) - len(stripped))

    if min_indent == float("inf"):
        min_indent = 0
    min_indent = int(min_indent)
    indented_message = message.rstrip() + "\n" + (" " * min_indent)
    obj.__doc__ = indented_message + original_doc


def _modify_annotation(obj, stability) -> None:
    if stability:
        obj._public_stability = stability
    if hasattr(obj, "__name__"):
        obj._annotated = obj.__name__


def _modify_mutability(obj, mutability) -> None:
    obj._mutability = mutability
