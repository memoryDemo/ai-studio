"""外部数据源连接器实现，负责接入图数据库和业务数据源。"""


import json
from dataclasses import dataclass, field
from typing import Dict, Generator, Iterator, List, Type, cast

from meyo.model.resource import (
    TAGS_ORDER_HIGH,
    ResourceCategory,
    auto_register_resource,
)
from meyo.datasource.base import BaseConnector
from meyo.datasource.parameter import BaseDatasourceParameters
from meyo.util.i18n_utils import _


@auto_register_resource(
    label=_("TuGraph datasource"),
    category=ResourceCategory.DATABASE,
    tags={"order": TAGS_ORDER_HIGH},
    description=_(
        "TuGraph is a high-performance graph database jointly developed by Ant Group "
        "and Tsinghua University."
    ),
)
@dataclass
class TuGraphParameters(BaseDatasourceParameters):
    """配置参数定义。"""

    __type__ = "tugraph"

    host: str = field(metadata={"help": _("TuGraph server host")})
    user: str = field(metadata={"help": _("TuGraph server user")})
    password: str = field(
        default="${env:MEYO_DB_PASSWORD}",
        metadata={
            "help": _(
                "Database password, you can write your password directly, of course, "
                "you can also use environment variables, such as "
                "${env:MEYO_DB_PASSWORD}"
            ),
            "tags": "privacy",
        },
    )
    port: int = field(
        default=7687, metadata={"help": _("TuGraph server port, default 7687")}
    )
    database: str = field(
        default="default", metadata={"help": _("Database name, default 'default'")}
    )

    def create_connector(self) -> "BaseConnector":
        """创建对象实例。"""
        return TuGraphConnector.from_parameters(self)

    def db_url(self, ssl=False, charset=None):
        """执行当前函数对应的业务逻辑。"""
        raise NotImplementedError("TuGraph does not support db_url")


