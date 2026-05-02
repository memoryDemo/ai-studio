---
title: 通用 Scene 注册开发清单
---

# 通用 Scene 注册开发清单

> 文件名保留 `scense` 是为了沿用当前路径；正文统一使用 `Scene`。

## 0. 开发目标

这一节只做一件事：把 **通用 Scene 注册能力** 开发成可落库、可发布、可路由、可审计的生产能力。

它不是 `rag_qa` 的业务 workflow。`rag_qa` 是一个具体 Scene，放在 [RAG 问答 Scene Workflow 设计](../design/scenes/01_rag_qa_scene_workflow_design.md)。

它也不是推理入口运行框架的全部。入口框架放在 [Meyo 推理入口运行框架设计](../design/01_inference_runtime_framework_design.md)。

本开发清单覆盖：

```text
App Registry
Scene Registry
Scene Route Examples
Scene Workflow Spec
Scene Asset / Graph / Vector / Tool / Model Binding
Flow Template
Flow Version
Scene Flow Binding
Eval Case Set
Approval
Activation
Rollback
Run 可路由性校验
```

## 1. 硬性规则

### 1.1 不允许隐式开发内容

每一个功能必须落到下面至少一个位置：

```text
schema
repository
service
router
client
migration
test
docs
```

禁止出现：

```text
“后续自动补”
“运行时临时生成”
“代码里判断一下”
“prompt 里约束一下”
“先用配置写死”
“先从 studio-flow 本地库读”
“没有表也可以先跑”
```

### 1.2 三库事实源约束

Scene 注册相关生产事实只允许来自：

```text
PostgreSQL：App、Scene、Flow、Binding、Route Example、Approval、Eval、Run、Evidence、Policy
Neo4j / TuGraph：图谱 profile 校验、实体关系可用性校验
Milvus / Chroma：向量 collection 可用性校验
```

禁止：

```text
配置文件保存业务 scene
代码里硬编码 scene_id -> flow_id
Router Workflow 输出未注册 scene_id
studio-flow 本地 DB 作为生产 Flow Registry
chatbot 判断 scene
```

## 2. 开发边界

| 项目 | 本节必须开发 | 本节禁止开发 |
|---|---|---|
| `packages/meyo-core` | Scene 注册协议、节点、schema、错误码、事件、gateway 协议 | 数据库连接、FastAPI router |
| `packages/meyo-ext` | PostgreSQL migration / repository，Milvus / Neo4j 校验 gateway | 业务路由判断 |
| `packages/meyo-serve` | Scene 注册 service、Flow 绑定 service、审批发布 service、NodeRunner 记录 | 直接连接三库 SDK |
| `packages/meyo-app` | Public API router、依赖装配 | 直接写 repository |
| `packages/meyo-client` | Scene / Flow / App SDK | 直连数据库 |
| `apps/meyo-studio-flow` | 设计态选择 app / scene、导出 artifact、注册 flow version | 生产激活 scene、直连生产三库 |
| `apps/meyo-chatbot` | 不需要改 scene 注册能力 | 任何 scene 注册逻辑 |
| `configs` | 连接和开关配置 | 业务 scene、资产绑定、路由规则 |

## 3. 必须新增的目录和文件

### 3.1 `packages/meyo-core`

```text
packages/meyo-core/src/meyo/scene/
  __init__.py
  node_ids.py
  errors.py
  schemas.py
  events.py
  gateways.py
```

| 文件 | 开发清单 | 验收 |
|---|---|---|
| `node_ids.py` | 定义 `SD00-SD14`，定义 `SceneLifecycleNodeId`，定义 `SceneRuntimeRef` | 枚举完整，不与 `FW`、`QA` 混用 |
| `errors.py` | 定义 `app_not_found`、`scene_not_found`、`scene_not_active`、`scene_schema_invalid`、`flow_artifact_invalid`、`flow_binding_conflict`、`approval_required` | service 不抛裸异常 |
| `schemas.py` | 定义 App、Scene、RouteExample、WorkflowSpec、FlowTemplate、FlowVersion、FlowBinding、EvalCaseSet、Approval、Activation request / response | 每个 schema 有 `tenant_id`、`status`、`version` 或明确说明无版本 |
| `events.py` | 定义 `SceneNodeStarted`、`SceneNodeSucceeded`、`SceneNodeFailed`、`SceneNodeSkipped`、`SceneActivated`、`SceneRolledBack` | 每个事件有 `node_code`、`entity_id`、`trace_id` |
| `gateways.py` | 定义 `SceneRegistryGateway`、`FlowRegistryGateway`、`ScenePolicyGateway`、`SceneValidationGateway` 协议 | core 只定义协议，不 import ext |

