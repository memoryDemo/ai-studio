"""全文检索存储抽象，为后续知识库检索能力预留统一接口。"""


import logging
from abc import abstractmethod
from concurrent.futures import Executor
from typing import List, Optional

from meyo.core import Chunk
from meyo.storage.base import IndexStoreBase
from meyo.storage.vector_store.filters import MetadataFilters
from meyo.util.executor_utils import blocking_func_to_async

logger = logging.getLogger(__name__)


class FullTextStoreBase(IndexStoreBase):
    """存储能力实现。"""

    def __init__(self, executor: Optional[Executor] = None):
        """初始化实例。"""
        super().__init__(executor)

    def is_support_full_text_search(self) -> bool:
        # 重写，新增抽象类
        """执行查询并返回结果。"""
        return True  # 全文检索存储类应该始终支持全文检索

    def full_text_search(
        self, text: str, topk: int, filters: Optional[MetadataFilters] = None
    ) -> List[Chunk]:
        # 重写，新增抽象类
        """执行查询并返回结果。"""
        # 执行检索。
        # 或者子类需要实现具体的全文检索逻辑

        return self.similar_search_with_scores(
            text, topk, score_threshold=0.0, filters=filters
        )

    @abstractmethod
    def load_document(self, chunks: List[Chunk]) -> List[str]:
        """加载数据或资源。"""

    async def aload_document(
        self, chunks: List[Chunk], file_id: Optional[str] = None
    ) -> List[str]:
        """执行当前函数对应的业务逻辑。"""
        return await blocking_func_to_async(self._executor, self.load_document, chunks)

    @abstractmethod
    def similar_search_with_scores(
        self,
        text,
        topk,
        score_threshold: float,
        filters: Optional[MetadataFilters] = None,
    ) -> List[Chunk]:
        """执行查询并返回结果。"""

    @abstractmethod
    def delete_by_ids(self, ids: str) -> List[str]:
        """删除对应数据。"""

    def delete_vector_name(self, index_name: str):
        """删除对应数据。"""

    def truncate(self) -> List[str]:
        """执行调用逻辑。"""
        raise NotImplementedError
