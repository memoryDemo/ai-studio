"""图存储基础抽象，为知识图谱和图数据库扩展提供统一接口。"""


import base64
import json
import logging
import os
from dataclasses import dataclass, field
from typing import List

from meyo.model.resource import Parameter, ResourceCategory, register_resource
from meyo.storage.graph_store.base import GraphStoreBase, GraphStoreConfig
from meyo.storage.graph_store.graph import GraphElemType
from meyo.util.i18n_utils import _
from meyo_ext.datasource.conn_tugraph import TuGraphConnector

logger = logging.getLogger(__name__)


@register_resource(
    _("TuGraph Graph Config"),
    "tugraph_config",
    category=ResourceCategory.KNOWLEDGE_GRAPH,
    description=_("TuGraph config."),
    parameters=[
        Parameter.build_from(
            _("host"),
            "host",
            str,
            optional=True,
            default="127.0.0.1",
            description=_("TuGraph host"),
        ),
        Parameter.build_from(
            _("port"),
            "port",
            int,
            optional=True,
            default="7687",
            description=_("TuGraph port"),
        ),
        Parameter.build_from(
            _("username"),
            "username",
            str,
            optional=True,
            default="admin",
            description=_("TuGraph username"),
        ),
        Parameter.build_from(
            _("password"),
            "password",
            str,
            optional=True,
            default="73@TuGraph",
            description=_("TuGraph password"),
        ),
    ],
)
@dataclass
class TuGraphStoreConfig(GraphStoreConfig):
    """配置参数定义。"""

    __type__ = "tugraph"

    host: str = field(
        default="127.0.0.1",
        metadata={
            "description": "TuGraph host",
        },
    )
    port: int = field(
        default=7687,
        metadata={
            "description": "TuGraph port",
        },
    )
    username: str = field(
        default="admin",
        metadata={
            "description": "login username",
        },
    )
    password: str = field(
        default="73@TuGraph",
        metadata={
            "description": "login password",
        },
    )
    vertex_type: str = field(
        default=GraphElemType.ENTITY.value,
        metadata={
            "description": "The type of vertex, `entity` by default.",
        },
    )
    document_type: str = field(
        default=GraphElemType.DOCUMENT.value,
        metadata={
            "description": "The type of document vertex, `document` by default.",
        },
    )
    chunk_type: str = field(
        default=GraphElemType.CHUNK.value,
        metadata={
            "description": "The type of chunk vertex, `relation` by default.",
        },
    )
    edge_type: str = field(
        default=GraphElemType.RELATION.value,
        metadata={
            "description": "The type of relation edge, `relation` by default.",
        },
    )
    include_type: str = field(
        default=GraphElemType.INCLUDE.value,
        metadata={
            "description": "The type of include edge, `include` by default.",
        },
    )
    next_type: str = field(
        default=GraphElemType.NEXT.value,
        metadata={
            "description": "The type of next edge, `next` by default.",
        },
    )
    plugin_names: List[str] = field(
        default_factory=lambda: ["leiden"],
        metadata={
            "description": "The list of plugin names to be uploaded to the database.",
        },
    )
    enable_summary: bool = field(
        default=True,
        metadata={
            "description": "Enable graph community summary or not.",
        },
    )
    enable_similarity_search: bool = field(
        default=False,
        metadata={
            "description": "Enable the similarity search or not",
        },
    )


class TuGraphStore(GraphStoreBase):
    """存储能力实现。"""

    def __init__(self, config: TuGraphStoreConfig) -> None:
        """初始化实例。"""
        self._config = config
        self._host = config.host or os.getenv("TUGRAPH_HOST")
        self._port = int(config.port or os.getenv("TUGRAPH_PORT"))
        self._username = config.username or os.getenv("TUGRAPH_USERNAME")
        self._password = config.password or os.getenv("TUGRAPH_PASSWORD")
        self.enable_summary = config.enable_summary or (
            os.getenv("GRAPH_COMMUNITY_SUMMARY_ENABLED", "").lower() == "true"
        )
        self.enable_similarity_search = config.enable_similarity_search or (
            os.getenv("SIMILARITY_SEARCH_ENABLED", "").lower() == "true"
        )
        self._plugin_names = config.plugin_names or (
            os.getenv("TUGRAPH_PLUGIN_NAMES", "leiden").split(",")
        )

        self._graph_name = config.name

        self.conn = TuGraphConnector.from_uri_db(
            host=self._host,
            port=self._port,
            user=self._username,
            pwd=self._password,
            db_name=config.name,
        )

    def get_config(self) -> TuGraphStoreConfig:
        """获取对应数据。"""
        return self._config

    def is_exist(self, name) -> bool:
        """校验条件并返回判断结果。"""
        return self.conn.is_exist(name)

    def _add_vertex_index(self, field_name):
        """执行当前函数对应的业务逻辑。"""
        # 待办事项。
        gql = f"CALL db.addIndex('{GraphElemType.ENTITY.value}', '{field_name}', false)"
        self.conn.run(gql)

    def _upload_plugin(self):
        """执行当前函数对应的业务逻辑。"""
        gql = "CALL db.plugin.listPlugin('CPP','v1')"
        result = self.conn.run(gql)
        result_names = [
            json.loads(record["plugin_description"])["name"] for record in result
        ]
        missing_plugins = [
            name for name in self._plugin_names if name not in result_names
        ]

        if len(missing_plugins):
            for name in missing_plugins:
                try:
                    from dbgpt_tugraph_plugins import (  # type: ignore
                        get_plugin_binary_path,
                    )
                except ImportError:
                    logger.error(
                        "meyo-tugraph-plugins is not installed, "
                        "pip install dbgpt-tugraph-plugins==0.1.1"
                    )
                plugin_path = get_plugin_binary_path("leiden")  # type: ignore
                with open(plugin_path, "rb") as f:
                    content = f.read()
                content = base64.b64encode(content).decode()
                gql = (
                    f"CALL db.plugin.loadPlugin('CPP', '{name}', '{content}', 'SO', "
                    f"'{name} Plugin', false, 'v1')"
                )
                self.conn.run(gql)
