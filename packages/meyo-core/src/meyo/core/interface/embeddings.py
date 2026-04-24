"""向量生成基础接口定义，统一向量模型的调用协议。"""


import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union

from meyo.util.annotations import PublicAPI
from meyo.util.parameter_utils import BaseParameters

from .parameter import EmbeddingDeployModelParameters, RerankerDeployModelParameters


@dataclass
@PublicAPI(stability="beta")
class EmbeddingModelMetadata(BaseParameters):
    """向量生成或重排能力实现。"""

    model: Union[str, List[str]] = field(
        metadata={"help": "Model name"},
    )
    label: Optional[str] = field(
        default=None,
        metadata={"help": "Model label"},
    )
    dimension: Optional[int] = field(
        default=None,
        metadata={"help": "Model dimension"},
    )
    context_length: Optional[int] = field(
        default=None,
        metadata={"help": "Context length of model"},
    )
    description: Optional[str] = field(
        default=None,
        metadata={"help": "Model description"},
    )
    link: Optional[str] = field(
        default=None,
        metadata={"help": "Model link"},
    )
    metadata: Optional[Dict[str, Any]] = field(
        default_factory=dict,
        metadata={"help": "Model metadata"},
    )
    is_reranker: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether the model is a reranker model"},
    )
    languages: Optional[List[str]] = field(
        default=None,
        metadata={"help": "Model language, e.g. ['en', 'zh']"},
    )


class RerankEmbeddings(ABC):
    """向量生成或重排能力实现。"""

    @classmethod
    def param_class(cls) -> Type[RerankerDeployModelParameters]:
        """执行当前函数对应的业务逻辑。"""
        return RerankerDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: RerankerDeployModelParameters
    ) -> "RerankEmbeddings":
        """根据输入参数创建对象。"""
        raise NotImplementedError

    @classmethod
    def _match(
        cls, provider: str, lower_model_name_or_path: Optional[str] = None
    ) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return cls.param_class().get_type_value() == provider

    @abstractmethod
    def predict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""

    async def apredict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.predict, query, candidates
        )


class Embeddings(ABC):
    """向量生成或重排能力实现。"""

    @classmethod
    def param_class(cls) -> Type[EmbeddingDeployModelParameters]:
        """执行当前函数对应的业务逻辑。"""
        return EmbeddingDeployModelParameters

    @classmethod
    def from_parameters(
        cls, parameters: EmbeddingDeployModelParameters
    ) -> "Embeddings":
        """根据输入参数创建对象。"""
        raise NotImplementedError

    @classmethod
    def _match(
        cls, provider: str, lower_model_name_or_path: Optional[str] = None
    ) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return cls.param_class().get_type_value() == provider

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed_documents, texts
        )

    async def aembed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        return await asyncio.get_running_loop().run_in_executor(
            None, self.embed_query, text
        )
