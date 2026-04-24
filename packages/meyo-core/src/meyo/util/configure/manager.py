"""配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。
"""

import abc
import logging
import os
import re
from collections.abc import Callable
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from ..i18n_utils import _
from ..parameter_utils import BaseParameters, ParameterDescription

try:
    # 代码说明。
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

T = TypeVar("T")

logger = logging.getLogger(__name__)


_DEFAULT_ENV_VAR_PATTERN = re.compile(r"\${env:([^}]+)}")

CHECK_I18N_PARAMETER_DESC = (
    os.getenv("CHECK_I18N_PARAMETER_DESC", "false").lower() == "true"
)


class PolymorphicMeta(abc.ABCMeta):
    def __new__(mcs, name, bases, namespace, **kwargs):
        """执行当前函数对应的业务逻辑。"""
        cls = super().__new__(mcs, name, bases, namespace)
        # 代码说明。
        if abc.ABC not in bases:
            # 代码说明。
            base_cls = next(
                (base for base in bases if isinstance(base, PolymorphicMeta)),
                None,
            )

            if base_cls is not None:
                # 获取对应数据。
                type_value = getattr(cls, "__type__", None)
                type_field = getattr(base_cls, "__type_field__", "type")

                if type_value is None and type_field and hasattr(cls, type_field):
                    type_value = getattr(cls, type_field)
                if type_value is None:
                    # 转换数据格式。
                    base_suffix = base_cls.__name__.lower()
                    type_value = name.lower()
                    if type_value.endswith(base_suffix):
                        type_value = type_value[: -len(base_suffix)]

                # 创建相关资源。
                # 检查条件是否满足。
                if RegisterParameters in bases:
                    cls._type_registry = {}

                # 获取对应数据。
                registry = getattr(base_cls, "_type_registry", {})

                type_value = _resolve_env_vars(type_value)
                if type_value in registry:
                    raise ValueError(
                        f"Type value '{type_value}' already registered for "
                        f"{registry[type_value].__name__} in {base_cls.__name__}"
                    )
                # 代码说明。
                registry[type_value] = cls

        return cls


@dataclass
class HookConfig:
    """配置参数定义。"""

    path: str = field(
        metadata={
            "help": _(
                "Hook path, it can be a class path or a function path. "
                "eg: 'meyo.config.hooks.env_var_hook'"
            )
        }
    )
    init_params: Dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "help": _(
                "Hook init params to pass to the hook constructor(Just for class "
                "hook), must be key-value pairs"
            )
        },
    )
    params: Dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "help": _("Hook params to pass to the hook, must be key-value pairs")
        },
    )
    enabled: bool = field(
        default=True,
        metadata={"help": _("Whether the hook is enabled, default is True")},
    )


class RegisterParameters(abc.ABC, metaclass=PolymorphicMeta):
    """配置参数定义。"""

    __type_field__: ClassVar[str] = "type"  # 默认配置说明。

    @classmethod
    def get_subclass(cls, type_value: str) -> Optional[Type["RegisterParameters"]]:
        """获取对应数据。"""
        registry = getattr(cls, "_type_registry", {})
        return registry.get(type_value)

    @classmethod
    def get_register_class(cls) -> Optional[Dict[str, Type["RegisterParameters"]]]:
        """获取对应数据。"""
        return getattr(cls, "_type_registry", None)

    @classmethod
    def register_subclass(cls, type_value: str, subclass: Type["RegisterParameters"]):
        """注册对象。"""
        if not hasattr(cls, "_type_registry"):
            cls._type_registry = {}
        cls._type_registry[type_value.lower()] = subclass

    @classmethod
    def get_type_value(cls) -> str:
        """获取对应数据。"""
        # 获取对应数据。
        type_value = getattr(cls, "__type__", None)
        if type_value is not None:
            return type_value

        # 获取对应数据。
        type_field = getattr(cls, "__type_field__", "type")
        if type_field and hasattr(cls, type_field):
            type_value = getattr(cls, type_field)
            if type_value is not None:
                return type_value

        # 获取对应数据。
        base_cls = next(
            (base for base in cls.__bases__ if isinstance(base, PolymorphicMeta)),
            None,
        )

        if base_cls is not None:
            # 转换数据格式。
            base_suffix = base_cls.__name__.lower()
            type_value = cls.__name__.lower()
            if type_value.endswith(base_suffix):
                type_value = type_value[: -len(base_suffix)]
            return type_value

        return cls.__name__.lower()


