"""向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。"""


from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, List, Optional

from meyo.core import Chunk, Embeddings
from meyo.model.resource import Parameter, ResourceCategory, register_resource
from meyo.storage.vector_store.base import (
    _COMMON_PARAMETERS,
    _VECTOR_STORE_COMMON_PARAMETERS,
    VectorStoreBase,
    VectorStoreConfig,
)
from meyo.storage.vector_store.filters import MetadataFilters
from meyo.util import string_utils
from meyo.util.i18n_utils import _

logger = logging.getLogger(__name__)


@register_resource(
    _("Elastic Vector Config"),
    "elasticsearch_vector_config",
    category=ResourceCategory.VECTOR_STORE,
    parameters=[
        *_COMMON_PARAMETERS,
        Parameter.build_from(
            _("Uri"),
            "uri",
            str,
            description=_(
                "The uri of elasticsearch store, if not set, will use the default uri."
            ),
            optional=True,
            default="localhost",
        ),
        Parameter.build_from(
            _("Port"),
            "port",
            str,
            description=_(
                "The port of elasticsearch store, if not set, will use the default "
                "port."
            ),
            optional=True,
            default="9200",
        ),
        Parameter.build_from(
            _("Alias"),
            "alias",
            str,
            description=_(
                "The alias of elasticsearch store, if not set, will use the default "
                "alias."
            ),
            optional=True,
            default="default",
        ),
        Parameter.build_from(
            _("Index Name"),
            "index_name",
            str,
            description=_(
                "The index name of elasticsearch store, if not set, will use the "
                "default index name."
            ),
            optional=True,
            default="index_name_test",
        ),
    ],
    description=_("Elasticsearch vector config."),
)
@dataclass
class ElasticsearchStoreConfig(VectorStoreConfig):
    """配置参数定义。"""

    __type__ = "elasticsearch"

    uri: str = field(
        default="localhost",
        metadata={
            "description": "The uri of elasticsearch store, if not set, "
            "will use the default uri."
        },
    )
    port: str = field(
        default="9200",
        metadata={
            "description": "The port of elasticsearch store, if not set, will use the "
            "default port."
        },
    )

    alias: str = field(
        default="default",
        metadata={
            "description": "The alias of elasticsearch store, if not set, will use the "
            "default alias."
        },
    )
    index_name: str = field(
        default="index_name_test",
        metadata={
            "description": "The index name of elasticsearch store, if not set, will"
            " use "
            "the default index name."
        },
    )
    metadata_field: str = field(
        default="metadata",
        metadata={
            "description": "The metadata field of elasticsearch store, "
            "if not set, will "
            "use the default metadata field."
        },
    )
    secure: str = field(
        default="",
        metadata={
            "description": "The secure of elasticsearch store, i"
            "f not set, will use the "
            "default secure."
        },
    )

    def create_store(self, **kwargs) -> "ElasticStore":
        """创建对象实例。"""
        return ElasticStore(vector_store_config=self, **kwargs)


