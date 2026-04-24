"""知识对象接口定义，为后续知识库和检索增强能力提供基础数据结构。"""


import json
import uuid
from typing import Any, Dict, List, Optional

from meyo._private.pydantic import BaseModel, Field, model_to_dict


class Document(BaseModel):
    """当前类的职责定义。"""

    content: str = Field(default="", description="document text content")

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="metadata fields",
    )
    chunks: List["Chunk"] = Field(
        default_factory=list,
        description="list of chunks",
    )

    def set_content(self, content: str) -> None:
        """设置对应数据。"""
        self.content = content

    def get_content(self) -> str:
        """获取对应数据。"""
        return self.content

    @classmethod
    def langchain2doc(cls, document):
        """执行当前函数对应的业务逻辑。"""
        metadata = document.metadata or {}
        return cls(content=document.page_content, metadata=metadata)

    @classmethod
    def doc2langchain(cls, chunk):
        """执行当前函数对应的业务逻辑。"""
        from langchain.schema import Document as LCDocument

        return LCDocument(page_content=chunk.content, metadata=chunk.metadata)


class Chunk(Document):
    """当前类的职责定义。"""

    chunk_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="unique id for the chunk"
    )
    chunk_name: str = Field(default="", description="chunk name")
    content: str = Field(default="", description="chunk text content")

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="metadata fields",
    )
    score: float = Field(default=0.0, description="chunk text similarity score")
    summary: str = Field(default="", description="chunk text summary")
    separator: str = Field(
        default="\n",
        description="Separator between metadata fields when converting to string.",
    )
    retriever: Optional[str] = Field(default=None, description="retriever name")
    embedding: Optional[List[float]] = Field(
        default=None, description="chunk embedding"
    )

    def to_dict(self, **kwargs: Any) -> Dict[str, Any]:
        """转换为目标数据结构。"""
        data = model_to_dict(self, **kwargs)
        data["class_name"] = self.class_name()
        return data

    def to_json(self, **kwargs: Any) -> str:
        """转换为目标数据结构。"""
        data = self.to_dict(**kwargs)
        return json.dumps(data)

    def __hash__(self):
        """执行当前函数对应的业务逻辑。"""
        return hash((self.chunk_id,))

    def __eq__(self, other):
        """执行当前函数对应的业务逻辑。"""
        return self.chunk_id == other.chunk_id

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs: Any):  # type: ignore
        """根据输入参数创建对象。"""
        if isinstance(kwargs, dict):
            data.update(kwargs)

        data.pop("class_name", None)
        return cls(**data)

    @classmethod
    def from_json(cls, data_str: str, **kwargs: Any):  # type: ignore
        """根据输入参数创建对象。"""
        data = json.loads(data_str)
        return cls.from_dict(data, **kwargs)

    @classmethod
    def langchain2chunk(cls, document):
        """执行当前函数对应的业务逻辑。"""
        metadata = document.metadata or {}
        return cls(content=document.page_content, metadata=metadata)

    @classmethod
    def llamaindex2chunk(cls, node):
        """执行当前函数对应的业务逻辑。"""
        metadata = node.metadata or {}
        return cls(content=node.content, metadata=metadata)

    @classmethod
    def chunk2langchain(cls, chunk):
        """执行当前函数对应的业务逻辑。"""
        try:
            from langchain.schema import Document as LCDocument  # mypy: ignore
        except ImportError:
            raise ValueError(
                "Could not import python package: langchain "
                "Please install langchain by command `pip install langchain"
            )
        return LCDocument(page_content=chunk.content, metadata=chunk.metadata)

    @classmethod
    def chunk2llamaindex(cls, chunk):
        """执行当前函数对应的业务逻辑。"""
        try:
            from llama_index.schema import TextNode
        except ImportError:
            raise ValueError(
                "Could not import python package: llama_index "
                "Please install llama_index by command `pip install llama_index"
            )
        return TextNode(text=chunk.content, metadata=chunk.metadata)
