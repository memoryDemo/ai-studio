"""存储层基础模块，统一缓存、向量库、图库和知识库相关接口。"""


import asyncio
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import Executor, ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional

from meyo.core import Chunk
from meyo.storage.vector_store.filters import MetadataFilters
from meyo.util import BaseParameters
from meyo.util.executor_utils import blocking_func_to_async_no_executor

logger = logging.getLogger(__name__)


@dataclass
class IndexStoreConfig(BaseParameters):
    """配置参数定义。"""

    def create_store(self, **kwargs) -> "IndexStoreBase":
        """创建对象实例。"""
        raise NotImplementedError("Current index store does not support create_store")


class IndexStoreBase(ABC):
    """存储能力实现。"""

    def __init__(
        self,
        executor: Optional[Executor] = None,
        max_chunks_once_load: Optional[int] = None,
        max_threads: Optional[int] = None,
    ):
        """初始化实例。"""
        self._executor = executor or ThreadPoolExecutor()
        self._max_chunks_once_load = max_chunks_once_load or 10
        self._max_threads = max_threads or 1

    @abstractmethod
    def get_config(self) -> IndexStoreConfig:
        """获取对应数据。"""

    @abstractmethod
    def load_document(self, chunks: List[Chunk]) -> List[str]:
        """加载数据或资源。"""

    @abstractmethod
    async def aload_document(
        self, chunks: List[Chunk], file_id: Optional[str] = None
    ) -> List[str]:
        """执行当前函数对应的业务逻辑。"""

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

    @abstractmethod
    def truncate(self) -> List[str]:
        """执行调用逻辑。"""

    @abstractmethod
    def delete_vector_name(self, index_name: str):
        """删除对应数据。"""

    def vector_name_exists(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return True

    def load_document_with_limit(
        self,
        chunks: List[Chunk],
        max_chunks_once_load: Optional[int] = None,
        max_threads: Optional[int] = None,
    ) -> List[str]:
        """加载数据或资源。"""
        max_chunks_once_load = max_chunks_once_load or self._max_chunks_once_load
        max_threads = max_threads or self._max_threads
        # 代码说明。
        chunk_groups = [
            chunks[i : i + max_chunks_once_load]
            for i in range(0, len(chunks), max_chunks_once_load)
        ]
        logger.info(
            f"Loading {len(chunks)} chunks in {len(chunk_groups)} groups with "
            f"{max_threads} threads."
        )
        ids = []
        loaded_cnt = 0
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            tasks = []
            for chunk_group in chunk_groups:
                tasks.append(executor.submit(self.load_document, chunk_group))
            for future in tasks:
                success_ids = future.result()
                ids.extend(success_ids)
                loaded_cnt += len(success_ids)
                logger.info(f"Loaded {loaded_cnt} chunks, total {len(chunks)} chunks.")
        logger.info(
            f"Loaded {len(chunks)} chunks in {time.time() - start_time} seconds"
        )
        return ids

    async def aload_document_with_limit(
        self,
        chunks: List[Chunk],
        max_chunks_once_load: Optional[int] = None,
        max_threads: Optional[int] = None,
        file_id: Optional[str] = None,
    ) -> List[str]:
        """执行当前函数对应的业务逻辑。"""
        max_chunks_once_load = max_chunks_once_load or self._max_chunks_once_load
        max_threads = max_threads or self._max_threads
        file_id = file_id or None
        chunk_groups = [
            chunks[i : i + max_chunks_once_load]
            for i in range(0, len(chunks), max_chunks_once_load)
        ]
        logger.info(
            f"Loading {len(chunks)} chunks in {len(chunk_groups)} groups with "
            f"{max_threads} threads."
        )
        tasks = []
        for chunk_group in chunk_groups:
            tasks.append(self.aload_document(chunk_group, file_id))

        results = await self._run_tasks_with_concurrency(tasks, max_threads)

        ids = []
        loaded_cnt = 0
        for idx, success_ids in enumerate(results):
            if isinstance(success_ids, Exception):
                raise RuntimeError(
                    f"Failed to load chunk group {idx + 1}: {str(success_ids)}"
                ) from success_ids
            ids.extend(success_ids)
            loaded_cnt += len(success_ids)
            logger.info(f"Loaded {loaded_cnt} chunks, total {len(chunks)} chunks.")

        return ids

    async def _run_tasks_with_concurrency(self, tasks, max_concurrent):
        results = []
        for i in range(0, len(tasks), max_concurrent):
            batch = tasks[i : i + max_concurrent]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        return results

    def similar_search(
        self, text: str, topk: int, filters: Optional[MetadataFilters] = None
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        return self.similar_search_with_scores(text, topk, 1.0, filters)

    async def asimilar_search(
        self,
        query: str,
        topk: int,
        filters: Optional[MetadataFilters] = None,
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        return await blocking_func_to_async_no_executor(
            self.similar_search, query, topk, filters
        )

    async def asimilar_search_with_scores(
        self,
        query: str,
        topk: int,
        score_threshold: float,
        filters: Optional[MetadataFilters] = None,
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        return await blocking_func_to_async_no_executor(
            self.similar_search_with_scores, query, topk, score_threshold, filters
        )

    def full_text_search(
        self, text: str, topk: int, filters: Optional[MetadataFilters] = None
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        raise NotImplementedError(
            "Full text search is not supported in this index store."
        )

    async def afull_text_search(
        self, text: str, topk: int, filters: Optional[MetadataFilters] = None
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        return await blocking_func_to_async_no_executor(
            self.full_text_search, text, topk, filters
        )

    def is_support_full_text_search(self) -> bool:
        """执行查询并返回结果。"""
        logger.warning("Full text search is not supported in this index store.")
        return False
