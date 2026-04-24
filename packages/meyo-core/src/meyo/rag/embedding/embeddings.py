"""向量生成运行抽象，统一文本向量生成模型的调用和元数据描述。"""


from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

import aiohttp
import requests

from meyo._private.pydantic import EXTRA_FORBID, BaseModel, ConfigDict, Field
from meyo.core import EmbeddingModelMetadata, Embeddings
from meyo.model.resource import Parameter, ResourceCategory, register_resource
from meyo.core.interface.parameter import EmbeddingDeployModelParameters
from meyo.model.adapter.base import register_embedding_adapter
from meyo.model.adapter.embed_metadata import (
    EMBED_COMMON_HF_BGE_MODELS,
    EMBED_COMMON_HF_JINA_MODELS,
    EMBED_COMMON_HF_QWEN_MODELS,
)
from meyo.util.i18n_utils import _
from meyo.util.tracer import MEYO_TRACER_SPAN_ID, root_tracer

DEFAULT_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
DEFAULT_INSTRUCT_MODEL = "hkunlp/instructor-large"
DEFAULT_BGE_MODEL = "BAAI/bge-large-en"
DEFAULT_EMBED_INSTRUCTION = "Represent the document for retrieval: "
DEFAULT_QUERY_INSTRUCTION = (
    "Represent the question for retrieving supporting documents: "
)
DEFAULT_QUERY_BGE_INSTRUCTION_EN = (
    "Represent this question for searching relevant passages: "
)
DEFAULT_QUERY_BGE_INSTRUCTION_ZH = "为这个句子生成表示以用于检索相关文章："

try:
    import transformers

    if not hasattr(transformers, "is_torch_npu_available"):
        # 参考链接。
        from transformers.utils import is_torch_npu_available

        transformers.is_torch_npu_available = is_torch_npu_available
except Exception:
    pass


