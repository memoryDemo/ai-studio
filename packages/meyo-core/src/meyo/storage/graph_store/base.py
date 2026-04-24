"""图存储基础抽象，为知识图谱和图数据库扩展提供统一接口。"""


import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from meyo.util import BaseParameters, RegisterParameters

logger = logging.getLogger(__name__)


@dataclass
class GraphStoreConfig(BaseParameters, RegisterParameters):
    """配置参数定义。"""

    __cfg_type__ = "graph_store"

    # 代码说明。
    # 集合相关操作。
    # 代码说明。
    # )
    # 向量生成配置。
    # 默认配置说明。
    # 向量生成配置。
    # )
    # 摘要配置。
    # 默认配置说明。
    # 摘要配置。
    # )
    # 执行检索。
    # 默认配置说明。
    # 执行检索。
    # )


class GraphStoreBase(ABC):
    """存储能力实现。"""

    def __init__(self, config: GraphStoreConfig):
        """初始化实例。"""
        self._config = config
        self._conn = None
        self.enable_summary = config.enable_summary
        self.enable_similarity_search = config.enable_similarity_search

    @abstractmethod
    def get_config(self) -> GraphStoreConfig:
        """获取对应数据。"""

    def is_exist(self, name) -> bool:
        """校验条件并返回判断结果。"""
        raise NotImplementedError
