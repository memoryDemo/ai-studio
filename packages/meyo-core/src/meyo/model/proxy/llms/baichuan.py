import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional, Type, Union, cast

from meyo.core import ModelMetadata
from meyo.model.proxy.llms.proxy_model import ProxyModel, parse_model_request
from meyo.model.resource import (
    TAGS_ORDER_HIGH,
    ResourceCategory,
    auto_register_resource,
)
from meyo.util.i18n_utils import _

from ..base import (
    AsyncGenerateStreamFunction,
    GenerateStreamFunction,
    register_proxy_model_adapter,
)
from .chatgpt import OpenAICompatibleDeployModelParameters, OpenAILLMClient

if TYPE_CHECKING:
    from httpx._types import ProxiesTypes
    from openai import AsyncAzureOpenAI, AsyncOpenAI

    ClientType = Union[AsyncAzureOpenAI, AsyncOpenAI]

_DEFAULT_MODEL = "Baichuan4-Turbo"


@auto_register_resource(
    label=_("Baichuan Proxy LLM"),
    category=ResourceCategory.LLM_CLIENT,
    tags={"order": TAGS_ORDER_HIGH},
    description=_("Baichuan Proxy LLM"),
    documentation_url="https://platform.baichuan-ai.com/docs/api",
    show_in_ui=False,
)
@dataclass
class BaichuanDeployModelParameters(OpenAICompatibleDeployModelParameters):
    """百川模型部署参数。"""

    provider: str = "proxy/baichuan"

    api_base: Optional[str] = field(
        default="${env:BAICHUAN_API_BASE:-https://api.baichuan-ai.com/v1}",
        metadata={
            "help": _("The base url of the Baichuan API."),
        },
    )

    api_key: Optional[str] = field(
        default="${env:BAICHUAN_API_KEY}",
        metadata={
            "help": _("The API key of the Baichuan API."),
            "tags": "privacy",
        },
    )


async def baichuan_generate_stream(
    model: ProxyModel, tokenizer, params, device, context_len=2048
):
    client: BaichuanLLMClient = cast(BaichuanLLMClient, model.proxy_llm_client)
    request = parse_model_request(params, client.default_model, stream=True)
    async for r in client.generate_stream(request):
        yield r


class BaichuanLLMClient(OpenAILLMClient):
    """百川大模型客户端。

    百川 API 兼容 OpenAI API，因此直接继承 OpenAILLMClient。

    API 参考：https://platform.baichuan-ai.com/docs/api
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_type: Optional[str] = None,
        api_version: Optional[str] = None,
        model: Optional[str] = _DEFAULT_MODEL,
        proxies: Optional["ProxiesTypes"] = None,
        timeout: Optional[int] = 240,
        model_alias: Optional[str] = _DEFAULT_MODEL,
        context_length: Optional[int] = None,
        openai_client: Optional["ClientType"] = None,
        openai_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        api_base = (
            api_base
            or os.getenv("BAICHUAN_API_BASE")
            or "https://api.baichuan-ai.com/v1"
        )
        api_key = api_key or os.getenv("BAICHUAN_API_KEY")
        model = model or _DEFAULT_MODEL

        if not api_key:
            raise ValueError(
                "Baichuan API key is required, please set 'BAICHUAN_API_KEY' in "
                "environment variable or pass it to the client."
            )
        super().__init__(
            api_key=api_key,
            api_base=api_base,
            api_type=api_type,
            api_version=api_version,
            model=model,
            proxies=proxies,
            timeout=timeout,
            model_alias=model_alias,
            context_length=context_length,
            openai_client=openai_client,
            openai_kwargs=openai_kwargs,
            **kwargs,
        )

    def check_sdk_version(self, version: str) -> None:
        if not version >= "1.0":
            raise ValueError(
                "Baichuan API requires openai>=1.0, please upgrade it by "
                "`pip install --upgrade 'openai>=1.0'`"
            )

    @property
    def default_model(self) -> str:
        model = self._model
        if not model:
            model = _DEFAULT_MODEL
        return model

    @classmethod
    def param_class(cls) -> Type[BaichuanDeployModelParameters]:
        """获取模型部署参数类。"""
        return BaichuanDeployModelParameters

    @classmethod
    def generate_stream_function(
        cls,
    ) -> Optional[Union[GenerateStreamFunction, AsyncGenerateStreamFunction]]:
        """获取流式生成函数。"""
        return baichuan_generate_stream


register_proxy_model_adapter(
    BaichuanLLMClient,
    supported_models=[
        ModelMetadata(
            model=["Baichuan4-Turbo", "Baichuan4-Air", "Baichuan4"],
            context_length=32 * 1024,
            description="Baichuan4 by Baichuan",
            link="https://platform.baichuan-ai.com/docs/api",
            function_calling=True,
        ),
        ModelMetadata(
            model=["Baichuan3-Turbo"],
            context_length=32 * 1024,
            description="Baichuan3 by Baichuan",
            link="https://platform.baichuan-ai.com/docs/api",
            function_calling=True,
        ),
        ModelMetadata(
            model=["Baichuan3-Turbo-128k"],
            context_length=128 * 1024,
            description="Baichuan3 128k by Baichuan",
            link="https://platform.baichuan-ai.com/docs/api",
            function_calling=True,
        ),
    ],
)
