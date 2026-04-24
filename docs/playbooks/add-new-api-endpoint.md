---
title: 新增一个 HTTP 接口
---

# Playbook：新增一个 HTTP 接口

## 1. 什么时候用这份 playbook

你的需求命中下面任意一条：

- 前端要调一个新的接口拿数据或触发动作
- 第三方系统要调用一个新接口
- 需要一个内部工具接口做调试或人工触发

**当前状态说明：**

`Meyo` 当前还没有完整的 FastAPI / OpenAPI 目录，所以这份 playbook 已经按当前仓库改写成“**预置可落地版本**”。

也就是说：

- 如果你是在补**第一个** HTTP 入口，需要先把 `app` 层 API 骨架建出来
- 如果仓库以后已经有 `openapi/` 目录，这份 playbook 就可以直接按常规步骤使用

**不适用的情况：**

- 你要加一个新的场景分发层 → 看 [`add-new-scene.md`](./add-new-scene.md)
- 你要接一个新的 runtime / gateway adapter → 先改 `ext`

## 2. 主干定位

```text
[2] API 入口
     └── packages/meyo-app/src/meyo_app/openapi/

[3] App 装配
     └── packages/meyo-app/src/meyo_app/

[5] Serve 服务域
     └── packages/meyo-serve/src/meyo_serve/
```

你不应该在路由函数里直接调 `ext` 或 `core` 的具体实现。

正确方向是：

`app/openapi -> serve -> core contracts / ext implementation`

## 3. 改动清单

### 步骤 1：先确认 API 骨架是否存在

如果下面这些目录还不存在，先补最小骨架：

```text
packages/meyo-app/src/meyo_app/openapi/
├── __init__.py
├── api_v1.py
└── view_models.py
```

如果你是在补仓库里的第一个 API，这一步是必须的。

### 步骤 2：定义入参出参模型

HTTP 视角的入参出参模型，建议放在：

```text
packages/meyo-app/src/meyo_app/openapi/view_models.py
```

系统级运行时模型继续放在：

```text
packages/meyo-core/src/meyo/contracts/models.py
```

最小模板：

```python
from pydantic import BaseModel, Field


class CreateRunRequestVo(BaseModel):
    thread_id: str = Field(..., description="thread id")
    input: str = Field(..., description="user input")
```

### 步骤 3：先在 `serve` 层暴露应用服务

如果接口背后对应的是一个真实 use case，就先在 `serve` 层提供稳定服务入口。

当前最接近的样板是：

```text
packages/meyo-serve/src/meyo_serve/run_service.py
```

原则：

- 路由不直接拼业务
- 路由不直接 new 底层实现
- 路由调 `RunService` 这类服务层对象

### 步骤 4：在 `app` 层写 FastAPI 路由并完成挂载

如果你已经有 FastAPI app，对应路由函数最小模板可以是：

```python
import logging
from fastapi import APIRouter

from meyo_app.openapi.view_models import CreateRunRequestVo

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/v1/runs")
async def create_run(req: CreateRunRequestVo):
    logger.info("create_run: thread_id=%s", req.thread_id)
    return {"ok": True}
```

### 步骤 5：做最小验证

当前仓库最小验证建议：

```bash
python -m compileall packages
```

如果你已经把 FastAPI app 起起来了，再补：

```bash
uv run pytest
```

## 4. 验证

至少确认：

- 新路由没有越过 `serve`
- `app` 里没有直接 import `ext` 的具体实例去处理业务
- `core` 没被写进 FastAPI / HTTP 细节
- `python -m compileall packages` 通过

## 5. 影响面说明

```markdown
## 主干定位
- 落在【API 入口】主干
- 路由所在位置：`packages/meyo-app/src/meyo_app/openapi/`
- 服务入口：`packages/meyo-serve/src/meyo_serve/`

## 边界检查
- 路由只调 `serve`，没有越过服务层直接调 `ext` 具体实现
- `core` 没有新增 HTTP 细节

## 验证
- [x] python -m compileall packages
- [ ] uv run pytest

## 影响面
- 是否引入了第一个 FastAPI / OpenAPI 骨架
- 是否新增了外部 HTTP 契约
- 是否需要同步文档
```
