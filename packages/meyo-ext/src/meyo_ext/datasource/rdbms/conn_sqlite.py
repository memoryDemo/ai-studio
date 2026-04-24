"""外部关系型数据库连接器实现，负责把具体数据库接入统一数据源接口。"""


import dataclasses
import logging
import os
import tempfile
from typing import Any, Iterable, List, Optional, Tuple, Type

from sqlalchemy import create_engine, text

from meyo.model.resource import (
    TAGS_ORDER_HIGH,
    ResourceCategory,
    auto_register_resource,
)
from meyo.datasource.parameter import BaseDatasourceParameters
from meyo.datasource.rdbms.base import RDBMSConnector
from meyo.util.i18n_utils import _

logger = logging.getLogger(__name__)


@auto_register_resource(
    label=_("SQLite datasource"),
    category=ResourceCategory.DATABASE,
    tags={"order": TAGS_ORDER_HIGH},
    description=_(
        "Lightweight embedded relational database with simplicity and portability."
    ),
)
@dataclasses.dataclass
class SQLiteConnectorParameters(BaseDatasourceParameters):
    """配置参数定义。"""

    __type__ = "sqlite"

    path: str = dataclasses.field(
        metadata={
            "help": _(
                "SQLite database file path. Use ':memory:' for in-memory database"
            ),
            "required": True,
        }
    )
    check_same_thread: bool = dataclasses.field(
        default=False,
        metadata={
            "help": _(
                "Check same thread or not, default is False. Set False to allow "
                "sharing connection across threads"
            )
        },
    )

    driver: str = dataclasses.field(
        default="sqlite", metadata={"help": _("Driver name, default is sqlite")}
    )

    def create_connector(self) -> "SQLiteConnector":
        """创建对象实例。"""
        return SQLiteConnector.from_parameters(self)

    def db_url(self, ssl: bool = False, charset: Optional[str] = None):
        return f"{self.driver}:///{self.path}"


class SQLiteConnector(RDBMSConnector):
    """外部服务连接和调用实现。"""

    db_type: str = "sqlite"
    db_dialect: str = "sqlite"

    @classmethod
    def param_class(cls) -> Type[SQLiteConnectorParameters]:
        """执行当前函数对应的业务逻辑。"""
        return SQLiteConnectorParameters

    @classmethod
    def from_parameters(
        cls, parameters: SQLiteConnectorParameters
    ) -> "SQLiteConnector":
        """根据输入参数创建对象。"""
        _engine_args = {
            "connect_args": {"check_same_thread": parameters.check_same_thread}
        }
        return cls(create_engine(f"sqlite:///{parameters.path}", **_engine_args))

    @classmethod
    def from_file_path(
        cls, file_path: str, engine_args: Optional[dict] = None, **kwargs: Any
    ) -> "SQLiteConnector":
        """根据输入参数创建对象。"""
        _engine_args = engine_args or {}
        _engine_args["connect_args"] = {"check_same_thread": False}
        # 代码说明。
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return cls(create_engine("sqlite:///" + file_path, **_engine_args), **kwargs)

    def get_indexes(self, table_name):
        """获取对应数据。"""
        with self.session_scope() as session:
            cursor = session.execute(text(f"PRAGMA index_list({table_name})"))
            indexes = cursor.fetchall()
            result = []
            for idx in indexes:
                index_name = idx[1]
                cursor = session.execute(text(f"PRAGMA index_info({index_name})"))
                index_infos = cursor.fetchall()
                column_names = [index_info[2] for index_info in index_infos]
                result.append({"name": index_name, "column_names": column_names})
            return result

    def get_show_create_table(self, table_name):
        """获取对应数据。"""
        with self.session_scope() as session:
            cursor = session.execute(
                text(
                    "SELECT sql FROM sqlite_master WHERE type='table' "
                    f"AND name='{table_name}'"
                )
            )
            ans = cursor.fetchall()
            return ans[0][0]

    def get_fields(self, table_name, db_name=None) -> List[Tuple]:
        """获取对应数据。"""
        with self.session_scope() as session:
            cursor = session.execute(text(f"PRAGMA table_info('{table_name}')"))
            fields = cursor.fetchall()
            logger.info(fields)
            return [
                (field[1], field[2], field[3], field[4], field[5]) for field in fields
            ]

    def get_simple_fields(self, table_name):
        """获取对应数据。"""
        return self.get_fields(table_name)

    def get_users(self):
        """获取对应数据。"""
        return []

    def get_grants(self):
        """获取对应数据。"""
        return []

    def get_collation(self):
        """获取对应数据。"""
        return "UTF-8"

    def get_charset(self):
        """获取对应数据。"""
        return "UTF-8"

    def get_database_names(self):
        """获取对应数据。"""
        return []

    def _sync_tables_from_db(self) -> Iterable[str]:
        """执行当前函数对应的业务逻辑。"""
        with self.session_scope() as session:
            table_results = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            view_results = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='view'")
            )
            table_results = set(row[0] for row in table_results)  # noqa
            view_results = set(row[0] for row in view_results)  # noqa
            self._all_tables = table_results.union(view_results)
            self._metadata.reflect(bind=self._engine)
            return self._all_tables

    def _write(self, write_sql):
        logger.info(f"Write[{write_sql}]")
        with self.session_scope() as session:
            result = session.execute(text(write_sql))
            # 待办事项。
            # 获取对应数据。
            logger.info(f"SQL[{write_sql}], result:{result.rowcount}")
            return result.rowcount

    def get_table_comments(self, db_name=None):
        """获取对应数据。"""
        with self.session_scope() as session:
            cursor = session.execute(
                text(
                    """
                    SELECT name, sql FROM sqlite_master WHERE type='table'
                    """
                )
            )
            table_comments = cursor.fetchall()
            return [
                (table_comment[0], table_comment[1]) for table_comment in table_comments
            ]

    def get_current_db_name(self) -> str:
        """获取对应数据。"""
        full_path = self._engine.url.database
        db_name = os.path.basename(full_path)
        if db_name.endswith(".db"):
            db_name = db_name[:-3]
        return db_name

    def table_simple_info(self) -> Iterable[str]:
        """执行当前函数对应的业务逻辑。"""
        _tables_sql = """
                SELECT name FROM sqlite_master WHERE type='table'
            """
        with self.session_scope() as session:
            cursor = session.execute(text(_tables_sql))
            tables_results = cursor.fetchall()
            results = []
            for row in tables_results:
                table_name = row[0]
                _sql = f"""
                    PRAGMA  table_info({table_name})
                """
                cursor_colums = session.execute(text(_sql))
                colum_results = cursor_colums.fetchall()
                table_colums = []
                for row_col in colum_results:
                    field_info = list(row_col)
                    table_colums.append(field_info[1])

                results.append(f"{table_name}({','.join(table_colums)});")
            return results


