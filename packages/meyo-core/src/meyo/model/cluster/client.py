"""模型服务运行层基础模块，连接工作进程、控制器、注册表和接口服务。"""

import asyncio
from typing import AsyncIterator, List, Optional

from meyo.model.resource import Parameter, ResourceCategory, register_resource
from meyo.core.interface.llm import (
    DefaultMessageConverter,
    LLMClient,
    MessageConverter,
    ModelMetadata,
    ModelOutput,
    ModelRequest,
)
from meyo.model.cluster.manager_base import WorkerManager
from meyo.model.parameter import WorkerType
from meyo.util.i18n_utils import _


class DAGVar:
    @staticmethod
    def get_current_system_app():
        return None


@register_resource(
    label=_("Default LLM Client"),
    name="default_llm_client",
    category=ResourceCategory.LLM_CLIENT,
    description=_("Default LLM client(Connect to your MEYO model serving)"),
    parameters=[
        Parameter.build_from(
            _("Auto Convert Message"),
            name="auto_convert_message",
            type=bool,
            optional=True,
            default=True,
            description=_(
                "Whether to auto convert the messages that are not supported "
                "by the LLM to a compatible format"
            ),
        )
    ],
)
class DefaultLLMClient(LLMClient):
    """外部服务连接和调用实现。"""

    def __init__(
        self,
        worker_manager: Optional[WorkerManager] = None,
        auto_convert_message: bool = True,
    ):
        self._worker_manager = worker_manager
        self._auto_covert_message = auto_convert_message

    @property
    def worker_manager(self) -> WorkerManager:
        """执行当前函数对应的业务逻辑。"""
        if not self._worker_manager:
            system_app = DAGVar.get_current_system_app()
            if not system_app:
                raise ValueError("System app is not initialized")
            from meyo.model.cluster import WorkerManagerFactory

            return WorkerManagerFactory.get_instance(system_app).create()
        return self._worker_manager

    async def generate(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> ModelOutput:
        if not message_converter and self._auto_covert_message:
            message_converter = DefaultMessageConverter()
        request = await self.covert_message(request, message_converter)
        return await self.worker_manager.generate(request.to_dict())

    async def generate_stream(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> AsyncIterator[ModelOutput]:
        if not message_converter and self._auto_covert_message:
            message_converter = DefaultMessageConverter()
        request = await self.covert_message(request, message_converter)
        async for output in self.worker_manager.generate_stream(request.to_dict()):
            yield output

    async def models(self) -> List[ModelMetadata]:
        instances = await self.worker_manager.get_all_model_instances(
            WorkerType.LLM.value, healthy_only=True
        )
        query_metadata_task = []
        for instance in instances:
            worker_name, _ = WorkerType.parse_worker_key(instance.worker_key)
            query_metadata_task.append(
                self.worker_manager.get_model_metadata({"model": worker_name})
            )
        models: List[ModelMetadata] = await asyncio.gather(*query_metadata_task)
        model_map = {}
        for single_model in models:
            model_map[single_model.model] = single_model
        return [model_map[model_name] for model_name in sorted(model_map.keys())]

    async def count_token(self, model: str, prompt: str) -> int:
        return await self.worker_manager.count_token({"model": model, "prompt": prompt})


@register_resource(
    label=_("Remote LLM Client"),
    name="remote_llm_client",
    category=ResourceCategory.LLM_CLIENT,
    description=_("Remote LLM client(Connect to the remote MEYO model serving)"),
    parameters=[
        Parameter.build_from(
            _("Controller Address"),
            name="controller_address",
            type=str,
            optional=True,
            default=_("http://127.0.0.1:8000"),
            description=_("Model controller address"),
        ),
        Parameter.build_from(
            _("Auto Convert Message"),
            name="auto_convert_message",
            type=bool,
            optional=True,
            default=True,
            description=_(
                "Whether to auto convert the messages that are not supported "
                "by the LLM to a compatible format"
            ),
        ),
    ],
)
class RemoteLLMClient(DefaultLLMClient):
    """外部服务连接和调用实现。"""

    def __init__(
        self,
        controller_address: str = "http://127.0.0.1:8000",
        auto_convert_message: bool = True,
    ):
        """初始化实例。"""
        from meyo.model.cluster import ModelRegistryClient, RemoteWorkerManager

        model_registry_client = ModelRegistryClient(controller_address)
        worker_manager = RemoteWorkerManager(model_registry_client)
        super().__init__(worker_manager, auto_convert_message)
