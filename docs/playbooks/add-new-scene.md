---
title: 新增一个 Chat 场景(chat_mode)
---

# Playbook:新增一个 Chat 场景

## 1. 什么时候用这份 playbook

你的需求命中下面任意一条:

- 要一个新的"聊天模式",前端 `chat_mode` 传一个新值
- 要一种新的对话形态(和现有 `chat_normal` / `chat_with_db_execute` / `chat_knowledge` 等不同)
- 需要专属的 prompt 模板、专属的上下文装配

**不适用的情况**:

- 你只是想改 `chat_normal` 的 prompt 或加一点上下文 → 直接改 `scene/chat_normal/`,不用新建场景
- 你只是想加一个 HTTP 接口 → 看 [`add-new-api-endpoint.md`](./add-new-api-endpoint.md)
- 你要接一个新 AWEL 工作流 → 走 `chat_flow` 场景即可,不用新建 chat_mode

## 2. 主干定位

```
[4] Scene 分发 ← 你在这里加一套场景实现
     ├── scene/base.py                  # ChatScene 枚举:加一项
     ├── scene/<your_scene>/            # 新建目录:chat.py / config.py / prompt.py
     └── scene/chat_factory.py          # 顶部 import 里加两行(import 副作用注册)

[5] Serve 服务域 ← 如果新场景要用新的 Serve 能力(可选)
     └── umber-studio-serve/src/umber_studio_serve/...
```

**重要真相**:项目里有两个 "registry" 概念,别搞混:

| 概念 | 文件 | 用途 |
|---|---|---|
| ChatScene 枚举 | `scene/base.py` | **这才是新增 chat_mode 的必经之路** |
| `scene/registry.py`(SceneRegistration) | `scene/registry.py` | 次级注册表,用于 skill/flow/render_policy 的映射。目前只有 `financial-report-analyzer` 一个项,常规新场景**不需要**在这里注册 |
| prompt_template_registry | `CFG.prompt_template_registry` | prompt 模板运行时注册,通过 `scene/<x>/prompt.py` 里的 `.register(...)` 完成 |

## 3. 改动清单(5 步,带真实样板)

### 步骤 1:在 `ChatScene` 枚举加一项

编辑 `packages/umber-studio-app/src/umber_studio_app/scene/base.py`,在 `class ChatScene(Enum):` 里追加:

```python
MyNewScene = Scene(
    code="my_new_scene",                      # chat_mode 的值,snake_case,对前端契约
    name="My New Scene",                      # UI 展示名
    describe="<一句话描述这个场景做什么>",
    param_types=["DB Select"],                # 前端参数选择器的类型(可选)
    is_inner=False,                           # 是否只在内部使用(True = 不在"新对话"入口展示)
    show_disable=False,                       # 是否灰显
)
```

`param_types` 常见值:`"DB Select"` / `"Knowledge Space Select"` / `"File Select"` / `"Plugin Select"` / `"Flow Select"`。如果你的场景不需要选择器,留空。

> **红线**:`code` 一旦发布就不能改(这是前后端契约),所以命名要一次到位。

### 步骤 2:新建场景目录,至少 3 个文件

在 `packages/umber-studio-app/src/umber_studio_app/scene/` 下新建目录 `my_new_scene/`(snake_case,和 `code` 一致)。参考最简场景 `chat_normal/`:

```
scene/my_new_scene/
├── __init__.py     # 空文件
├── chat.py         # BaseChat 子类
├── config.py       # 场景配置(继承 GPTsAppCommonConfig)
├── prompt.py       # prompt 模板 + 注册
└── out_parser.py   # 输出解析器(可复用 chat_normal 的,非必需)
```

#### `__init__.py`

```python
```

(空文件即可)

#### `config.py`

```python
from dataclasses import dataclass, field
from typing import Optional

from umber_studio.util.i18n_utils import _
from umber_studio_app.scene import ChatScene
from umber_studio_serve.core.config import (
    BaseGPTsAppMemoryConfig,
    GPTsAppCommonConfig,
    TokenBufferGPTsAppMemoryConfig,
)


@dataclass
class MyNewSceneConfig(GPTsAppCommonConfig):
    """My New Scene Configuration"""

    name = ChatScene.MyNewScene.value()
    memory: Optional[BaseGPTsAppMemoryConfig] = field(
        default_factory=lambda: TokenBufferGPTsAppMemoryConfig(
            max_token_limit=20 * 1024
        ),
        metadata={"help": _("Memory configuration")},
    )
```