class SQLiteTempConnector(SQLiteConnector):
    """外部服务连接和调用实现。"""

    def __init__(self, engine, temp_file_path, *args, **kwargs):
        """初始化实例。"""
        super().__init__(engine, *args, **kwargs)
        self.temp_file_path = temp_file_path

    @classmethod
    def create_temporary_db(
        cls, engine_args: Optional[dict] = None, **kwargs: Any
    ) -> "SQLiteTempConnector":
        """创建对象实例。"""
        _engine_args = engine_args or {}
        _engine_args["connect_args"] = {"check_same_thread": False}

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        temp_file.close()

        engine = create_engine(f"sqlite:///{temp_file_path}", **_engine_args)
        return cls(engine, temp_file_path, **kwargs)

    def close(self):
        """关闭或停止资源。"""
        try:
            if os.path.exists(self.temp_file_path):
                os.remove(self.temp_file_path)
            super().close()
        except Exception as e:
            logger.error(f"Error removing temporary database file: {e}")

    def create_temp_tables(self, tables_info):
        """创建对象实例。"""
        with self.session_scope() as session:
            for table_name, table_data in tables_info.items():
                columns = ", ".join(
                    [f"{col} {dtype}" for col, dtype in table_data["columns"].items()]
                )
                create_sql = f"CREATE TABLE {table_name} ({columns});"
                session.execute(text(create_sql))
                for row in table_data.get("data", []):
                    placeholders = ", ".join(
                        [":param" + str(index) for index, _ in enumerate(row)]
                    )
                    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders});"

                    param_dict = {
                        "param" + str(index): value for index, value in enumerate(row)
                    }
                    session.execute(text(insert_sql), param_dict)
                session.commit()
            self._sync_tables_from_db()

    def __enter__(self):
        """执行当前函数对应的业务逻辑。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """执行当前函数对应的业务逻辑。"""
        self.close()

    def __del__(self):
        """执行当前函数对应的业务逻辑。"""
        self.close()

    @classmethod
    def is_normal_type(cls) -> bool:
        """校验条件并返回判断结果。"""
        return False
