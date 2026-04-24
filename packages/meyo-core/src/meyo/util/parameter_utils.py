"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import argparse
import os
from collections import OrderedDict
from dataclasses import MISSING, asdict, dataclass, field, fields, is_dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

from meyo.util.annotations import Deprecated

if TYPE_CHECKING:
    from meyo._private.pydantic import BaseModel

T = TypeVar("T")

MISSING_DEFAULT_VALUE = "__MISSING_DEFAULT_VALUE__"

_DEFAULT_PRIVACY_FIELDS = {
    "password",
    "token",
    "key",
    "secret",
    "credential",
    "api_key",
    "api_secret",
    "db_password",
}


@dataclass
class ParameterDescription:
    """配置参数定义。"""

    required: bool = False
    is_array: bool = False
    param_name: Optional[str] = None
    param_class: Optional[str] = None
    param_type: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    default_value: Optional[Any] = None
    valid_values: Optional[List[Any]] = None
    ext_metadata: Optional[Dict[str, Any]] = None
    nested_fields: Optional[Dict[str, List["ParameterDescription"]]] = None
    param_order: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为目标数据结构。"""
        return asdict(self)


@dataclass
class BaseParameters:
    @classmethod
    def from_dict(cls: Type[T], data: dict, ignore_extra_fields: bool = False) -> T:
        """根据输入参数创建对象。"""
        all_field_names = {f.name for f in fields(cls)}
        if ignore_extra_fields:
            data = {
                key: value
                for key, value in data.items()
                if key in all_field_names and value is not None
            }
        else:
            extra_fields = set(data.keys()) - all_field_names
            if extra_fields:
                raise TypeError(f"Unexpected fields: {', '.join(extra_fields)}")
        return cls(**data)

    def update_from(self, source: Union["BaseParameters", dict]) -> bool:
        """执行当前函数对应的业务逻辑。"""
        updated = False  # 代码说明。
        if isinstance(source, (BaseParameters, dict)):
            for field_info in fields(self):
                # 整理元数据。
                tags = field_info.metadata.get("tags")
                tags = [] if not tags else tags.split(",")
                if tags and "fixed" in tags:
                    continue  # 代码说明。
                # 获取对应数据。
                # 代码说明。
                new_value = (
                    getattr(source, field_info.name)
                    if isinstance(source, BaseParameters)
                    else source.get(field_info.name, None)
                )

                # 代码说明。
                # 设置对应数据。
                if new_value is not None and new_value != getattr(
                    self, field_info.name
                ):
                    setattr(self, field_info.name, new_value)
                    updated = True
        else:
            raise ValueError(
                "Source must be an instance of BaseParameters (or its derived class) "
                "or a dictionary."
            )

        return updated

    def __str__(self) -> str:
        return _get_dataclass_print_str(self)

    def to_command_args(self, args_prefix: str = "--") -> List[str]:
        """转换为目标数据结构。"""
        return _dict_to_command_args(asdict(self), args_prefix=args_prefix)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def get_parameter_descriptions(cls) -> List[ParameterDescription]:
        """获取对应数据。"""
        return _get_parameter_descriptions(cls)

    @classmethod
    def _resolve_root_path(
        cls, path: Optional[str] = None, root_path: Optional[str] = None
    ) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        from meyo.configs.model_config import resolve_root_path

        return resolve_root_path(path, root_path)


def _get_dataclass_print_str(obj):
    class_name = obj.__class__.__name__
    parameters = [
        f"\n\n=========================== {class_name} ===========================\n"
    ]
    for field_info in fields(obj):
        value = _get_simple_privacy_field_value(obj, field_info)
        parameters.append(f"{field_info.name}: {value}")
    parameters.append(
        "\n======================================================================\n\n"
    )
    return "\n".join(parameters)


def _dict_to_command_args(obj: Dict, args_prefix: str = "--") -> List[str]:
    """执行当前函数对应的业务逻辑。"""
    args = []
    for key, value in obj.items():
        if value is None:
            continue
        args.append(f"{args_prefix}{key}")
        args.append(str(value))
    return args


def _get_simple_privacy_field_value(
    obj, field_info, sensitive_fields: Optional[set] = None
):
    """执行当前函数对应的业务逻辑。"""
    if sensitive_fields is None:
        sensitive_fields = _DEFAULT_PRIVACY_FIELDS
    tags = field_info.metadata.get("tags")
    tags = [] if not tags else tags.split(",")
    is_privacy = False
    if tags and "privacy" in tags:
        is_privacy = True
    elif field_info.name in sensitive_fields:
        is_privacy = True
    value = getattr(obj, field_info.name)
    if not is_privacy or not value:
        return value
    field_type = EnvArgumentParser._get_argparse_type(field_info.type)
    if field_type is int:
        return -999
    if field_type is float:
        return -999.0
    if field_type is bool:
        return False
    # 代码说明。
    if len(value) > 5:
        return "".join(value[:2]) + "******" + "".join(value[-2:])
    return "******"


def _genenv_ignoring_key_case(
    env_key: str, env_prefix: Optional[str] = None, default_value: Optional[str] = None
):
    """执行当前函数对应的业务逻辑。"""
    if env_prefix:
        env_key = env_prefix + env_key
    return os.getenv(
        env_key, os.getenv(env_key.upper(), os.getenv(env_key.lower(), default_value))
    )


def _genenv_ignoring_key_case_with_prefixes(
    env_key: str,
    env_prefixes: Optional[List[str]] = None,
    default_value: Optional[str] = None,
) -> str:
    if env_prefixes:
        for env_prefix in env_prefixes:
            env_var_value = _genenv_ignoring_key_case(env_key, env_prefix)
            if env_var_value:
                return env_var_value
    return _genenv_ignoring_key_case(env_key, default_value=default_value)


class EnvArgumentParser:
    @staticmethod
    def get_env_prefix(env_key: str) -> Optional[str]:
        if not env_key:
            return None
        env_key = env_key.replace("-", "_")
        return env_key + "_"

    def parse_args_into_dataclass(
        self,
        dataclass_type: Type,
        env_prefixes: Optional[List[str]] = None,
        command_args: Optional[List[str]] = None,
        **kwargs,
    ) -> Any:
        """解析输入并返回标准结果。"""
        parser = argparse.ArgumentParser(allow_abbrev=False)
        for fd in fields(dataclass_type):
            env_var_value: Any = _genenv_ignoring_key_case_with_prefixes(
                fd.name, env_prefixes
            )
            if env_var_value:
                env_var_value = env_var_value.strip()
                if fd.type is int or fd.type == Optional[int]:
                    env_var_value = int(env_var_value)
                elif fd.type is float or fd.type == Optional[float]:
                    env_var_value = float(env_var_value)
                elif fd.type is bool or fd.type == Optional[bool]:
                    env_var_value = env_var_value.lower() == "true"
                elif fd.type is str or fd.type == Optional[str]:
                    pass
                else:
                    raise ValueError(f"Unsupported parameter type {fd.type}")
            if not env_var_value:
                env_var_value = kwargs.get(fd.name)

            # 代码说明。
            # 添加对应数据。
            EnvArgumentParser._build_single_argparse_option(parser, fd, env_var_value)

        # 代码说明。
        cmd_args, cmd_argv = parser.parse_known_args(args=command_args)
        # 代码说明。
        # 代码说明。
        for fd in fields(dataclass_type):
            # 获取对应数据。
            if fd.name in cmd_args:
                cmd_line_value = getattr(cmd_args, fd.name)
                if cmd_line_value is not None:
                    kwargs[fd.name] = cmd_line_value

        return dataclass_type(**kwargs)

    @staticmethod
    def _create_arg_parser(dataclass_type: Type) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description=dataclass_type.__doc__)
        for fd in fields(dataclass_type):
            help_text = fd.metadata.get("help", "")
            valid_values = fd.metadata.get("valid_values", None)
            argument_kwargs = {
                "type": EnvArgumentParser._get_argparse_type(fd.type),
                "help": help_text,
                "choices": valid_values,
                "required": EnvArgumentParser._is_require_type(fd.type),
            }
            if fd.default != MISSING:
                argument_kwargs["default"] = fd.default
                argument_kwargs["required"] = False
            parser.add_argument(f"--{fd.name}", **argument_kwargs)
        return parser

    @staticmethod
    def _create_click_option_from_field(field_name: str, fd: Type, is_func=True):
        import click

        help_text = fd.metadata.get("help", "")
        valid_values = fd.metadata.get("valid_values", None)
        cli_params = {
            "default": None if fd.default is MISSING else fd.default,
            "help": help_text,
            "show_default": True,
            "required": fd.default is MISSING,
        }
        if valid_values:
            cli_params["type"] = click.Choice(valid_values)
        real_type = EnvArgumentParser._get_argparse_type(fd.type)
        if real_type is int:
            cli_params["type"] = click.INT
        elif real_type is float:
            cli_params["type"] = click.FLOAT
        elif real_type is str:
            cli_params["type"] = click.STRING
        elif real_type is bool:
            cli_params["is_flag"] = True
        name = f"--{field_name}"
        if is_func:
            return click.option(
                name,
                **cli_params,
            )
        else:
            return click.Option([name], **cli_params)

    @staticmethod
    def create_click_option(
        *dataclass_types: Type,
        _dynamic_factory: Optional[Callable[[], List[Type]]] = None,
    ):
        import functools
        from collections import OrderedDict

        combined_fields = OrderedDict()
        if _dynamic_factory:
            _types = _dynamic_factory()
            if _types:
                dataclass_types = list(_types)  # type: ignore
        for dataclass_type in dataclass_types:
            # type: ignore
            for fd in fields(dataclass_type):
                if fd.name not in combined_fields:
                    combined_fields[fd.name] = fd

        def decorator(func):
            for field_name, fd in reversed(combined_fields.items()):
                option_decorator = EnvArgumentParser._create_click_option_from_field(
                    field_name, fd
                )
                func = option_decorator(func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def _create_raw_click_option(
        *dataclass_types: Type,
        _dynamic_factory: Optional[Callable[[], List[Type]]] = None,
    ):
        combined_fields = _merge_dataclass_types(
            *dataclass_types, _dynamic_factory=_dynamic_factory
        )
        options = []

        for field_name, fd in reversed(combined_fields.items()):
            options.append(
                EnvArgumentParser._create_click_option_from_field(
                    field_name, fd, is_func=False
                )
            )
        return options

    @staticmethod
    def create_argparse_option(
        *dataclass_types: Type,
        _dynamic_factory: Optional[Callable[[], List[Type]]] = None,
    ) -> argparse.ArgumentParser:
        combined_fields = _merge_dataclass_types(
            *dataclass_types, _dynamic_factory=_dynamic_factory
        )
        parser = argparse.ArgumentParser()
        for _, fd in reversed(combined_fields.items()):
            EnvArgumentParser._build_single_argparse_option(parser, fd)
        return parser

    @staticmethod
    def _build_single_argparse_option(
        parser: argparse.ArgumentParser, field, default_value=None
    ):
        # 添加对应数据。
        help_text = field.metadata.get("help", "")
        valid_values = field.metadata.get("valid_values", None)
        short_name = field.metadata.get("short", None)
        argument_kwargs = {
            "type": EnvArgumentParser._get_argparse_type(field.type),
            "help": help_text,
            "choices": valid_values,
            "required": EnvArgumentParser._is_require_type(field.type),
        }
        if field.default != MISSING:
            argument_kwargs["default"] = field.default
            argument_kwargs["required"] = False
        if default_value:
            argument_kwargs["default"] = default_value
            argument_kwargs["required"] = False
        if field.type is bool or field.type == Optional[bool]:
            argument_kwargs["action"] = "store_true"
            del argument_kwargs["type"]
            del argument_kwargs["choices"]
        names = []
        if short_name:
            names.append(f"-{short_name}")
        names.append(f"--{field.name}")
        parser.add_argument(*names, **argument_kwargs)

    @staticmethod
    def _get_argparse_type(
        field_type: Type, only_support_base_type: bool = True
    ) -> Type:
        # 返回对应结果。
        if field_type is int or field_type == Optional[int]:
            return int
        elif field_type is float or field_type == Optional[float]:
            return float
        elif field_type is bool or field_type == Optional[bool]:
            return bool
        elif field_type is str or field_type == Optional[str]:
            return str
        elif field_type is dict or field_type == Optional[dict]:
            return dict
        elif only_support_base_type:
            raise ValueError(f"Unsupported parameter type {field_type}")
        else:
            return field_type

    @staticmethod
    def _get_argparse_type_str(field_type: Type, only_support_base_type: bool) -> str:
        from .function_utils import type_to_string

        argparse_type = EnvArgumentParser._get_argparse_type(
            field_type, only_support_base_type
        )
        str_type, sub_types = type_to_string(field_type)

        if argparse_type is int:
            return "int"
        elif argparse_type is float:
            return "float"
        elif argparse_type is bool:
            return "bool"
        elif argparse_type is dict:
            return "dict"
        elif argparse_type is str:
            return "str"
        elif only_support_base_type:
            raise ValueError(f"Unsupported parameter type {field_type}")
        else:
            str_type, sub_types = type_to_string(field_type)
            return field_type.__name__

    @staticmethod
    def _is_require_type(field_type: Type) -> bool:
        return field_type not in [Optional[int], Optional[float], Optional[bool]]

    @staticmethod
    def _kwargs_to_env_key_value(
        kwargs: Dict, prefix: str = "__meyo_gunicorn__env_prefix__"
    ) -> Dict[str, str]:
        return {prefix + k: str(v) for k, v in kwargs.items()}

    @staticmethod
    def _read_env_key_value(
        prefix: str = "__meyo_gunicorn__env_prefix__",
    ) -> List[str]:
        env_args = []
        for key, value in os.environ.items():
            if key.startswith(prefix):
                arg_key = "--" + key.replace(prefix, "")
                if value.lower() in ["true", "1"]:
                    # 代码说明。
                    env_args.append(arg_key)
                elif value.lower() not in ["false", "0"]:
                    env_args.extend([arg_key, value])
        return env_args


def _merge_dataclass_types(
    *dataclass_types: Type, _dynamic_factory: Optional[Callable[[], List[Type]]] = None
) -> OrderedDict:
    combined_fields = OrderedDict()
    if _dynamic_factory:
        _types = _dynamic_factory()
        if _types:
            dataclass_types = list(_types)  # type: ignore
    for dataclass_type in dataclass_types:
        for fd in fields(dataclass_type):
            if fd.name not in combined_fields:
                combined_fields[fd.name] = fd
    return combined_fields


def _type_str_to_python_type(type_str: str) -> Type:
    type_mapping: Dict[str, Type] = {
        "int": int,
        "float": float,
        "bool": bool,
        "str": str,
    }
    return type_mapping.get(type_str, str)


def _get_parameter_descriptions(
    dataclass_type: Type, parent_field: Optional[str] = None, **kwargs
) -> List[ParameterDescription]:
    """执行当前函数对应的业务逻辑。"""

    from meyo.util.configure.manager import ConfigurationManager

    return ConfigurationManager.parse_description(dataclass_type)


def _build_parameter_class(desc: List[ParameterDescription]) -> Type:
    from meyo.util.module_utils import import_from_string

    if not desc:
        raise ValueError("Parameter descriptions cant be empty")
    param_class_str = desc[0].param_class
    class_name = None
    if param_class_str:
        param_class = import_from_string(param_class_str, ignore_import_error=True)
        if param_class:
            return param_class
        module_name, _, class_name = param_class_str.rpartition(".")

    fields_dict = {}  # 默认配置说明。
    annotations = {}  # 代码说明。

    for d in desc:
        metadata = d.ext_metadata if d.ext_metadata else {}
        metadata["help"] = d.description
        metadata["valid_values"] = d.valid_values

        annotations[d.param_name] = _type_str_to_python_type(
            d.param_type  # type: ignore
        )  # 设置对应数据。
        # 整理元数据。
        if d.param_name == "ignore_patterns":
            fields_dict[d.param_name] = field(default=None, metadata=metadata)
        else:
            fields_dict[d.param_name] = field(
                default=d.default_value, metadata=metadata
            )

    # 运行时检查类型标注。
    new_class = type(
        class_name,  # type: ignore
        (object,),
        {**fields_dict, "__annotations__": annotations},  # type: ignore
    )
    # 代码说明。
    result_class = dataclass(new_class)  # type: ignore

    return result_class


@Deprecated(version="0.7.0", remove_version="0.8.0")
def _extract_parameter_details(
    parser: argparse.ArgumentParser,
    param_class: Optional[str] = None,
    skip_names: Optional[List[str]] = None,
    overwrite_default_values: Optional[Dict[str, Any]] = None,
) -> List[ParameterDescription]:
    from .function_utils import format_type_string

    if overwrite_default_values is None:
        overwrite_default_values = {}
    descriptions = []

    for action in parser._actions:
        if (
            action.default == argparse.SUPPRESS
        ):  # 代码说明。
            continue

        # 代码说明。
        # 代码说明。
        # 代码说明。
        # )

        # 代码说明。
        param_name = action.option_strings[0] if action.option_strings else action.dest
        if param_name.startswith("--"):
            param_name = param_name[2:]
        if param_name.startswith("-"):
            param_name = param_name[1:]

        param_name = param_name.replace("-", "_")

        if skip_names and param_name in skip_names:
            continue

        # 代码说明。
        default_value = action.default
        if param_name in overwrite_default_values:
            default_value = overwrite_default_values[param_name]
        arg_type = (
            action.type if not callable(action.type) else str(action.type.__name__)  # type: ignore
        )
        arg_type = format_type_string(arg_type)
        description = action.help

        # 代码说明。
        required = action.required

        # 代码说明。
        valid_values = list(action.choices) if action.choices is not None else None

        # 整理元数据。
        ext_metadata: Dict[str, Any] = {}

        descriptions.append(
            ParameterDescription(
                param_class=param_class,
                param_name=param_name,
                param_type=arg_type,
                default_value=default_value,
                description=description,
                required=required,
                valid_values=valid_values,
                ext_metadata=ext_metadata,
            )
        )

    return descriptions


def _get_dict_from_obj(obj, default_value=None) -> Optional[Dict]:
    if not obj:
        return None
    if is_dataclass(type(obj)):
        params = {}
        for field_info in fields(obj):
            value = _get_simple_privacy_field_value(obj, field_info)
            params[field_info.name] = value
        return params
    if isinstance(obj, dict):
        return obj
    return default_value


@Deprecated(version="0.7.0", remove_version="0.8.0")
def _get_base_model_descriptions(model_cls: "BaseModel") -> List[ParameterDescription]:
    from meyo._private import pydantic

    version = int(pydantic.VERSION.split(".")[0])  # type: ignore
    schema = model_cls.model_json_schema() if version >= 2 else model_cls.schema()
    required_fields = set(schema.get("required", []))
    param_descs = []
    for field_name, field_schema in schema.get("properties", {}).items():
        field = model_cls.model_fields[field_name]
        param_type = field_schema.get("type")
        if not param_type and "anyOf" in field_schema:
            for any_of in field_schema["anyOf"]:
                if any_of["type"] != "null":
                    param_type = any_of["type"]
                    break
        if version >= 2:
            default_value = (
                field.default
                if hasattr(field, "default")
                and str(field.default) != "PydanticUndefined"
                else None
            )
        else:
            default_value = (
                field.default
                if not field.allow_none
                else (
                    field.default_factory() if callable(field.default_factory) else None
                )
            )
        description = field_schema.get("description", "")
        is_required = field_name in required_fields
        valid_values = None
        ext_metadata = None
        if hasattr(field, "field_info"):
            valid_values = (
                list(field.field_info.choices)
                if hasattr(field.field_info, "choices")
                else None
            )
            ext_metadata = (
                field.field_info.extra if hasattr(field.field_info, "extra") else None
            )
        param_class = f"{model_cls.__module__}.{model_cls.__name__}"
        param_desc = ParameterDescription(
            param_class=param_class,
            param_name=field_name,
            param_type=param_type,
            default_value=default_value,
            description=description,
            required=is_required,
            valid_values=valid_values,
            ext_metadata=ext_metadata,
        )
        param_descs.append(param_desc)
    return param_descs


class _SimpleArgParser:
    def __init__(self, *args):
        self.params = {arg.replace("_", "-"): None for arg in args}

    def parse(self, args=None):
        import sys

        if args is None:
            args = sys.argv[1:]
        else:
            args = list(args)
        prev_arg = None
        for arg in args:
            if arg.startswith("--"):
                if prev_arg:
                    self.params[prev_arg] = None
                prev_arg = arg[2:]
            else:
                if prev_arg:
                    self.params[prev_arg] = arg
                    prev_arg = None

        if prev_arg:
            self.params[prev_arg] = None

    def _get_param(self, key):
        return self.params.get(key.replace("_", "-")) or self.params.get(key)

    def __getattr__(self, item):
        return self._get_param(item)

    def __getitem__(self, key):
        return self._get_param(key)

    def get(self, key, default=None):
        return self._get_param(key) or default

    def __str__(self):
        return "\n".join(
            [f"{key.replace('-', '_')}: {value}" for key, value in self.params.items()]
        )


def build_lazy_click_command(*dataclass_types: Type, _dynamic_factory=None):
    import click

    class LazyCommand(click.Command):
        def __init__(self, *args, **kwargs):
            super(LazyCommand, self).__init__(*args, **kwargs)
            self.dynamic_params_added = False

        def get_params(self, ctx):
            if ctx and not self.dynamic_params_added:
                dynamic_params = EnvArgumentParser._create_raw_click_option(
                    *dataclass_types, _dynamic_factory=_dynamic_factory
                )
                for param in reversed(dynamic_params):
                    self.params.append(param)
                self.dynamic_params_added = True
            return super(LazyCommand, self).get_params(ctx)

    return LazyCommand
