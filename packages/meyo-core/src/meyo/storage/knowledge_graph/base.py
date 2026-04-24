"""知识图谱存储抽象，为后续检索增强和知识管理能力提供结构化接口。"""


import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from pydantic import Field

from meyo.core import Chunk, Embeddings
from meyo.storage.base import IndexStoreBase, IndexStoreConfig
from meyo.storage.graph_store.graph import Graph
from meyo.util import RegisterParameters

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeGraphConfig(IndexStoreConfig, RegisterParameters):
    """配置参数定义。"""

    __cfg_type__ = "graph_store"


class KnowledgeGraphBase(IndexStoreBase, ABC):
    """当前类的职责定义。"""

    @abstractmethod
    def get_config(self) -> KnowledgeGraphConfig:
        """获取对应数据。"""

    @property
    def embeddings(self) -> Embeddings:
        """生成向量结果。"""
        raise NotImplementedError

    @abstractmethod
    def query_graph(self, limit: Optional[int] = None) -> Graph:
        """执行查询并返回结果。"""

    @abstractmethod
    def delete_by_ids(self, ids: str) -> List[str]:
        """删除对应数据。"""


class ParagraphChunk(Chunk):
    """当前类的职责定义。"""

    chunk_parent_id: str = Field(default=None, description="id of parent chunk")
    chunk_parent_name: str = Field(default=None, description="parent chunk name")
    parent_content: str = Field(default=None, description="parent chunk text content")
    parent_is_document: bool = Field(
        default=False, description="is parent chunk a document"
    )
