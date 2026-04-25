import os
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic.v1 import SecretStr

from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import BoolInput, DictInput, IntInput, SecretStrInput, SliderInput, StrInput
from lfx.log.logger import logger


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return default


def _secret_value(value: Any) -> str:
    if isinstance(value, SecretStr):
        value = value.get_secret_value()
    text = str(value or "").strip()
    if text and text == text.upper() and text.replace("_", "").isalnum() and text[0].isalpha():
        return os.getenv(text, "").strip()
    return text


class MeyoLanguageModelComponent(LCModelComponent):
    display_name = "Meyo Language Model"
    description = "Runs a Meyo OpenAI-compatible language model."
    icon = "BrainCircuit"
    name = "MeyoLanguageModel"
    category = "models"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        StrInput(
            name="model_name",
            display_name="Model Name",
            value=_env(
                "MEYO_LANGUAGE_MODEL_NAME",
                "MEYO_DEFAULT_LANGUAGE_MODEL",
                default="Pro/zai-org/GLM-5.1",
            ),
            required=True,
        ),
        StrInput(
            name="api_base",
            display_name="API Base",
            value=_env(
                "MEYO_OPENAI_API_BASE_URL",
                "OPENAI_API_BASE_URL",
                "OPENAI_API_BASE",
                default="http://127.0.0.1:5670/api/v1",
            ),
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="Optional when Meyo does not enforce API keys.",
            value="MEYO_OPENAI_API_KEY",
            required=False,
        ),
        BoolInput(
            name="json_mode",
            display_name="JSON Mode",
            advanced=True,
            info="If True, the model is asked to return a JSON object.",
        ),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
            info="Additional keyword arguments passed to the model.",
        ),
        SliderInput(
            name="temperature",
            display_name="Temperature",
            value=0.1,
            range_spec=RangeSpec(min=0, max=1, step=0.01),
            advanced=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            advanced=True,
            range_spec=RangeSpec(min=0, max=128000),
        ),
        BoolInput(
            name="stream",
            display_name="Stream",
            value=False,
            advanced=True,
        ),
        IntInput(
            name="max_retries",
            display_name="Max Retries",
            value=5,
            advanced=True,
        ),
        IntInput(
            name="timeout",
            display_name="Timeout",
            value=700,
            advanced=True,
        ),
    ]

    def build_model(self) -> LanguageModel:
        logger.debug("Executing request with Meyo language model: %s", self.model_name)
        api_key = _secret_value(self.api_key) or _env("MEYO_OPENAI_API_KEY") or "meyo-local"

        parameters = {
            "api_key": api_key,
            "model_name": self.model_name,
            "base_url": self.api_base,
            "model_kwargs": self.model_kwargs or {},
            "streaming": self.stream,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
        }
        if self.max_tokens:
            parameters["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            parameters["temperature"] = self.temperature

        output = ChatOpenAI(**parameters)
        if self.json_mode:
            output = output.bind(response_format={"type": "json_object"})
        return output