禁止：

```text
packages/meyo-core import psycopg
packages/meyo-core import neo4j
packages/meyo-core import pymilvus
packages/meyo-core import fastapi
packages/meyo-core import meyo_app
```

### 3.2 `packages/meyo-ext`

```text
packages/meyo-ext/src/meyo_ext/scene/
  __init__.py
  postgres/
    __init__.py
    migrations/
      001_scene_registry.sql
      002_scene_flow_registry.sql
      003_scene_eval_approval.sql
    repositories.py
  milvus/
    collection_validator.py
  neo4j/
    graph_profile_validator.py
  object_store/
    flow_artifact_store.py
```

| 文件 | 开发清单 | 验收 |
|---|---|---|
| `001_scene_registry.sql` | 建 `app_registry`、`scene_registry`、`scene_route_examples`、`scene_workflow_specs` | 表、索引、唯一约束、状态字段完整 |
| `002_scene_flow_registry.sql` | 建 `flow_templates`、`flow_versions`、`app_scene_flow_bindings` | 同一 `app_id + scene_id` 只能一个 active binding |
| `003_scene_eval_approval.sql` | 建 `scene_eval_case_sets`、`scene_eval_results`、`scene_approvals`、`scene_activation_history` | 审批和激活有审计记录 |
| `repositories.py` | 实现所有 PostgreSQL CRUD 和状态查询 | repository 不做 LLM / router 判断 |
| `collection_validator.py` | 校验 Milvus / Chroma collection 是否存在、维度是否匹配、collection 是否属于 tenant | 只返回校验结果，不返回正文 |
| `graph_profile_validator.py` | 校验 Neo4j / TuGraph profile、ontology relation、基础连通性 | 不执行任意未审计 Cypher |
| `flow_artifact_store.py` | 保存 / 读取 flow artifact，计算 checksum | object store 不作为事实源 |

### 3.3 `packages/meyo-serve`

```text
packages/meyo-serve/src/meyo_serve/scene/
  __init__.py
  node_runner.py
  app_registry_service.py
  scene_registry_service.py
  scene_workflow_service.py
  scene_binding_service.py
  flow_registry_service.py
  scene_eval_service.py
  scene_approval_service.py
  scene_activation_service.py
  scene_router_query_service.py
```

| Service | 节点 | 开发清单 | 验收 |
|---|---|---|---|
| `NodeRunner` | `SD00-SD14` | 写 started / succeeded / failed / skipped 到 `run_steps` 或 `scene_job_steps` | 所有 public service 方法必须通过它 |
| `AppRegistryService` | `SD00` 前置 | 创建 app、查询 app、校验 tenant / domain / status | app 不存在不能创建 scene |
| `SceneRegistryService` | `SD00-SD03` | 创建 draft、更新 intent、更新 input / output schema | schema 不合法不能进入 testing |
| `SceneWorkflowService` | `SD04` | 保存 workflow nodes / edges / node contracts | 缺节点、孤立节点、未知 node type 均失败 |
| `SceneBindingService` | `SD05-SD08` | 绑定知识、向量、图谱、工具、模型策略 | 绑定对象必须回查事实源 |
| `FlowRegistryService` | `SD09-SD11` | 接收 studio-flow artifact、保存 flow template / version、校验 checksum | flow_version 不完整不能评测 |
| `SceneEvalService` | `SD12` | 绑定 eval case set、执行评测、写 eval result | 未达阈值不能审批 |
| `SceneApprovalService` | `SD13` | 审批、拒绝、记录审批人和原因 | 无审批不能激活 |
| `SceneActivationService` | `SD14` | 激活 binding、停用旧 active、写 activation history | 同一 scene 只能一个 active |
| `SceneRouterQueryService` | `FW05-FW09` | 提供 active scenes 给 router，校验 route decision | router 不能选择未 active scene |

