# 接入模型 Provider 和 Worker Manager
> 这一节记录模型服务后端的开发顺序：先把配置和模型抽象立住，再接 SiliconFlow，最后用 worker manager 把模型服务跑起来

上一节已经把 Meyo 的基础依赖补齐了。

这一节开始做模型服务。

目标不是先写一个聊天接口，而是先做出一条完整的后端运行链路：

```text
配置文件
-> 模型参数
-> provider
-> worker
-> controller / registry
-> apiserver
-> app 启动
```

本次只接一个供应商：

```text
provider = "proxy/siliconflow"
```

并且先覆盖三种模型能力：

```text
LLM       chat / completion
Embedding 文本向量
Rerank    相关性排序
```

前端不在这一节做。Open WebUI 和 admin 前端后续都作为独立前端项目调用 Meyo 后端 API。

## 1. 先做配置解析

第一步先做配置解析。

原因是模型服务不能硬编码模型和密钥。后端应该从 TOML 里读出要启动哪些模型、用哪个 provider、密钥从哪个环境变量读取。

这一层主要解决：

- 支持 TOML 配置
- 支持 `${env:KEY}` 读取环境变量
- 支持 `.env` 本地开发变量
- 支持 `meyo.toml`、`/meyo.toml`、`configs/meyo.toml` 这几种路径写法

相关文件：

```text
packages/meyo-app/src/meyo_app/meyo_server.py
packages/meyo-core/src/meyo/_private/config.py
packages/meyo-core/src/meyo/_private/pydantic.py
packages/meyo-core/src/meyo/util/configure/
configs/meyo.toml
.env.example
```

为什么先做它：

如果配置解析不稳定，后面的 provider、worker、apiserver 都不知道该启动什么模型。

## 2. 再做模型参数

第二步做模型参数结构。

配置文件里的内容只是普通字典，不能直接交给模型服务运行。需要先解析成明确的参数对象。

这一层主要解决：

- LLM 参数
- Embedding 参数
- Rerank 参数
- Worker 参数
- API server 参数
- provider 名称到具体参数类的映射

相关文件：

```text
packages/meyo-core/src/meyo/model/parameter.py
packages/meyo-core/src/meyo/core/interface/parameter.py
packages/meyo-core/src/meyo/configs/model_config.py
```

为什么第二步做它：

worker manager 后面要按参数对象启动 worker。如果没有参数层，启动逻辑就会变成一堆临时字典判断。

## 3. 再做 core 接口

第三步做 core 接口。

provider 和 worker 不能各自定义一套输入输出，否则 API 层会很难统一。

这一层主要解决：

- 模型消息结构
- 模型输出结构
- LLM 基础接口
- Embedding 基础接口
- Rerank 基础接口
- API 请求和响应 schema

相关文件：

```text
packages/meyo-core/src/meyo/core/interface/
packages/meyo-core/src/meyo/core/schema/
packages/meyo-core/src/meyo/rag/embedding/
```

为什么第三步做它：

这是 provider、worker、apiserver 之间的共同语言。共同语言确定后，后面的层只需要围绕接口实现。

## 4. 再做 provider 基础层

第四步做 provider 基础层。

SiliconFlow 是具体供应商，但它不应该直接散落在 worker 或 API 里。它要挂在统一的 provider/proxy 模型体系下。

这一层主要解决：

- 代理模型基础类
- OpenAI-compatible 客户端
- 模型请求解析
- 流式输出适配
- provider 注册入口

相关文件：

```text
packages/meyo-core/src/meyo/model/base.py
packages/meyo-core/src/meyo/model/proxy/base.py
packages/meyo-core/src/meyo/model/proxy/llms/chatgpt.py
packages/meyo-core/src/meyo/model/proxy/llms/proxy_model.py
packages/meyo-core/src/meyo/model/adapter/
packages/meyo-core/src/meyo/model/utils/
```

为什么第四步做它：

这样以后新增别的供应商时，只需要新增 provider 实现，不需要改 worker manager 和 API 层。

## 5. 再接 SiliconFlow

