"""包入口，集中导出当前目录下的模型服务相关能力。"""


from meyo.core import Chunk, Document  # noqa: F401

__ALL__ = [
    "Chunk",
    "Document",
]