### 3.4 `packages/meyo-app`

```text
packages/meyo-app/src/meyo_app/routers/
  scene_apps.py
  scene_registry.py
  scene_workflow_specs.py
  scene_bindings.py
  scene_flows.py
  scene_eval.py
  scene_approvals.py
```

| Router | API | Service | 验收 |
|---|---|---|---|
| `scene_apps.py` | `POST /api/v1/apps`、`GET /api/v1/apps/{app_id}` | `AppRegistryService` | router 不直接查库 |
| `scene_registry.py` | `POST /api/v1/apps/{app_id}/scenes`、`PATCH /api/v1/apps/{app_id}/scenes/{scene_id}`、`GET /api/v1/apps/{app_id}/scenes` | `SceneRegistryService` | 每个 API 返回明确 status |
| `scene_workflow_specs.py` | `PUT /api/v1/apps/{app_id}/scenes/{scene_id}/workflow-spec`、`GET .../workflow-spec` | `SceneWorkflowService` | workflow spec 校验失败返回结构化错误 |
| `scene_bindings.py` | knowledge / vector / graph / tool / model binding API | `SceneBindingService` | binding 对象必须回查三库 |
| `scene_flows.py` | flow template / version / binding API | `FlowRegistryService` | artifact checksum 必须校验 |
| `scene_eval.py` | eval case set / run / result API | `SceneEvalService` | eval result 可追溯 |
| `scene_approvals.py` | approve / reject / activate / rollback API | `SceneApprovalService`、`SceneActivationService` | 无审批不能 active |

### 3.5 `packages/meyo-client`

```text
packages/meyo-client/src/meyo_client/scene/
  __init__.py
  apps.py
  scenes.py
  workflow_specs.py
  bindings.py
  flows.py
  eval.py
  approvals.py
```

| Client | 开发清单 | 验收 |
|---|---|---|
| `AppClient` | create / get / list apps | 只调用 HTTP |
| `SceneClient` | create draft、update intent、update schema、list active scenes | 不包含业务路由判断 |
| `WorkflowSpecClient` | put / get workflow spec | 不生成隐藏节点 |
| `SceneBindingClient` | bind knowledge / vector / graph / tool / model | 返回 binding id |
| `FlowClient` | register template、publish version、bind flow | 不直接上传到对象存储绕过 API |
| `SceneEvalClient` | create eval set、run eval、get result | eval result 有版本 |
| `SceneApprovalClient` | approve、reject、activate、rollback | 每次动作返回 audit id |

### 3.6 `apps/meyo-studio-flow`

```text
apps/meyo-studio-flow/src/backend/base/langflow/api/meyo_scene.py
apps/meyo-studio-flow/src/backend/base/langflow/services/meyo_scene_client.py
apps/meyo-studio-flow/src/backend/base/langflow/services/meyo_flow_exporter.py
apps/meyo-studio-flow/src/frontend/src/customization/meyo-scene/
```

| 能力 | 开发清单 | 禁止 |
|---|---|---|
| Scene 选择器 | 从 Meyo Public API 查询 app / scene / workflow spec | 本地写死 scene |
| Workflow Spec 导入 | 按 `scene_workflow_specs` 生成 flow 草稿 | 自动补隐藏节点 |
| Flow Artifact 导出 | 导出 artifact、schema、checksum | checksum 缺失 |
| Flow Version 注册 | 调 Meyo Public API 注册 flow version | 直接写 PostgreSQL |
| 运行态上下文透传 | 透传 `app_run_id`、`flow_run_id`、`scene_id`、`scene_node_code` | 直连生产三库 |

### 3.7 `apps/meyo-chatbot`

本节不开发 scene 注册 UI。

必须确认：

