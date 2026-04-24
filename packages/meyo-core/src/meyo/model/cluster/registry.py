"""模型注册表抽象，负责记录和查询当前可用的模型服务实例。
"""

import itertools
import logging
import random
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from meyo.component import BaseComponent, ComponentType, SystemApp
from meyo.model.base import ModelInstance

logger = logging.getLogger(__name__)


class ModelRegistry(BaseComponent, ABC):
    """模型服务运行组件定义。"""

    name = ComponentType.MODEL_REGISTRY

    def __init__(self, system_app: SystemApp | None = None):
        self.system_app = system_app
        super().__init__(system_app)

    def init_app(self, system_app: SystemApp):
        """初始化并启动相关能力。"""
        self.system_app = system_app

    @abstractmethod
    async def register_instance(self, instance: ModelInstance) -> bool:
        """注册对象。"""
        pass

    @abstractmethod
    async def deregister_instance(self, instance: ModelInstance) -> bool:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def get_all_instances(
        self, model_name: str, healthy_only: bool = False
    ) -> List[ModelInstance]:
        """获取对应数据。"""

    @abstractmethod
    def sync_get_all_instances(
        self, model_name: str, healthy_only: bool = False
    ) -> List[ModelInstance]:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    async def get_all_model_instances(
        self, healthy_only: bool = False
    ) -> List[ModelInstance]:
        """获取对应数据。"""

    async def select_one_health_instance(self, model_name: str) -> ModelInstance:
        """执行当前函数对应的业务逻辑。"""
        instances = await self.get_all_instances(model_name, healthy_only=True)
        instances = [i for i in instances if i.enabled]
        if not instances:
            return None
        return random.choice(instances)

    @abstractmethod
    async def send_heartbeat(self, instance: ModelInstance) -> bool:
        """执行当前函数对应的业务逻辑。"""


class EmbeddedModelRegistry(ModelRegistry):
    def __init__(
        self,
        system_app: SystemApp | None = None,
        heartbeat_interval_secs: int = 60,
        heartbeat_timeout_secs: int = 120,
    ):
        super().__init__(system_app)
        self.registry: Dict[str, List[ModelInstance]] = defaultdict(list)
        self.heartbeat_interval_secs = heartbeat_interval_secs
        self.heartbeat_timeout_secs = heartbeat_timeout_secs
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_checker)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def _get_instances(
        self, model_name: str, host: str, port: int, healthy_only: bool = False
    ) -> Tuple[List[ModelInstance], List[ModelInstance]]:
        instances = self.registry[model_name]
        if healthy_only:
            instances = [ins for ins in instances if ins.healthy is True]
        exist_ins = [ins for ins in instances if ins.host == host and ins.port == port]
        return instances, exist_ins

    def _remove_instance(self, model_name: str, host: str, port: int):
        instances, exist_ins = self._get_instances(
            model_name, host, port, healthy_only=False
        )
        if exist_ins:
            ins = exist_ins[0]
            ins.healthy = False
            if ins.remove_from_registry:
                self.registry[model_name].remove(ins)

    def _heartbeat_checker(self):
        while True:
            for instances in self.registry.values():
                for instance in instances:
                    if (
                        instance.check_healthy
                        and datetime.now() - instance.last_heartbeat
                        > timedelta(seconds=self.heartbeat_timeout_secs)
                    ):
                        instance.healthy = False
            time.sleep(self.heartbeat_interval_secs)

    async def register_instance(self, instance: ModelInstance) -> bool:
        model_name = instance.model_name.strip()
        host = instance.host.strip()
        port = instance.port

        instances, exist_ins = self._get_instances(
            model_name, host, port, healthy_only=False
        )
        if exist_ins:
            # 代码说明。
            ins = exist_ins[0]
            # 代码说明。
            ins.weight = instance.weight
            ins.healthy = True
            ins.prompt_template = instance.prompt_template
            ins.last_heartbeat = datetime.now()
        else:
            instance.healthy = True
            instance.last_heartbeat = datetime.now()
            instances.append(instance)
        return True

    async def deregister_instance(self, instance: ModelInstance) -> bool:
        model_name = instance.model_name.strip()
        host = instance.host.strip()
        port = instance.port
        _, exist_ins = self._get_instances(model_name, host, port, healthy_only=False)
        if exist_ins:
            ins = exist_ins[0]
            ins.healthy = False
            if instance.remove_from_registry:
                self.registry[model_name].remove(ins)
        return True

    async def get_all_instances(
        self, model_name: str, healthy_only: bool = False
    ) -> List[ModelInstance]:
        return self.sync_get_all_instances(model_name, healthy_only)

    def sync_get_all_instances(
        self, model_name: str, healthy_only: bool = False
    ) -> List[ModelInstance]:
        instances = self.registry[model_name]
        if healthy_only:
            instances = [ins for ins in instances if ins.healthy is True]
        return instances

    async def get_all_model_instances(
        self, healthy_only: bool = False
    ) -> List[ModelInstance]:
        logger.debug("Current registry metadata:\n{self.registry}")
        instances = list(itertools.chain(*self.registry.values()))
        if healthy_only:
            instances = [ins for ins in instances if ins.healthy is True]
        return instances

    async def send_heartbeat(self, instance: ModelInstance) -> bool:
        _, exist_ins = self._get_instances(
            instance.model_name, instance.host, instance.port, healthy_only=False
        )
        if not exist_ins:
            # 代码说明。
            await self.register_instance(instance)
            return True

        ins = exist_ins[0]
        ins.last_heartbeat = datetime.now()
        ins.healthy = True
        return True
