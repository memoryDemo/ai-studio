"""模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from meyo.core import ModelMessage
from meyo.core.interface.parameter import LLMDeployModelParameters
from meyo.model.adapter.base import LLMModelAdapter, register_model_adapter
from meyo.model.adapter.model_metadata import COMMON_HF_MODELS
from meyo.model.adapter.template import ConversationAdapter
from meyo.model.base import ModelType
from meyo.util.i18n_utils import _

logger = logging.getLogger(__name__)


@dataclass
class MLXDeployModelParameters(LLMDeployModelParameters):
    """配置参数定义。"""

    provider: str = "mlx"

    path: Optional[str] = field(
        default=None,
        metadata={
            "order": -800,
            "help": _("The path of the model, if you want to deploy a local model."),
        },
    )
    device: Optional[str] = field(
        default="auto",
        metadata={
            "order": -700,
            "help": _(
                "Device to run model. If None, the device is automatically determined"
            ),
        },
    )

    concurrency: Optional[int] = field(
        default=100, metadata={"help": _("Model concurrency limit")}
    )

    @property
    def real_model_path(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        return self._resolve_root_path(self.path)

    @property
    def real_device(self) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        return self.device or super().real_device


class MLXModelAdapter(LLMModelAdapter):
    def match(
        self,
        provider: str,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
    ) -> bool:
        return provider == ModelType.MLX

    def model_type(self) -> str:
        return ModelType.MLX

    def model_param_class(
        self, model_type: str = None
    ) -> Type[MLXDeployModelParameters]:
        return MLXDeployModelParameters

    def get_default_conv_template(
        self, model_name: str, model_path: str
    ) -> Optional[ConversationAdapter]:
        return None

    def load_from_params(self, params: MLXDeployModelParameters):
        """加载数据或资源。"""
        try:
            from mlx_lm import load
        except ImportError:
            logger.error(
                "MLX model adapter requires mlx_lm package. "
                "Please install it with `pip install mlx-lm`."
            )
            raise

        model_path = params.real_model_path
        model, tokenizer = load(model_path)
        return model, tokenizer

    def support_generate_function(self) -> bool:
        return False

    def get_generate_stream_function(
        self, model, deploy_model_params: LLMDeployModelParameters
    ):
        from meyo.model.llm.llm_out.mlx_llm import generate_stream

        return generate_stream

    def get_str_prompt(
        self,
        params: Dict,
        messages: List[ModelMessage],
        tokenizer: Any,
        prompt_template: str = None,
        convert_to_compatible_format: bool = False,
    ) -> Optional[str]:
        if not tokenizer:
            raise ValueError("tokenizer is is None")
        if hasattr(tokenizer, "apply_chat_template"):
            messages = self.transform_model_messages(
                messages, convert_to_compatible_format
            )
            logger.debug(f"The messages after transform: \n{messages}")
            str_prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            return str_prompt
        return None


register_model_adapter(MLXModelAdapter, supported_models=COMMON_HF_MODELS)