#### `chat.py`

```python
from typing import Type

from umber_studio import SystemApp
from umber_studio_app.scene import BaseChat, ChatScene
from umber_studio_app.scene.base_chat import ChatParam
from umber_studio_app.scene.my_new_scene.config import MyNewSceneConfig


class MyNewSceneChat(BaseChat):
    chat_scene: str = ChatScene.MyNewScene.value()

    @classmethod
    def param_class(cls) -> Type[MyNewSceneConfig]:
        return MyNewSceneConfig

    def __init__(self, chat_param: ChatParam, system_app: SystemApp):
        super().__init__(chat_param=chat_param, system_app=system_app)

    # 如需自定义 prompt 输入、上下文装配,重写 BaseChat 对应钩子
    # async def generate_input_values(self) -> dict: ...
```

#### `prompt.py`

```python
from umber_studio._private.config import Config
from umber_studio.core import (
    ChatPromptTemplate,
    HumanPromptTemplate,
    MessagesPlaceholder,
    SystemPromptTemplate,
)
from umber_studio_app.scene import AppScenePromptTemplateAdapter, ChatScene
from umber_studio_app.scene.chat_normal.out_parser import NormalChatOutputParser

PROMPT_SCENE_DEFINE_EN = "You are an expert assistant that ..."
PROMPT_SCENE_DEFINE_ZH = "你是一个擅长 … 的 AI 助手。"

CFG = Config()

PROMPT_SCENE_DEFINE = (
    PROMPT_SCENE_DEFINE_ZH if CFG.LANGUAGE == "zh" else PROMPT_SCENE_DEFINE_EN
)


prompt = ChatPromptTemplate(
    messages=[
        SystemPromptTemplate.from_template(PROMPT_SCENE_DEFINE),
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="media_input"),
        HumanPromptTemplate.from_template("{input}"),
    ]
)

prompt_adapter = AppScenePromptTemplateAdapter(
    prompt=prompt,
    template_scene=ChatScene.MyNewScene.value(),
    stream_out=True,
    output_parser=NormalChatOutputParser(),
)

CFG.prompt_template_registry.register(
    prompt_adapter, language=CFG.LANGUAGE, is_default=True
)
```

### 步骤 3:在 `chat_factory.py` 顶部 import 你的 chat 和 prompt(**必须**)

编辑 `packages/umber-studio-app/src/umber_studio_app/scene/chat_factory.py`,在 `get_implementation` 方法顶部的 import 列表里追加两行:

```python
from umber_studio_app.scene.my_new_scene.chat import MyNewSceneChat  # noqa: F401
from umber_studio_app.scene.my_new_scene.prompt import prompt  # noqa: F401, F811
```

> **为什么必须这么做(真相 & 常见踩坑)**:
>
> `ChatFactory.get_implementation` 通过 `BaseChat.__subclasses__()` 动态查找所有已被 Python 加载过的 `BaseChat` 子类。如果你不在这里 import,你的 `MyNewSceneChat` 类文件可能永远不会被执行,`__subclasses__()` 就发现不了它,运行时就会抛 `Invalid implementation name: my_new_scene`。
>
> 同样,`prompt.py` 必须被 import 才会触发 `CFG.prompt_template_registry.register(...)` 这句副作用,否则你的 prompt 根本没注册进去。

### 步骤 4:(可选)如果你的场景需要新的 Serve 能力

如果你的场景要调 DB、RAG、文件、Flow 的能力:

- 在 `packages/umber-studio-serve/src/umber_studio_serve/<域>/service/` 加业务方法,在 `api/` 暴露函数
- **绝不**在场景的 `chat.py` 里直接 `from umber_studio_serve.xxx.dao import ...`
- 参考 `.cursor/rules/30-serve-layer.mdc`

如果你的场景需要专属的上下文装配或工具逻辑:

- 优先扩展 `runtime/react_context_loader.py` / `runtime/react_toolkit_builder.py` 已有分支
- **不要**新建 `react_my_scene_*.py`
- 参考 `.cursor/rules/20-runtime-layer.mdc`