第五步接 SiliconFlow。

这时底层配置、参数、接口、provider 基础层都已经有了，SiliconFlow 只需要作为一个具体 provider 挂进去。

这一层主要解决：

- SiliconFlow LLM
- SiliconFlow embedding
- SiliconFlow rerank
- 默认 API base
- 从 `SILICONFLOW_API_KEY` 读取密钥

相关文件：

```text
packages/meyo-core/src/meyo/model/proxy/llms/siliconflow.py
packages/meyo-ext/src/meyo_ext/rag/embeddings/siliconflow.py
configs/meyo.toml
configs/meyo-proxy-siliconflow.toml
```

为什么第五步做它：

如果先写 SiliconFlow 文件，代码会到处依赖临时结构。先把基础层做好，再接 provider，代码边界会清楚很多。

## 6. 再做 worker

第六步做 worker。

provider 只负责“怎么调用模型供应商”，worker 负责“把这个 provider 跑成一个后端运行单元”。

这一层主要解决：

- 启动 LLM worker
- 启动 embedding worker
- 启动 rerank worker
- 执行模型调用
- 向 controller 注册自己
- 定时心跳

相关文件：

```text
packages/meyo-core/src/meyo/model/cluster/worker/
packages/meyo-core/src/meyo/model/cluster/worker_base.py
packages/meyo-core/src/meyo/model/cluster/embedding/
```

为什么第六步做它：

后端不是直接调用 provider 文件，而是通过 worker 承接模型运行。这样本地进程、远程进程、多模型实例都可以用同一种管理方式。

## 7. 再做 controller 和 registry

第七步做 controller 和 registry。

worker 启动后，需要有一个地方记录“现在有哪些模型可以用”。这个地方就是 controller 和 registry。

这一层主要解决：

- worker 注册
- worker 心跳
- 模型实例列表
- 模型地址查询
- 模型可用性管理

相关文件：

```text
packages/meyo-core/src/meyo/model/cluster/controller/
packages/meyo-core/src/meyo/model/cluster/registry.py
packages/meyo-core/src/meyo/model/cluster/registry_impl/
packages/meyo-core/src/meyo/model/cluster/storage.py
```

为什么第七步做它：

API 层不应该自己维护 worker 状态。API 层只问 controller：某个模型现在该发给哪个 worker。

## 8. 再做 worker manager

第八步做 worker manager。

worker manager 是这一节的核心。它把配置里的模型列表变成真实运行的 worker。

它的工作顺序是：

```text
读取 models.llms / models.embeddings / models.rerankers
-> 根据 provider 找到参数类
-> 根据参数创建模型实例
-> 创建对应 worker
-> 启动 worker
-> 注册到 controller
```

相关文件：

```text
packages/meyo-core/src/meyo/model/cluster/worker/manager.py
packages/meyo-core/src/meyo/model/cluster/manager_base.py
```

为什么第八步做它：

前面几层都只是“能力零件”。worker manager 才是把这些零件组装成模型服务的地方。

## 9. 最后做 apiserver

第九步做 apiserver。

worker 已经能跑，controller 已经能找到 worker，这时才适合对外开放 API。

这一层主要解决：

- `/api/v1/chat/completions`
- `/api/v1/embeddings`
- `/api/v1/beta/relevance`
- `/api/v1/models`
- 流式响应
- 错误响应

相关文件：

```text
packages/meyo-core/src/meyo/model/cluster/apiserver/api.py
```

为什么最后做它：

API 是最外层出口。它不应该直接了解 provider 细节，只需要通过 controller 找 worker，再把请求转发过去。

## 10. 接到 app 启动

最后一步把整条链路接到 `meyo start webserver`。

启动顺序是：

```text
load_config
-> scan_model_providers
-> initialize_worker_manager_in_client
-> initialize_apiserver
-> mount_static_files
-> run_uvicorn
```

相关文件：

```text
packages/meyo-app/src/meyo_app/_cli.py
packages/meyo-app/src/meyo_app/meyo_server.py
```

