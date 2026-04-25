import os
from typing import Any

from langchain_openai import OpenAIEmbeddings
from pydantic.v1 import SecretStr

from lfx.base.embeddings.model import LCEmbeddingsModel
from lfx.field_typing import Embeddings
from lfx.inputs.inputs import BoolInput, DictInput, FloatInput, IntInput, SecretStrInput, StrInput


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


class MeyoEmbeddingModelComponent(LCEmbeddingsModel):
    display_name = "Meyo Embedding Model"
    description = "Generates embeddings through Meyo's OpenAI-compatible API."
    icon = "Binary"
    name = "MeyoEmbeddingModel"
    category = "models"

    inputs = [
        StrInput(
            name="model_name",
            display_name="Model Name",
            value=_env(
                "MEYO_EMBEDDING_MODEL_NAME",
                default="Qwen/Qwen3-Embedding-8B",
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
        IntInput(name="dimensions", display_name="Dimensions", advanced=True),
        IntInput(name="chunk_size", display_name="Chunk Size", advanced=True, value=1000),
        FloatInput(name="request_timeout", display_name="Request Timeout", advanced=True),
        IntInput(name="max_retries", display_name="Max Retries", advanced=True, value=3),
        BoolInput(name="show_progress_bar", display_name="Show Progress Bar", advanced=True),
        BoolInput(name="skip_empty", display_name="Skip Empty", advanced=True),
        DictInput(
            name="model_kwargs",
            display_name="Model Kwargs",
            advanced=True,
            info="Additional keyword arguments passed to the embedding model.",
        ),
    ]

    def build_embeddings(self) -> Embeddings:
        api_key = _secret_value(self.api_key) or _env("MEYO_OPENAI_API_KEY") or "meyo-local"

        return OpenAIEmbeddings(
            model=self.model_name,
            base_url=self.api_base,
            api_key=api_key,
            dimensions=self.dimensions or None,
            chunk_size=self.chunk_size,
            max_retries=self.max_retries,
            timeout=self.request_timeout or None,
            show_progress_bar=self.show_progress_bar,
            skip_empty=self.skip_empty,
            model_kwargs=self.model_kwargs or {},
        )