```text
chatbot 不出现 scene 注册 API
chatbot 不出现 flow 发布 API
chatbot 不出现 scene keyword routing
chatbot 不出现 PostgreSQL / Neo4j / Milvus 连接配置
```

## 4. PostgreSQL 表清单

### 4.1 `app_registry`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `app_id` | uuid | 是 | app 唯一 ID |
| `tenant_id` | uuid | 是 | 租户 |
| `domain_id` | uuid | 是 | 业务域 |
| `name` | text | 是 | 展示名 |
| `description` | text | 否 | 描述 |
| `status` | text | 是 | draft / active / paused / retired |
| `default_router_id` | uuid | 否 | 默认 router |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

约束：

```text
unique(tenant_id, app_id)
status in ('draft', 'active', 'paused', 'retired')
```

### 4.2 `scene_registry`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `scene_id` | uuid | 是 | scene 唯一 ID |
| `app_id` | uuid | 是 | 所属 app |
| `tenant_id` | uuid | 是 | 租户 |
| `domain_id` | uuid | 是 | 业务域 |
| `name` | text | 是 | 展示名 |
| `description` | text | 是 | 业务说明 |
| `intent_description` | text | 是 | router 可读意图 |
| `input_schema_ref` | text | 是 | 输入 schema 引用 |
| `output_schema_ref` | text | 是 | 输出 schema 引用 |
| `status` | text | 是 | draft / testing / approved / active / paused / retired |
| `version` | integer | 是 | scene 元数据版本 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `updated_by_user_id` | uuid | 是 | 更新人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

约束：

```text
unique(tenant_id, app_id, scene_id)
status in ('draft', 'testing', 'approved', 'active', 'paused', 'retired')
active scene 必须存在 active flow binding
```

### 4.3 `scene_route_examples`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `example_id` | uuid | 是 | 样例 ID |
| `scene_id` | uuid | 是 | 所属 scene |
| `tenant_id` | uuid | 是 | 租户 |
| `text` | text | 是 | 用户输入样例 |
| `label` | text | 是 | positive / negative |
| `reason` | text | 是 | 命中或排除原因 |
| `status` | text | 是 | active / disabled |

约束：

```text
label in ('positive', 'negative')
每个 active scene 至少 3 个 positive 和 3 个 negative examples
```

### 4.4 `scene_workflow_specs`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `workflow_spec_id` | uuid | 是 | workflow spec ID |
| `scene_id` | uuid | 是 | 所属 scene |
| `tenant_id` | uuid | 是 | 租户 |
| `nodes` | jsonb | 是 | 显式节点列表 |
| `edges` | jsonb | 是 | 显式边列表 |
| `input_contract` | jsonb | 是 | 输入契约 |
| `output_contract` | jsonb | 是 | 输出契约 |
| `status` | text | 是 | draft / validated / retired |
| `schema_version` | integer | 是 | schema 版本 |

约束：

```text
nodes 不能为空
edges 不能为空
每个 node 必须有 node_code / type / input_schema / output_schema / failure_policy
不允许存在未连接节点
不允许存在未声明 failure_policy 的节点
```

### 4.5 `flow_templates`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `flow_template_id` | uuid | 是 | 模板 ID |
| `source` | text | 是 | studio-flow / code / imported |
| `name` | text | 是 | 名称 |
| `description` | text | 否 | 描述 |
| `artifact_schema_ref` | text | 是 | artifact schema |
| `status` | text | 是 | draft / active / retired |

### 4.6 `flow_versions`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `flow_version_id` | uuid | 是 | flow 版本 ID |
| `flow_template_id` | uuid | 是 | 模板 ID |
| `artifact_uri` | text | 是 | artifact 存储 URI |
| `checksum` | text | 是 | artifact checksum |
| `runtime` | text | 是 | studio-flow |
| `status` | text | 是 | draft / testing / approved / active / retired |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### 4.7 `app_scene_flow_bindings`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `binding_id` | uuid | 是 | 绑定 ID |
| `tenant_id` | uuid | 是 | 租户 |
| `app_id` | uuid | 是 | app |
| `scene_id` | uuid | 是 | scene |
| `flow_version_id` | uuid | 是 | flow version |
| `status` | text | 是 | draft / testing / approved / active / retired |
| `effective_from` | timestamptz | 否 | 生效时间 |
| `activated_by_user_id` | uuid | 否 | 激活人 |
| `activated_at` | timestamptz | 否 | 激活时间 |

