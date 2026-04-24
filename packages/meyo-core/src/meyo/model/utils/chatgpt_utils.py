"""模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。"""

from __future__ import annotations

import importlib.metadata as metadata
import logging
import os
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Optional,
    Tuple,
    Union,
)

if TYPE_CHECKING:
    from httpx._types import ProxiesTypes, ProxyTypes
    from openai import AsyncAzureOpenAI, AsyncOpenAI

    ClientType = Union[AsyncAzureOpenAI, AsyncOpenAI]

logger = logging.getLogger(__name__)


@dataclass
class OpenAIParameters:
    """配置参数定义。"""

    api_type: str = "open_ai"
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    api_azure_deployment: Optional[str] = None
    full_url: Optional[str] = None
    proxies: Optional["ProxiesTypes"] = None
    proxy: Optional["ProxyTypes"] = None


def _initialize_openai_v1(init_params: OpenAIParameters):
    try:
        from openai import OpenAI  # noqa: F401
    except ImportError as exc:
        raise ValueError(
            "Could not import python package: openai "
            "Please install openai by command `pip install openai"
        ) from exc

    if not metadata.version("openai") >= "1.0.0":
        raise ImportError("Please upgrade openai package to version 1.0.0 or above")

    api_type: Optional[str] = init_params.api_type
    api_base: Optional[str] = init_params.api_base
    api_key: Optional[str] = init_params.api_key
    api_version: Optional[str] = init_params.api_version
    full_url: Optional[str] = init_params.full_url

    api_type = api_type or os.getenv("OPENAI_API_TYPE", "open_ai")

    base_url = api_base or os.getenv(
        "OPENAI_API_BASE",
        os.getenv("AZURE_OPENAI_ENDPOINT") if api_type == "azure" else None,
    )
    api_key = api_key or os.getenv(
        "OPENAI_API_KEY",
        os.getenv("AZURE_OPENAI_KEY") if api_type == "azure" else None,
    )
    api_version = api_version or os.getenv("OPENAI_API_VERSION")

    api_azure_deployment = init_params.api_azure_deployment or os.getenv(
        "API_AZURE_DEPLOYMENT"
    )
    if not base_url and full_url:
        base_url = full_url.split("/chat/completions")[0]

    if api_key is None:
        raise ValueError("api_key is required, please set OPENAI_API_KEY environment")
    if base_url and base_url.endswith("/"):
        base_url = base_url[:-1]

    openai_params = {"api_key": api_key}
    if base_url:
        openai_params["base_url"] = base_url
    return openai_params, api_type, api_version, api_azure_deployment


def _build_openai_client(init_params: OpenAIParameters) -> Tuple[str, ClientType]:
    import httpx

    openai_params, api_type, api_version, api_azure_deployment = _initialize_openai_v1(
        init_params
    )
    if api_type == "azure":
        from openai import AsyncAzureOpenAI

        async_client = AsyncAzureOpenAI(
            api_key=openai_params["api_key"],
            api_version=api_version,
            azure_deployment=api_azure_deployment,
            azure_endpoint=openai_params["base_url"],
        )
    else:
        from openai import AsyncOpenAI

        # 代码说明。
        httpx_version = metadata.version("httpx")
        if httpx_version >= "0.28.0":
            if init_params.proxy:
                http_client = httpx.AsyncClient(proxy=init_params.proxy)
            else:
                http_client = httpx.AsyncClient()
        elif init_params.proxies:
            http_client = httpx.AsyncClient(proxies=init_params.proxies)
        else:
            http_client = httpx.AsyncClient()
        async_client = AsyncOpenAI(**openai_params, http_client=http_client)
    return api_type, async_client
