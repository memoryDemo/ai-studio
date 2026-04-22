---
title: 新增一个 HTTP 接口
---

# Playbook:新增一个 HTTP 接口

## 1. 什么时候用这份 playbook

你的需求命中下面任意一条:

- 前端要调一个新的接口拿数据或触发动作
- 第三方系统要用一个新的接口
- 需要一个内部工具接口(调试、手动触发同步等)

**不适用的情况**(请看其他 playbook):

- 你要加一个新的"聊天模式" → 看 [`add-new-scene.md`](./add-new-scene.md)
- 你要接一个新数据源 → 看 `add-new-datasource.md`(待补)

## 2. 主干定位

```
[2] API 入口 ← 你在这一层加东西
     ├── packages/umber-studio-app/src/umber_studio_app/openapi/api_v1/*.py
     └── packages/umber-studio-app/src/umber_studio_app/openapi/api_v2.py
```

你**不**应该在这个 playbook 里动:`runtime/`、`scene/`、`umber-studio-serve/`。
如果你发现自己必须动它们中任何一个,说明这不是一个"纯新增接口"需求,回头找 Lead 讨论。

## 3. 改动清单(5 步)

### 步骤 1:选一个归属子模块

看一下 `packages/umber-studio-app/src/umber_studio_app/openapi/api_v1/` 下现有子模块:

```
api_v1/
├── agentic_data_api.py     # 工作区、数据态、agent 级聚合入口(最常用的样板)
├── api_v1.py               # 核心聚合 router(chat / db / model / file)
├── editor/                 # 编辑器相关
├── feedback/               # 用户反馈
├── links/                  # 链接/分享
├── examples_api.py         # 内置示例
└── python_upload_api.py    # Python 代码上传
```

**选择原则**:能归到已有子模块就不新建;只有当你确信这是一个全新业务域(且 Lead 同意)时才新建一个 `<domain>_api.py`。

### 步骤 2:定义入参出参模型(Pydantic)

集中在 `packages/umber-studio-app/src/umber_studio_app/openapi/api_view_model.py`。

> **红线**:不要在路由函数里直接写 `dict` 做入参,也不要在路由函数所在文件里随手定义模型类。模型要么放 `api_view_model.py`,要么放 `editor_view_model.py`(编辑器专属)。

追加一个请求模型的最小模板:

```python
from umber_studio._private.pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class MyNewRequestVo(BaseModel):
    """<一句话说明这个请求做什么>"""

    model_config = ConfigDict(protected_namespaces=())

    conv_uid: str = Field(..., description="会话 uid")
    some_param: Optional[str] = Field(None, description="<业务字段含义>")
```

响应用统一的 `Result[T]`,`T` 可以是 `bool` / `str` / `List[XxxVo]` / `dict`。如果 `T` 是复杂对象,也在 `api_view_model.py` 定义 `XxxVo`。

### 步骤 3:写路由函数

在步骤 1 选中的文件里追加。**路由函数只做 3 件事:解析入参 → 调下游 → 包装返回**。

同步(非流式)接口模板:

```python
import logging
from fastapi import Body, Depends
from umber_studio_app.openapi.api_view_model import Result, MyNewRequestVo
from umber_studio_serve.utils.auth import UserRequest, get_user_from_headers

logger = logging.getLogger(__name__)


@router.post("/v1/chat/my-new-endpoint", response_model=Result[dict])
async def my_new_endpoint(
    req: MyNewRequestVo = Body(),
    user_token: UserRequest = Depends(get_user_from_headers),
):
    logger.info(f"my_new_endpoint: conv_uid={req.conv_uid}, user={user_token.user_id}")
    try:
        # 1) 调下游(Scene / Serve 的 api/,绝不直接 import dao 或 umber_studio.*)
        result = await _do_business(req, user_token.user_id)
        # 2) 包装返回
        return Result.succ(result)
    except ValueError as e:
        return Result.failed(code="E1001", msg=str(e))
    except Exception as e:
        logger.exception("my_new_endpoint failed")
        return Result.failed(code="E1000", msg=str(e))
```

流式接口模板(SSE):

```python
from fastapi.responses import StreamingResponse


@router.post("/v1/chat/my-stream-endpoint")
async def my_stream_endpoint(
    req: MyNewRequestVo = Body(),
    user_token: UserRequest = Depends(get_user_from_headers),
):
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Transfer-Encoding": "chunked",
    }
    return StreamingResponse(
        _do_streaming(req, user_token.user_id),
        headers=headers,
        media_type="text/event-stream",
    )
```

