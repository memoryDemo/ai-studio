"""包入口，集中导出当前目录下的模型服务相关能力。"""

try:
    from meyo.model.cluster.client import DefaultLLMClient, RemoteLLMClient
except ImportError:
    DefaultLLMClient = None
    RemoteLLMClient = None

from .adapter.auto_client import AutoLLMClient  # noqa: F401

_exports = [
    "AutoLLMClient",
]
if DefaultLLMClient:
    _exports.append("DefaultLLMClient")
if RemoteLLMClient:
    _exports.append("RemoteLLMClient")

__ALL__ = _exports

_HAS_SCAN = False


def scan_model_providers():
    """执行当前函数对应的业务逻辑。"""
    from meyo.core.interface.parameter import (
        EmbeddingDeployModelParameters,
        LLMDeployModelParameters,
    )
    from meyo.util.module_utils import ModelScanner, ScannerConfig

    global _HAS_SCAN

    if _HAS_SCAN:
        return
    scanner = ModelScanner[LLMDeployModelParameters]()
    config = ScannerConfig(
        module_path="meyo.model.adapter",
        base_class=LLMDeployModelParameters,
        specific_files=[
            "vllm_adapter",
            "mlx_adapter",
            "hf_adapter",
            "llama_cpp_adapter",
            "llama_cpp_py_adapter",
        ],
    )
    config_llms = ScannerConfig(
        module_path="meyo.model.proxy.llms",
        base_class=LLMDeployModelParameters,
        recursive=True,
    )
    embedding_config = ScannerConfig(
        module_path="meyo.rag.embedding",
        base_class=EmbeddingDeployModelParameters,
        specific_files=["embeddings"],
    )
    ext_embedding_config = ScannerConfig(
        module_path="meyo_ext.rag.embeddings",
        base_class=EmbeddingDeployModelParameters,
    )
    reranker_config = ScannerConfig(
        module_path="meyo.rag.embedding",
        base_class=EmbeddingDeployModelParameters,
        specific_files=["rerank"],
    )
    scanner.scan_and_register(config)
    scanner.scan_and_register(config_llms)
    scanner.scan_and_register(embedding_config)
    scanner.scan_and_register(ext_embedding_config)
    scanner.scan_and_register(reranker_config)

    _HAS_SCAN = True
    return scanner.get_registered_items()
