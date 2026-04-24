"""模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。"""

from pathlib import Path
from typing import Any, Dict, List

import cachetools

from meyo.core import ModelRequest, ModelRequestContext
from meyo.model.base import SupportedModel
from meyo.util.annotations import Deprecated
from meyo.util.parameter_utils import _get_parameter_descriptions


def is_sentence_complete(output: str):
    """校验条件并返回判断结果。"""
    end_symbols = (".", "?", "!", "...", "。", "？", "！", "…", '"', "'", "”")
    return output.endswith(end_symbols)


def is_partial_stop(output: str, stop_str: str):
    """校验条件并返回判断结果。"""
    for i in range(0, min(len(output), len(stop_str))):
        if stop_str.startswith(output[-i:]):
            return True
    return False


@cachetools.cached(cachetools.TTLCache(maxsize=100, ttl=10))
def list_supported_models():
    from meyo.model.adapter.base import get_supported_models
    from meyo.model.parameter import WorkerType

    models = get_supported_models(WorkerType.LLM.value)
    models += get_supported_models(WorkerType.TEXT2VEC.value)
    models += get_supported_models(WorkerType.RERANKER.value)
    return models


def _list_supported_models_from_adapter(worker_type: str) -> List[SupportedModel]:
    pass


@Deprecated(version="0.7.0", remove_version="0.8.8")
def _list_supported_models(
    worker_type: str, model_config: Dict[str, str]
) -> List[SupportedModel]:
    from meyo.model.adapter.loader import _get_model_real_path
    from meyo.model.adapter.model_adapter import get_llm_model_adapter

    ret = []
    for model_name, model_path in model_config.items():
        model_path = _get_model_real_path(model_name, model_path)
        model = SupportedModel(
            model=model_name,
            path=model_path,
            worker_type=worker_type,
            path_exist=False,
            proxy=False,
            enabled=False,
            params=None,
        )
        if "proxyllm" in model_name:
            model.proxy = True
        else:
            path = Path(model_path)
            model.path_exist = path.exists()
        param_cls = None
        try:
            llm_adapter = get_llm_model_adapter(model_name, model_path)
            param_cls = llm_adapter.model_param_class()
            model.enabled = True
            params = _get_parameter_descriptions(
                param_cls, model_name=model_name, model_path=model_path
            )
            model.params = params
        except Exception:
            pass
        ret.append(model)
    return ret


def parse_model_request(
    params: Dict[str, Any], default_model: str, stream: bool = True
) -> ModelRequest:
    """解析输入并返回标准结果。"""
    context = ModelRequestContext(
        stream=stream,
        user_name=params.get("user_name"),
        request_id=params.get("request_id"),
        is_reasoning_model=params.get("is_reasoning_model", False),
    )
    request = ModelRequest.build_request(
        default_model,
        messages=params["messages"],
        temperature=params.get("temperature"),
        context=context,
        max_new_tokens=params.get("max_new_tokens"),
        stop=params.get("stop"),
        top_p=params.get("top_p"),
    )
    return request