约束：

```text
unique active(tenant_id, app_id, scene_id)
active binding 的 flow_version 必须 approved 或 active
```

### 4.8 `scene_approvals`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `approval_id` | uuid | 是 | 审批 ID |
| `scene_id` | uuid | 是 | scene |
| `flow_version_id` | uuid | 是 | flow version |
| `eval_result_id` | uuid | 是 | 评测结果 |
| `decision` | text | 是 | approved / rejected |
| `reason` | text | 是 | 审批原因 |
| `approved_by_user_id` | uuid | 是 | 审批人 |
| `approved_at` | timestamptz | 是 | 审批时间 |

## 5. API 开发清单

### 5.1 App API

```text
POST /api/v1/apps
GET  /api/v1/apps/{app_id}
GET  /api/v1/apps
PATCH /api/v1/apps/{app_id}
```

必须实现：

| API | 输入 | 输出 | 节点 | 失败 |
|---|---|---|---|---|
| `POST /api/v1/apps` | tenant、domain、name、description | app profile | app 前置 | tenant 无效返回 `tenant_not_found` |
| `GET /api/v1/apps/{app_id}` | app_id | app profile | app 前置 | 不存在返回 `app_not_found` |
| `GET /api/v1/apps` | tenant、domain、status | app list | app 前置 | 无数据返回空列表 |
| `PATCH /api/v1/apps/{app_id}` | patch fields | updated app | app 前置 | active app 关键字段变更需要审批 |

### 5.2 Scene API

```text
POST  /api/v1/apps/{app_id}/scenes
GET   /api/v1/apps/{app_id}/scenes
GET   /api/v1/apps/{app_id}/scenes/{scene_id}
PATCH /api/v1/apps/{app_id}/scenes/{scene_id}
```

必须实现：

| API | 输入 | 输出 | 节点 | 失败 |
|---|---|---|---|---|
| `POST /api/v1/apps/{app_id}/scenes` | name、description、owner | draft scene | `SD00` | app 不存在失败 |
| `PATCH .../scenes/{scene_id}` | intent、schema refs、status patch | updated scene | `SD01-SD03` | schema 不合法失败 |
| `GET .../scenes` | app_id、status | scene list | `FW05` | 空列表可返回 |
| `GET .../scenes/{scene_id}` | scene_id | scene detail | `FW09` | scene 不存在失败 |

### 5.3 Route Example API

```text
POST   /api/v1/apps/{app_id}/scenes/{scene_id}/route-examples
GET    /api/v1/apps/{app_id}/scenes/{scene_id}/route-examples
PATCH  /api/v1/apps/{app_id}/scenes/{scene_id}/route-examples/{example_id}
DELETE /api/v1/apps/{app_id}/scenes/{scene_id}/route-examples/{example_id}
```

必须实现：

```text
新增 positive 样例
新增 negative 样例
禁用样例
查询 active 样例
发布前校验正反例数量
```

### 5.4 Workflow Spec API

```text
PUT /api/v1/apps/{app_id}/scenes/{scene_id}/workflow-spec
GET /api/v1/apps/{app_id}/scenes/{scene_id}/workflow-spec
POST /api/v1/apps/{app_id}/scenes/{scene_id}/workflow-spec/validate
```

必须校验：

```text
nodes 非空
edges 非空
每个 node_code 唯一
每个 node 有 input_schema
每个 node 有 output_schema
每个 node 有 failure_policy
每条 edge 的 from/to 都存在
没有孤立节点
没有未声明的隐式节点
```

### 5.5 Binding API

