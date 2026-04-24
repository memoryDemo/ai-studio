"""模型工作进程基础接口，定义注册、心跳、调用和关闭流程。"""

from abc import ABC, abstractmethod
from typing import Dict, Iterator, List, Type

from meyo.core import ModelMetadata, ModelOutput
from meyo.core.interface.parameter import BaseDeployModelParameters
from meyo.model.parameter import WorkerType
from meyo.util.parameter_utils import ParameterDescription, _get_parameter_descriptions


class ModelWorker(ABC):
    """模型服务运行组件定义。"""

    def worker_type(self) -> WorkerType:
        """执行当前函数对应的业务逻辑。"""
        return WorkerType.LLM

    def model_param_class(self) -> Type[BaseDeployModelParameters]:
        """执行当前函数对应的业务逻辑。"""
        raise BaseDeployModelParameters

    def support_async(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return False

    # 代码说明。
    # 历史调试代码，当前不启用。
    # 代码说明。
    #
    # 代码说明。
    # 默认配置说明。
    # 代码说明。
    #     """

    @abstractmethod
    def load_worker(
        self, model_name: str, deploy_model_params: BaseDeployModelParameters, **kwargs
    ) -> None:
        """加载数据或资源。"""

    @abstractmethod
    def start(self, command_args: List[str] = None) -> None:
        """初始化并启动相关能力。"""

    @abstractmethod
    def stop(self) -> None:
        """关闭或停止资源。"""

    def restart(self, command_args: List[str] = None) -> None:
        """执行当前函数对应的业务逻辑。"""
        self.stop()
        self.start(command_args)

    def parameter_descriptions(self) -> List[ParameterDescription]:
        """执行当前函数对应的业务逻辑。"""
        param_cls = self.model_param_class()
        return _get_parameter_descriptions(param_cls)

    @abstractmethod
    def generate_stream(self, params: Dict) -> Iterator[ModelOutput]:
        """生成模型输出。"""

    async def async_generate_stream(self, params: Dict) -> Iterator[ModelOutput]:
        """生成模型输出。"""
        raise NotImplementedError

    @abstractmethod
    def generate(self, params: Dict) -> ModelOutput:
        """生成模型输出。"""

    async def async_generate(self, params: Dict) -> ModelOutput:
        """生成模型输出。"""
        raise NotImplementedError

    @abstractmethod
    def count_token(self, prompt: str) -> int:
        """执行当前函数对应的业务逻辑。"""

    async def async_count_token(self, prompt: str) -> int:
        """执行当前函数对应的业务逻辑。"""
        raise NotImplementedError

    @abstractmethod
    def get_model_metadata(self, params: Dict) -> ModelMetadata:
        """获取对应数据。"""

    async def async_get_model_metadata(self, params: Dict) -> ModelMetadata:
        """执行当前函数对应的业务逻辑。"""
        raise NotImplementedError

    @abstractmethod
    def embeddings(self, params: Dict) -> List[List[float]]:
        """生成向量结果。"""

    async def async_embeddings(self, params: Dict) -> List[List[float]]:
        """生成向量结果。"""
        raise NotImplementedError
