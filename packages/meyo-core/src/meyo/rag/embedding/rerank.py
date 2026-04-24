"""重排运行抽象，统一相关性排序模型的请求和结果结构。"""


import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, cast

import aiohttp
import numpy as np
import requests

from meyo._private.pydantic import EXTRA_FORBID, BaseModel, ConfigDict, Field
from meyo.configs.model_config import get_device
from meyo.core import RerankEmbeddings
from meyo.core.interface.parameter import RerankerDeployModelParameters
from meyo.model.adapter.base import register_embedding_adapter
from meyo.model.adapter.embed_metadata import (
    RERANKER_COMMON_HF_MODELS,
    RERANKER_COMMON_HF_QWEN_MODELS,
)
from meyo.util.i18n_utils import _
from meyo.util.tracer import MEYO_TRACER_SPAN_ID, root_tracer


@dataclass
class CrossEncoderRerankEmbeddingsParameters(RerankerDeployModelParameters):
    """配置参数定义。"""

    provider: str = "hf"
    path: Optional[str] = field(
        default=None,
        metadata={
            "order": -800,
            "help": _("The path of the model, if you want to deploy a local model."),
        },
    )
    device: Optional[str] = field(
        default=None,
        metadata={
            "order": -700,
            "help": _(
                "Device to run model. If None, the device is automatically determined"
            ),
        },
    )
    max_length: Optional[int] = field(
        default=None,
        metadata={
            "help": _(
                "Max length for input sequences. Longer sequences will be truncated."
            )
        },
    )

    model_kwargs: Dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "help": _("Keyword arguments to pass to the model."),
        },
    )

    @property
    def real_provider_model_name(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self.path or self.name

    @property
    def real_model_path(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        return self._resolve_root_path(self.path)

    @property
    def real_device(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        return self.device or super().real_device

    @property
    def real_model_kwargs(self) -> Dict:
        """执行当前函数对应的业务逻辑。"""
        model_kwargs = self.model_kwargs or {}
        if self.device:
            model_kwargs["device"] = self.device
        return model_kwargs


class CrossEncoderRerankEmbeddings(BaseModel, RerankEmbeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(extra=EXTRA_FORBID, protected_namespaces=())

    client: Any  # 代码说明。
    model_name: str = "BAAI/bge-reranker-base"
    max_length: Optional[int] = None
    """输入序列最大长度，超出部分会被截断；为空时使用模型默认长度。"""
    """使用的模型名称。"""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """传给模型或编码方法的关键字参数。"""

    def __init__(self, **kwargs: Any):
        """初始化实例。"""
        try:
            from sentence_transformers import CrossEncoder
        except ImportError:
            raise ImportError(
                "please `pip install sentence-transformers`",
            )

        kwargs["client"] = CrossEncoder(
            kwargs.get("model_name", "BAAI/bge-reranker-base"),
            max_length=kwargs.get("max_length"),  # type: ignore
            **(kwargs.get("model_kwargs") or {}),
        )
        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[CrossEncoderRerankEmbeddingsParameters]:
        """执行当前函数对应的业务逻辑。"""
        return CrossEncoderRerankEmbeddingsParameters

    @classmethod
    def from_parameters(
        cls, parameters: CrossEncoderRerankEmbeddingsParameters
    ) -> "RerankEmbeddings":
        """根据输入参数创建对象。"""
        return cls(
            model_name=parameters.real_model_path,
            max_length=parameters.max_length,
            model_kwargs=parameters.real_model_kwargs,
        )

    @classmethod
    def _match(
        cls, provider: str, lower_model_name_or_path: Optional[str] = None
    ) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return (
            super()._match(provider, lower_model_name_or_path)
            and lower_model_name_or_path
            and (
                "reranker" in lower_model_name_or_path
                or "rerank" in lower_model_name_or_path
            )
        )

    def predict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        from sentence_transformers import CrossEncoder

        query_content_pairs = [[query, candidate] for candidate in candidates]
        _model = cast(CrossEncoder, self.client)
        rank_scores = _model.predict(sentences=query_content_pairs)
        if isinstance(rank_scores, np.ndarray):
            rank_scores = rank_scores.tolist()
        return rank_scores  # type: ignore


@dataclass
class QwenRerankEmbeddingsParameters(RerankerDeployModelParameters):
    """配置参数定义。"""

    provider: str = "qwen"
    path: Optional[str] = field(
        default=None,
        metadata={
            "order": -800,
            "help": _(
                "The path of the model, if you want to deploy a local model. Defaults "
                "to 'Qwen/Qwen3-Reranker-0.6B'."
            ),
        },
    )
    device: Optional[str] = field(
        default=None,
        metadata={
            "order": -700,
            "help": _(
                "Device to run model. If None, the device is automatically determined"
            ),
        },
    )

    @property
    def real_provider_model_name(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self.path or self.name

    @property
    def real_model_path(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        return self._resolve_root_path(self.path)

    @property
    def real_device(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        return self.device or super().real_device


class QwenRerankEmbeddings(BaseModel, RerankEmbeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(extra=EXTRA_FORBID, protected_namespaces=())
    model_name: str = "Qwen/Qwen3-Reranker-0.6B"
    max_length: int = 8192
    model: Any  # 代码说明。
    tokenizer: Any  # 代码说明。
    token_false_id: int  # 代码说明。
    token_true_id: int  # 代码说明。
    prefix_tokens: List[int]  # 代码说明。
    suffix_tokens: List[int]  # 代码说明。
    task: str = (
        "Given a web search query, retrieve relevant passages that answer the "
        "query"
    )  # 代码说明。
    device: Optional[str] = None  # 代码说明。

    def __init__(self, **kwargs: Any):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            raise ImportError(
                "please `pip install transformers`",
            )

        try:
            import torch  # noqa: F401
        except ImportError:
            raise ImportError(
                "please `pip install torch`",
            )
        tokenizer = AutoTokenizer.from_pretrained(
            kwargs.get("model_name", "Qwen/Qwen3-Reranker-0.6B"), padding_side="left"
        )
        model = AutoModelForCausalLM.from_pretrained(
            kwargs.get("model_name", "Qwen/Qwen3-Reranker-0.6B"),
        ).eval()
        device = kwargs.get("device", get_device())
        if device:
            model = model.to(device=device)

        token_false_id = tokenizer.convert_tokens_to_ids("no")
        token_true_id = tokenizer.convert_tokens_to_ids("yes")
        prefix = (
            "<|im_start|>system\nJudge whether the Document meets the requirements"
            " based on the Query and the Instruct provided. Note that the answer can "
            'only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
        )
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
        suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

        kwargs["model"] = model
        kwargs["tokenizer"] = tokenizer
        kwargs["token_false_id"] = token_false_id
        kwargs["token_true_id"] = token_true_id
        kwargs["prefix_tokens"] = prefix_tokens
        kwargs["suffix_tokens"] = suffix_tokens
        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[QwenRerankEmbeddingsParameters]:
        """执行当前函数对应的业务逻辑。"""
        return QwenRerankEmbeddingsParameters

    @classmethod
    def from_parameters(
        cls, parameters: QwenRerankEmbeddingsParameters
    ) -> "RerankEmbeddings":
        """根据输入参数创建对象。"""
        return cls(
            model_name=parameters.real_model_path,
            device=parameters.real_device,
        )

    def format_instruction(self, instruction, query, doc):
        if instruction is None:
            instruction = (
                "Given a web search query, retrieve relevant passages that "
                "answer the query"
            )
        output = (
            "<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}".format(
                instruction=instruction, query=query, doc=doc
            )
        )
        return output

    def process_inputs(self, pairs):
        inputs = self.tokenizer(
            pairs,
            padding=False,
            truncation="longest_first",
            return_attention_mask=False,
            max_length=self.max_length
            - len(self.prefix_tokens)
            - len(self.suffix_tokens),
        )
        for i, ele in enumerate(inputs["input_ids"]):
            inputs["input_ids"][i] = self.prefix_tokens + ele + self.suffix_tokens
        inputs = self.tokenizer.pad(
            inputs, padding=True, return_tensors="pt", max_length=self.max_length
        )
        for key in inputs:
            inputs[key] = inputs[key].to(self.model.device)
        return inputs

    def compute_logits(self, inputs, **kwargs):
        import torch

        with torch.no_grad():
            batch_scores = self.model(**inputs).logits[:, -1, :]
            true_vector = batch_scores[:, self.token_true_id]
            false_vector = batch_scores[:, self.token_false_id]
            batch_scores = torch.stack([false_vector, true_vector], dim=1)
            batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
            scores = batch_scores[:, 1].exp().tolist()
            return scores

    def predict(self, query: str, candidates: List[str]) -> List[float]:
        queries = [query] * len(candidates)
        pairs = [
            self.format_instruction(self.task, query, doc)
            for query, doc in zip(queries, candidates)
        ]
        # 代码说明。
        inputs = self.process_inputs(pairs)
        scores = self.compute_logits(inputs)
        return scores


@dataclass
class OpenAPIRerankerDeployModelParameters(RerankerDeployModelParameters):
    """配置参数定义。"""

    provider: str = "proxy/openapi"

    api_url: str = field(
        default="http://localhost:8100/v1/beta/relevance",
        metadata={
            "help": _("The URL of the rerank API."),
        },
    )
    api_key: Optional[str] = field(
        default=None,
        metadata={
            "help": _("The API key for the rerank API."),
        },
    )
    backend: Optional[str] = field(
        default=None,
        metadata={
            "help": _(
                "The real model name to pass to the provider, default is None. If "
                "backend is None, use name as the real model name."
            ),
        },
    )

    timeout: int = field(
        default=60,
        metadata={
            "help": _("The timeout for the request in seconds."),
        },
    )

    @property
    def real_provider_model_name(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self.backend or self.name


class OpenAPIRerankEmbeddings(BaseModel, RerankEmbeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    api_url: str = Field(
        default="http://localhost:8100/v1/beta/relevance",
        description="The URL of the embeddings API.",
    )
    api_key: Optional[str] = Field(
        default=None, description="The API key for the embeddings API."
    )
    model_name: str = Field(
        default="bge-reranker-base", description="The name of the model to use."
    )
    timeout: int = Field(
        default=60, description="The timeout for the request in seconds."
    )
    pass_trace_id: bool = Field(
        default=True, description="Whether to pass the trace ID to the API."
    )

    session: Optional[requests.Session] = None

    def __init__(self, **kwargs):
        """初始化实例。"""
        try:
            import requests
        except ImportError:
            raise ValueError(
                "The requests python package is not installed. "
                "Please install it with `pip install requests`"
            )
        if "session" not in kwargs:  # noqa: SIM401
            session = requests.Session()
        else:
            session = kwargs["session"]
        api_key = kwargs.get("api_key")
        if api_key:
            session.headers.update({"Authorization": f"Bearer {api_key}"})
        kwargs["session"] = session
        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[OpenAPIRerankerDeployModelParameters]:
        """执行当前函数对应的业务逻辑。"""
        return OpenAPIRerankerDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: OpenAPIRerankerDeployModelParameters
    ) -> "RerankEmbeddings":
        """根据输入参数创建对象。"""
        return cls(
            api_url=parameters.api_url,
            api_key=parameters.api_key,
            model_name=parameters.real_provider_model_name,
            timeout=parameters.timeout,
        )

    def _parse_results(self, response: Dict[str, Any]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        data = response.get("data")
        if not data:
            if "detail" in response:
                raise RuntimeError(response["detail"])
            raise RuntimeError("Cannot find results in the response")
        if not isinstance(data, list):
            raise RuntimeError("Results should be a list")
        return data

    def predict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        if not candidates:
            return []
        headers = {}
        current_span_id = root_tracer.get_current_span_id()
        if self.pass_trace_id and current_span_id:
            # 设置对应数据。
            headers[MEYO_TRACER_SPAN_ID] = current_span_id
        data = {"model": self.model_name, "query": query, "documents": candidates}
        response = self.session.post(  # type: ignore
            self.api_url, json=data, timeout=self.timeout, headers=headers
        )
        response.raise_for_status()
        return self._parse_results(response.json())

    async def apredict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        current_span_id = root_tracer.get_current_span_id()
        if self.pass_trace_id and current_span_id:
            # 设置对应数据。
            headers[MEYO_TRACER_SPAN_ID] = current_span_id
        async with aiohttp.ClientSession(
            headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            data = {"model": self.model_name, "query": query, "documents": candidates}
            async with session.post(self.api_url, json=data) as resp:
                resp.raise_for_status()
                response_data = await resp.json()
                return self._parse_results(response_data)


@dataclass
class SiliconFlowRerankEmbeddingsParameters(OpenAPIRerankerDeployModelParameters):
    """配置参数定义。"""

    provider: str = "proxy/siliconflow"

    api_url: str = field(
        default="https://api.siliconflow.cn/v1/rerank",
        metadata={
            "help": _("The URL of the rerank API."),
        },
    )
    api_key: Optional[str] = field(
        default="${env:SILICONFLOW_API_KEY}",
        metadata={
            "help": _("The API key for the rerank API."),
        },
    )


class SiliconFlowRerankEmbeddings(OpenAPIRerankEmbeddings):
    """向量生成或重排能力实现。"""

    def __init__(self, **kwargs: Any):
        """初始化实例。"""
        # 全局接口密钥配置。
        if "api_key" not in kwargs:
            kwargs["api_key"] = os.getenv("SILICONFLOW_API_KEY")

        if "api_url" not in kwargs:
            env_api_url = os.getenv("SILICONFLOW_API_BASE")
            if env_api_url:
                env_api_url = env_api_url.rstrip("/")
                kwargs["api_url"] = env_api_url + "/rerank"
            else:
                kwargs["api_url"] = "https://api.siliconflow.cn/v1/rerank"

        if "model_name" not in kwargs:
            kwargs["model_name"] = "BAAI/bge-reranker-v2-m3"

        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[SiliconFlowRerankEmbeddingsParameters]:
        """执行当前函数对应的业务逻辑。"""
        return SiliconFlowRerankEmbeddingsParameters

    def _parse_results(self, response: Dict[str, Any]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        results = response.get("results")
        if not results:
            raise RuntimeError("Cannot find results in the response")
        if not isinstance(results, list):
            raise RuntimeError("Results should be a list")
        # 代码说明。
        results = sorted(results, key=lambda x: x.get("index", 0))
        scores = [float(result.get("relevance_score")) for result in results]
        return scores


@dataclass
class TeiEmbeddingsParameters(OpenAPIRerankerDeployModelParameters):
    """配置参数定义。"""

    provider: str = "proxy/tei"

    api_url: str = field(
        default="http://localhost:8001/rerank",
        metadata={
            "help": _("The URL of the rerank API."),
        },
    )
    api_key: Optional[str] = field(
        default=None,
        metadata={
            "help": _("The API key for the rerank API."),
        },
    )


class TeiRerankEmbeddings(OpenAPIRerankEmbeddings):
    """向量生成或重排能力实现。"""

    def __init__(self, **kwargs: Any):
        """初始化实例。"""
        # 全局接口密钥配置。
        if "api_key" not in kwargs:
            kwargs["api_key"] = os.getenv("TEI_API_KEY")

        if "api_url" not in kwargs:
            raise ValueError("Please provide the api_url param")

        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[TeiEmbeddingsParameters]:
        """执行当前函数对应的业务逻辑。"""
        return TeiEmbeddingsParameters

    def _parse_results(self, response: List[Dict[str, Any]]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        if not isinstance(response, list) and len(response) == 0:
            raise RuntimeError("Results should be a not empty list")

        # 代码说明。
        results = sorted(response, key=lambda x: x.get("index", 0))
        scores = [float(result.get("score")) for result in results]
        return scores

    def predict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        if not candidates:
            return []
        headers = {}
        current_span_id = root_tracer.get_current_span_id()
        if self.pass_trace_id and current_span_id:
            # 设置对应数据。
            headers[MEYO_TRACER_SPAN_ID] = current_span_id
        data = {"query": query, "texts": candidates}
        response = self.session.post(  # type: ignore
            self.api_url, json=data, timeout=self.timeout, headers=headers
        )
        response.raise_for_status()
        return self._parse_results(response.json())

    async def apredict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        current_span_id = root_tracer.get_current_span_id()
        if self.pass_trace_id and current_span_id:
            # 设置对应数据。
            headers[MEYO_TRACER_SPAN_ID] = current_span_id
        async with aiohttp.ClientSession(
            headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            data = {"query": query, "texts": candidates}
            async with session.post(self.api_url, json=data) as resp:
                resp.raise_for_status()
                response_data = await resp.json()
                return self._parse_results(response_data)


@dataclass
class InfiniAIRerankEmbeddingsParameters(OpenAPIRerankerDeployModelParameters):
    """配置参数定义。"""

    provider: str = "proxy/infiniai"

    api_url: str = field(
        default="https://cloud.infini-ai.com/maas/v1/rerank",
        metadata={
            "help": _("The URL of the rerank API."),
        },
    )
    api_key: Optional[str] = field(
        default="${env:INFINIAI_API_KEY}",
        metadata={
            "help": _("The API key for the rerank API."),
        },
    )


class InfiniAIRerankEmbeddings(OpenAPIRerankEmbeddings):
    """向量生成或重排能力实现。"""

    def __init__(self, **kwargs: Any):
        """初始化实例。"""
        # 全局接口密钥配置。
        if "api_key" not in kwargs:
            kwargs["api_key"] = os.getenv("InfiniAI_API_KEY")

        if "api_url" not in kwargs:
            env_api_url = os.getenv("InfiniAI_API_BASE")
            if env_api_url:
                env_api_url = env_api_url.rstrip("/")
                kwargs["api_url"] = env_api_url + "/rerank"
            else:
                kwargs["api_url"] = "https://cloud.infini-ai.com/maas/v1/rerank"

        if "model_name" not in kwargs:
            kwargs["model_name"] = "bge-reranker-v2-m3"

        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[InfiniAIRerankEmbeddingsParameters]:
        """执行当前函数对应的业务逻辑。"""
        return InfiniAIRerankEmbeddingsParameters

    def _parse_results(self, response: Dict[str, Any]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        results = response.get("results")
        if not results:
            raise RuntimeError("Cannot find results in the response")
        if not isinstance(results, list):
            raise RuntimeError("Results should be a list")
        # 代码说明。
        results = sorted(results, key=lambda x: x.get("index", 0))
        scores = [float(result.get("relevance_score")) for result in results]
        return scores


register_embedding_adapter(
    CrossEncoderRerankEmbeddings, supported_models=RERANKER_COMMON_HF_MODELS
)
register_embedding_adapter(
    OpenAPIRerankEmbeddings, supported_models=RERANKER_COMMON_HF_MODELS
)
register_embedding_adapter(
    SiliconFlowRerankEmbeddings, supported_models=RERANKER_COMMON_HF_MODELS
)
register_embedding_adapter(
    TeiRerankEmbeddings, supported_models=RERANKER_COMMON_HF_MODELS
)
register_embedding_adapter(
    InfiniAIRerankEmbeddings, supported_models=RERANKER_COMMON_HF_MODELS
)
register_embedding_adapter(
    QwenRerankEmbeddings, supported_models=RERANKER_COMMON_HF_QWEN_MODELS
)
