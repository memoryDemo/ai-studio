"""外部数据源连接器实现，负责接入图数据库和业务数据源。"""


import os
from enum import Enum
from typing import Optional


class DbInfo:
    """接口数据结构定义。"""

    def __init__(self, name, is_file_db: bool = False):
        """初始化实例。"""
        self.name = name
        self.is_file_db = is_file_db


class DBType(Enum):
    """枚举类型定义。"""

    MySQL = DbInfo("mysql")
    OceanBase = DbInfo("oceanbase")
    DuckDb = DbInfo("duckdb", True)
    SQLite = DbInfo("sqlite", True)
    Oracle = DbInfo("oracle")
    MSSQL = DbInfo("mssql")
    Postgresql = DbInfo("postgresql")
    GaussDB = DbInfo("gaussdb")
    Vertica = DbInfo("vertica")
    Clickhouse = DbInfo("clickhouse")
    StarRocks = DbInfo("starrocks")
    Spark = DbInfo("spark", True)
    Doris = DbInfo("doris")
    Hive = DbInfo("hive")
    TuGraph = DbInfo("tugraph")
    Neo4j = DbInfo("neo4j")

    def value(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self._value_.name

    def is_file_db(self) -> bool:
        """校验条件并返回判断结果。"""
        return self._value_.is_file_db

    @staticmethod
    def of_db_type(db_type: str) -> Optional["DBType"]:
        """执行当前函数对应的业务逻辑。"""
        for item in DBType:
            if item.value() == db_type:
                return item
        return None

    @staticmethod
    def parse_file_db_name_from_path(db_type: str, local_db_path: str):
        """解析输入并返回标准结果。"""
        base_name = os.path.basename(local_db_path)
        db_name = os.path.splitext(base_name)[0]
        if "." in db_name:
            db_name = os.path.splitext(db_name)[0]
        return db_type + "_" + db_name
