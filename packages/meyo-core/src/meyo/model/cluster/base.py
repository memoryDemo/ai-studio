"""模型服务运行层基础模块，连接工作进程、控制器、注册表和接口服务。"""

from typing import Any, Dict, List, Optional, Union

from meyo._private.pydantic import BaseModel, Field
from meyo.core.interface.message import ModelMessage
from meyo.model.base import WorkerApplyType
from meyo.model.parameter import WorkerType

WORKER_MANAGER_SERVICE_TYPE = "service"
WORKER_MANAGER_SERVICE_NAME = "WorkerManager"


class PromptRequest(BaseModel):
    model: str
    messages: List[ModelMessage] = Field(
        default_factory=list, description="List of ModelMessage objects"
    )
    prompt: str = None
    temperature: float = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_new_tokens: int = None
    stop: Optional[Union[str, List[str]]] = None
    stop_token_ids: List[int] = []
    context_len: int = None
    echo: bool = True
    span_id: str = None
    metrics: bool = False
    """是否返回推理指标。"""
    version: str = "v2"
    """消息版本，默认使用第二版。"""
    context: Dict[str, Any] = None
    """模型上下文信息。"""
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    chat_model: Optional[bool] = True
    """是否使用对话模型。"""


class EmbeddingsRequest(BaseModel):
    model: str
    input: List[str]
    worker_type: str = WorkerType.TEXT2VEC.value
    span_id: Optional[str] = None
    query: Optional[str] = None
    """重排模型必须提供查询文本。"""


class CountTokenRequest(BaseModel):
    model: str
    prompt: str


class ModelMetadataRequest(BaseModel):
    model: str


class WorkerApplyRequest(BaseModel):
    model: str
    apply_type: WorkerApplyType
    worker_type: WorkerType = WorkerType.LLM
    params: Dict = Field(
        default_factory=dict,
        description="Additional parameters for the apply operation",
    )
    apply_user: Optional[str] = Field(
        None, description="The user name for the apply operation"
    )


class WorkerParameterRequest(BaseModel):
    model: str
    worker_type: WorkerType = WorkerType.LLM


class WorkerStartupRequest(BaseModel):
    """接口数据结构定义。"""

    host: str
    port: int
    model: str
    worker_type: WorkerType
    params: Dict
    delete_after: Optional[bool] = Field(
        False,
        description="Whether to delete the worker after operation. For debugging and "
        "delete worker from model memory.",
    )
    worker_name: Optional[str] = Field(None, description="The name of the worker.")
    sys_code: Optional[str] = Field(
        None, description="The system code for the worker, used for authentication"
    )
    user_name: Optional[str] = Field(
        None, description="The user name for the worker, used for authentication"
    )
