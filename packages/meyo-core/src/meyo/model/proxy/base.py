"""代理模型基础能力，负责统一远程模型供应商的参数和调用方式。
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from concurrent.futures import Executor, ThreadPoolExecutor
from functools import cache
from inspect import isasyncgenfunction, iscoroutinefunction
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Type,
    Union,
)

from meyo.core import (
    LLMClient,
    MessageConverter,
    ModelMetadata,
    ModelOutput,
    ModelRequest,
)
from meyo.core.interface.parameter import LLMDeployModelParameters
from meyo.util.configure.manager import _resolve_env_vars
from meyo.util.executor_utils import blocking_func_to_async

from ..utils.token_utils import LRUTokenCache

if TYPE_CHECKING:
    from tiktoken import Encoding

    from .llms.proxy_model import ProxyModel

logger = logging.getLogger(__name__)

GenerateStreamFunction = Callable[
    ["ProxyModel", Any, Dict[str, Any], str, int], AsyncGenerator[ModelOutput, None]
]
AsyncGenerateStreamFunction = Callable[
    ["ProxyModel", Any, Dict[str, Any], str, int],
    Generator[ModelOutput, None, None],
]
GenerateFunction = Callable[["ProxyModel", Any, Dict[str, Any], str, int], ModelOutput]
AsyncGenerateFunction = Callable[
    ["ProxyModel", Any, Dict[str, Any], str, int],
    ModelOutput,
]


class ProxyTokenizer(ABC):
    @abstractmethod
    def count_token(self, model_name: str, prompts: List[str]) -> List[int]:
        """执行当前函数对应的业务逻辑。"""

    def support_async(self) -> bool:
        """执行当前函数对应的业务逻辑。"""
        return False

    async def count_token_async(self, model_name: str, prompts: List[str]) -> List[int]:
        """执行当前函数对应的业务逻辑。"""
        raise NotImplementedError()


class TiktokenProxyTokenizer(ProxyTokenizer):
    def __init__(self, cache_size: int = 100000, cache_memory_mb: int = 100):
        self._token_cache = LRUTokenCache(
            max_size=cache_size, max_memory_mb=cache_memory_mb
        )
        self._cache = {}

    def count_token(self, model_name: str, prompts: List[str]) -> List[int]:
        encoding_model = self._get_or_create_encoding_model(model_name)
        if not encoding_model:
            return [-1] * len(prompts)
        results = []
        for prompt in prompts:
            # 代码说明。
            cache_key = self._generate_cache_key(model_name, prompt)

            # 获取对应数据。
            cached_count = self._token_cache.get(cache_key)
            if cached_count is not None:
                results.append(cached_count)
                continue

            # 代码说明。
            token_count = len(encoding_model.encode(prompt, disallowed_special=()))

            # 代码说明。
            self._token_cache.put(cache_key, token_count)
            results.append(token_count)

        return results

    def _generate_cache_key(self, model_name: str, prompt: str) -> str:
        """生成模型输出。"""
        # 代码说明。
        prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()
        return f"{model_name}:{prompt_hash}"

    def _get_or_create_encoding_model(self, model_name: str) -> Optional["Encoding"]:
        if model_name in self._cache:
            return self._cache[model_name]
        encoding_model = None
        try:
            import tiktoken

            logger.info(
                "tiktoken installed, using it to count tokens, tiktoken will download "
                "tokenizer from network, also you can download it and put it in the "
                "directory of environment variable TIKTOKEN_CACHE_DIR"
            )
        except ImportError:
            self._support_encoding = False
            logger.warning("tiktoken not installed, cannot count tokens")
            return None
        try:
            if not model_name:
                model_name = "gpt-3.5-turbo"
            encoding_model = tiktoken.model.encoding_for_model(model_name)
        except KeyError:
            logger.warning(
                f"{model_name}'s tokenizer not found, using cl100k_base encoding."
            )
            encoding_model = tiktoken.model.get_encoding("cl100k_base")
        if encoding_model:
            self._cache[model_name] = encoding_model
        return encoding_model

    def get_token_cache_stats(self) -> Dict[str, any]:
        """获取对应数据。"""
        return {
            "cache_size": len(self._token_cache.cache),
            "max_cache_size": self._token_cache.max_size,
            "memory_usage_bytes": self._token_cache.current_memory,
            "max_memory_bytes": self._token_cache.max_memory_bytes,
        }

    def clear_token_cache(self):
        """执行当前函数对应的业务逻辑。"""
        self._token_cache.clear()


class ProxyLLMClient(LLMClient):
    """外部服务连接和调用实现。"""

    executor: Executor
    model_names: List[str]

    def __init__(
        self,
        model_names: List[str],
        context_length: int = 4096,
        executor: Optional[Executor] = None,
        proxy_tokenizer: Optional[ProxyTokenizer] = None,
    ):
        self.model_names = model_names
        self.context_length = context_length
        self.executor = executor or ThreadPoolExecutor()
        self._proxy_tokenizer = proxy_tokenizer

    def __getstate__(self):
        """执行当前函数对应的业务逻辑。"""
        state = self.__dict__.copy()
        state.pop("executor")
        return state

    def __setstate__(self, state):
        """执行当前函数对应的业务逻辑。"""
        self.__dict__.update(state)
        self.executor = ThreadPoolExecutor()

    @property
    def proxy_tokenizer(self) -> ProxyTokenizer:
        """执行当前函数对应的业务逻辑。"""
        if not self._proxy_tokenizer:
            self._proxy_tokenizer = TiktokenProxyTokenizer()
        return self._proxy_tokenizer

    @classmethod
    def _resolve_env_vars(cls, value: Optional[str]) -> Optional[str]:
        """执行当前函数对应的业务逻辑。"""
        if not value:
            return None
        return _resolve_env_vars(value)

    @classmethod
    def param_class(cls) -> Type[LLMDeployModelParameters]:
        """执行当前函数对应的业务逻辑。"""
        return LLMDeployModelParameters

    @classmethod
    @abstractmethod
    def new_client(
        cls,
        model_params: LLMDeployModelParameters,
        default_executor: Optional[Executor] = None,
    ) -> "ProxyLLMClient":
        """创建对象实例。"""

    @classmethod
    def generate_stream_function(
        cls,
    ) -> Optional[Union[GenerateStreamFunction, AsyncGenerateStreamFunction]]:
        """生成模型输出。"""
        return None

    @classmethod
    def generate_function(
        cls,
    ) -> Optional[Union[GenerateFunction, AsyncGenerateFunction]]:
        """生成模型输出。"""
        return None

    async def generate(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> ModelOutput:
        """生成模型输出。"""
        return await blocking_func_to_async(
            self.executor, self.sync_generate, request, message_converter
        )

    def sync_generate(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> ModelOutput:
        """生成模型输出。"""
        output = None
        for out in self.sync_generate_stream(request, message_converter):
            output = out
        return output

    async def generate_stream(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> AsyncIterator[ModelOutput]:
        """生成模型输出。"""
        from starlette.concurrency import iterate_in_threadpool

        async for output in iterate_in_threadpool(
            self.sync_generate_stream(request, message_converter)
        ):
            yield output

    def sync_generate_stream(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> Iterator[ModelOutput]:
        """生成模型输出。"""

        raise NotImplementedError()

    async def models(self) -> List[ModelMetadata]:
        """执行当前函数对应的业务逻辑。"""
        return self._models()

    @property
    def default_model(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self.model_names[0]

    @cache
    def _models(self) -> List[ModelMetadata]:
        results = []
        for model in self.model_names:
            results.append(
                ModelMetadata(model=model, context_length=self.context_length)
            )
        return results

    def local_covert_message(
        self,
        request: ModelRequest,
        message_converter: Optional[MessageConverter] = None,
    ) -> ModelRequest:
        """执行当前函数对应的业务逻辑。"""
        if not message_converter:
            return request
        metadata = self._models[0].ext_metadata
        new_request = request.copy()
        new_messages = message_converter.convert(request.messages, metadata)
        new_request.messages = new_messages
        return new_request

    async def count_token(self, model: str, prompt: str) -> int:
        """执行当前函数对应的业务逻辑。"""
        if self.proxy_tokenizer.support_async():
            cnts = await self.proxy_tokenizer.count_token_async(model, [prompt])
            return cnts[0]
        counts = await blocking_func_to_async(
            self.executor, self.proxy_tokenizer.count_token, model, [prompt]
        )
        return counts[0]


def _is_async_function(
    func: Optional[
        Union[
            GenerateStreamFunction,
            AsyncGenerateStreamFunction,
            GenerateFunction,
            AsyncGenerateFunction,
        ]
    ],
) -> bool:
    """执行当前函数对应的业务逻辑。"""
    if func is None:
        return False

    return iscoroutinefunction(func) or isasyncgenfunction(func)


def register_proxy_model_adapter(
    client_cls: Type[ProxyLLMClient],
    supported_models: List[ModelMetadata],
):
    """注册对象。"""
    from meyo.model.adapter.base import register_model_adapter
    from meyo.model.adapter.proxy_adapter import ProxyLLMModelAdapter

    generate_stream_function = client_cls.generate_stream_function()
    is_async_stream = _is_async_function(generate_stream_function)
    generate_function = client_cls.generate_function()
    is_async = _is_async_function(generate_function)
    param_cls = client_cls.param_class()
    provider = param_cls.get_type_value()

    class _DynProxyLLMModelAdapter(ProxyLLMModelAdapter):
        """模型能力抽象或实现。"""

        __provider__ = provider

        def support_async(self) -> bool:
            return is_async_stream or is_async

        def match(
            self,
            _provider: str,
            model_name: Optional[str] = None,
            model_path: Optional[str] = None,
        ) -> bool:
            return _provider == provider

        def model_param_class(
            self, model_type: str = None
        ) -> Type[LLMDeployModelParameters]:
            return param_cls

        def supported_models(self) -> List[ModelMetadata]:
            return supported_models

        def do_match(self, lower_model_name_or_path: Optional[str] = None):
            raise NotImplementedError()

        def get_llm_client_class(
            self, params: LLMDeployModelParameters
        ) -> Type[ProxyLLMClient]:
            """获取对应数据。"""
            return client_cls

        def get_generate_stream_function(self, model, model_path: str):
            """获取对应数据。"""
            if not is_async_stream and generate_stream_function is not None:
                return generate_stream_function
            raise NotImplementedError("Sync generate stream not supported")

        def get_async_generate_stream_function(self, model, model_path: str):
            if is_async_stream and generate_stream_function is not None:
                return generate_stream_function
            raise NotImplementedError("Async generate stream not supported")

        def get_generate_function(self, model, model_path: str):
            """获取对应数据。"""
            if not is_async and generate_function is not None:
                return generate_function
            raise NotImplementedError

        def get_async_generate_function(self, model, model_path: str):
            """获取对应数据。"""
            if is_async and generate_function is not None:
                return generate_function
            raise NotImplementedError

    register_model_adapter(_DynProxyLLMModelAdapter)