为什么最后接 app：

app 层只负责装配，不负责模型调用细节。这样后续 Open WebUI、admin 前端、其它客户端都只需要调用 API，不需要关心后端内部怎么启动模型。

## 11. 当前验证方式

先验证配置能读：

```bash
SILICONFLOW_API_KEY=test uv run python - <<'PY'
from meyo_app.meyo_server import load_config
config = load_config('meyo.toml')
print(config.models.llms[0].provider)
PY
```

再验证语法：

```bash
uv run python -m compileall -q packages
```

启动服务：

```bash
uv run meyo start webserver --config meyo.toml
```

如果配置里用了：

```toml
api_key = "${env:SILICONFLOW_API_KEY}"
```

本地需要二选一：

```bash
export SILICONFLOW_API_KEY=你的真实key
```

或者创建 `.env`：

```bash
cp .env.example .env
```

然后把 `.env` 里的 `SILICONFLOW_API_KEY` 改成真实值。

`.env` 已经被 `.gitignore` 忽略，不会提交。

配置文件分两类：

- `configs/meyo.toml`：默认公开配置，不传 `--config` 时会读取它。
- `configs/meyo-*.toml`：可提交的公开配置模板，启动时直接写 `--config 文件名.toml`。
- `configs/my/`：个人本地覆盖目录，默认被忽略，不作为团队共享配置。

当前只默认启用 SiliconFlow 远程 provider。`fschat_adapter.py`、HF、vLLM、MLX、llama.cpp 这些本地模型适配器是模型运行层的预留能力，不是默认启动链路。只跑 SiliconFlow 时不需要安装 `fastchat` 和 `torch`。

## 12. 后续开发原则

后面继续接其它模型供应商时，按同样顺序开发：

```text
先补参数
再补 provider
再确认 worker manager 能识别
最后确认 apiserver 能调用
```

不要从 API 层直接写供应商逻辑。

也不要一开始就写前端。

先把后端模型服务链路稳定下来，再让独立前端来调用。

## 13. 本批次到底做了一件什么事

短答：是，一件事。

今天这批代码只服务一个目标：让 Meyo 后端可以从配置启动并管理 SiliconFlow 模型服务。

但它不是只改 `worker manager` 一个文件。`worker manager` 是中间的组装器，它要能工作，前面必须有配置、参数、provider、模型接口，后面必须有 controller、registry、apiserver 和 app 启动装配。

所以这批一百多个文件可以理解成一个主题：

```text
model worker manager 驱动的模型服务运行链路
```

不是多个业务方向同时开发。

## 14. 本批次文件索引

下面把这批涉及的文件都列出来。看文件时可以按这个顺序理解：先看 app/config，再看 core/model，再看 ext/provider，最后看 serve 和删除项。

### 14.1 meyo-app：应用启动层

- `packages/meyo-app/src/meyo_app/__init__.py`：包入口，集中导出当前目录下的能力。
- `packages/meyo-app/src/meyo_app/_cli.py`：应用层模块，负责后端启动装配和服务入口组织。
- `packages/meyo-app/src/meyo_app/cli.py`：应用层模块，负责后端启动装配和服务入口组织。
- `packages/meyo-app/src/meyo_app/config.py`：应用配置定义，负责把开发配置文件解析为网页服务、模型服务和系统参数。
- `packages/meyo-app/src/meyo_app/meyo_server.py`：后端应用启动装配，负责创建服务应用、初始化模型服务并挂载路由。

### 14.2 meyo-core：模型服务核心层

