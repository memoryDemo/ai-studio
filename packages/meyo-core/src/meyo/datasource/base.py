"""数据源基础抽象，定义外部数据连接器的统一生命周期和调用接口。"""


from abc import ABC, abstractmethod
from typing import Dict, Iterable, List, Optional, Tuple, Type, TypeVar

from .parameter import BaseDatasourceParameters  # noqa: F401

C = TypeVar("C", bound="BaseDatasourceParameters")
T = TypeVar("T", bound="BaseConnector")


class BaseConnector(ABC):
    """外部服务连接和调用实现。"""

    db_type: str = "__abstract__db_type__"
    driver: str = ""

    @classmethod
    def param_class(cls) -> Type[C]:
        """执行当前函数对应的业务逻辑。"""

    @classmethod
    def from_parameters(cls, parameters: C) -> T:
        """根据输入参数创建对象。"""
        raise NotImplementedError("Current connector does not support from_parameters")

    @property
    def db_url(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        raise NotImplementedError("Current connector does not support db_url")

    def get_table_names(self) -> Iterable[str]:
        """获取对应数据。"""
        raise NotImplementedError("Current connector does not support get_table_names")

    def get_table_info(self, table_names: Optional[List[str]] = None) -> str:
        """获取对应数据。"""
        raise NotImplementedError("Current connector does not support get_table_info")

    def get_index_info(self, table_names: Optional[List[str]] = None) -> str:
        """获取对应数据。"""
        raise NotImplementedError("Current connector does not support get_index_info")

    def get_example_data(self, table: str, count: int = 3):
        """获取对应数据。"""
        raise NotImplementedError("Current connector does not support get_example_data")

    def get_database_names(self) -> List[str]:
        """获取对应数据。"""
        raise NotImplementedError(
            "Current connector does not support get_database_names"
        )

    def get_table_comments(self, db_name: str) -> List[Tuple[str, str]]:
        """获取对应数据。"""
        raise NotImplementedError(
            "Current connector does not support get_table_comments"
        )

    def get_table_comment(self, table_name: str) -> Dict:
        """获取对应数据。"""
        raise NotImplementedError(
            "Current connector does not support get_table_comment"
        )

    def get_columns(self, table_name: str) -> List[Dict]:
        """获取对应数据。"""
        raise NotImplementedError("Current connector does not support get_columns")

    def get_column_comments(self, db_name: str, table_name: str):
        """获取对应数据。"""
        raise NotImplementedError(
            "Current connector does not support get_column_comments"
        )

    @abstractmethod
    def run(self, command: str, fetch: str = "all") -> List:
        """执行调用逻辑。"""

    def run_to_df(self, command: str, fetch: str = "all"):
        """执行调用逻辑。"""
        raise NotImplementedError("Current connector does not support run_to_df")

    def get_users(self) -> List[Tuple[str, str]]:
        """获取对应数据。"""
        return []

    def get_grants(self) -> List[Tuple]:
        """获取对应数据。"""
        return []

    def get_collation(self) -> Optional[str]:
        """获取对应数据。"""
        return None

    def get_charset(self) -> str:
        """获取对应数据。"""
        return "utf-8"

    def get_fields(self, table_name: str) -> List[Tuple]:
        """获取对应数据。"""
        raise NotImplementedError("Current connector does not support get_fields")

    def get_simple_fields(self, table_name: str) -> List[Tuple]:
        """获取对应数据。"""
        return self.get_fields(table_name)

    def get_show_create_table(self, table_name: str) -> str:
        """获取对应数据。"""
        raise NotImplementedError(
            "Current connector does not support get_show_create_table"
        )

    def get_indexes(self, table_name: str) -> List[Dict]:
        """获取对应数据。"""
        raise NotImplementedError("Current connector does not support get_indexes")

    @classmethod
    def is_normal_type(cls) -> bool:
        """校验条件并返回判断结果。"""
        return True

    @classmethod
    def is_graph_type(cls) -> bool:
        """校验条件并返回判断结果。"""
        return False

    def close(self):
        """关闭或停止资源。"""

    def __enter__(self):
        """执行当前函数对应的业务逻辑。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """执行当前函数对应的业务逻辑。"""
        self.close()

    def __del__(self):
        """执行当前函数对应的业务逻辑。"""
        self.close()
