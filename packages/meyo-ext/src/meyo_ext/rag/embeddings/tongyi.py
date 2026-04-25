"""通义千问向量模型供应商实现，负责调用 DashScope 向量化接口。"""

from dataclasses import dataclass, field
from typing import List, Optional, Type

from meyo._private.pydantic import BaseModel, ConfigDict, Field
from meyo.core import EmbeddingModelMetadata, Embeddings
from meyo.core.interface.parameter import EmbeddingDeployModelParameters
from meyo.model.adapter.base import register_embedding_adapter
from meyo.util.i18n_utils import _


@dataclass
class TongyiEmbeddingDeployModelParameters(EmbeddingDeployModelParameters):
    """配置参数定义。"""

    provider: str = "proxy/tongyi"

    api_key: Optional[str] = field(
        default=None, metadata={"help": _("The API key for the embeddings API.")}
    )
    backend: Optional[str] = field(
        default="text-embedding-v1",
        metadata={
            "help": _(
                "The real model name to pass to the provider, default is None. If "
                "backend is None, use name as the real model name."
            ),
        },
    )

    @property
    def real_provider_model_name(self) -> str:
        """获取实际传给供应商的模型名称。"""
        return self.backend or self.name


class TongYiEmbeddings(BaseModel, Embeddings):
    """向量生成能力实现。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())
    api_key: Optional[str] = Field(
        default=None, description="The API key for the embeddings API."
    )
    model_name: str = Field(
        default="text-embedding-v1", description="The name of the model to use."
    )

    def __init__(self, **kwargs):
        """初始化实例。"""
        try:
            import dashscope  # type: ignore
        except ImportError as exc:
            raise ValueError(
                "Could not import python package: dashscope "
                "Please install dashscope by command `pip install dashscope"
            ) from exc
        dashscope.TextEmbedding.api_key = kwargs.get("api_key")
        super().__init__(**kwargs)
        self._api_key = kwargs.get("api_key")

    @classmethod
    def param_class(cls) -> Type[TongyiEmbeddingDeployModelParameters]:
        """获取配置参数类型。"""
        return TongyiEmbeddingDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: TongyiEmbeddingDeployModelParameters
    ) -> "Embeddings":
        """根据输入参数创建对象。"""
        return cls(
            api_key=parameters.api_key,
            model_name=parameters.real_provider_model_name,
        )

    def embed_documents(
        self, texts: List[str], max_batch_chunks_size=25
    ) -> List[List[float]]:
        """批量生成文本向量。"""
        from dashscope import TextEmbedding

        embeddings = []
        # 批量过大时在线向量化容易失败，普通模型最多 25 条。
        # text-embedding-v3 的批量大小建议不超过 6 条。
        if str(self.model_name) == "text-embedding-v3":
            max_batch_chunks_size = 6

        for i in range(0, len(texts), max_batch_chunks_size):
            batch_texts = texts[i : i + max_batch_chunks_size]
            resp = TextEmbedding.call(
                model=self.model_name, input=batch_texts, api_key=self._api_key
            )
            if "output" not in resp:
                raise RuntimeError(resp["message"])

            # 提取并排序嵌入
            batch_embeddings = resp["output"]["embeddings"]
            sorted_embeddings = sorted(batch_embeddings, key=lambda e: e["text_index"])
            embeddings.extend([result["embedding"] for result in sorted_embeddings])

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """生成单条查询文本向量。"""
        return self.embed_documents([text])[0]


register_embedding_adapter(
    TongYiEmbeddings,
    supported_models=[
        EmbeddingModelMetadata(
            model="text-embedding-v3",
            dimension=1024,
            context_length=8192,
            description=_(
                "The embedding model are trained by TongYi, it support more than 50 "
                "working languages."
            ),
        )
    ],
)
