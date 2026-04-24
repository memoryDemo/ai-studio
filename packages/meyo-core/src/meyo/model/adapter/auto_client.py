"""模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。"""

from meyo.core import LLMClient


class AutoLLMClient(LLMClient):
    def __init__(self, provider: str, name: str, **kwargs):
        from meyo.model import scan_model_providers
        from meyo.model.adapter.base import get_model_adapter
        from meyo.model.adapter.proxy_adapter import ProxyLLMModelAdapter

        scan_model_providers()

        kwargs["name"] = name
        adapter = get_model_adapter(provider, model_name=name)
        if not adapter:
            raise ValueError(
                f"Can not find adapter for model {name} and provider {provider}"
            )
        if not isinstance(adapter, ProxyLLMModelAdapter):
            raise ValueError(
                f"Now only support proxy model, but got {adapter.model_type()}"
            )
        param_cls = adapter.model_param_class()
        param = param_cls(**kwargs)
        model, _ = adapter.load_from_params(param)
        self._client_impl = model.proxy_llm_client

    def __getattr__(self, name: str):
        """执行当前函数对应的业务逻辑。"""
        if hasattr(self._client_impl, name):
            return getattr(self._client_impl, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def generate(self, *args, **kwargs):
        return self._client_impl.generate(*args, **kwargs)

    def generate_stream(self, *args, **kwargs):
        return self._client_impl.generate_stream(*args, **kwargs)

    def count_token(self, *args, **kwargs):
        return self._client_impl.count_token(*args, **kwargs)

    def models(self, *args, **kwargs):
        return self._client_impl.models(*args, **kwargs)
