#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""模型实例和输出基础结构，连接供应商、工作进程和接口响应。"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from meyo.util.parameter_utils import ParameterDescription


class ModelType:
    """模型能力抽象或实现。"""

    HF = "hf"
    LLAMA_CPP = "llama.cpp"
    LLAMA_CPP_SERVER = "llama.cpp.server"
    PROXY = "proxy"
    VLLM = "vllm"
    MLX = "mlx"
    # 待办事项。


@dataclass
class ModelInstance:
    """模型能力抽象或实现。"""

    model_name: str
    host: str
    port: int
    weight: Optional[float] = 1.0
    check_healthy: Optional[bool] = True
    healthy: Optional[bool] = False
    enabled: Optional[bool] = True
    prompt_template: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    # 代码说明。
    remove_from_registry: Optional[bool] = False

    def to_dict(self) -> Dict:
        """转换为目标数据结构。"""
        return asdict(self)

    @property
    def str_last_heartbeat(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        if not self.last_heartbeat:
            return None
        if isinstance(self.last_heartbeat, str):
            return self.last_heartbeat
        return self.last_heartbeat.strftime("%Y-%m-%d %H:%M:%S")


class WorkerApplyType(str, Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    UPDATE_PARAMS = "update_params"


@dataclass
class WorkerApplyOutput:
    message: str
    success: Optional[bool] = True
    # 代码说明。
    timecost: Optional[int] = -1

    @staticmethod
    def reduce(outs: List["WorkerApplyOutput"]) -> "WorkerApplyOutput":
        """执行当前函数对应的业务逻辑。"""
        if not outs:
            return WorkerApplyOutput("Not outputs")
        combined_success = all(out.success for out in outs)
        max_timecost = max(out.timecost for out in outs)
        combined_message = "\n;".join(out.message for out in outs)
        return WorkerApplyOutput(combined_message, combined_success, max_timecost)


@dataclass
class SupportedModel:
    model: str = field(metadata={"help": "The name of the model"})
    worker_type: str = field(
        metadata={"help": "The type of the worker, llm, tex2vec and reranker"}
    )
    provider: Optional[str] = field(
        default="hf",
        metadata={
            "help": "The provider of the model. eg. hf, vllm, llama.cpp, proxy/openai"
        },
    )
    path: Optional[str] = field(
        default=None, metadata={"help": "The path of the model"}
    )
    path_exist: bool = field(
        default=False, metadata={"help": "Whether the path exists"}
    )
    proxy: bool = field(
        default=False, metadata={"help": "Whether the model is a proxy"}
    )
    enabled: bool = field(
        default=False, metadata={"help": "Whether the model is enabled"}
    )
    params: List[ParameterDescription] = field(
        default_factory=list, metadata={"help": "The parameters of the model"}
    )
    description: Optional[str] = field(
        default=None, metadata={"help": "The description of the model"}
    )

    @classmethod
    def from_dict(cls, model_data: Dict) -> "SupportedModel":
        params = model_data.get("params", [])
        if params:
            params = [ParameterDescription(**param) for param in params]
        model_data["params"] = params
        return cls(**model_data)


@dataclass
class WorkerSupportedModel:
    host: str
    port: int
    models: List[SupportedModel]

    @classmethod
    def from_dict(cls, worker_data: Dict) -> "WorkerSupportedModel":
        models = [
            SupportedModel.from_dict(model_data) for model_data in worker_data["models"]
        ]
        worker_data["models"] = models
        return cls(**worker_data)


@dataclass
class FlatSupportedModel(SupportedModel):
    """模型能力抽象或实现。"""

    host: Optional[str] = field(
        default=None, metadata={"help": "The host of the model"}
    )
    port: Optional[int] = field(
        default=None, metadata={"help": "The port of the model"}
    )
    worker_name: Optional[str] = field(
        default=None, metadata={"help": "The name of the model worker"}
    )

    @staticmethod
    def from_supports(
        supports: List[WorkerSupportedModel],
    ) -> List["FlatSupportedModel"]:
        results = []
        for s in supports:
            host, port, models = s.host, s.port, s.models
            for m in models:
                kwargs = asdict(m)
                kwargs["host"] = host
                kwargs["port"] = port
                results.append(FlatSupportedModel(**kwargs))
        return results
