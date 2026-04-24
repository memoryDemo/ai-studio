"""远程向量生成工作进程调用封装，让接口层可以通过统一接口请求向量模型。"""

from typing import List

from meyo.core import Embeddings, RerankEmbeddings
from meyo.model.cluster.manager_base import WorkerManager
from meyo.model.parameter import WorkerType


class RemoteEmbeddings(Embeddings):
    def __init__(self, model_name: str, worker_manager: WorkerManager) -> None:
        self.model_name = model_name
        self.worker_manager = worker_manager

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        params = {"model": self.model_name, "input": texts}
        return self.worker_manager.sync_embeddings(params)

    def embed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        return self.embed_documents([text])[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """生成向量结果。"""
        params = {"model": self.model_name, "input": texts}
        return await self.worker_manager.embeddings(params)

    async def aembed_query(self, text: str) -> List[float]:
        """执行查询并返回结果。"""
        result = await self.aembed_documents([text])
        return result[0]


class RemoteRerankEmbeddings(RerankEmbeddings):
    def __init__(self, model_name: str, worker_manager: WorkerManager) -> None:
        self.model_name = model_name
        self.worker_manager = worker_manager

    def predict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        params = {
            "model": self.model_name,
            "input": candidates,
            "query": query,
            "worker_type": WorkerType.RERANKER.value,
        }
        return self.worker_manager.sync_embeddings(params)[0]

    async def apredict(self, query: str, candidates: List[str]) -> List[float]:
        """执行当前函数对应的业务逻辑。"""
        params = {
            "model": self.model_name,
            "input": candidates,
            "query": query,
            "worker_type": WorkerType.RERANKER.value,
        }
        # 向量生成配置。
        scores = await self.worker_manager.embeddings(params)
        # 执行查询。
        return scores[0]
