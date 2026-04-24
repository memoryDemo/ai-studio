"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, is_dataclass
from typing import Any, Callable, Coroutine, List, Union

from meyo._private.pydantic import BaseModel, model_to_json

SSE_DATA_TYPE = Union[str, BaseModel, dict]


async def run_async_tasks(
    tasks: List[Coroutine],
    concurrency_limit: int = None,
) -> List[Any]:
    """执行调用逻辑。"""
    tasks_to_execute: List[Any] = tasks

    async def _gather() -> List[Any]:
        if concurrency_limit:
            semaphore = asyncio.Semaphore(concurrency_limit)

            async def _execute_task(task):
                async with semaphore:
                    return await task

            # 代码说明。
            return await asyncio.gather(
                *[_execute_task(task) for task in tasks_to_execute]
            )
        else:
            return await asyncio.gather(*tasks_to_execute)

    # 执行相关操作。
    return await _gather()


def run_tasks(
    tasks: List[Callable],
    concurrency_limit: int = None,
) -> List[Any]:
    """执行调用逻辑。"""
    max_workers = concurrency_limit if concurrency_limit else None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 获取对应数据。
        futures = [executor.submit(task) for task in tasks]

        # 代码说明。
        results = []
        for future in futures:
            try:
                results.append(future.result())
            except Exception as e:
                # 代码说明。
                for f in futures:
                    f.cancel()
                raise e

    return results


def transform_to_sse(data: SSE_DATA_TYPE) -> str:
    """转换输入数据格式。"""
    if isinstance(data, BaseModel):
        return (
            f"data: {model_to_json(data, exclude_unset=True, ensure_ascii=False)}\n\n"
        )
    elif isinstance(data, dict):
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    elif isinstance(data, str):
        return f"data: {data}\n\n"
    elif is_dataclass(data):
        return f"data: {json.dumps(asdict(data), ensure_ascii=False)}\n\n"
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")
