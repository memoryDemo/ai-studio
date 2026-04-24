"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import asyncio
import contextvars
from abc import ABC, abstractmethod
from concurrent.futures import Executor, ThreadPoolExecutor
from functools import partial
from typing import Any, Callable

from meyo.component import BaseComponent, ComponentType, SystemApp


class ExecutorFactory(BaseComponent, ABC):
    name = ComponentType.EXECUTOR_DEFAULT.value

    @abstractmethod
    def create(self) -> "Executor":
        """创建对象实例。"""


class DefaultExecutorFactory(ExecutorFactory):
    def __init__(self, system_app: SystemApp | None = None, max_workers=None):
        super().__init__(system_app)
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix=self.name
        )

    def init_app(self, system_app: SystemApp):
        pass

    def create(self) -> Executor:
        return self._executor


BlockingFunction = Callable[..., Any]


async def blocking_func_to_async(
    executor: Executor, func: BlockingFunction, *args, **kwargs
):
    """执行当前函数对应的业务逻辑。"""
    if asyncio.iscoroutinefunction(func):
        raise ValueError(f"The function {func} is not blocking function")

    # 代码说明。
    ctx = contextvars.copy_context()

    def run_with_context():
        return ctx.run(partial(func, *args, **kwargs))

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, run_with_context)


async def blocking_func_to_async_no_executor(func: BlockingFunction, *args, **kwargs):
    """执行当前函数对应的业务逻辑。"""
    return await blocking_func_to_async(None, func, *args, **kwargs)  # type: ignore


class AsyncToSyncIterator:
    def __init__(self, async_iterable, loop: asyncio.BaseEventLoop):
        self.async_iterable = async_iterable
        self.async_iterator = None
        self._loop = loop

    def __iter__(self):
        self.async_iterator = self.async_iterable.__aiter__()
        return self

    def __next__(self):
        if self.async_iterator is None:
            raise StopIteration

        try:
            return self._loop.run_until_complete(self.async_iterator.__anext__())
        except StopAsyncIteration:
            raise StopIteration