@register_resource(
    _("Elastic Vector Store"),
    "elastic_vector_store",
    category=ResourceCategory.VECTOR_STORE,
    description=_("Elastic vector store."),
    parameters=[
        Parameter.build_from(
            _("Elastic Config"),
            "vector_store_config",
            ElasticsearchStoreConfig,
            description=_("the elastic config of vector store."),
            optional=True,
            default=None,
        ),
        *_VECTOR_STORE_COMMON_PARAMETERS,
    ],
)
class ElasticStore(VectorStoreBase):
    """存储能力实现。"""

    def __init__(
        self,
        vector_store_config: ElasticsearchStoreConfig,
        name: Optional[str],
        embedding_fn: Optional[Embeddings] = None,
        max_chunks_once_load: Optional[int] = None,
        max_threads: Optional[int] = None,
    ) -> None:
        """初始化实例。"""
        super().__init__(
            max_chunks_once_load=max_chunks_once_load, max_threads=max_threads
        )
        self._vector_store_config = vector_store_config

        connect_kwargs = {}
        elasticsearch_vector_config = vector_store_config.to_dict()
        self.uri = os.getenv(
            "ELASTICSEARCH_URL", None
        ) or elasticsearch_vector_config.get("uri", "localhost")
        self.port = os.getenv(
            "ELASTICSEARCH_PORT", None
        ) or elasticsearch_vector_config.get("post", "9200")
        self.username = os.getenv(
            "ELASTICSEARCH_USERNAME"
        ) or elasticsearch_vector_config.get("user")
        self.password = os.getenv(
            "ELASTICSEARCH_PASSWORD"
        ) or elasticsearch_vector_config.get("password")

        self.collection_name = name
        # 将名称转换为十六进制形式。
        if string_utils.contains_chinese(self.collection_name):
            bytes_str = self.collection_name.encode("utf-8")
            hex_str = bytes_str.hex()
            self.collection_name = hex_str
        if embedding_fn is None:
            # 向量生成配置。
            # 检查条件是否满足。
            raise ValueError("embedding_fn is required for ElasticSearchStore")
        # 转换为小写。
        self.index_name = self.collection_name.lower()
        self.embedding: Embeddings = embedding_fn
        self.fields: List = []

        if (self.username is None) != (self.password is None):
            raise ValueError(
                "Both username and password must be set to use authentication for "
                "ElasticSearch"
            )

        if self.username:
            connect_kwargs["username"] = self.username
            connect_kwargs["password"] = self.password

        # 索引配置。
        self.index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,  # 副本数量。
            }
        }
        """"""
        try:
            from elasticsearch import Elasticsearch
            from langchain.vectorstores.elasticsearch import ElasticsearchStore
        except ImportError:
            raise ValueError(
                "Could not import langchain and elasticsearch python package. "
                "Please install it with `pip install langchain` and "
                "`pip install elasticsearch`."
            )
        try:
            # 这里同时检查空值和空字符串。
            # 读取不存在的配置键时会得到空值。
            # 代码说明。
            if self.username and self.password:
                self.es_client_python = Elasticsearch(
                    f"http://{self.uri}:{self.port}",
                    basic_auth=(self.username, self.password),
                )
                # 创建检索索引。
                self.create_collection(collection_name=self.index_name)
            else:
                logger.warning("ElasticSearch not set username and password")
                self.es_client_python = Elasticsearch(f"http://{self.uri}:{self.port}")
                self.create_collection(collection_name=self.index_name)
        except ConnectionError:
            logger.error("ElasticSearch connection failed")
        except Exception as e:
            logger.error(f"ElasticSearch connection failed : {e}")

        # 创建检索索引。
        try:
            if self.username and self.password:
                self.db_init = ElasticsearchStore(
                    es_url=f"http://{self.uri}:{self.port}",
                    index_name=self.index_name,
                    query_field="context",
                    vector_query_field="dense_vector",
                    embedding=self.embedding,  # type: ignore
                    es_user=self.username,
                    es_password=self.password,
                )
            else:
                logger.warning("ElasticSearch not set username and password")
                self.db_init = ElasticsearchStore(
                    es_url=f"http://{self.uri}:{self.port}",
                    index_name=self.index_name,
                    query_field="context",
                    vector_query_field="dense_vector",
                    embedding=self.embedding,  # type: ignore
                )
        except ConnectionError:
            logger.error("ElasticSearch connection failed")
        except Exception as e:
            logger.error(f"ElasticSearch connection failed: {e}")

    def get_config(self) -> ElasticsearchStoreConfig:
        """获取对应数据。"""
        return self._vector_store_config

    def create_collection(self, collection_name: str, **kwargs) -> Any:
        if not self.vector_name_exists():
            self.es_client_python.indices.create(
                index=collection_name, body=self.index_settings
            )
        return True

    def load_document(
        self,
        chunks: List[Chunk],
    ) -> List[str]:
        """加载数据或资源。"""
        logger.info("ElasticStore load document")
        try:
            from langchain.vectorstores.elasticsearch import ElasticsearchStore
        except ImportError:
            raise ValueError(
                "Could not import langchain python package. "
                "Please install it with `pip install langchain` and "
                "`pip install elasticsearch`."
            )
        try:
            texts = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [chunk.chunk_id for chunk in chunks]
            if self.username != "" and self.password != "":
                self.db = ElasticsearchStore.from_texts(
                    texts=texts,
                    embedding=self.embedding,  # type: ignore
                    metadatas=metadatas,
                    ids=ids,
                    es_url=f"http://{self.uri}:{self.port}",
                    index_name=self.index_name,
                    # 默认值说明。
                    # 代码说明。
                    distance_strategy="COSINE",
                    # 用于保存字段数据的字段名。
                    query_field="context",
                    # 向量生成配置。
                    vector_query_field="dense_vector",
                    # 历史调试代码，当前不启用。
                    # 历史调试代码，当前不启用。
                    # 代码说明。
                    # 默认值说明。
                    # 代码说明。
                    # 代码说明。
                    es_user=self.username,
                    es_password=self.password,
                )  # type: ignore
                logger.info("Elasticsearch save success.......")
                return ids
            else:
                self.db = ElasticsearchStore.from_documents(
                    texts=texts,
                    embedding=self.embedding,  # type: ignore
                    metadatas=metadatas,
                    ids=ids,
                    es_url=f"http://{self.uri}:{self.port}",
                    index_name=self.index_name,
                    distance_strategy="COSINE",
                    query_field="context",
                    vector_query_field="dense_vector",
                    # 历史调试代码，当前不启用。
                )  # type: ignore
                return ids
        except ConnectionError as ce:
            logger.error(f"ElasticSearch connect failed {ce}")
        except Exception as e:
            logger.error(f"ElasticSearch load_document failed : {e}")
        return []

    def delete_by_ids(self, ids):
        """删除对应数据。"""
        logger.info(f"begin delete elasticsearch len ids: {len(ids)}")
        ids = ids.split(",")
        try:
            self.db_init.delete(ids=ids)
            self.es_client_python.indices.refresh(index=self.index_name)
        except Exception as e:
            logger.error(f"ElasticSearch delete_by_ids failed : {e}")

    def similar_search(
        self,
        text: str,
        topk: int,
        filters: Optional[MetadataFilters] = None,
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        info_docs = self._search(query=text, topk=topk, filters=filters)
        return info_docs

    def similar_search_with_scores(
        self, text, topk, score_threshold, filters: Optional[MetadataFilters] = None
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        query = text
        info_docs = self._search(query=query, topk=topk, filters=filters)
        docs_and_scores = [
            chunk for chunk in info_docs if chunk.score >= score_threshold
        ]
        if len(docs_and_scores) == 0:
            logger.warning(
                "No relevant docs were retrieved using the relevance score"
                f" threshold {score_threshold}"
            )
        return docs_and_scores

    def _search(
        self, query: str, topk: int, filters: Optional[MetadataFilters] = None, **kwargs
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        jieba_tokenize = kwargs.pop("jieba_tokenize", None)
        if jieba_tokenize:
            try:
                import jieba
                import jieba.analyse
            except ImportError:
                raise ValueError("Please install it with `pip install jieba`.")
            query_list = jieba.analyse.textrank(query, topK=20, withWeight=False)
            query = " ".join(query_list)
        body = {"query": {"match": {"context": query}}}
        search_results = self.es_client_python.search(
            index=self.index_name, body=body, size=topk
        )
        search_results = search_results["hits"]["hits"]

        if not search_results:
            logger.warning("""No ElasticSearch results found.""")
            return []
        info_docs = []
        for result in search_results:
            doc_id = result["_id"]
            source = result["_source"]
            context = source["context"]
            metadata = source["metadata"]
            score = result["_score"]
            doc_with_score = Chunk(
                content=context, metadata=metadata, score=score, chunk_id=doc_id
            )
            info_docs.append(doc_with_score)
        return info_docs

    def vector_name_exists(self):
        """执行当前函数对应的业务逻辑。"""
        return self.es_client_python.indices.exists(index=self.index_name)

    def delete_vector_name(self, vector_name: str):
        """删除对应数据。"""
        if self.es_client_python.indices.exists(index=self.index_name):
            self.es_client_python.indices.delete(index=self.index_name)