### 步骤 5:(可选)前端参数入口

如果你的场景需要在前端"新对话"菜单里出现:

1. 后端 `GET /api/v1/chat/dialogue/scenes` 的返回列表(见 `api_v1.py` 里的 `dialogue_scenes`)会自动列出 `ChatScene` 所有**非 inner** 的项,你的场景只要 `is_inner=False` 就会出现。
2. 如果需要参数选择器,`param_types` 要和前端已经支持的类型对齐(`DB Select` / `Knowledge Space Select` / `File Select` / `Plugin Select` / `Flow Select`)。
3. 前端具体改动参考 `add-frontend-page.md`(待补),或直接问前端同事。

## 4. 验证

### 验证 1:场景被正确注册

启动 WebServer:

```bash
uv run umber-studio start webserver --config configs/umber-studio-proxy-siliconflow-pg-milvus.toml
```

用 curl 打 `dialogue_scenes` 接口(需要 auth header):

```bash
curl -X POST http://127.0.0.1:5670/api/v1/chat/dialogue/scenes -H 'Content-Type: application/json'
```

确认返回里看到 `{"chat_scene": "my_new_scene", ...}`。

### 验证 2:场景能跑通

用 `/api/v1/chat/prepare` 和 `/api/v1/chat/completions` 触发一次对话,`chat_mode` 传 `my_new_scene`。

```bash
curl -X POST http://127.0.0.1:5670/api/v1/chat/prepare \
  -H 'Content-Type: application/json' \
  -d '{"chat_mode":"my_new_scene","user_input":"hello","user_name":"test"}'
```

能拿到 `success=True` 的响应,且日志里能看到 `ChatNormal` / `MyNewSceneChat` 的加载轨迹。

### 验证 3:形式化检查

```bash
make fmt
make fmt-check
make mypy
make test
```

## 5. PR 描述模板

```markdown
## 主干定位
- 落在【Scene 分发】主干,新增 chat_mode `my_new_scene`
- 动了:
  - `scene/base.py`(ChatScene 枚举 +1 项)
  - `scene/my_new_scene/`(chat.py / config.py / prompt.py)
  - `scene/chat_factory.py`(顶部 import 新场景,触发副作用注册)

## 边界检查
- 依赖方向:✅
- 绕过主干:✅(新场景通过 ChatFactory.get_implementation 正常分发)
- prompt 注册是否依赖 chat_factory 的 import:✅ 已在顶部加 import

## 红线检查
- [ ] 没在 runtime 新建 react_*.py:✅
- [ ] 没在 API 层 import serve.dao:✅
- [ ] prompt 已在 chat_factory 顶部 import 触发注册:✅
- [ ] ChatScene 的 `code` 是新的、snake_case、未与现有冲突:✅

## 验证
- [x] make fmt-check / mypy / test
- [x] 本地启动 + curl /v1/chat/dialogue/scenes 能看到新场景
- [x] 本地 curl /v1/chat/prepare 能成功

## 影响面
- 前后端契约:新增 chat_mode `my_new_scene`,已通知前端
- 需同步文档:是,更新 `docs/docs/application/base_project/menu_and_feature_map.md` 场景表格
- 前端联调:需要(新增场景的前端入口)
```

## 反模式速查

| 症状 | 问题 | 正确做法 |
|---|---|---|
| 新建了 `scene/my_new_scene/chat.py` 但运行时报 `Invalid implementation name` | 没在 `chat_factory.py` 顶部 import | 补 import,两行都要(chat + prompt) |
| Prompt 修改没生效 | `prompt.py` 没被 import,`register(...)` 没执行 | 同上,确认 `chat_factory.py` import 了 prompt |
| 直接改 `scene/registry.py` 期望注册新场景 | 搞错了 registry,那个是 skill/flow 的 | 走本 playbook 三件套 |
| 在 `chat.py` 里 `from umber_studio_serve.conversation.dao import ...` | 破坏依赖方向 | 走 serve 对应域的 `api/` |
| 新建了 `runtime/react_my_scene_session.py` | 违反 runtime 红线 | 扩展现有 `react_session.py` 或 `react_context_loader.py` |
| `ChatScene.MyNewScene` 的 code 后来又改名 | 破坏前后端契约 | 一次命名到位 |
