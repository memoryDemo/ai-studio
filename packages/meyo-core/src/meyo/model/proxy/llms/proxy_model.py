"""代理模型请求解析和通用调用逻辑，供具体大语言模型供应商复用。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Union

from meyo.core.interface.parameter import LLMDeployModelParameters
from meyo.model.proxy.base import ProxyLLMClient
from meyo.model.utils.llm_utils import parse_model_request  # noqa: F401
from meyo.model.utils.token_utils import ProxyTokenizerWrapper

if TYPE_CHECKING:
    from meyo.core.interface.message import BaseMessage, ModelMessage

logger = logging.getLogger(__name__)


class ProxyModel:
    def __init__(
        self,
        model_params: LLMDeployModelParameters,
        proxy_llm_client: Optional[ProxyLLMClient] = None,
    ) -> None:
        self._model_params = model_params
        self._tokenizer = ProxyTokenizerWrapper()
        self.proxy_llm_client = proxy_llm_client

    def get_params(self) -> LLMDeployModelParameters:
        return self._model_params

    def count_token(
        self,
        messages: Union[str, BaseMessage, ModelMessage, List[ModelMessage]],
        model_name: Optional[int] = None,
    ) -> int:
        """执行当前函数对应的业务逻辑。"""
        return self._tokenizer.count_token(messages, model_name)