@dataclass
class HFEmbeddingDeployModelParameters(EmbeddingDeployModelParameters):
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
    cache_folder: Optional[str] = field(
        default=None,
        metadata={
            "help": _("Path of the cache folder."),
        },
    )

    normalize_embeddings: bool = field(
        default=False,
        metadata={
            "help": _("Normalize embeddings."),
        },
    )
    multi_process: bool = field(
        default=False,
        metadata={
            "help": _("Run encode() on multiple GPUs."),
        },
    )
    model_kwargs: Dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "help": _("Keyword arguments to pass to the model."),
        },
    )
    encode_kwargs: Dict[str, Any] = field(
        default_factory=dict,
        metadata={
            "help": _("Keyword arguments to pass when calling the `encode` method."),
        },
    )
    embed_instruction: Optional[str] = field(
        default=None,
        metadata={
            "help": _(
                "Instruction to use for embedding documents. Just for Instructor model."
            ),
        },
    )
    query_instruction: Optional[str] = field(
        default=None,
        metadata={
            "help": _(
                "Instruction to use for embedding query. Just for Instructor model."
            )
        },
    )

    @property
    def real_provider_model_name(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self.real_model_path or self.name

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
        model_kwargs = self.model_kwargs or {}
        if self.device:
            model_kwargs["device"] = self.device
        return model_kwargs

    @property
    def real_encode_kwargs(self) -> Dict:
        encode_kwargs = self.encode_kwargs or {}
        if self.normalize_embeddings:
            encode_kwargs["normalize_embeddings"] = self.normalize_embeddings
        return encode_kwargs


@register_resource(
    _("HuggingFace Embeddings"),
    "huggingface_embeddings",
    category=ResourceCategory.EMBEDDINGS,
    description=_("HuggingFace sentence_transformers embedding models."),
    parameters=[
        Parameter.build_from(
            _("Model Name"),
            "model_name",
            str,
            optional=True,
            default=DEFAULT_MODEL_NAME,
            description=_("Model name to use."),
        ),
        # 待办事项。
    ],
)
class HuggingFaceEmbeddings(BaseModel, Embeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(extra=EXTRA_FORBID, protected_namespaces=())

    client: Any  # 代码说明。
    model_name: str = DEFAULT_MODEL_NAME
    """使用的模型名称。"""
    cache_folder: Optional[str] = Field(None, description="Path of the cache folder.")
    """模型缓存路径，也可通过环境变量设置。"""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """传给模型或编码方法的关键字参数。"""
    encode_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """传给模型或编码方法的关键字参数。"""
    multi_process: bool = False
    """是否使用多卡执行编码。"""

    def __init__(self, **kwargs: Any):
        """初始化实例。"""
        try:
            import sentence_transformers

        except ImportError as exc:
            raise ImportError(
                "Could not import sentence_transformers python package. "
                "Please install it with `pip install sentence-transformers`."
            ) from exc

        kwargs["client"] = sentence_transformers.SentenceTransformer(
            kwargs.get("model_name") or DEFAULT_MODEL_NAME,
            cache_folder=kwargs.get("cache_folder"),
            **(kwargs.get("model_kwargs") or {}),
        )
        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[HFEmbeddingDeployModelParameters]:
        return HFEmbeddingDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: HFEmbeddingDeployModelParameters
    ) -> "Embeddings":
        """根据输入参数创建对象。"""
        return cls(
            model_name=parameters.real_provider_model_name,
            model_kwargs=parameters.real_model_kwargs,
            encode_kwargs=parameters.real_encode_kwargs,
            cache_folder=parameters.cache_folder,
            multi_process=parameters.multi_process,
        )

    @classmethod
    def _match(
        cls, provider: str, lower_model_name_or_path: Optional[str] = None
    ) -> bool:
        return (
            super()._match(provider, lower_model_name_or_path)
            and lower_model_name_or_path
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        import sentence_transformers

        texts = list(map(lambda x: x.replace("\n", " "), texts))
        if self.multi_process:
            pool = self.client.start_multi_process_pool()
            embeddings = self.client.encode_multi_process(texts, pool)
            sentence_transformers.SentenceTransformer.stop_multi_process_pool(pool)
        else:
            embeddings = self.client.encode(texts, **self.encode_kwargs)

        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        return self.embed_documents([text])[0]


@register_resource(
    _("HuggingFace Instructor Embeddings"),
    "huggingface_instructor_embeddings",
    category=ResourceCategory.EMBEDDINGS,
    description=_("HuggingFace Instructor embeddings."),
    parameters=[
        Parameter.build_from(
            _("Model Name"),
            "model_name",
            str,
            optional=True,
            default=DEFAULT_INSTRUCT_MODEL,
            description=_("Model name to use."),
        ),
        Parameter.build_from(
            _("Embed Instruction"),
            "embed_instruction",
            str,
            optional=True,
            default=DEFAULT_EMBED_INSTRUCTION,
            description=_("Instruction to use for embedding documents."),
        ),
        Parameter.build_from(
            _("Query Instruction"),
            "query_instruction",
            str,
            optional=True,
            default=DEFAULT_QUERY_INSTRUCTION,
            description=_("Instruction to use for embedding query."),
        ),
    ],
)
class HuggingFaceInstructEmbeddings(BaseModel, Embeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(extra=EXTRA_FORBID, protected_namespaces=())

    client: Any  # 代码说明。
    model_name: str = DEFAULT_INSTRUCT_MODEL
    """使用的模型名称。"""
    cache_folder: Optional[str] = None
    """模型缓存路径，也可通过环境变量设置。"""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """传给模型或编码方法的关键字参数。"""
    encode_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """传给模型或编码方法的关键字参数。"""
    embed_instruction: str = DEFAULT_EMBED_INSTRUCTION
    """生成文档向量时使用的指令。"""
    query_instruction: str = DEFAULT_QUERY_INSTRUCTION
    """生成查询向量时使用的指令。"""

    def __init__(self, **kwargs: Any):
        """初始化实例。"""
        try:
            from InstructorEmbedding import INSTRUCTOR

            kwargs["client"] = INSTRUCTOR(
                kwargs.get("model_name"),
                cache_folder=kwargs.get("cache_folder"),
                **kwargs.get("model_kwargs"),
            )
        except ImportError as e:
            raise ImportError("Dependencies for InstructorEmbedding not found.") from e

        super().__init__(**kwargs)

    @classmethod
    def param_class(cls) -> Type[HFEmbeddingDeployModelParameters]:
        return HFEmbeddingDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: HFEmbeddingDeployModelParameters
    ) -> "Embeddings":
        """根据输入参数创建对象。"""
        return cls(
            model_name=parameters.real_provider_model_name,
            model_kwargs=parameters.real_model_kwargs,
            encode_kwargs=parameters.real_encode_kwargs,
            cache_folder=parameters.cache_folder,
            embed_instruction=parameters.embed_instruction or DEFAULT_EMBED_INSTRUCTION,
            query_instruction=parameters.query_instruction or DEFAULT_QUERY_INSTRUCTION,
        )

    @classmethod
    def _match(
        cls, provider: str, lower_model_name_or_path: Optional[str] = None
    ) -> bool:
        return (
            super()._match(provider, lower_model_name_or_path)
            and lower_model_name_or_path
            and ("instructor" in lower_model_name_or_path)
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        instruction_pairs = [[self.embed_instruction, text] for text in texts]
        embeddings = self.client.encode(instruction_pairs, **self.encode_kwargs)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        instruction_pair = [self.query_instruction, text]
        embedding = self.client.encode([instruction_pair], **self.encode_kwargs)[0]
        return embedding.tolist()


# 待办事项。
class HuggingFaceBgeEmbeddings(BaseModel, Embeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(extra=EXTRA_FORBID, protected_namespaces=())

    client: Any  # 代码说明。
    model_name: str = DEFAULT_BGE_MODEL
    """使用的模型名称。"""
    cache_folder: Optional[str] = None
    """模型缓存路径，也可通过环境变量设置。"""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """传给模型或编码方法的关键字参数。"""
    encode_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """传给模型或编码方法的关键字参数。"""
    query_instruction: str = DEFAULT_QUERY_BGE_INSTRUCTION_EN
    """生成查询向量时使用的指令。"""

    def __init__(self, **kwargs: Any):
        """初始化实例。"""
        try:
            import sentence_transformers

        except ImportError as exc:
            raise ImportError(
                "Could not import sentence_transformers python package. "
                "Please install it with `pip install sentence_transformers`."
            ) from exc

        kwargs["client"] = sentence_transformers.SentenceTransformer(
            kwargs.get("model_name"),
            cache_folder=kwargs.get("cache_folder"),
            **(kwargs.get("model_kwargs") or {}),
        )

        super().__init__(**kwargs)
        if "-zh" in self.model_name:
            self.query_instruction = DEFAULT_QUERY_BGE_INSTRUCTION_ZH

    @classmethod
    def param_class(cls) -> Type[HFEmbeddingDeployModelParameters]:
        return HFEmbeddingDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: HFEmbeddingDeployModelParameters
    ) -> "Embeddings":
        """根据输入参数创建对象。"""
        return cls(
            model_name=parameters.real_provider_model_name,
            model_kwargs=parameters.real_model_kwargs,
            encode_kwargs=parameters.real_encode_kwargs,
            cache_folder=parameters.cache_folder,
            query_instruction=parameters.query_instruction
            or DEFAULT_QUERY_BGE_INSTRUCTION_EN,
        )

    @classmethod
    def _match(
        cls, provider: str, lower_model_name_or_path: Optional[str] = None
    ) -> bool:
        return (
            super()._match(provider, lower_model_name_or_path)
            and lower_model_name_or_path
            and "bge" in lower_model_name_or_path
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        texts = [t.replace("\n", " ") for t in texts]
        embeddings = self.client.encode(texts, **self.encode_kwargs)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        text = text.replace("\n", " ")
        embedding = self.client.encode(
            self.query_instruction + text, **self.encode_kwargs
        )
        return embedding.tolist()


@register_resource(
    _("HuggingFace Inference API Embeddings"),
    "huggingface_inference_api_embeddings",
    category=ResourceCategory.EMBEDDINGS,
    description=_("HuggingFace Inference API embeddings."),
    parameters=[
        Parameter.build_from(
            _("API Key"),
            "api_key",
            str,
            description=_("Your API key for the HuggingFace Inference API."),
        ),
        Parameter.build_from(
            _("Model Name"),
            "model_name",
            str,
            optional=True,
            default="sentence-transformers/all-MiniLM-L6-v2",
            description=_("The name of the model to use for text embeddings."),
        ),
    ],
)
class HuggingFaceInferenceAPIEmbeddings(BaseModel, Embeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    api_key: str
    """调用外部推理接口的密钥。"""
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    """文本向量模型名称。"""

    @property
    def _api_url(self) -> str:
        return (
            "https://api-inference.huggingface.co"
            "/pipeline"
            "/feature-extraction"
            f"/{self.model_name}"
        )

    @property
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        response = requests.post(
            self._api_url,
            headers=self._headers,
            json={
                "inputs": texts,
                "options": {"wait_for_model": True, "use_cache": True},
            },
        )
        return response.json()

    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        return self.embed_documents([text])[0]


def _handle_request_result(res: requests.Response) -> List[List[float]]:
    """执行当前函数对应的业务逻辑。"""
    res.raise_for_status()
    resp = res.json()
    if "data" not in resp:
        raise RuntimeError(resp["detail"])
    embeddings = resp["data"]
    # 向量生成配置。
    sorted_embeddings = sorted(embeddings, key=lambda e: e["index"])  # type: ignore
    # 向量生成配置。
    return [result["embedding"] for result in sorted_embeddings]


@dataclass
class OpenAPIEmbeddingDeployModelParameters(EmbeddingDeployModelParameters):
    """配置参数定义。"""

    provider: str = "proxy/openai"

    api_url: str = field(
        default="http://localhost:8100/api/v1/embeddings",
        metadata={
            "help": _("The URL of the embeddings API."),
        },
    )
    api_key: Optional[str] = field(
        default=None,
        metadata={
            "help": _("The API key for the embeddings API."),
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


@register_resource(
    _("OpenAPI Embeddings"),
    "openapi_embeddings",
    category=ResourceCategory.EMBEDDINGS,
    description=_("OpenAPI embeddings."),
    parameters=[
        Parameter.build_from(
            _("API URL"),
            "api_url",
            str,
            optional=True,
            default="http://localhost:8100/api/v1/embeddings",
            description=_("The URL of the embeddings API."),
        ),
        Parameter.build_from(
            _("API Key"),
            "api_key",
            str,
            optional=True,
            default=None,
            description=_("Your API key for the Open API."),
        ),
        Parameter.build_from(
            _("Model Name"),
            "model_name",
            str,
            optional=True,
            default="text2vec",
            description=_("The name of the model to use for text embeddings."),
        ),
        Parameter.build_from(
            _("Timeout"),
            "timeout",
            int,
            optional=True,
            default=60,
            description=_("The timeout for the request in seconds."),
        ),
    ],
)
class OpenAPIEmbeddings(BaseModel, Embeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    api_url: str = Field(
        default="http://localhost:8100/api/v1/embeddings",
        description="The URL of the embeddings API.",
    )
    api_key: Optional[str] = Field(
        default=None, description="The API key for the embeddings API."
    )
    model_name: str = Field(
        default="text2vec", description="The name of the model to use."
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
    def param_class(cls) -> Type[OpenAPIEmbeddingDeployModelParameters]:
        return OpenAPIEmbeddingDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: OpenAPIEmbeddingDeployModelParameters
    ) -> "Embeddings":
        """根据输入参数创建对象。"""
        return cls(
            api_url=parameters.api_url,
            api_key=parameters.api_key,
            model_name=parameters.real_provider_model_name,
            timeout=parameters.timeout,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        # 向量生成配置。
        headers = {}
        current_span_id = root_tracer.get_current_span_id()
        if self.pass_trace_id and current_span_id:
            # 设置对应数据。
            headers[MEYO_TRACER_SPAN_ID] = current_span_id
        res = self.session.post(  # type: ignore
            self.api_url,
            json={"input": texts, "model": self.model_name},
            timeout=self.timeout,
            headers=headers,
        )
        return _handle_request_result(res)

    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        return self.embed_documents([text])[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        current_span_id = root_tracer.get_current_span_id()
        if self.pass_trace_id and current_span_id:
            # 设置对应数据。
            headers[MEYO_TRACER_SPAN_ID] = current_span_id
        async with aiohttp.ClientSession(
            headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.post(
                self.api_url, json={"input": texts, "model": self.model_name}
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "data" not in data:
                    raise RuntimeError(data["detail"])
                embeddings = data["data"]
                sorted_embeddings = sorted(embeddings, key=lambda e: e["index"])
                return [result["embedding"] for result in sorted_embeddings]

    async def aembed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        embeddings = await self.aembed_documents([text])
        return embeddings[0]


register_embedding_adapter(
    HuggingFaceEmbeddings,
    supported_models=[
        EmbeddingModelMetadata(
            model=["thenlper/gte-large-zh"],
            context_length=512,
            description=_(
                "The GTE models are trained by Alibaba DAMO Academy, supporting "
                "Chinese."
            ),
            link="https://huggingface.co/thenlper/gte-large-zh",
            languages=["zh"],
        ),
        EmbeddingModelMetadata(
            model=["thenlper/gte-large"],
            context_length=512,
            description=_(
                "The GTE models are trained by Alibaba DAMO Academy, supporting "
                "English."
            ),
            link="https://huggingface.co/thenlper/gte-large",
            languages=["en"],
        ),
        EmbeddingModelMetadata(
            model=["moka-ai/m3e-base"],
            context_length=768,
            description=_(
                "The embedding model are trained by MokaAI, this version support "
                "English and Chinese."
            ),
            link="https://huggingface.co/moka-ai/m3e-base",
            languages=["en", "zh"],
        ),
        EmbeddingModelMetadata(
            model=["moka-ai/m3e-large"],
            context_length=768,
            description=_(
                "The embedding model are trained by MokaAI, this version support "
                "Chinese."
            ),
            link="https://huggingface.co/moka-ai/m3e-large",
            languages=["zh"],
        ),
    ]
    + EMBED_COMMON_HF_JINA_MODELS
    + EMBED_COMMON_HF_QWEN_MODELS,
)
register_embedding_adapter(
    HuggingFaceInstructEmbeddings,
    supported_models=[
        EmbeddingModelMetadata(
            model=["hkunlp/instructor-large", "hkunlp/instructor-base"],
            description=_(
                "The embedding model are trained by HKUNLP, it support English."
            ),
            link="https://huggingface.co/hkunlp/instructor-large",
            languages=["en"],
        )
    ],
)
register_embedding_adapter(
    HuggingFaceBgeEmbeddings, supported_models=EMBED_COMMON_HF_BGE_MODELS
)
register_embedding_adapter(
    OpenAPIEmbeddings,
    supported_models=[
        EmbeddingModelMetadata(
            model=["text-embedding-3-small"],
            dimension=1536,
            context_length=8191,
            description=_(
                "The embedding model are trained by OpenAI, it support English."
            ),
            link="https://platform.openai.com/docs/guides/embeddings",
            languages=["en"],
        ),
        EmbeddingModelMetadata(
            model=["text-embedding-3-small"],
            dimension=3072,
            context_length=8191,
            description=_(
                "The embedding model are trained by OpenAI, it support English."
            ),
            link="https://platform.openai.com/docs/guides/embeddings",
            languages=["en"],
        ),
    ],
)