```text
POST /api/v1/apps/{app_id}/scenes/{scene_id}/bindings/knowledge
POST /api/v1/apps/{app_id}/scenes/{scene_id}/bindings/vector
POST /api/v1/apps/{app_id}/scenes/{scene_id}/bindings/graph
POST /api/v1/apps/{app_id}/scenes/{scene_id}/bindings/tools
POST /api/v1/apps/{app_id}/scenes/{scene_id}/bindings/models
GET  /api/v1/apps/{app_id}/scenes/{scene_id}/bindings
```

每个 binding 必须：

```text
写 PostgreSQL
回查被绑定对象是否存在
记录 binding_id
记录 binding_version
记录 created_by
记录 validation_result
```

### 5.6 Flow API

```text
POST /api/v1/flow-templates
POST /api/v1/flow-templates/{flow_template_id}/versions
GET  /api/v1/flow-templates/{flow_template_id}/versions/{flow_version_id}
POST /api/v1/apps/{app_id}/scenes/{scene_id}/flow-bindings
GET  /api/v1/apps/{app_id}/scenes/{scene_id}/flow-bindings
```

必须校验：

```text
artifact_uri 存在
checksum 匹配
flow runtime 是允许值
flow_version status 是 draft / testing / approved / active
binding scene_id 与 app_id 匹配
```

### 5.7 Eval / Approval / Activation API

```text
POST /api/v1/apps/{app_id}/scenes/{scene_id}/eval-case-sets
POST /api/v1/apps/{app_id}/scenes/{scene_id}/eval-runs
GET  /api/v1/apps/{app_id}/scenes/{scene_id}/eval-runs/{eval_run_id}
POST /api/v1/apps/{app_id}/scenes/{scene_id}/approvals
POST /api/v1/apps/{app_id}/scenes/{scene_id}/activate
POST /api/v1/apps/{app_id}/scenes/{scene_id}/rollback
```

发布前必须满足：

```text
workflow spec validated
bindings validated
flow version registered
eval result passed
approval approved
```

## 6. SD00-SD14 节点开发清单

| 节点 | 开发内容 | 必须落库 | 必须测试 |
|---|---|---|---|
| `SD00` 创建 scene draft | `SceneRegistryService.create_draft` + `POST /scenes` | `scene_registry` | app 不存在失败 |
| `SD01` 定义触发意图 | `SceneRegistryService.update_intent` + route examples API | `scene_registry`、`scene_route_examples` | 正反例不足不能 testing |
| `SD02` 定义输入契约 | `SceneRegistryService.update_input_schema` | `scene_registry.input_schema_ref` | schema 不合法失败 |
| `SD03` 定义输出契约 | `SceneRegistryService.update_output_schema` | `scene_registry.output_schema_ref` | output schema 缺 required 字段失败 |
| `SD04` 定义 workflow 节点 | `SceneWorkflowService.put_spec` | `scene_workflow_specs` | 孤立节点失败 |
| `SD05` 绑定知识资产 | `SceneBindingService.bind_knowledge` | binding 表 | asset 未发布失败 |
| `SD06` 绑定向量集合 | `SceneBindingService.bind_vector` | binding 表 | collection 不存在失败 |
| `SD07` 绑定图谱 profile | `SceneBindingService.bind_graph` | binding 表 | graph profile 不存在失败 |
| `SD08` 绑定工具和模型 | `SceneBindingService.bind_tool_model` | binding 表 | tool policy deny 失败 |
| `SD09` 设计 Studio Flow | studio-flow 导入 workflow spec | studio-flow draft，不是生产事实 | 草稿不能 active |
| `SD10` 导出 Flow Artifact | studio-flow exporter | object store artifact + checksum | checksum 缺失失败 |
| `SD11` 注册 Flow Version | `FlowRegistryService.register_version` | `flow_versions` | artifact 不存在失败 |
| `SD12` 运行评测 | `SceneEvalService.run_eval` | `scene_eval_results` | 未达阈值失败 |
| `SD13` 审批发布 | `SceneApprovalService.approve` | `scene_approvals` | 无权限审批失败 |
| `SD14` 激活绑定 | `SceneActivationService.activate` | `app_scene_flow_bindings`、`scene_activation_history` | 同 scene 多 active 失败 |