- `packages/meyo-core/src/meyo/__init__.py`：包入口，集中导出当前目录下的能力。
- `packages/meyo-core/src/meyo/_private/config.py`：配置基础能力，提供环境变量替换、路径解析和参数对象构造的通用实现。
- `packages/meyo-core/src/meyo/_private/pydantic.py`：数据校验兼容导出层，统一项目内部对数据模型库的引用入口。
- `packages/meyo-core/src/meyo/cli/__init__.py`：包入口，集中导出当前目录下的能力。
- `packages/meyo-core/src/meyo/cli/cli_scripts.py`：后端模型服务运行链路模块，负责补齐当前目录对应的基础能力。
- `packages/meyo-core/src/meyo/component.py`：系统组件和应用上下文定义，用于在模型服务启动时共享运行时对象。
- `packages/meyo-core/src/meyo/configs/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/configs/model_config.py`：模型服务配置常量和默认路径定义，集中管理开发配置、日志和静态资源位置。
- `packages/meyo-core/src/meyo/core/__init__.py`：核心公共导出入口，向上层暴露模型、消息、向量生成和结构定义。
- `packages/meyo-core/src/meyo/core/_private/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/core/_private/prompt_registry.py`：提示词模板注册辅助模块，预留给后续提示词管理和复用能力。
- `packages/meyo-core/src/meyo/core/interface/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/core/interface/cache.py`：缓存接口定义，约束模型服务和后续业务缓存实现的基础协议。
- `packages/meyo-core/src/meyo/core/interface/embeddings.py`：向量生成基础接口定义，统一向量模型的调用协议。
- `packages/meyo-core/src/meyo/core/interface/knowledge.py`：知识对象接口定义，为后续知识库和检索增强能力提供基础数据结构。
- `packages/meyo-core/src/meyo/core/interface/llm.py`：大语言模型基础接口和消息输出定义，是对话与补全能力的核心抽象。
- `packages/meyo-core/src/meyo/core/interface/media.py`：多媒体消息接口定义，用于描述图片、音频等模型输入输出载体。
- `packages/meyo-core/src/meyo/core/interface/message.py`：模型消息结构定义，统一对话请求、响应和流式消息的数据格式。
- `packages/meyo-core/src/meyo/core/interface/parameter.py`：参数模型基础接口，负责描述供应商、工作进程和服务配置的可解析结构。
- `packages/meyo-core/src/meyo/core/interface/serialization.py`：序列化接口定义，统一复杂对象在模型服务链路中的转换方式。
- `packages/meyo-core/src/meyo/core/interface/storage.py`：存储接口定义，为缓存、向量库、图存储和知识库提供统一抽象。
- `packages/meyo-core/src/meyo/core/schema/api.py`：开放接口兼容结构和通用响应结构，供接口服务直接复用。
- `packages/meyo-core/src/meyo/core/schema/ext_types.py`：扩展类型定义，补充接口结构和配置解析中需要的特殊字段类型。
- `packages/meyo-core/src/meyo/core/schema/types.py`：核心通用类型定义，支撑模型接口、接口结构和存储接口复用。
- `packages/meyo-core/src/meyo/datasource/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/datasource/base.py`：数据源基础抽象，定义外部数据连接器的统一生命周期和调用接口。
- `packages/meyo-core/src/meyo/datasource/parameter.py`：数据源参数定义，负责描述外部连接器初始化所需的配置项。
- `packages/meyo-core/src/meyo/datasource/rdbms/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/datasource/rdbms/base.py`：关系型数据库数据源基础实现，统一数据库连接和查询能力。
- `packages/meyo-core/src/meyo/model/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/adapter/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/adapter/auto_client.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/base.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/embed_metadata.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/fschat_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/hf_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/llama_cpp_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/llama_cpp_py_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/loader.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/mlx_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/model_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/model_metadata.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/proxy_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/template.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/adapter/vllm_adapter.py`：模型适配器实现，负责把不同推理后端统一成项目内的模型调用接口。
- `packages/meyo-core/src/meyo/model/base.py`：模型实例和输出基础结构，连接供应商、工作进程和接口响应。
- `packages/meyo-core/src/meyo/model/cluster/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/cluster/apiserver/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/cluster/apiserver/api.py`：模型服务接口层，负责路由、鉴权、错误处理和流式响应。
- `packages/meyo-core/src/meyo/model/cluster/base.py`：模型服务运行层基础模块，连接工作进程、控制器、注册表和接口服务。
- `packages/meyo-core/src/meyo/model/cluster/client.py`：模型服务运行层基础模块，连接工作进程、控制器、注册表和接口服务。
- `packages/meyo-core/src/meyo/model/cluster/controller/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/cluster/controller/controller.py`：模型控制器实现，负责维护工作进程注册、心跳和模型实例查询。
- `packages/meyo-core/src/meyo/model/cluster/controller/ray_controller.py`：模型控制器实现，负责维护工作进程注册、心跳和模型实例查询。
- `packages/meyo-core/src/meyo/model/cluster/controller_base.py`：模型服务运行层基础模块，连接工作进程、控制器、注册表和接口服务。
- `packages/meyo-core/src/meyo/model/cluster/embedding/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/cluster/embedding/remote_embedding.py`：远程向量生成工作进程调用封装，让接口层可以通过统一接口请求向量模型。
- `packages/meyo-core/src/meyo/model/cluster/manager_base.py`：工作进程管理器基础接口，定义模型工作进程的创建、启动和管理协议。
- `packages/meyo-core/src/meyo/model/cluster/registry.py`：模型注册表抽象，负责记录和查询当前可用的模型服务实例。
- `packages/meyo-core/src/meyo/model/cluster/registry_impl/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/cluster/registry_impl/db_storage.py`：模型注册表存储实现，负责持久化或查询可用模型实例信息。
- `packages/meyo-core/src/meyo/model/cluster/registry_impl/storage.py`：模型注册表存储实现，负责持久化或查询可用模型实例信息。
- `packages/meyo-core/src/meyo/model/cluster/storage.py`：模型集群存储抽象，负责保存工作进程、模型实例和注册表相关状态。
- `packages/meyo-core/src/meyo/model/cluster/worker/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/cluster/worker/default_worker.py`：模型工作进程运行实现，负责执行模型调用并向控制器注册。
- `packages/meyo-core/src/meyo/model/cluster/worker/embedding_worker.py`：模型工作进程运行实现，负责执行模型调用并向控制器注册。
- `packages/meyo-core/src/meyo/model/cluster/worker/manager.py`：模型工作进程运行实现，负责执行模型调用并向控制器注册。
- `packages/meyo-core/src/meyo/model/cluster/worker/ray_worker.py`：模型工作进程运行实现，负责执行模型调用并向控制器注册。
- `packages/meyo-core/src/meyo/model/cluster/worker/remote_manager.py`：模型工作进程运行实现，负责执行模型调用并向控制器注册。
- `packages/meyo-core/src/meyo/model/cluster/worker/remote_worker.py`：模型工作进程运行实现，负责执行模型调用并向控制器注册。
- `packages/meyo-core/src/meyo/model/cluster/worker_base.py`：模型工作进程基础接口，定义注册、心跳、调用和关闭流程。
- `packages/meyo-core/src/meyo/model/parameter.py`：模型服务参数定义，负责描述大语言模型、向量生成、重排、工作进程和接口服务配置。
- `packages/meyo-core/src/meyo/model/proxy/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/proxy/base.py`：代理模型基础能力，负责统一远程模型供应商的参数和调用方式。
- `packages/meyo-core/src/meyo/model/proxy/llms/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/proxy/llms/chatgpt.py`：兼容协议的大语言模型客户端实现，为远程供应商提供基础调用能力。
- `packages/meyo-core/src/meyo/model/proxy/llms/proxy_model.py`：代理模型请求解析和通用调用逻辑，供具体大语言模型供应商复用。
- `packages/meyo-core/src/meyo/model/proxy/llms/siliconflow.py`：硅基流动大语言模型供应商实现，负责把对话调用转发到硅基流动。
- `packages/meyo-core/src/meyo/model/resource.py`：模型资源注册兼容层，用于保留供应商参数注册入口并隔离非核心编排依赖。
- `packages/meyo-core/src/meyo/model/utils/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/model/utils/chatgpt_utils.py`：模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。
- `packages/meyo-core/src/meyo/model/utils/hf_stream_utils.py`：模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。
- `packages/meyo-core/src/meyo/model/utils/llm_metrics.py`：模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。
- `packages/meyo-core/src/meyo/model/utils/llm_utils.py`：模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。
- `packages/meyo-core/src/meyo/model/utils/media_utils.py`：模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。
- `packages/meyo-core/src/meyo/model/utils/parse_utils.py`：模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。
- `packages/meyo-core/src/meyo/model/utils/token_utils.py`：模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。
- `packages/meyo-core/src/meyo/rag/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/rag/embedding/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/rag/embedding/embeddings.py`：向量生成运行抽象，统一文本向量生成模型的调用和元数据描述。
- `packages/meyo-core/src/meyo/rag/embedding/rerank.py`：重排运行抽象，统一相关性排序模型的请求和结果结构。
- `packages/meyo-core/src/meyo/storage/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/storage/base.py`：存储层基础模块，统一缓存、向量库、图库和知识库相关接口。
- `packages/meyo-core/src/meyo/storage/cache/manager.py`：缓存存储基础模块，为模型服务和后续业务缓存提供统一实现入口。
- `packages/meyo-core/src/meyo/storage/cache/storage/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/storage/cache/storage/base.py`：缓存存储基础模块，为模型服务和后续业务缓存提供统一实现入口。
- `packages/meyo-core/src/meyo/storage/full_text/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/storage/full_text/base.py`：全文检索存储抽象，为后续知识库检索能力预留统一接口。
- `packages/meyo-core/src/meyo/storage/graph_store/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/storage/graph_store/base.py`：图存储基础抽象，为知识图谱和图数据库扩展提供统一接口。
- `packages/meyo-core/src/meyo/storage/graph_store/graph.py`：图存储基础抽象，为知识图谱和图数据库扩展提供统一接口。
- `packages/meyo-core/src/meyo/storage/knowledge_graph/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/storage/knowledge_graph/base.py`：知识图谱存储抽象，为后续检索增强和知识管理能力提供结构化接口。
- `packages/meyo-core/src/meyo/storage/vector_store/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/storage/vector_store/base.py`：向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。
- `packages/meyo-core/src/meyo/storage/vector_store/filters.py`：向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。
- `packages/meyo-core/src/meyo/util/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/util/annotations.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/api_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/chat_util.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/config_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/configure/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/util/configure/base.py`：配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。
- `packages/meyo-core/src/meyo/util/configure/env_hook.py`：配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。
- `packages/meyo-core/src/meyo/util/configure/manager.py`：配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。
- `packages/meyo-core/src/meyo/util/configure/markdown.py`：配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。
- `packages/meyo-core/src/meyo/util/executor_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/fastapi.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/function_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/i18n_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/json_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/memory_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/model_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/module_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/net_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/pagination_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/parameter_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/serialization/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/util/serialization/json_serialization.py`：序列化工具模块，负责把模型服务中的复杂对象转换为可传输结构。
- `packages/meyo-core/src/meyo/util/singleton.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/sql_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/string_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/system_utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。
- `packages/meyo-core/src/meyo/util/tracer/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-core/src/meyo/util/tracer/base.py`：链路追踪工具模块，负责模型服务请求的追踪初始化、记录和中间件集成。
- `packages/meyo-core/src/meyo/util/tracer/opentelemetry.py`：链路追踪工具模块，负责模型服务请求的追踪初始化、记录和中间件集成。
- `packages/meyo-core/src/meyo/util/tracer/span_storage.py`：链路追踪工具模块，负责模型服务请求的追踪初始化、记录和中间件集成。
- `packages/meyo-core/src/meyo/util/tracer/tracer_cli.py`：链路追踪工具模块，负责模型服务请求的追踪初始化、记录和中间件集成。
- `packages/meyo-core/src/meyo/util/tracer/tracer_impl.py`：链路追踪工具模块，负责模型服务请求的追踪初始化、记录和中间件集成。
- `packages/meyo-core/src/meyo/util/tracer/tracer_middleware.py`：链路追踪工具模块，负责模型服务请求的追踪初始化、记录和中间件集成。
- `packages/meyo-core/src/meyo/util/utils.py`：通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。

### 14.3 meyo-ext：外部扩展层

- `packages/meyo-ext/src/meyo_ext/__init__.py`：包入口，集中导出当前目录下的能力。
- `packages/meyo-ext/src/meyo_ext/datasource/conn_tugraph.py`：外部数据源连接器实现，负责接入图数据库和业务数据源。
- `packages/meyo-ext/src/meyo_ext/datasource/rdbms/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-ext/src/meyo_ext/datasource/rdbms/conn_postgresql.py`：外部关系型数据库连接器实现，负责把具体数据库接入统一数据源接口。
- `packages/meyo-ext/src/meyo_ext/datasource/rdbms/conn_sqlite.py`：外部关系型数据库连接器实现，负责把具体数据库接入统一数据源接口。
- `packages/meyo-ext/src/meyo_ext/datasource/schema.py`：外部数据源连接器实现，负责接入图数据库和业务数据源。
- `packages/meyo-ext/src/meyo_ext/rag/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-ext/src/meyo_ext/rag/embeddings/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-ext/src/meyo_ext/rag/embeddings/siliconflow.py`：硅基流动向量生成和重排供应商实现，负责调用硅基流动向量和排序接口。
- `packages/meyo-ext/src/meyo_ext/storage/graph_store/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-ext/src/meyo_ext/storage/graph_store/tugraph_store.py`：图存储基础抽象，为知识图谱和图数据库扩展提供统一接口。
- `packages/meyo-ext/src/meyo_ext/storage/vector_store/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-ext/src/meyo_ext/storage/vector_store/chroma_store.py`：向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。
- `packages/meyo-ext/src/meyo_ext/storage/vector_store/elastic_store.py`：向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。
- `packages/meyo-ext/src/meyo_ext/storage/vector_store/milvus_store.py`：向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。

### 14.4 meyo-serve：服务层预留

- `packages/meyo-serve/src/meyo_serve/__init__.py`：包入口，集中导出当前目录下的能力。
- `packages/meyo-serve/src/meyo_serve/core/config.py`：服务层通用配置定义，描述服务模块启动所需的基础参数。
- `packages/meyo-serve/src/meyo_serve/core/schemas.py`：服务层通用结构定义，为后续服务接口提供共享数据结构。
- `packages/meyo-serve/src/meyo_serve/model/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。
- `packages/meyo-serve/src/meyo_serve/model/service/__init__.py`：包入口，集中导出当前目录下的模型服务相关能力。

