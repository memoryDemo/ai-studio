import os
from concurrent.futures import Executor
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

_DEFAULT_MODEL = "claude-sonnet-4-20250514"


@auto_register_resource(
    label=_("BurnCloud Proxy LLM"),
    category=ResourceCategory.LLM_CLIENT,
    tags={"order": TAGS_ORDER_HIGH},
    description=_("BurnCloud proxy LLM configuration."),
    documentation_url="https://ai.burncloud.com/",
    show_in_ui=False,
)
@dataclass
class BurnCloudDeployModelParameters(OpenAICompatibleDeployModelParameters):
    """BurnCloud 模型部署参数。"""

    provider: str = "proxy/burncloud"

    api_base: Optional[str] = field(
        default="${env:BURNCLOUD_API_BASE:-https://ai.burncloud.com/v1}",
        metadata={
            "help": _("The base url of the BurnCloud API."),
        },
    )

    api_key: Optional[str] = field(
        default="${env:BURNCLOUD_API_KEY}",
        metadata={
            "help": _("The API key of the BurnCloud API."),
            "tags": "privacy",
        },
    )


async def burncloud_generate_stream(
    model: ProxyModel, tokenizer, params, device, context_len=2048
):
    client: BurnCloudLLMClient = cast(BurnCloudLLMClient, model.proxy_llm_client)
    request = parse_model_request(params, client.default_model, stream=True)
    async for r in client.generate_stream(request):
        yield r


