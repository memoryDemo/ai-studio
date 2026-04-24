"""向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。"""


from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional

from pymilvus.milvus_client import IndexParams, MilvusClient

from meyo.core import Chunk, Embeddings
from meyo.model.resource import Parameter, ResourceCategory, register_resource
from meyo.storage.vector_store.base import (
    _COMMON_PARAMETERS,
    _VECTOR_STORE_COMMON_PARAMETERS,
    VectorStoreBase,
    VectorStoreConfig,
)
from meyo.storage.vector_store.filters import FilterOperator, MetadataFilters
from meyo.util import string_utils
from meyo.util.i18n_utils import _
from meyo.util.json_utils import serialize

logger = logging.getLogger(__name__)


@register_resource(
    _("Milvus Config"),
    "milvus_vector_config",
    category=ResourceCategory.VECTOR_STORE,
    parameters=[
        *_COMMON_PARAMETERS,
        Parameter.build_from(
            _("Uri"),
            "uri",
            str,
            description=_(
                "The uri of milvus store, if not set, will use the default uri."
            ),
            optional=True,
            default=None,
        ),
        Parameter.build_from(
            _("Port"),
            "port",
            str,
            description=_(
                "The port of milvus store, if not set, will use the default port."
            ),
            optional=True,
            default="19530",
        ),
        Parameter.build_from(
            _("Alias"),
            "alias",
            str,
            description=_(
                "The alias of milvus store, if not set, will use the default alias."
            ),
            optional=True,
            default="default",
        ),
        Parameter.build_from(
            _("Primary Field"),
            "primary_field",
            str,
            description=_(
                "The primary field of milvus store, if not set, will use the "
                "default primary field."
            ),
            optional=True,
            default="pk_id",
        ),
        Parameter.build_from(
            _("Text Field"),
            "text_field",
            str,
            description=_(
                "The text field of milvus store, if not set, will use the "
                "default text field."
            ),
            optional=True,
            default="content",
        ),
        Parameter.build_from(
            _("Embedding Field"),
            "embedding_field",
            str,
            description=_(
                "The embedding field of milvus store, if not set, will use the "
                "default embedding field."
            ),
            optional=True,
            default="vector",
        ),
    ],
    description=_("Milvus vector config."),
)
@dataclass
class MilvusVectorConfig(VectorStoreConfig):
    """配置参数定义。"""

    __type__ = "milvus"

    uri: str = field(
        default=None,
        metadata={
            "help": _("The uri of milvus store, if not set, will use the default uri.")
        },
    )
    port: str = field(
        default="19530",
        metadata={
            "help": _(
                "The port of milvus store, if not set, will use the default port."
            )
        },
    )

    alias: str = field(
        default="default",
        metadata={
            "help": _(
                "The alias of milvus store, if not set, will use the default alias."
            )
        },
    )
    primary_field: str = field(
        default="pk_id",
        metadata={
            "help": _(
                "The primary field of milvus store, i"
                "f not set, will use the default primary field."
            )
        },
    )
    text_field: str = field(
        default="content",
        metadata={
            "help": _(
                "The text field of milvus store, if not set, will use the "
                "default text field."
            )
        },
    )
    embedding_field: str = field(
        default="vector",
        metadata={
            "help": _(
                "The embedding field of milvus store, if not set, will use the "
                "default embedding field."
            )
        },
    )
    metadata_field: str = field(
        default="metadata",
        metadata={
            "help": _(
                "The metadata field of milvus store, if not set, will use the "
                "default metadata field."
            )
        },
    )
    secure: str = field(
        default="",
        metadata={
            "help": _("The secure of milvus store, if not set, will use the default ")
        },
    )

    def create_store(self, **kwargs) -> "MilvusStore":
        """创建对象实例。"""
        return MilvusStore(vector_store_config=self, **kwargs)