**命名规范**:

- 路由路径必须带版本前缀:`/v1/...` 或 `/v2/...`
- 业务前缀按域划分:`/v1/chat/...`、`/v1/resource/...`、`/v1/feedback/...`、`/v1/permission/...`
- 不要出现 `/api/my_new_thing` 这种无版本、无域的路径

### 步骤 4:确认 router 被挂进 FastAPI

大多数情况你**不需要动这一步**——只要你的文件里有一个 `router = APIRouter()`,并且这个文件已经被 `openapi/api_v1/api_v1.py` 或 `umber_studio_server.py` 导入/include,路由就自动生效。

**例外**:如果你**新建了一个子模块文件**(步骤 1 里极少发生),必须去检查下列两处之一,确保 router 被 include:

```python
# packages/umber-studio-app/src/umber_studio_app/openapi/api_v1/api_v1.py
# 或 umber_studio_server.py 的 mount_routers 函数
from umber_studio_app.openapi.api_v1.<your_new_module> import router as your_router
app.include_router(your_router, prefix="/api")
```

> **红线**:不要自己在业务模块里 `app.include_router(...)`,include 只能发生在聚合层。

### 步骤 5:写一个最小集成测试

在 `tests/` 下新建或扩展一个测试文件(命名 `test_<module>.py`)。最小用例至少覆盖:

- 请求成功路径(返回 `success=True`)
- 请求失败路径(参数错误 / 无权限)

```python
from fastapi.testclient import TestClient


def test_my_new_endpoint_success(test_client: TestClient, auth_headers: dict):
    resp = test_client.post(
        "/api/v1/chat/my-new-endpoint",
        json={"conv_uid": "abc-123", "some_param": "x"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
```

## 4. 验证

在仓库根目录依次跑(**全部通过**才能提 PR):

```bash
make fmt              # 自动格式化
make fmt-check        # 格式化自检
make mypy             # 类型检查(至少 core 层通过)
make test             # 单元 + 集成测试
```

手动联调:

```bash
uv run umber-studio start webserver --config configs/umber-studio-proxy-siliconflow-pg-milvus.toml
```

用 `curl` 或 Postman 打你新增的接口,确认:

- 返回的 JSON 结构是 `{"success": ..., "err_code": ..., "err_msg": ..., "data": ...}`
- 日志里能看到你写的 `logger.info(...)`
- 流式接口能看到 `data: ...` 一行行吐出来

## 5. PR 描述模板

```markdown
## 主干定位
- 落在【API 入口】主干,新增接口 `POST /api/v1/<path>`
- 归属子模块:`packages/umber-studio-app/src/umber_studio_app/openapi/api_v1/<file>.py`
- 入参出参模型:`api_view_model.py` 中新增 `MyNewRequestVo`

## 边界检查
- 依赖方向:✅(本改动只读 serve 的 `api/` 公开函数,未 import dao/models)
- 绕过主干:✅(未直接调 runtime,也未直接读 DB)

## 红线检查
- [ ] API 层 import serve.dao 或 umber_studio.*:❌ 未命中
- [ ] 新建顶级目录/子模块:❌ 未命中(或"命中 + 已讨论")
- [ ] `except Exception: pass` / `print`:❌ 未命中

## 验证
- [x] make fmt-check
- [x] make mypy
- [x] make test
- [x] 手动 curl:<贴一条 curl 示例 + 返回>

## 影响面
- 前后端契约:是,新增 `MyNewRequestVo` 与响应 schema;已通知前端
- 需同步文档:否(接口较小)/ 是(同步到 `docs/docs/.../api-reference.md`)
- 前端联调:需要 / 不需要
```

## 反模式速查(这样写会被打回)

| 症状 | 问题 | 正确做法 |
|---|---|---|
| 路由函数里 `from umber_studio_serve.xxx.dao import ...` | 破坏依赖方向 | 调 serve 对应域的 `api/` |
| 路由函数参数是 `data: dict = Body()` | 没走 Pydantic | 定义 `XxxVo` 放 `api_view_model.py` |
| 返回 `return {"ok": True}` | 没走统一 `Result[T]` | 用 `Result.succ(...)` |
| 自己 `fastapi.FastAPI()` 并 include_router | 绕过聚合层 | 让聚合层自动 include |
| 硬编码中文错误消息 | 弱 i18n | 用错误码 + 英文 key,前端按 key 本地化 |
| 接口路径 `/my_thing` 无版本 | 版本失控 | `/v1/<domain>/<action>` |