## 7. 状态机

### 7.1 Scene 状态机

```text
draft
 -> testing
 -> approved
 -> active
 -> paused
 -> retired
```

允许流转：

| From | To | 前置条件 |
|---|---|---|
| draft | testing | intent、schema、workflow spec、binding 都存在 |
| testing | approved | eval passed |
| approved | active | approval approved，flow binding approved |
| active | paused | operator 有权限 |
| paused | active | 未 retired，binding 仍有效 |
| active | retired | operator 有权限，有替代 scene 或确认下线 |

禁止流转：

```text
draft -> active
testing -> active
retired -> active
paused -> approved
```

### 7.2 Flow Version 状态机

```text
draft
 -> testing
 -> approved
 -> active
 -> retired
```

约束：

```text
只有 approved / active flow_version 可以绑定 active scene
retired flow_version 不能再被新 binding 使用
```

## 8. Router 可见性

Router 只能看到满足以下条件的 scene：

```text
scene_registry.status = active
app_registry.status = active
app_scene_flow_bindings.status = active
flow_versions.status in approved / active
scene_route_examples positive >= 3
scene_route_examples negative >= 3
workflow_spec.status = validated
```

Router 查询 API 只返回：

```text
app_id
scene_id
scene_name
intent_description
positive_examples
negative_examples
input_schema_ref
output_schema_ref
flow_binding_id
flow_version_id
policy_summary
```

Router 不允许获得：

```text
未激活 scene
已 retired scene
无 active flow binding 的 scene
studio-flow 本地 draft
任意未发布 flow artifact
```

## 9. 错误码清单

| 错误码 | 触发条件 | HTTP 状态 |
|---|---|---|
| `tenant_not_found` | tenant 不存在 | 404 |
| `app_not_found` | app 不存在 | 404 |
| `scene_not_found` | scene 不存在 | 404 |
| `scene_not_active` | route 或 run 请求命中非 active scene | 409 |
| `scene_schema_invalid` | input / output schema 不合法 | 400 |
| `scene_route_examples_insufficient` | 正反例不足 | 400 |
| `scene_workflow_spec_invalid` | workflow spec 不合法 | 400 |
| `scene_binding_invalid` | binding 指向不存在或未发布对象 | 400 |
| `flow_artifact_invalid` | artifact 不存在或 checksum 不匹配 | 400 |
| `flow_binding_conflict` | 同一 app + scene 已有 active binding | 409 |
| `eval_required` | 未评测 | 409 |
| `eval_failed` | 评测未达阈值 | 409 |
| `approval_required` | 未审批 | 409 |
| `permission_denied` | 无权限 | 403 |

## 10. 测试清单

### 10.1 单元测试

```text
tests/scene/test_scene_node_ids.py
tests/scene/test_scene_schemas.py
tests/scene/test_scene_workflow_spec_validator.py
tests/scene/test_scene_state_machine.py
tests/scene/test_scene_router_visibility.py
tests/scene/test_scene_error_codes.py
```

必须覆盖：

| 测试 | 断言 |
|---|---|
| node id 完整性 | `SD00-SD14` 全部存在 |
| schema 校验 | 缺必填字段失败 |
| workflow spec 校验 | 孤立节点、未知边、缺 failure policy 全部失败 |
| 状态机 | 禁止 `draft -> active` |
| router 可见性 | 只有 active scene 可见 |
| 错误码 | service 不抛裸异常 |

### 10.2 Repository 测试

```text
tests/scene/test_scene_postgres_repositories.py
```

必须覆盖：

```text
create app
create scene draft
update scene schema
insert route examples
insert workflow spec
insert flow template
insert flow version
insert active binding
query active scenes
unique active binding conflict
retired scene not returned
```

### 10.3 Service 测试

```text
tests/scene/test_scene_registry_service.py
tests/scene/test_scene_binding_service.py
tests/scene/test_flow_registry_service.py
tests/scene/test_scene_activation_service.py
```

必须覆盖：