def _resolve_env_vars(value: str, env_var_patten=None) -> str:
    """执行当前函数对应的业务逻辑。"""

    def replace_env_var(match):
        env_var = match.group(1)
        # 默认配置说明。
        if ":-" in env_var:
            env_name, default = env_var.split(":-", 1)
        else:
            env_name, default = env_var, None

        value = os.environ.get(env_name)
        if value is None:
            if default is not None:
                return default
            raise ValueError(f"Environment variable {env_name} not found")
        return value

    env_var_patten = env_var_patten or _DEFAULT_ENV_VAR_PATTERN
    return env_var_patten.sub(replace_env_var, value)


def _get_concrete_class(base_class: Type[T], data: Dict[str, Any]) -> Type[T]:
    """执行当前函数对应的业务逻辑。"""
    if not isinstance(base_class, PolymorphicMeta):
        return base_class

    type_field = getattr(base_class, "__type_field__", "type")
    type_value = data.get(type_field)
    if not type_value:
        return base_class
    type_value = _resolve_env_vars(type_value)
    real_cls = base_class.get_subclass(type_value.lower())
    if not real_cls:
        raise ValueError(
            f"Unknown type value: {type_value}, known types: "
            f"{list(_get_all_subclasses(base_class).keys())}"
        )
    return real_cls


def _get_all_subclasses(base_class: Type[T]) -> Dict[str, Type[T]]:
    """执行当前函数对应的业务逻辑。"""
    if not isinstance(base_class, PolymorphicMeta):
        # 代码说明。
        return {base_class.__name__.lower(): base_class}
    return base_class.get_register_class() or {}


def _is_base_config(target_cls):
    return (
        hasattr(target_cls, "__config_type__")
        and getattr(target_cls, "__config_type__") == "base"
    )


