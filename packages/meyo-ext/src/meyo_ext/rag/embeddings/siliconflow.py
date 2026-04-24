"""硅基流动向量生成和重排供应商实现，负责调用硅基流动向量和排序接口。"""

from dataclasses import dataclass, field
from typing import List, Optional, Type

from meyo._private.pydantic import BaseModel, ConfigDict, Field
from meyo.core import EmbeddingModelMetadata, Embeddings
from meyo.core.interface.parameter import EmbeddingDeployModelParameters
from meyo.model.adapter.base import register_embedding_adapter
from meyo.util.i18n_utils import _


@dataclass
class SiliconFlowEmbeddingDeployModelParameters(EmbeddingDeployModelParameters):
    """配置参数定义。"""

    provider: str = "proxy/siliconflow"

    api_key: Optional[str] = field(
        default="${env:SILICONFLOW_API_KEY}",
        metadata={
            "help": _("The API key for the rerank API."),
        },
    )
    backend: Optional[str] = field(
        default="BAAI/bge-m3",
        metadata={
            "help": _(
                "The real model name to pass to the provider, default is None. If "
                "backend is None, use name as the real model name."
            ),
        },
    )

    @property
    def real_provider_model_name(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self.backend or self.name


class SiliconFlowEmbeddings(BaseModel, Embeddings):
    """向量生成或重排能力实现。"""

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())
    api_key: Optional[str] = Field(
        default=None, description="The API key for the embeddings API."
    )
    model_name: str = Field(
        default="BAAI/bge-m3", description="The name of the model to use."
    )

    def __init__(self, **kwargs):
        """初始化实例。"""
        super().__init__(**kwargs)
        self._api_key = self.api_key

    @classmethod
    def param_class(cls) -> Type[SiliconFlowEmbeddingDeployModelParameters]:
        """执行当前函数对应的业务逻辑。"""
        return SiliconFlowEmbeddingDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: SiliconFlowEmbeddingDeployModelParameters
    ) -> "Embeddings":
        """根据输入参数创建对象。"""
        return cls(
            api_key=parameters.api_key,
            model_name=parameters.real_provider_model_name,
        )

    def embed_documents(
        self, texts: List[str], max_batch_chunks_size=25
    ) -> List[List[float]]:
        """生成向量结果。"""
        import requests

        embeddings = []
        headers = {"Authorization": f"Bearer {self._api_key}"}

        for i in range(0, len(texts), max_batch_chunks_size):
            batch_texts = texts[i : i + max_batch_chunks_size]
            response = requests.post(
                url="https://api.siliconflow.cn/v1/embeddings",
                json={"model": self.model_name, "input": batch_texts},
                headers=headers,
            )

            if response.status_code != 200:
                raise RuntimeError(f"Embedding failed: {response.text}")

            # 提取并排序嵌入
            data = response.json()
            batch_embeddings = data["data"]
            sorted_embeddings = sorted(batch_embeddings, key=lambda e: e["index"])
            embeddings.extend([result["embedding"] for result in sorted_embeddings])

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        return self.embed_documents([text])[0]


register_embedding_adapter(
    SiliconFlowEmbeddings,
    supported_models=[
        EmbeddingModelMetadata(
            model="BAAI/bge-m3",
            dimension=1024,
            context_length=8192,
            description=_(
                "The embedding model is provided by SiliconFlow, supporting multiple "
                "languages and high-quality text embeddings."
            ),
        ),
        EmbeddingModelMetadata(
            model="BAAI/bge-large-zh-v1.5",
            dimension=1024,
            context_length=512,
            description=_(
                "The embedding model is provided by SiliconFlow, supporting multiple "
                "languages and high-quality text embeddings."
            ),
        ),
        EmbeddingModelMetadata(
            model="BAAI/bge-large-en-v1.5",
            dimension=1024,
            context_length=512,
            description=_(
                "The embedding model is provided by SiliconFlow, supporting multiple "
                "languages and high-quality text embeddings."
            ),
        ),
    ],
)