@register_resource(
    _("Milvus Vector Store"),
    "milvus_vector_store",
    category=ResourceCategory.VECTOR_STORE,
    description=_("Milvus vector store."),
    parameters=[
        Parameter.build_from(
            _("Milvus Config"),
            "vector_store_config",
            MilvusVectorConfig,
            description=_("the milvus config of vector store."),
            optional=True,
            default=None,
        ),
        *_VECTOR_STORE_COMMON_PARAMETERS,
    ],
)
class MilvusStore(VectorStoreBase):
    """存储能力实现。"""

    def __init__(
        self,
        vector_store_config: MilvusVectorConfig,
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

        # 历史调试代码，当前不启用。
        # 历史调试代码，当前不启用。
        # 历史调试代码，当前不启用。
        # 历史调试代码，当前不启用。
        # 代码说明。
        # 代码说明。
        #     )
        connect_kwargs = {}
        milvus_vector_config = vector_store_config.to_dict()
        self.uri = milvus_vector_config.get("uri") or os.getenv(
            "MILVUS_URL", "localhost"
        )
        self.port = milvus_vector_config.get("post") or os.getenv(
            "MILVUS_PORT", "19530"
        )
        self.username = milvus_vector_config.get("user", "") or os.getenv(
            "MILVUS_USERNAME"
        )
        self.password = milvus_vector_config.get("password") or os.getenv(
            "MILVUS_PASSWORD"
        )
        self.secure = milvus_vector_config.get("secure") or os.getenv("MILVUS_SECURE")

        self.collection_name = name
        if string_utils.contains_chinese(self.collection_name):
            bytes_str = self.collection_name.encode("utf-8")
            hex_str = bytes_str.hex()
            self.collection_name = hex_str
        if embedding_fn is None:
            # 向量生成配置。
            # 检查条件是否满足。
            raise ValueError("embedding_fn is required for MilvusStore")
        self.embedding: Embeddings = embedding_fn
        self.fields: List = []
        self.alias = milvus_vector_config.get("alias") or "default"
        self._consistency_level = "Session"

        # 默认配置说明。
        self.index_params = {
            "index_type": "HNSW",
            "metric_type": "COSINE",
        }

        # 默认配置说明。
        self.index_params_map = {
            "IVF_FLAT": {"params": {"nprobe": 10}},
            "IVF_SQ8": {"params": {"nprobe": 10}},
            "IVF_PQ": {"params": {"nprobe": 10}},
            "HNSW": {"params": {"M": 8, "efConstruction": 64}},
            "RHNSW_FLAT": {"params": {"ef": 10}},
            "RHNSW_SQ": {"params": {"ef": 10}},
            "RHNSW_PQ": {"params": {"ef": 10}},
            "IVF_HNSW": {"params": {"nprobe": 10, "ef": 10}},
            "ANNOY": {"params": {"search_k": 10}},
        }
        # 集合相关操作。
        self.primary_field = milvus_vector_config.get("primary_field") or "pk_id"
        self.vector_field = milvus_vector_config.get("embedding_field") or "vector"
        self.text_field = milvus_vector_config.get("text_field") or "content"
        self.sparse_vector = (
            milvus_vector_config.get("sparse_vector") or "sparse_vector"
        )
        self.metadata_field = milvus_vector_config.get("metadata_field") or "metadata"
        self.props_field = milvus_vector_config.get("props_field") or "props_field"

        if (self.username is None) != (self.password is None):
            raise ValueError(
                "Both username and password must be set to use authentication for "
                "Milvus"
            )
        if self.username:
            connect_kwargs["user"] = self.username
            connect_kwargs["password"] = self.password

        url = f"http://{self.uri}:{self.port}"
        self._milvus_client = MilvusClient(
            uri=url, user=self.username, db_name="default"
        )
        self.col = self.create_collection(collection_name=self.collection_name)

    def create_collection(self, collection_name: str, **kwargs) -> Any:
        """创建对象实例。"""
        try:
            from pymilvus import (
                Collection,
                CollectionSchema,
                DataType,
                FieldSchema,
                Function,
                FunctionType,
                connections,
                utility,
            )
            from pymilvus.orm.types import infer_dtype_bydata  # noqa: F401
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )
        if not connections.has_connection("default"):
            connections.connect(
                host=self.uri or "127.0.0.1",
                port=self.port or "19530",
                alias="default",
                # 历史调试代码，当前不启用。
            )
        embeddings = self.embedding.embed_query(collection_name)

        if utility.has_collection(collection_name):
            return Collection(self.collection_name, using=self.alias)
            # 历史调试代码，当前不启用。

        dim = len(embeddings)
        # 生成唯一名称。
        primary_field = self.primary_field
        vector_field = self.vector_field
        text_field = self.text_field
        metadata_field = self.metadata_field
        sparse_vector = self.sparse_vector
        props_field = self.props_field
        fields = []
        # 历史调试代码，当前不启用。
        # 创建文本字段。
        fields.append(
            FieldSchema(
                text_field,
                DataType.VARCHAR,
                max_length=65535,
                enable_analyzer=self.is_support_full_text_search(),
            )
        )
        # 主键字段。
        fields.append(
            FieldSchema(primary_field, DataType.INT64, is_primary=True, auto_id=True)
        )
        # 向量字段。
        fields.append(FieldSchema(vector_field, DataType.FLOAT_VECTOR, dim=dim))
        if self.is_support_full_text_search():
            fields.append(FieldSchema(sparse_vector, DataType.SPARSE_FLOAT_VECTOR))

        fields.append(FieldSchema(metadata_field, DataType.VARCHAR, max_length=65535))
        fields.append(FieldSchema(props_field, DataType.JSON))
        schema = CollectionSchema(fields)
        if self.is_support_full_text_search():
            bm25_fn = Function(
                name="text_bm25_emb",
                input_field_names=[self.text_field],
                output_field_names=[self.sparse_vector],
                function_type=FunctionType.BM25,
            )
            schema.add_function(bm25_fn)
        # 集合相关操作。
        collection = Collection(collection_name, schema)
        self.col = collection
        index_params = IndexParams()
        # 集合相关操作。
        index_params.add_index(field_name=self.vector_field, **self.index_params)
        # 集合相关操作。
        if self.is_support_full_text_search():
            collection.create_index(
                self.sparse_vector,
                {
                    "index_type": "AUTOINDEX",
                    "metric_type": "BM25",
                },
            )
        collection.create_index(vector_field, self.index_params)
        collection.load()
        return self.col

    def _load_documents(self, documents) -> List[str]:
        """执行当前函数对应的业务逻辑。"""
        try:
            from pymilvus import (
                DataType,
            )
            from pymilvus.orm.types import infer_dtype_bydata  # noqa: F401
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )
        texts = [d.content for d in documents]
        metadatas = [d.metadata for d in documents]
        self.fields = []
        for x in self.col.schema.fields:
            self.fields.append(x.name)
            if x.auto_id:
                self.fields.remove(x.name)
            if x.is_primary:
                self.primary_field = x.name
            if x.dtype == DataType.FLOAT_VECTOR or x.dtype == DataType.BINARY_VECTOR:
                self.vector_field = x.name
        return self._add_documents(texts, metadatas)

    def _add_documents(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        partition_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> List[str]:
        """执行当前函数对应的业务逻辑。"""
        insert_dict: Any = {self.text_field: list(texts)}
        try:
            import numpy as np  # noqa: F401

            text_vector = self.embedding.embed_documents(list(texts))
            insert_dict[self.vector_field] = text_vector
        except NotImplementedError:
            insert_dict[self.vector_field] = [
                self.embedding.embed_query(x) for x in texts
            ]
        # 整理元数据。
        # 历史调试代码，当前不启用。
        if len(self.fields) > 2 and metadatas is not None:
            for d in metadatas:
                metadata_json = json.dumps(d, default=serialize, ensure_ascii=False)
                # 历史调试代码，当前不启用。
                insert_dict.setdefault("metadata", []).append(metadata_json)
                insert_dict.setdefault("props_field", []).append(metadata_json)
        # 插入数据。
        insert_list = [insert_dict[x] for x in self.fields if self.sparse_vector != x]
        # 集合相关操作。
        res = self.col.insert(
            insert_list, partition_name=partition_name, timeout=timeout
        )

        return res.primary_keys

    def get_config(self) -> MilvusVectorConfig:
        """获取对应数据。"""
        return self._vector_store_config

    def load_document(self, chunks: List[Chunk]) -> List[str]:
        """加载数据或资源。"""
        batch_size = 500
        batched_list = [
            chunks[i : i + batch_size] for i in range(0, len(chunks), batch_size)
        ]
        doc_ids = []
        for doc_batch in batched_list:
            doc_ids.extend(self._load_documents(doc_batch))
        doc_ids = [str(doc_id) for doc_id in doc_ids]
        return doc_ids

    def similar_search(
        self, text, topk, filters: Optional[MetadataFilters] = None
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        try:
            from pymilvus import Collection, DataType
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )
        """在向量数据库中执行相似度检索。"""
        self.col = Collection(self.collection_name)
        schema = self.col.schema
        for x in schema.fields:
            self.fields.append(x.name)
            if x.auto_id:
                self.fields.remove(x.name)
            if x.is_primary:
                self.primary_field = x.name
            if x.dtype == DataType.FLOAT_VECTOR or x.dtype == DataType.BINARY_VECTOR:
                self.vector_field = x.name
        # 转换过滤条件。
        milvus_filter_expr = self.convert_metadata_filters(filters) if filters else None
        _, docs_and_scores = self._search(text, topk, expr=milvus_filter_expr)

        return [
            Chunk(
                metadata=json.loads(doc.metadata.get("metadata", "")),
                content=doc.content,
            )
            for doc, _, _ in docs_and_scores
        ]

    def similar_search_with_scores(
        self,
        text: str,
        topk: int,
        score_threshold: float,
        filters: Optional[MetadataFilters] = None,
    ) -> List[Chunk]:
        """执行查询并返回结果。"""
        try:
            from pymilvus import Collection, DataType
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )

        self.col = Collection(self.collection_name)
        schema = self.col.schema
        for x in schema.fields:
            self.fields.append(x.name)
            if x.auto_id:
                self.fields.remove(x.name)
            if x.is_primary:
                self.primary_field = x.name

            if x.dtype == DataType.FLOAT_VECTOR or x.dtype == DataType.BINARY_VECTOR:
                self.vector_field = x.name
        # 转换过滤条件。
        milvus_filter_expr = self.convert_metadata_filters(filters) if filters else None
        _, docs_and_scores = self._search(query=text, k=topk, expr=milvus_filter_expr)
        if any(score < 0.0 or score > 1.0 for _, score, id in docs_and_scores):
            logger.warning(
                f"similarity score need between 0 and 1, got {docs_and_scores}"
            )

        if score_threshold is not None:
            docs_and_scores = [
                Chunk(
                    metadata=doc.metadata,
                    content=doc.content,
                    score=score,
                    chunk_id=str(id),
                )
                for doc, score, id in docs_and_scores
                if score >= score_threshold
            ]
            if len(docs_and_scores) == 0:
                logger.warning(
                    "No relevant docs were retrieved using the relevance score"
                    f" threshold {score_threshold}"
                )
        return docs_and_scores

    def _search(
        self,
        query: str,
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        partition_names: Optional[List[str]] = None,
        round_decimal: int = -1,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ):
        """执行查询并返回结果。"""
        self.col.load()
        # 默认配置说明。
        if param is None:
            for index in self.col.indexes:
                if index.params["index_type"] == self.index_params.get("index_type"):
                    param = index.params
                    break
        # 向量生成配置。
        query_vector = self.embedding.embed_query(query)
        # 整理元数据。
        output_fields = self.fields[:]
        output_fields.remove(self.vector_field)
        if self.sparse_vector in output_fields:
            output_fields.remove(self.sparse_vector)
        # 执行检索。
        res = self.col.search(
            [query_vector],
            self.vector_field,
            param,
            k,
            expr=expr,
            output_fields=output_fields,
            partition_names=partition_names,
            round_decimal=round_decimal,
            timeout=60,
            **kwargs,
        )
        ret = []
        for result in res[0]:
            meta = {x: result.entity.get(x) for x in output_fields}
            ret.append(
                (
                    Chunk(
                        content=meta.pop(self.text_field),
                        metadata=json.loads(meta.pop(self.metadata_field)),
                    ),
                    result.distance,
                    result.id,
                )
            )
        if len(ret) == 0:
            logger.warning("No relevant docs were retrieved.")
            return None, []
        return ret[0], ret

    def vector_name_exists(self):
        """执行当前函数对应的业务逻辑。"""
        try:
            if not self._milvus_client.has_collection(self.collection_name):
                logger.info(f"Collection {self.collection_name} does not exist")
                return False

            stats = self._milvus_client.get_collection_stats(self.collection_name)
            row_count = stats.get("row_count", 0)
            return row_count > 0

        except Exception as e:
            logger.error(f"vector_name_exists error, {str(e)}")
            return False

    def delete_vector_name(self, vector_name: str):
        """删除对应数据。"""
        try:
            from pymilvus import utility
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )
        """删除向量集合名称。"""
        logger.info(f"milvus vector_name:{vector_name} begin delete...")
        utility.drop_collection(self.collection_name)
        return True

    def delete_by_ids(self, ids):
        """删除对应数据。"""
        try:
            from pymilvus import Collection
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )
        self.col = Collection(self.collection_name)
        # 删除对应数据。
        logger.info(f"begin delete milvus ids: {ids}")
        delete_ids = ids.split(",")
        doc_ids = [int(doc_id) for doc_id in delete_ids]
        delete_expr = f"{self.primary_field} in {doc_ids}"
        self.col.delete(delete_expr)
        return True

    # 删除对应数据。
    def delete_by_file_id(self, file_id: str):
        print("MilvusStore.delete_by_file_id")
        """按文件编号删除向量。"""
        try:
            from pymilvus import Collection
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )
        self.col = Collection(self.collection_name)
        print(self.col)
        # 删除对应数据。
        logger.info(f"begin delete milvus file_id: {file_id}")
        delete_expr = f"{self.metadata_field} like '%\"file_id\": {file_id}%'"
        self.col.delete(delete_expr)
        return True

    def convert_metadata_filters(self, filters: MetadataFilters) -> str:
        """转换为目标数据结构。"""
        metadata_filters = []
        for metadata_filter in filters.filters:
            if isinstance(metadata_filter.value, str):
                expr = (
                    f"{self.props_field}['{metadata_filter.key}'] "
                    f"{FilterOperator.EQ.value} '{metadata_filter.value}'"
                )
                metadata_filters.append(expr)
            elif isinstance(metadata_filter.value, List):
                expr = (
                    f"{self.props_field}['{metadata_filter.key}'] "
                    f"{FilterOperator.IN.value} {metadata_filter.value}"
                )
                metadata_filters.append(expr)
            else:
                expr = (
                    f"{self.props_field}['{metadata_filter.key}'] "
                    f"{FilterOperator.EQ.value} {str(metadata_filter.value)}"
                )
                metadata_filters.append(expr)
        if len(metadata_filters) > 1:
            metadata_filter_expr = f" {filters.condition.value} ".join(metadata_filters)
        else:
            metadata_filter_expr = metadata_filters[0]
        return metadata_filter_expr

    def truncate(self):
        """执行调用逻辑。"""
        try:
            from pymilvus import Collection, utility
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )
        """字段说明。"""
        logger.info(f"Begin truncate Milvus collection: {self.collection_name}")
        # 集合相关操作。
        if utility.has_collection(self.collection_name):
            collection = Collection(self.collection_name)
            # 集合相关操作。
            collection.load()
            # 通过pk_id删除所有数据
            collection.delete("pk_id >= 0")
            # 代码说明。
            collection.flush()
            logger.info(f"Truncate Milvus collection {self.collection_name} success")
        else:
            logger.warning(
                f"Collection {self.collection_name} not found, skip truncate."
            )

    def full_text_search(
        self, text: str, topk: int = 10, filters: Optional[MetadataFilters] = None
    ) -> List[Chunk]:
        if self.is_support_full_text_search():
            milvus_filters = self.convert_metadata_filters(filters) if filters else None
            results = self._milvus_client.search(
                collection_name=self.collection_name,
                data=[text],
                anns_field=self.sparse_vector,
                limit=topk,
                output_fields=["*"],
                filter=milvus_filters,
            )
            chunk_results = [
                Chunk(
                    content=r.get("entity").get("content"),
                    chunk_id=str(r.get("pk_id")),
                    score=r.get("distance"),
                    metadata=json.loads(r.get("entity").get("metadata")),
                    retriever="full_text",
                )
                for r in results[0]
            ]

            return chunk_results

    def is_support_full_text_search(self) -> bool:
        """执行查询并返回结果。"""
        try:
            milvus_version_text = self._milvus_client.get_server_version()
            pattern = r"v(\d+\.\d+\.\d+)"
            match = re.search(pattern, milvus_version_text)
            if match:
                milvus_version = match.group(1)
                logger.info(f"milvus version is {milvus_version}")
                # 检查条件是否满足。
                return milvus_version >= "2.5.0"
            return False
        except Exception as e:
            logger.warning(
                f"Failed to check Milvus version:{str(e)}."
                f"do not support full text index."
            )
            return False
