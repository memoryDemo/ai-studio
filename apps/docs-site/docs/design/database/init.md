---
title: 数据库表字典
---

# 数据库表字典

## 1. 三个服务

| 服务 | schema | 表来源 | 是否生产事实源 | 文档 |
|---|---|---|---|---|
| `meyo` | `meyo` | Meyo 设计创建 | 是 | [Meyo 数据库表字典](./01_inference_scene_runtime_db.md) |
| `chatbot` | `chatbot` | Open WebUI 自带刚需 | 否 | [Meyo Chatbot 数据库表字典](./02_meyo_chatbot.md) |
| `flow` | `flow` | Langflow 自带刚需 | 否 | [Meyo Studio Flow 数据库表字典](./03_meyo_studio_flow.md) |

## 2. 服务对应表

### `meyo`

| 分组 | 表 |
|---|---|
| 用户和 workspace | `tenants`、`domains`、`users`、`user_identities`、`workspaces`、`workspace_members` |
| 文件和聊天 | `files`、`chat_threads`、`chat_messages`、`chat_message_attachments` |
| DataOps 和知识库 | `data_source_profiles`、`secret_refs`、`sync_policies`、`ontology_profiles`、`ontology_versions`、`ontology_entity_types`、`ontology_relation_types`、`vector_collections`、`graph_profiles`、`knowledge_bases`、`knowledge_documents`、`knowledge_chunks`、`knowledge_versions`、`knowledge_publish_batches`、`knowledge_index_jobs`、`knowledge_permissions`、`knowledge_vector_refs`、`knowledge_graph_refs` |
| 能力、模型和策略 | `capability_registry`、`capability_versions`、`capability_permissions`、`model_profiles`、`policy_profiles`、`policy_rules`、`policy_decisions` |
| App / Scene / Flow | `app_registry`、`scene_registry`、`scene_route_examples`、`scene_workflow_specs`、`scene_knowledge_bindings`、`scene_vector_bindings`、`scene_graph_bindings`、`scene_tool_bindings`、`scene_model_bindings`、`router_versions`、`flow_templates`、`flow_versions`、`app_scene_flow_bindings` |
| 发布、评测和审批 | `scene_eval_case_sets`、`scene_eval_cases`、`scene_eval_runs`、`scene_eval_results`、`scene_approvals`、`scene_activation_history`、`approval_requests`、`approval_events` |
| 运行、审计和证据 | `app_runs`、`route_decisions`、`flow_runs`、`run_steps`、`scene_node_events`、`data_access_events`、`trace_events`、`run_metrics`、`evidence_records`、`evidence_citations`、`no_answer_records`、`feedback_events` |
| 视图 | `active_scene_router_view` |

### `chatbot`

`chatbot` 生产上使用 `meyo` 的统一事实表；当前 Open WebUI 过渡期还需要 41 张内部表。

| 类型 | 表 |
|---|---|
| 生产用户 / workspace / chat / knowledge | `meyo.users`、`meyo.workspaces`、`meyo.chat_threads`、`meyo.chat_messages`、`meyo.knowledge_bases`、`meyo.knowledge_documents`、`meyo.knowledge_chunks` |
| Open WebUI 内部刚需 | `access_grant`、`alembic_version`、`api_key`、`auth`、`automation`、`automation_run`、`calendar`、`calendar_event`、`calendar_event_attendee`、`channel`、`channel_file`、`channel_member`、`channel_webhook`、`chat`、`chat_file`、`chat_message`、`chatidtag`、`config`、`document`、`feedback`、`file`、`folder`、`function`、`group`、`group_member`、`knowledge`、`knowledge_file`、`memory`、`message`、`message_reaction`、`migratehistory`、`model`、`note`、`oauth_session`、`prompt`、`prompt_history`、`shared_chat`、`skill`、`tag`、`tool`、`user` |

### `flow`

`flow` 生产上使用 `meyo` 的 Flow / Scene / Run 表；当前 Langflow 过渡期还需要 19 张内部表。

| 类型 | 表 |
|---|---|
| 生产 Flow / Scene / Run | `meyo.flow_templates`、`meyo.flow_versions`、`meyo.app_scene_flow_bindings`、`meyo.scene_workflow_specs`、`meyo.flow_runs`、`meyo.run_steps`、`meyo.scene_node_events` |
| Langflow 内部刚需 | `alembic_version`、`apikey`、`deployment`、`deployment_provider_account`、`file`、`flow`、`flow_version`、`flow_version_deployment_attachment`、`folder`、`job`、`message`、`span`、`sso_config`、`sso_user_profile`、`trace`、`transaction`、`user`、`variable`、`vertex_build` |
| LangChain 本地缓存 | `full_llm_cache`、`full_md5_llm_cache` |

## 3. 建表原则

| 原则 | 结论 |
|---|---|
| 统一真相 | 只在 `meyo` |
| chatbot 内部表 | 过渡期保留，不作为业务事实源 |
| flow 内部表 | 过渡期保留，不作为发布事实源 |
| ID 类型 | Meyo 自研表使用 `uuid`；Open WebUI / Langflow 自带表不强改字段类型 |
| 写入权限 | `chatbot` 和 `flow` 通过 Meyo API 写生产事实 |

## 4. 初始化 SQL 脚本

| schema | 脚本 | 说明 |
|---|---|---|
| `meyo` | [01_init_meyo.sql](./sql/01_init_meyo.sql) | 创建 Meyo 统一事实源表、字段注释和 Router 视图 |
| `chatbot` | [02_init_chatbot.sql](./sql/02_init_chatbot.sql) | 创建 Open WebUI 当前内部表和字段注释 |
| `flow` | [03_init_flow.sql](./sql/03_init_flow.sql) | 创建 Langflow 当前内部表、LangChain 本地缓存表和字段注释 |