class ConfigurationManager:
    """配置参数定义。"""

    ENV_VAR_PATTERN = re.compile(r"\${env:([^}]+)}")

    _description_cache: ClassVar[Dict[str, List[ParameterDescription]]] = {}

    def __init__(
        self, config_dict: Optional[Dict] = None, resolve_env_vars: bool = True
    ):
        """初始化实例。"""
        self.config: Dict[str, Any] = config_dict or {}
        self.resolve_env_vars = resolve_env_vars

    @classmethod
    def from_file(cls, file_path: str | Path) -> "ConfigurationManager":
        """根据输入参数创建对象。"""
        with open(file_path, "rb") as f:
            config_dict = tomllib.load(f)
        return cls(config_dict)

    def exists(self, key: str) -> bool:
        """执行当前函数对应的业务逻辑。"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """获取对应数据。"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def _resolve_env_vars(self, value: str) -> str:
        """执行当前函数对应的业务逻辑。"""
        return _resolve_env_vars(value, self.ENV_VAR_PATTERN)

    def _process_dataclass_env_vars(self, obj: Any) -> Any:
        """执行当前函数对应的业务逻辑。"""
        if not is_dataclass(obj):
            return obj

        for fd in fields(obj):
            field_value = getattr(obj, fd.name)
            if isinstance(field_value, str) and self.resolve_env_vars:
                # 代码说明。
                new_value = self._resolve_env_vars(field_value)
                if new_value != field_value:
                    setattr(obj, fd.name, new_value)
            elif is_dataclass(field_value):
                # 代码说明。
                setattr(obj, fd.name, self._process_dataclass_env_vars(field_value))
            elif isinstance(field_value, (list, tuple)):
                # 代码说明。
                new_value = [
                    (
                        self._process_dataclass_env_vars(item)
                        if is_dataclass(item)
                        else item
                    )
                    for item in field_value
                ]
                if any(a is not b for a, b in zip(new_value, field_value)):
                    setattr(obj, fd.name, type(field_value)(new_value))
            elif isinstance(field_value, dict):
                # 代码说明。
                new_value = {
                    k: self._process_dataclass_env_vars(v) if is_dataclass(v) else v
                    for k, v in field_value.items()
                }
                if new_value != field_value:
                    setattr(obj, fd.name, new_value)

        return obj

    def _convert_value(self, value: Any, field_type: Type) -> Any:
        """执行当前函数对应的业务逻辑。"""
        # 代码说明。
        if value is None:
            if get_origin(field_type) is Union and type(None) in get_args(field_type):
                return None
            raise ValueError("Non-optional field received None value")

        # 代码说明。
        if isinstance(value, str) and self.resolve_env_vars:
            value = self._resolve_env_vars(value)

        origin = get_origin(field_type)
        args = get_args(field_type)

        # 代码说明。
        if origin is None and field_type in (str, int, float, bool):
            try:
                return field_type(value)
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert {value} to {field_type}")

        # 代码说明。
        if origin is Union and type(None) in args:
            inner_type = next(arg for arg in args if arg is not type(None))
            return self._convert_value(value, inner_type) if value is not None else None

        # 代码说明。
        if origin is list or origin is List:
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"Expected list but got {type(value)}")
            element_type = args[0] if args else Any
            try:
                return [self._convert_value(item, element_type) for item in value]
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid list element type: {str(e)}")

        # 代码说明。
        if origin is dict or origin is Dict:
            if not isinstance(value, dict):
                raise ValueError(f"Expected dict but got {type(value)}")
            key_type, value_type = args if args else (Any, Any)
            try:
                return {
                    self._convert_value(k, key_type): self._convert_value(v, value_type)
                    for k, v in value.items()
                }
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid dictionary entry: {str(e)}")

        # 代码说明。
        if is_dataclass(field_type):
            if not isinstance(value, dict):
                raise ValueError(
                    f"Expected dict for {field_type.__name__} but got {type(value)}"
                )
            try:
                return self._convert_to_dataclass(field_type, value)
            except ValueError as e:
                raise ValueError(f"Invalid data for {field_type.__name__}: {str(e)}")

        return value

    def _convert_to_dataclass(self, cls: Type[T], data: Dict) -> T:
        """执行当前函数对应的业务逻辑。"""
        if not is_dataclass(cls):
            raise ValueError(f"{cls.__name__} is not a dataclass")

        if hasattr(cls, "_parse_class_") and callable(getattr(cls, "_parse_class_")):
            new_cls = cls._parse_class_(data)
            if new_cls is not None:
                cls = new_cls

        concrete_cls = _get_concrete_class(cls, data)

        def prepare_data_func(real_cls, dict_data: Dict[str, Any]):
            field_values = {}
            real_cls = _get_concrete_class(real_cls, dict_data)
            type_hints = get_type_hints(real_cls)

            for fd in fields(real_cls):
                field_type = type_hints[fd.name]
                field_value = dict_data.get(fd.name, MISSING)

                if field_value is MISSING and fd.default is not MISSING:
                    field_values[fd.name] = self._convert_value(fd.default, field_type)
                elif field_value is MISSING and fd.default_factory is not MISSING:
                    default_value = fd.default_factory()
                    if is_dataclass(default_value):
                        default_value = self._process_dataclass_env_vars(default_value)
                    field_values[fd.name] = default_value
                elif field_value is MISSING:
                    raise ValueError(f"Missing required field: {fd.name}")
                else:
                    field_values[fd.name] = self._convert_value(field_value, field_type)
            return field_values

        # 检查条件是否满足。
        if hasattr(concrete_cls, "_from_dict_") and callable(
            getattr(concrete_cls, "_from_dict_")
        ):
            # 转换数据格式。
            return concrete_cls._from_dict_(
                data, prepare_data_func, self._convert_value
            )
        prepared_field_values = prepare_data_func(concrete_cls, data)
        return concrete_cls(**prepared_field_values)

    def parse_config(
        self,
        cls: Type[T],
        prefix: str = "",
        config_handler: Optional[
            Callable[[Union[Dict[str, Any], List[Dict[str, Any]]]], Dict[str, Any]]
        ] = None,
        hook_section: Optional[str] = None,
    ) -> T:
        """解析输入并返回标准结果。"""
        config_section = self.config
        if prefix:
            for key in prefix.split("."):
                config_section = config_section.get(key, {})
        if hook_section:
            hook_configs = config_section.get(hook_section, [])
            if not isinstance(hook_configs, list):
                raise ValueError(f"Invalid hook section: {hook_section}")
            if hook_configs:
                # 代码说明。
                config_section = _load_hook(hook_configs, config_section)
        if config_section is None:
            raise ValueError(f"Configuration section not found: {prefix}")
        if config_handler:
            config_section = config_handler(config_section)
        return self._convert_to_dataclass(cls, config_section)

    @classmethod
    def parse_description(
        cls,
        target_cls: Type[T],
        cache_enable: bool = False,
        skip_base: bool = False,
        _visited: Optional[Set[str]] = None,
        _call_path: Optional[List[str]] = None,
        verbose: bool = False,
    ) -> List[ParameterDescription]:
        """解析输入并返回标准结果。"""
        from ..function_utils import type_to_string

        if target_cls is BaseParameters:
            return []

        # 代码说明。
        if _visited is None:
            _visited = set()
        if _call_path is None:
            _call_path = []

        class_key = f"{target_cls.__module__}.{target_cls.__name__}"
        logger.debug(f"Begin parse: {class_key}")
        logger.debug(f"Call Path: {_call_path}")
        # 检查条件是否满足。
        if class_key in _call_path:
            cycle_start = _call_path.index(class_key)
            cycle_path = _call_path[cycle_start:] + [class_key]
            raise ValueError(
                f"Circular dependency detected: {' -> '.join(cycle_path)}\n"
                f"Current call path: {' -> '.join(_call_path)}"
            )

        logger.debug(
            f"Parsing description for {target_cls.__module__}.{target_cls.__name__}"
        )

        # 添加对应数据。
        _call_path.append(class_key)

        if (
            skip_base
            and hasattr(target_cls, "__config_type__")
            and getattr(target_cls, "__config_type__") == "base"
        ):
            return []

        if not is_dataclass(target_cls):
            raise ValueError(f"{target_cls.__name__} is not a dataclass")
        cache_key = f"{target_cls.__module__}.{target_cls.__name__}"
        if cache_key in cls._description_cache and cache_enable:
            _call_path.pop()
            return cls._description_cache[cache_key]

        descriptions = []
        type_hints = get_type_hints(target_cls)

        parent_descriptions = {}
        for parent in target_cls.__mro__[1:]:
            if parent is object or not is_dataclass(parent) or parent is target_cls:
                continue
            for parent_param in cls.parse_description(
                parent, _visited=_visited, _call_path=_call_path, verbose=verbose
            ):
                if parent_param.description:
                    parent_descriptions[parent_param.param_name] = parent_param

        for raw_order, fd in enumerate(fields(target_cls)):
            field_type = type_hints[fd.name]
            origin = get_origin(field_type)
            args = get_args(field_type)

            # 代码说明。
            if origin is Union and type(None) in args:
                field_type = next(arg for arg in args if arg is not type(None))
                origin = get_origin(field_type)
                args = get_args(field_type)

            # 检查条件是否满足。
            is_array = origin is list or origin is List

            # 获取对应数据。
            if is_array:
                element_type = args[0] if args else Any
                str_type, _ = type_to_string(element_type)
            else:
                str_type, _ = type_to_string(field_type)

            description = fd.metadata.get("help") if fd.metadata else None
            param_order = fd.metadata.get("order") if fd.metadata else None
            parent_tags = {}
            if param_order is None:
                param_order = raw_order
            if not description and fd.name in parent_descriptions:
                description = parent_descriptions[fd.name].description
            if fd.name in parent_descriptions:
                parent_tags = parent_descriptions[fd.name].ext_metadata
            if description and CHECK_I18N_PARAMETER_DESC:
                from ..i18n_utils import is_i18n_string

                if not is_i18n_string(description):
                    raise ValueError(
                        f"Parameter description for {fd.name} in {target_cls.__name__} "
                        "is not i18n compliant"
                    )

            desc = ParameterDescription(
                param_name=fd.name,
                param_class=f"{target_cls.__module__}.{target_cls.__name__}",
                param_type=str_type,
                required=fd.default is MISSING and fd.default_factory is MISSING,
                is_array=is_array,
                description=description,
                param_order=param_order,
            )

            # 整理元数据。
            if fd.metadata:
                desc.label = fd.metadata.get("label")
                desc.valid_values = fd.metadata.get("valid_values")
                desc.ext_metadata = {
                    k: v
                    for k, v in fd.metadata.items()
                    if k not in ("help", "label", "valid_values")
                }
            elif parent_tags:
                desc.label = parent_tags.get("label")
                desc.ext_metadata = {
                    k: v
                    for k, v in parent_tags.items()
                    if k not in ("help", "label", "valid_values")
                }
            if not desc.label:
                desc.label = fd.name

            # 默认配置说明。
            if fd.default is not MISSING:
                desc.default_value = fd.default
            elif fd.default_factory is not MISSING:
                try:
                    desc.default_value = fd.default_factory()
                except Exception:
                    desc.default_value = f"<factory: {fd.default_factory.__name__}>"

            # 代码说明。
            if is_array and is_dataclass(element_type):
                if isinstance(element_type, PolymorphicMeta):
                    implementations = _get_all_subclasses(element_type)
                    desc.nested_fields = {
                        type_value: cls.parse_description(
                            impl_cls,
                            cache_enable=cache_enable,
                            skip_base=skip_base,
                            _visited=_visited,
                            _call_path=_call_path,
                            verbose=verbose,
                        )
                        for type_value, impl_cls in implementations.items()
                    }
                else:
                    desc.nested_fields = {
                        element_type.__name__.lower(): cls.parse_description(
                            element_type,
                            cache_enable=cache_enable,
                            skip_base=skip_base,
                            _visited=_visited,
                            _call_path=_call_path,
                            verbose=verbose,
                        )
                    }

            # 代码说明。
            elif origin is dict or origin is Dict:
                value_type = args[1] if args else Any
                if is_dataclass(value_type):
                    if isinstance(value_type, PolymorphicMeta):
                        implementations = _get_all_subclasses(value_type)
                        desc.nested_fields = {
                            type_value: cls.parse_description(
                                impl_cls,
                                cache_enable=cache_enable,
                                skip_base=skip_base,
                                _visited=_visited,
                                _call_path=_call_path,
                                verbose=verbose,
                            )
                            for type_value, impl_cls in implementations.items()
                        }
                    else:
                        desc.nested_fields = {
                            value_type.__name__.lower(): cls.parse_description(
                                value_type,
                                cache_enable=cache_enable,
                                skip_base=skip_base,
                                _visited=_visited,
                                _call_path=_call_path,
                                verbose=verbose,
                            )
                        }

            # 代码说明。
            elif is_dataclass(field_type):
                if isinstance(field_type, PolymorphicMeta):
                    implementations = _get_all_subclasses(field_type)
                    desc.nested_fields = {
                        type_value: cls.parse_description(
                            impl_cls,
                            cache_enable=cache_enable,
                            skip_base=skip_base,
                            _visited=_visited,
                            _call_path=_call_path,
                            verbose=verbose,
                        )
                        for type_value, impl_cls in implementations.items()
                    }
                else:
                    desc.nested_fields = {
                        field_type.__name__.lower(): cls.parse_description(
                            field_type,
                            cache_enable=cache_enable,
                            skip_base=skip_base,
                            _visited=_visited,
                            _call_path=_call_path,
                            verbose=verbose,
                        )
                    }

            descriptions.append(desc)

        # 代码说明。
        descriptions.sort(key=lambda d: d.param_order)
        cls._description_cache[cache_key] = descriptions
        _call_path.pop()
        return descriptions


def _load_hook(
    hook_config: List[Dict[str, Any]], config_section: Dict[str, Any]
) -> Dict[str, Any]:
    """执行当前函数对应的业务逻辑。"""
    import inspect

    from ..module_utils import import_from_string

    hooks = []
    for hook in hook_config:
        hook_cfg = HookConfig(**hook)
        if hook_cfg.enabled:
            hook_path = hook_cfg.path
            hook_cls = import_from_string(hook_path)
            if inspect.isclass(hook_cls):
                hook = hook_cls(**hook_cfg.init_params)
                hooks.append((hook, hook_cfg))
            elif callable(hook_cls):
                # 代码说明。
                hooks.append((hook_cls, hook_cfg))
            else:
                raise ValueError(f"Invalid hook: {hook_path}")
    logger.debug(f"Loaded hooks: {hooks}")
    for hook, hook_cfg in hooks:
        params = hook_cfg.params or {}
        config_section = hook(config_section, **params)
    return config_section
