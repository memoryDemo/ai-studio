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
        """统计给定消息的 token 数。

        参数：
            messages (Union[str, BaseMessage, ModelMessage, List[ModelMessage]])：
                需要统计 token 数的消息。
            model_name (Optional[int], optional)：模型名称，默认为 None。

        返回：
            int：token 数，失败时返回 -1。
        """
        return self._tokenizer.count_token(messages, model_name)
