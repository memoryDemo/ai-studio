"""工作进程管理器基础接口，定义模型工作进程的创建、启动和管理协议。"""

import asyncio
from abc import ABC, abstractmethod
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Callable, Dict, List, Optional

from meyo.component import BaseComponent, ComponentType, SystemApp
from meyo.core import ModelMetadata, ModelOutput
from meyo.core.interface.parameter import BaseDeployModelParameters
from meyo.model.base import WorkerApplyOutput, WorkerSupportedModel
from meyo.model.cluster.base import WorkerApplyRequest, WorkerStartupRequest
from meyo.model.cluster.worker_base import ModelWorker
from meyo.model.parameter import ModelWorkerParameters
from meyo.util.parameter_utils import ParameterDescription


@dataclass
class WorkerRunData:
    host: str
    port: int
    worker_type: str
    worker_key: str
    worker: ModelWorker
    worker_params: ModelWorkerParameters
    model_params: BaseDeployModelParameters
    stop_event: asyncio.Event
    semaphore: asyncio.Semaphore = None
    command_args: List[str] = None
    _heartbeat_future: Optional[Future] = None
    _last_heartbeat: Optional[datetime] = None
    # 代码说明。
    remove_from_registry: bool = False

    def _to_print_key(self):
        model_name = self.model_params.name
        provider = self.model_params.provider
        host = self.host
        port = self.port
        return f"model {model_name}@{provider}({host}:{port})"

    @property
    def stopped(self):
        """关闭或停止资源。"""
        return self.stop_event.is_set()


class WorkerManager(ABC):
    @abstractmethod
    async def start(self):
        """初始化并启动相关能力。"""

    @abstractmethod
    async def stop(self, ignore_exception: bool = False):
        """关闭或停止资源。"""

    @abstractmethod
    def after_start(self, listener: Callable[["WorkerManager"], None]):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def get_model_instances(
        self, worker_type: str, model_name: str, healthy_only: bool = True
    ) -> List[WorkerRunData]:
        """获取对应数据。"""

    @abstractmethod
    async def get_all_model_instances(
        self, worker_type: str, healthy_only: bool = True
    ) -> List[WorkerRunData]:
        """获取对应数据。"""

    @abstractmethod
    def sync_get_model_instances(
        self, worker_type: str, model_name: str, healthy_only: bool = True
    ) -> List[WorkerRunData]:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def select_one_instance(
        self, worker_type: str, model_name: str, healthy_only: bool = True
    ) -> WorkerRunData:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def sync_select_one_instance(
        self, worker_type: str, model_name: str, healthy_only: bool = True
    ) -> WorkerRunData:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def supported_models(self) -> List[WorkerSupportedModel]:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def model_startup(self, startup_req: WorkerStartupRequest):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def model_shutdown(self, shutdown_req: WorkerStartupRequest):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def generate_stream(
        self, params: Dict, **kwargs
    ) -> AsyncIterator[ModelOutput]:
        """生成模型输出。"""

    @abstractmethod
    async def generate(self, params: Dict) -> ModelOutput:
        """生成模型输出。"""

    @abstractmethod
    async def embeddings(self, params: Dict) -> List[List[float]]:
        """生成向量结果。"""

    @abstractmethod
    def sync_embeddings(self, params: Dict) -> List[List[float]]:
        """生成向量结果。"""

    @abstractmethod
    async def count_token(self, params: Dict) -> int:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def get_model_metadata(self, params: Dict) -> ModelMetadata:
        """获取对应数据。"""

    @abstractmethod
    async def worker_apply(self, apply_req: WorkerApplyRequest) -> WorkerApplyOutput:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def parameter_descriptions(
        self, worker_type: str, model_name: str
    ) -> List[ParameterDescription]:
        """执行当前函数对应的业务逻辑。"""


class WorkerManagerFactory(BaseComponent, ABC):
    name = ComponentType.WORKER_MANAGER_FACTORY.value

    def init_app(self, system_app: SystemApp):
        pass

    @abstractmethod
    def create(self) -> WorkerManager:
        """创建对象实例。"""