```text
SD00-SD14 每个节点 started / succeeded / failed
app 不存在不能创建 scene
正反例不足不能 testing
binding 对象不存在不能保存
flow artifact checksum 不匹配不能注册
eval 未通过不能 approval
无 approval 不能 active
```

### 10.4 API 测试

```text
tests/scene/test_scene_api.py
```

必须覆盖：

```text
POST /api/v1/apps
POST /api/v1/apps/{app_id}/scenes
PUT /api/v1/apps/{app_id}/scenes/{scene_id}/workflow-spec
POST /api/v1/apps/{app_id}/scenes/{scene_id}/bindings/knowledge
POST /api/v1/flow-templates/{flow_template_id}/versions
POST /api/v1/apps/{app_id}/scenes/{scene_id}/activate
GET active scenes for router
```

### 10.5 禁止项测试

必须增加静态或约定测试：

```text
packages/meyo-core 不 import psycopg / neo4j / pymilvus / fastapi
packages/meyo-app router 不直接 import 三库 SDK
apps/meyo-chatbot 不出现 scene 注册 API
apps/meyo-chatbot 不出现 scene keyword routing
apps/meyo-studio-flow 不出现生产三库连接配置
configs 不出现业务 scene_id -> flow_id 映射
```

## 11. 开发顺序

按下面顺序开发，不能跳步：

| 顺序 | 内容 | 完成标准 |
|---|---|---|
| 1 | `meyo-core` node id / schema / errors / events / gateway protocol | 单元测试通过 |
| 2 | PostgreSQL migration | 空库能建表，约束存在 |
| 3 | PostgreSQL repository | repository 测试通过 |
| 4 | `NodeRunner` | started / succeeded / failed / skipped 可写 |
| 5 | App / Scene service | `SD00-SD03` 可跑 |
| 6 | Workflow spec service | `SD04` 可校验 |
| 7 | Binding service | `SD05-SD08` 可校验 |
| 8 | Flow registry service | `SD09-SD11` 可注册 |
| 9 | Eval / Approval / Activation service | `SD12-SD14` 可发布 |
| 10 | Public API router | API 测试通过 |
| 11 | Client SDK | SDK 测试通过 |
| 12 | studio-flow 发布适配 | artifact 能注册成 flow_version |
| 13 | Router active scene query | 只返回 active scene |
| 14 | 禁止项测试 | 全部通过 |

## 12. 最小可验收闭环

最小闭环只验收一个 demo scene，不要求接入真实 RAG。

必须跑通：

```text
1. 创建 app
2. 创建 scene draft
3. 写 intent_description
4. 写 3 条 positive route examples
5. 写 3 条 negative route examples
6. 写 input_schema_ref
7. 写 output_schema_ref
8. 写 workflow spec
9. 注册 flow template
10. 注册 flow version
11. 绑定 scene -> flow version
12. 写 eval case set
13. 跑 eval 并通过
14. 审批 scene
15. 激活 binding
16. Router active scene query 能查到该 scene
17. 非 active scene 查不到
```

每一步必须能回答：

```text
调用哪个 API？
进入哪个 service？
执行哪个 SD 节点？
写入哪张表？
失败时错误码是什么？
测试文件是哪一个？
```

## 13. Definition of Done

通用 Scene 注册能力完成时，必须同时满足：

```text
SD00-SD14 全部有 service 实现
SD00-SD14 全部有 NodeRunner 记录
所有生产事实写 PostgreSQL
Milvus / Neo4j 只用于 binding 校验
studio-flow 只能提交 artifact，不能激活 scene
chatbot 不参与 scene 注册
router 只能看到 active scene
同一 app + scene 只能一个 active flow binding
无 eval / 无 approval 不能 active
所有 API 有结构化错误码
单元测试、repository 测试、service 测试、API 测试、禁止项测试全部存在
```

最终原则：

```text
Scene 是注册出来的，不是代码猜出来的。
Flow 是审批激活出来的，不是 studio-flow 本地草稿直接跑出来的。
Router 只能选择 PostgreSQL 里 active 的 scene。
任何没有落库、没有节点、没有测试的内容，都不算开发完成。
```