class BurnCloudLLMClient(OpenAILLMClient):
    """BurnCloud 大模型客户端。

    BurnCloud API 兼容 OpenAI API，因此直接继承 OpenAILLMClient。

    API 参考：https://ai.burncloud.com/v1/chat/completions
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
            api_base or os.getenv("BURNCLOUD_API_BASE") or "https://ai.burncloud.com/v1"
        )
        api_key = api_key or os.getenv("BURNCLOUD_API_KEY")
        model = model or _DEFAULT_MODEL

        # 根据模型名称设置上下文长度。
        if not context_length:
            if any(
                x in model for x in ["claude-opus-4", "claude-sonnet-4", "gpt-5", "o3"]
            ):
                context_length = 200 * 1024  # 200K
            elif any(
                x in model for x in ["claude-3", "gpt-4", "gemini-2.5", "DeepSeek-V3"]
            ):
                context_length = 128 * 1024  # 128K
            else:
                context_length = 32 * 1024  # 默认 32K

        if not api_key:
            raise ValueError(
                "BurnCloud API key is required, please set 'BURNCLOUD_API_KEY' in "
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
                "BurnCloud API requires openai>=1.0, please upgrade it by "
                "`pip install --upgrade 'openai>=1.0'`"
            )

    @property
    def default_model(self) -> str:
        model = self._model
        if not model:
            model = _DEFAULT_MODEL
        return model

    @classmethod
    def param_class(cls) -> Type[BurnCloudDeployModelParameters]:
        """获取模型部署参数类。"""
        return BurnCloudDeployModelParameters

    @classmethod
    def new_client(
        cls,
        model_params: BurnCloudDeployModelParameters,
        default_executor: Optional[Executor] = None,
    ) -> "BurnCloudLLMClient":
        """根据模型参数创建新的客户端。"""
        return cls(
            api_key=model_params.api_key,
            api_base=model_params.api_base,
            api_type=model_params.api_type,
            api_version=model_params.api_version,
            model=model_params.real_provider_model_name,
            proxy=model_params.http_proxy,
            model_alias=model_params.real_provider_model_name,
            context_length=max(model_params.context_length or 8192, 8192),
        )

    @classmethod
    def generate_stream_function(
        cls,
    ) -> Optional[Union[GenerateStreamFunction, AsyncGenerateStreamFunction]]:
        """获取流式生成函数。"""
        return burncloud_generate_stream


register_proxy_model_adapter(
    BurnCloudLLMClient,
    supported_models=[
        # Claude 模型。
        ModelMetadata(
            model="claude-opus-4-1-20250805",
            context_length=200 * 1024,
            max_output_length=8 * 1024,
            description="Claude Opus 4.1 by Anthropic via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="claude-sonnet-4-20250514",
            context_length=200 * 1024,
            max_output_length=8 * 1024,
            description="Claude Sonnet 4 by Anthropic via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="claude-opus-4-20250514",
            context_length=200 * 1024,
            max_output_length=8 * 1024,
            description="Claude Opus 4 by Anthropic via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="claude-3-7-sonnet-20250219",
            context_length=200 * 1024,
            max_output_length=8 * 1024,
            description="Claude 3.7 Sonnet by Anthropic via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="claude-3-5-sonnet-20241022",
            context_length=200 * 1024,
            max_output_length=8 * 1024,
            description="Claude 3.5 Sonnet by Anthropic via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        # GPT 模型。
        ModelMetadata(
            model="gpt-5-chat-latest",
            context_length=200 * 1024,
            max_output_length=16 * 1024,
            description="GPT-5 Chat Latest by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gpt-5",
            context_length=200 * 1024,
            max_output_length=16 * 1024,
            description="GPT-5 by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gpt-4.1",
            context_length=128 * 1024,
            max_output_length=16 * 1024,
            description="GPT-4.1 by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gpt-4.1-mini",
            context_length=128 * 1024,
            max_output_length=16 * 1024,
            description="GPT-4.1 Mini by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="chatgpt-4o-latest",
            context_length=128 * 1024,
            max_output_length=16 * 1024,
            description="ChatGPT-4o Latest by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gpt-4o-2024-11-20",
            context_length=128 * 1024,
            max_output_length=16 * 1024,
            description="GPT-4o by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gpt-4o",
            context_length=128 * 1024,
            max_output_length=16 * 1024,
            description="GPT-4o by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gpt-4o-mini",
            context_length=128 * 1024,
            max_output_length=16 * 1024,
            description="GPT-4o Mini by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gpt-image-1",
            context_length=32 * 1024,
            max_output_length=4 * 1024,
            description="GPT Image Generation Model via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=False,
        ),
        ModelMetadata(
            model="text-embedding-3-large",
            context_length=8 * 1024,
            max_output_length=3072,
            description="Text Embedding 3 Large by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=False,
        ),
        # 推理模型。
        ModelMetadata(
            model="o3",
            context_length=200 * 1024,
            max_output_length=100 * 1024,
            description="o3 Reasoning model by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="o3-mini",
            context_length=128 * 1024,
            max_output_length=65 * 1024,
            description="o3-mini Reasoning model by OpenAI via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        # Gemini 模型。
        ModelMetadata(
            model="gemini-2.5-pro",
            context_length=128 * 1024,
            max_output_length=8 * 1024,
            description="Gemini 2.5 Pro by Google via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gemini-2.5-flash",
            context_length=128 * 1024,
            max_output_length=8 * 1024,
            description="Gemini 2.5 Flash by Google via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gemini-2.5-flash-nothink",
            context_length=128 * 1024,
            max_output_length=8 * 1024,
            description="Gemini 2.5 Flash No Think by Google via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gemini-2.5-pro-search",
            context_length=128 * 1024,
            max_output_length=8 * 1024,
            description="Gemini 2.5 Pro Search by Google via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gemini-2.5-pro-preview-06-05",
            context_length=128 * 1024,
            max_output_length=8 * 1024,
            description="Gemini 2.5 Pro Preview by Google via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        ModelMetadata(
            model="gemini-2.5-pro-preview-05-06",
            context_length=128 * 1024,
            max_output_length=8 * 1024,
            description="Gemini 2.5 Pro Preview by Google via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
        # DeepSeek 模型。
        ModelMetadata(
            model="DeepSeek-V3",
            context_length=128 * 1024,
            max_output_length=8 * 1024,
            description="DeepSeek V3 by DeepSeek via BurnCloud",
            link="https://ai.burncloud.com/",
            function_calling=True,
        ),
    ],
)