### 14.5 meyo-accelerator：加速包入口

- `packages/meyo-accelerator/src/meyo_accelerator/__init__.py`：包入口，集中导出当前目录下的能力。

### 14.6 meyo-client：客户端包入口

- `packages/meyo-client/src/meyo_client/__init__.py`：包入口，集中导出当前目录下的能力。

### 14.7 meyo-sandbox：沙箱包入口

- `packages/meyo-sandbox/src/meyo_sandbox/__init__.py`：包入口，集中导出当前目录下的能力。

### 14.8 配置、依赖和文档

- `.env.example`：本地环境变量模板，给 `SILICONFLOW_API_KEY` 等本地密钥留示例，不提交真实值。
- `configs/meyo.toml`：默认公开配置，声明 SiliconFlow LLM、embedding、rerank 和模型服务端口，可提交。
- `configs/meyo-app-config.example.toml`：应用配置示例，保留 app 配置段和默认模型配置写法。
- `configs/meyo-bm25-rag.toml`：BM25 + 向量检索混合检索配置模板。
- `configs/meyo-cloud-storage.example.toml`：对象存储文件服务配置示例。
- `configs/meyo-graphrag.toml`：GraphRAG 相关图存储和检索配置模板。
- `configs/meyo-local-glm.toml`：本地 GLM 模型配置模板。
- `configs/meyo-local-llama-cpp-server.toml`：llama.cpp server 本地模型配置模板。
- `configs/meyo-local-llama-cpp.toml`：llama.cpp 本地模型配置模板。
- `configs/meyo-local-mlx.toml`：MLX 本地模型配置模板。
- `configs/meyo-local-qwen.toml`：本地 Qwen 模型配置模板。
- `configs/meyo-local-qwen3.example.toml`：本地 Qwen3 模型配置示例。
- `configs/meyo-local-vllm.toml`：vLLM 本地模型配置模板。
- `configs/meyo-proxy-aimlapi.toml`：AIML API 代理模型配置模板。
- `configs/meyo-proxy-burncloud.toml`：BurnCloud 代理模型配置模板。
- `configs/meyo-proxy-deepseek.toml`：DeepSeek 代理模型配置模板。
- `configs/meyo-proxy-infiniai.toml`：InfiniAI 代理模型配置模板。
- `configs/meyo-proxy-ollama.toml`：Ollama 代理模型配置模板。
- `configs/meyo-proxy-openai.toml`：OpenAI 代理模型配置模板。
- `configs/meyo-proxy-siliconflow.toml`：SiliconFlow SQLite + Chroma 默认代理配置模板。
- `configs/meyo-proxy-siliconflow-mysql.toml`：SiliconFlow + MySQL 配置模板。
- `configs/meyo-proxy-siliconflow-pg-milvus.toml`：SiliconFlow + PostgreSQL + Milvus 配置模板。
- `configs/meyo-proxy-tongyi.toml`：通义千问代理模型配置模板。
- `configs/my/`：本地私有配置目录，已被 `.gitignore` 忽略，只放个人覆盖配置。
- `README.md`：同步默认启动命令，从本地私有配置改成公开 `meyo.toml`。
- `docs/docs/application/base_project/from_zero_to_running.md`：同步配置解析规则和默认启动命令。
- `docs/docs/application/base_project/quick_code_onboarding.md`：同步当前配置目录的定位说明。
- `docs/docs/development/01_update_package_config.md`：同步配置路径规则。
- `docs/docs/development/02_add_technology_stack_dependency.md`：同步最小启动命令。
- `docs/docs/development/03_model_provider_serve.md`：记录本批次模型服务开发顺序和文件索引。
- `packages/meyo-core/pyproject.toml`：补模型服务运行所需依赖，例如 `aiohttp`、`cachetools`、`shortuuid`、`sqlparse` 等。
- `uv.lock`：锁定新增依赖版本，保证本地和后续环境安装一致。