class TuGraphConnector(BaseConnector):
    """外部服务连接和调用实现。"""

    db_type: str = "tugraph"
    driver: str = "bolt"
    dialect: str = "tugraph"

    def __init__(self, driver, graph):
        """初始化实例。"""
        self._driver = driver
        self._schema = None
        self._graph = graph
        self._session = None
        self._is_closed = False

    def create_graph(self, graph_name: str) -> bool:
        """创建对象实例。"""
        try:
            with self._driver.session(database="default") as session:
                graph_list = session.run("CALL dbms.graph.listGraphs()").data()
                exists = any(item["graph_name"] == graph_name for item in graph_list)
                if not exists:
                    session.run(
                        f"CALL dbms.graph.createGraph('{graph_name}', '', 2048)"
                    )
        except Exception as e:
            raise Exception(f"Failed to create graph '{graph_name}': {str(e)}") from e

        return not exists

    def is_exist(self, graph_name: str) -> bool:
        """校验条件并返回判断结果。"""
        try:
            with self._driver.session(database="default") as session:
                graph_list = session.run("CALL dbms.graph.listGraphs()").data()
                exists = any(item["graph_name"] == graph_name for item in graph_list)
        except Exception as e:
            raise Exception(
                f"Failed to check graph exist'{graph_name}': {str(e)}"
            ) from e

        return exists

    def delete_graph(self, graph_name: str) -> None:
        """删除对应数据。"""
        with self._driver.session(database="default") as session:
            graph_list = session.run("CALL dbms.graph.listGraphs()").data()
            exists = any(item["graph_name"] == graph_name for item in graph_list)
            if exists:
                session.run(f"Call dbms.graph.deleteGraph('{graph_name}')")

    @classmethod
    def param_class(cls) -> Type[TuGraphParameters]:
        """执行当前函数对应的业务逻辑。"""
        return TuGraphParameters

    @classmethod
    def from_parameters(cls, parameters: TuGraphParameters) -> "TuGraphConnector":
        """根据输入参数创建对象。"""
        return cls.from_uri_db(
            parameters.host,
            parameters.port,
            parameters.user,
            parameters.password,
            parameters.database,
        )

    @classmethod
    def from_uri_db(
        cls, host: str, port: int, user: str, pwd: str, db_name: str
    ) -> "TuGraphConnector":
        """根据输入参数创建对象。"""
        try:
            from neo4j import GraphDatabase

            db_url = f"{cls.driver}://{host}:{str(port)}"
            driver = GraphDatabase.driver(db_url, auth=(user, pwd))
            driver.verify_connectivity()
            return cast(TuGraphConnector, cls(driver=driver, graph=db_name))

        except ImportError as err:
            raise ImportError(
                "neo4j package is not installed, please install it with "
                "`pip install neo4j`"
            ) from err

    def get_system_info(self) -> Dict:
        """获取对应数据。"""
        with self._driver.session(database="default") as session:
            system_info_list = session.run("CALL dbms.system.info()")
            system_info = {}
            for info in system_info_list:
                system_info[info["name"]] = info["value"]
            return system_info

    def get_table_names(self) -> Iterator[str]:
        """获取对应数据。"""
        with self._driver.session(database=self._graph) as session:
            # 执行查询。
            raw_vertex_labels = session.run("CALL db.vertexLabels()").data()
            vertex_labels = [
                table_name["label"] + "_vertex" for table_name in raw_vertex_labels
            ]

            # 执行查询。
            raw_edge_labels = session.run("CALL db.edgeLabels()").data()
            edge_labels = [
                table_name["label"] + "_edge" for table_name in raw_edge_labels
            ]

            return iter(vertex_labels + edge_labels)

    def get_grants(self):
        """获取对应数据。"""
        return []

    def get_collation(self):
        """获取对应数据。"""
        return "UTF-8"

    def get_charset(self):
        """获取对应数据。"""
        return "UTF-8"

    def table_simple_info(self):
        """执行当前函数对应的业务逻辑。"""
        return []

    def close(self):
        """关闭或停止资源。"""
        if self._is_closed:
            return
        self._driver.close()
        self._is_closed = True

    def run(self, query: str, fetch: str = "all") -> List:
        """执行调用逻辑。"""
        with self._driver.session(database=self._graph) as session:
            try:
                result = session.run(query)
                return list(result)
            except Exception as e:
                raise Exception(f"Query execution failed: {e}\nQuery: {query}") from e

    def run_stream(self, query: str) -> Generator:
        """执行调用逻辑。"""
        with self._driver.session(database=self._graph) as session:
            result = session.run(query)
            yield from result

    def get_columns(self, table_name: str, table_type: str = "vertex") -> List[Dict]:
        """获取对应数据。"""
        with self._driver.session(database=self._graph) as session:
            data = []
            result = None
            if table_type == "vertex":
                result = session.run(f"CALL db.getVertexSchema('{table_name}')").data()
            else:
                result = session.run(f"CALL db.getEdgeSchema('{table_name}')").data()
            schema_info = json.loads(result[0]["schema"])
            for prop in schema_info.get("properties", []):
                prop_dict = {
                    "name": prop["name"],
                    "type": prop["type"],
                    "default_expression": "",
                    "is_in_primary_key": bool(
                        "primary" in schema_info
                        and prop["name"] == schema_info["primary"]
                    ),
                    "comment": prop["name"],
                }
                data.append(prop_dict)
            return data

    def get_indexes(self, table_name: str, table_type: str = "vertex") -> List[Dict]:
        """获取对应数据。"""
        # 代码说明。
        with self._driver.session(database=self._graph) as session:
            result = session.run(
                f"CALL db.listLabelIndexes('{table_name}','{table_type}')"
            ).data()
            transformed_data = []
            for item in result:
                new_dict = {"name": item["field"], "column_names": [item["field"]]}
                transformed_data.append(new_dict)
            return transformed_data

    @classmethod
    def is_graph_type(cls) -> bool:
        """校验条件并返回判断结果。"""
        return True