### 14.9 删除的旧实现

- `packages/meyo-app/src/meyo_app/logging.py`：删除旧的应用层日志封装，改用统一日志工具。
- `packages/meyo-core/src/meyo/model/errors.py`：删除旧的自写模型错误定义，避免和模型服务运行层重复。
- `packages/meyo-core/src/meyo/model/provider.py`：删除旧的自写 provider 抽象，切到 provider/proxy 和 worker manager 体系。
- `packages/meyo-core/src/meyo/model/schemas.py`：删除旧的自写模型 schema，改用 core schema 和 apiserver schema。
- `packages/meyo-serve/src/meyo_serve/model/service/model_service.py`：删除旧的模型 service，避免和 worker/controller/apiserver 体系并存。
- `tests/test_app_config.py`：删除围绕旧应用配置结构的测试，后续要按新配置链路重写。
- `tests/test_model_service.py`：删除围绕旧 model service 的测试，后续要按 worker manager 重写。
- `tests/test_openai_compatible_api.py`：删除围绕旧 OpenAI-compatible API 实现的测试，后续要按 apiserver 重写。

## 15. 怎么 review 这一批文件

review 时不要按文件名随机看，建议按链路看：

```text
meyo_app.meyo_server
-> meyo.model.parameter
-> meyo.model.proxy.llms.siliconflow
-> meyo_ext.rag.embeddings.siliconflow
-> meyo.model.cluster.worker.manager
-> meyo.model.cluster.controller
-> meyo.model.cluster.apiserver.api
```

这条主线能看懂，其它 util、storage、schema、adapter 文件都是为了支撑这条主线可以 import、注册、启动和对外提供 API。
