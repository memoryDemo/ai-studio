---
title: Meyo 数据库表字典
---

# Meyo 数据库表字典

## 1. 服务归属

| 项 | 值 |
|---|---|
| 服务 | `meyo` / `meyo-stack` |
| schema | `meyo` |
| 来源 | Meyo 设计创建 |
| 定位 | 统一事实源 |
| 写入入口 | Meyo API |
| ID 规则 | 主键、外键、业务 ID 全部使用 `uuid` |

## 2. 表总览

| 表名 | 业务场景 | 是否刚需 | 表注释 | 表说明 |
|---|---|---|---|---|
| `tenants` | 系统 | 是 | 租户主表 | 多租户私有化部署时，用它把不同客户的用户、知识库、场景和运行记录隔离开。 |
| `domains` | 系统 | 是 | 业务域主表 | 同一客户有客服、法务、财务等业务线时，用它把知识、Scene、评测和运行记录分到对应业务域。 |
| `users` | 系统 | 是 | 统一用户主表 | 用户登录 chatbot、维护知识库、发布 Flow、审批运行结果时，都用这张表确认统一身份。 |
| `user_identities` | 系统 | 是 | 外部账号和统一用户绑定 | 同一个人来自 Open WebUI、Langflow、SSO 等不同账号体系时，用它绑定到同一个 Meyo 用户。 |
| `workspaces` | 系统 | 是 | 统一 workspace 主表 | 团队协作场景用它承载一个工作空间下的成员、知识库、应用和 Flow。 |
| `workspace_members` | 系统 | 是 | workspace 成员和角色 | 判断用户在某个 workspace 里能看、能改、能发布还是能审批。 |
| `files` | 文件 | 是 | 文件元数据 | 用户上传文档、聊天附件或知识源文件时，用它保存文件归属、存储地址和校验信息。 |
| `chat_threads` | 聊天 | 是 | 聊天会话主表 | chatbot 会话列表场景用它保存一次对话主题，方便用户回看和继续追问。 |
| `chat_messages` | 聊天 | 是 | 聊天消息明细 | chatbot 问答场景用它保存用户问题、AI 回答和消息状态。 |
| `chat_message_attachments` | 聊天 | 是 | 聊天消息附件 | 用户在聊天里带文件提问时，用它把消息和上传文件关联起来。 |
| `knowledge_bases` | 知识库 | 是 | 知识库主表 | 领域专家维护知识资产时，用它定义一套可授权、可发布、可绑定到 Scene 的知识库。 |
| `knowledge_documents` | 知识库 | 是 | 知识文档主表 | 导入制度、手册、FAQ、合同等文档时，用它记录每份文档的来源和处理状态。 |
| `knowledge_chunks` | 知识库 | 是 | 文档切片 | 文档被切片后，RAG 检索和答案引用都回到这里拿正文事实。 |
| `knowledge_versions` | 知识库 | 是 | 知识库版本 | 知识库需要灰度、发布、回滚时，用它保存每个可追溯版本。 |
| `knowledge_publish_batches` | 知识库 | 是 | 知识发布批次 / active batch | 知识索引完成并发布给线上 RAG 时，用它标记当前生效的批次。 |
| `knowledge_index_jobs` | 知识库 | 是 | 知识索引任务 | 文档解析、切片、向量化、写图谱这些异步任务用它排队、追踪和失败重试。 |
| `knowledge_permissions` | 知识库 | 是 | 知识库权限 | 某个用户、角色或 Scene 是否能使用某个知识库，用它做权限判断。 |
| `knowledge_vector_refs` | 知识库 | 是 | 知识切片到向量库的引用 | RAG 要从向量库拿候选 chunk 时，用它把 meyo 的 chunk 和 Milvus / Chroma 里的向量记录对上。 |
| `knowledge_graph_refs` | 知识库 | 是 | 知识文档到图谱的引用 | GraphRAG 要从图数据库查实体关系时，用它把文档或 chunk 和 Neo4j / TuGraph 节点关系对上。 |
| `data_source_profiles` | DataOps | 是 | 数据源 profile | 对接企业数据源时，用它记录网盘、数据库、网页、工单系统等连接对象和同步来源。 |
| `secret_refs` | DataOps | 是 | 密钥引用 | 数据源或模型需要密钥时，用它记录密钥管理系统里的引用，业务库不存明文。 |
| `sync_policies` | DataOps | 是 | 数据同步策略 | 数据源要定时同步、增量同步或按规则过滤时，用它保存同步策略。 |
| `ontology_profiles` | 本体图谱 | 是 | 本体 profile | 需要按领域本体建设知识图谱时，用它定义这个业务域使用哪套本体。 |
| `ontology_versions` | 本体图谱 | 是 | 本体版本 | 本体规则调整、审核、发布和回滚时，用它保存每个可上线版本。 |
| `ontology_entity_types` | 本体图谱 | 是 | 本体实体类型 | 业务要约束图谱里只能有哪些实体时，用它定义产品、客户、条款等实体类型。 |
| `ontology_relation_types` | 本体图谱 | 是 | 本体关系类型 | 业务要约束实体之间能有哪些关系时，用它定义属于、引用、影响等关系类型。 |
| `vector_collections` | 向量检索 | 是 | 向量集合注册 | 每个知识库或场景使用哪个向量集合、维度和 embedding 模型，用它登记。 |
| `graph_profiles` | 本体图谱 | 是 | 图谱 profile 注册 | 每个业务域或场景使用哪个图数据库连接和本体版本，用它登记。 |
| `capability_registry` | 能力 | 是 | Skill / Tool / Prompt 统一能力注册 | 运营人员注册 Skill、Tool、Prompt 等可复用能力时，用它作为能力目录。 |
| `capability_versions` | 能力 | 是 | 能力版本 | 能力内容发生修改、发布、回滚时，用它保存每个版本和执行契约。 |
| `capability_permissions` | 能力 | 是 | 能力权限 | 控制谁能编辑能力、哪个 Scene 能调用能力、哪些能力需要授权。 |
| `model_profiles` | 模型策略 | 是 | 模型 profile | 选择模型供应商、模型名和用途时，用它统一配置路由、问答、改写等模型。 |
| `policy_profiles` | 模型策略 | 是 | 策略 profile | 入口安全、输出安全、权限控制、人工审批这些策略套装用它统一管理。 |
| `policy_rules` | 模型策略 | 是 | 策略规则 | 某个策略具体怎么判断、命中后怎么处理，用它保存规则。 |
| `policy_decisions` | 模型策略 | 是 | 策略裁决记录 | 每次请求是否被放行、拦截、脱敏或转人工，用它留下可审计记录。 |
| `app_registry` | 应用场景 | 是 | 可运行 App 注册 | 把 RAG 问答、客服助手、审批助手等可运行应用注册给 chatbot 入口使用。 |
| `scene_registry` | 应用场景 | 是 | App 下的业务 Scene 注册 | 一个 App 下有哪些可路由的业务场景，例如 RAG 问答、FAQ、工单查询，由它定义。 |
| `scene_route_examples` | 应用场景 | 是 | Scene 路由正反例 | 给场景识别器提供正例和反例，帮助判断用户自然语言该进入哪个 Scene。 |
| `scene_workflow_specs` | Flow 编排 | 是 | Scene Workflow 显式节点契约 | Scene 的完整 workflow 节点、边、输入输出契约都写这里，防止代码里隐式推理。 |
| `scene_knowledge_bindings` | Flow 编排 | 是 | Scene 和知识资产绑定 | 某个 Scene 只能查哪些知识库或知识版本，用它把场景和知识资产绑定。 |
| `scene_vector_bindings` | Flow 编排 | 是 | Scene 和向量集合绑定 | 某个 Scene 可以用哪些向量集合做召回，用它显式配置。 |
| `scene_graph_bindings` | Flow 编排 | 是 | Scene 和图谱 profile 绑定 | 某个 Scene 可以查哪些图谱 profile，用它显式配置。 |
| `scene_tool_bindings` | Flow 编排 | 是 | Scene 和工具能力绑定 | 某个 Scene 可以调用哪些工具或 Skill，用它显式配置。 |
| `scene_model_bindings` | Flow 编排 | 是 | Scene 和模型绑定 | 某个 Scene 在路由、改写、问答、校验等阶段分别用什么模型，用它显式配置。 |
| `router_versions` | 应用场景 | 是 | Router Workflow 版本 | 场景识别的 Router workflow 发布、回滚和生效版本用它管理。 |
| `flow_templates` | Flow 编排 | 是 | Flow 模板元数据 | Studio Flow 里可复用的流程模板用它登记，方便新 Scene 复制起步。 |
| `flow_versions` | Flow 编排 | 是 | 可发布 Flow 版本 | 一个 Flow 被评测通过并准备上线时，用它保存可执行版本、artifact 和 hash。 |
| `app_scene_flow_bindings` | Flow 编排 | 是 | App + Scene + Flow 生产绑定 | 线上真正执行哪个 App、Scene、Flow 版本组合，由这张表决定。 |
| `scene_eval_case_sets` | 评测发布 | 是 | Scene 评测集 | 发布前给某个 Scene 准备一组测试集时，用它管理测试集。 |
| `scene_eval_cases` | 评测发布 | 是 | Scene 评测用例 | 每条测试问题、期望答案、断言和证据要求都放在这里。 |
| `scene_eval_runs` | 评测发布 | 是 | Scene 评测执行 | 一次发布前或回归测试执行，用它记录整批评测运行。 |
| `scene_eval_results` | 评测发布 | 是 | Scene 评测结果 | 每条测试用例是否通过、失败原因和得分，用它保存明细。 |
| `scene_approvals` | 评测发布 | 是 | Scene / Flow 发布审批 | Scene 或 Flow 上线前需要人工审批时，用它记录审批单。 |
| `scene_activation_history` | 评测发布 | 是 | Scene / Flow 激活历史 | Scene 或 Flow 被启用、暂停、回滚或退役时，用它记录操作历史。 |
| `approval_requests` | 运行审批 | 是 | 运行时人工审批请求 | 运行中遇到高风险工具调用、缺少授权或需要人工确认时，用它创建待办。 |
| `approval_events` | 运行审批 | 是 | 运行时人工审批事件 | 人工审批被提交、通过、拒绝或超时的过程，用它记录状态变化。 |
| `app_runs` | 运行审计 | 是 | App 请求运行记录 | 用户从 chatbot 发起一次请求后，用它作为整条运行链路的主记录。 |
| `route_decisions` | 运行审计 | 是 | Router 决策记录 | Router 识别用户意图、候选 Scene、最终选择和拒绝原因都记录在这里。 |
| `flow_runs` | 运行审计 | 是 | Flow 执行记录 | 某个 Flow 被实际执行一次时，用它记录输入、输出、状态和耗时。 |
| `run_steps` | 运行审计 | 是 | 运行节点明细 | Framework 节点逐步执行时，用它保存路由、检索、生成、校验等每步结果。 |
| `scene_node_events` | 运行审计 | 是 | Scene 内部节点事件 | Studio Flow 内部节点运行事件用它保存，方便对齐画布节点排障。 |
| `data_access_events` | 运行审计 | 是 | Internal Data API 数据访问审计 | 任意节点查询 PostgreSQL、Milvus、Neo4j 时都写这里，审计它到底查了什么数据。 |
| `trace_events` | 运行审计 | 是 | 通用 trace 事件 | 跨 chatbot、meyo、flow 的全链路 trace 用它串起来，排查一次请求卡在哪里。 |
| `run_metrics` | 运行审计 | 是 | Run 指标 | 统计一次运行的延迟、token、召回数、命中率等指标，用于看板和优化。 |
| `evidence_records` | 运行审计 | 是 | 证据记录 | 最终答案引用了哪些 chunk、图谱路径或结构化记录，用它保存证据。 |
| `evidence_citations` | 运行审计 | 是 | 答案引用证据 | 答案里每一段话对应哪些证据，用它支撑可追溯引用。 |
| `no_answer_records` | 运行审计 | 是 | 无答案记录 | RAG 没找到证据或不允许回答时，用它记录为什么拒答。 |
| `feedback_events` | 运行审计 | 是 | 用户反馈 | 用户点赞、点踩、纠错或补充反馈时，用它沉淀改进数据。 |
| `active_scene_router_view` | 应用场景 | 是 | Router 候选 Scene 视图 | Router 查询当前可用 Scene 时只读这个视图，避免临时拼多个表。 |

## 3. 统一用户和 Workspace

### `tenants`

表注释：租户主表，所有生产事实表必须通过 `tenant_id` 隔离。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `tenant_id` | uuid | 是 | 租户 ID |
| `name` | text | 是 | 租户名称 |
| `status` | text | 是 | 状态：active / suspended / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `domains`

表注释：业务域主表。RAG、Agent、Skill、Run、Knowledge 都必须能追溯到 `domain_id`。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `domain_id` | uuid | 是 | 业务域 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `name` | text | 是 | 业务域名称 |
| `description` | text | 否 | 业务域描述 |
| `status` | text | 是 | active / archived / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `users`

表注释：Meyo 统一用户主表。chatbot 和 flow 的用户都映射到这里。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `user_id` | uuid | 是 | 统一用户 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `display_name` | text | 是 | 展示名 |
| `email` | text | 否 | 邮箱 |
| `phone` | text | 否 | 手机号 |
| `avatar_uri` | text | 否 | 头像 URI |
| `status` | text | 是 | 状态：active / disabled / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `user_identities`

表注释：外部账号绑定表，用于绑定 Open WebUI、Langflow、SSO、OIDC 等外部身份。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `identity_id` | uuid | 是 | 绑定记录 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `user_id` | uuid | 是 | 统一用户 ID |
| `provider` | text | 是 | 来源：chatbot / flow / oidc / saml |
| `external_ref` | text | 是 | 外部系统用户标识，非 UUID 不命名为 `*_id` |
| `email` | text | 否 | 外部身份邮箱 |
| `status` | text | 是 | 状态：active / disabled |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `workspaces`

表注释：统一 workspace 主表，chatbot 和 flow 只通过 Meyo API 使用它。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `workspace_id` | uuid | 是 | workspace ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `name` | text | 是 | workspace 名称 |
| `description` | text | 否 | 描述 |
| `owner_user_id` | uuid | 是 | 所有人 |
| `status` | text | 是 | 状态：active / archived / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `workspace_members`

表注释：workspace 成员关系和角色。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `workspace_member_id` | uuid | 是 | 成员关系 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `user_id` | uuid | 是 | 用户 ID |
| `role` | text | 是 | 角色：owner / admin / member / viewer |
| `status` | text | 是 | 状态：active / removed |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

## 4. 文件和 Chat History

### `files`

表注释：统一文件元数据表。文件 bytes 放对象存储，本表保存 URI、hash、归属和状态。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `file_id` | uuid | 是 | 文件 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `uploaded_by_user_id` | uuid | 是 | 上传用户 |
| `filename` | text | 是 | 原始文件名 |
| `content_type` | text | 否 | MIME 类型 |
| `byte_size` | bigint | 是 | 文件大小 |
| `storage_uri` | text | 是 | 对象存储 URI |
| `sha256` | text | 是 | 文件 SHA256 |
| `status` | text | 是 | 状态：uploaded / processing / ready / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `chat_threads`

表注释：统一聊天会话主表，chatbot 的历史会话读取这里。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `thread_id` | uuid | 是 | 会话 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `user_id` | uuid | 是 | 发起用户 |
| `app_id` | uuid | 否 | 关联 App |
| `title` | text | 是 | 会话标题 |
| `status` | text | 是 | 状态：active / archived / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `chat_messages`

表注释：统一聊天消息明细表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `message_id` | uuid | 是 | 消息 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `thread_id` | uuid | 是 | 会话 ID |
| `user_id` | uuid | 否 | 用户 ID，assistant/system 消息可为空 |
| `parent_message_id` | uuid | 否 | 父消息 |
| `role` | text | 是 | user / assistant / system / tool |
| `content` | jsonb | 是 | 消息内容 |
| `status` | text | 是 | created / streaming / completed / failed / deleted |
| `app_run_id` | uuid | 否 | 关联运行记录 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `chat_message_attachments`

表注释：聊天消息和文件附件关联表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `attachment_id` | uuid | 是 | 附件关系 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `message_id` | uuid | 是 | 消息 ID |
| `file_id` | uuid | 是 | 文件 ID |
| `attachment_type` | text | 是 | input_file / citation_file / generated_file |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |

## 5. Knowledge

### `data_source_profiles`

表注释：数据源 profile。用于记录数据来自哪里、由哪个同步策略维护。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `data_source_profile_id` | uuid | 是 | 数据源 profile ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `name` | text | 是 | 数据源名称 |
| `source_type` | text | 是 | file / web / database / api / sharepoint / manual |
| `connection_config` | jsonb | 是 | 脱敏连接配置 |
| `secret_ref_id` | uuid | 否 | 密钥引用 ID |
| `status` | text | 是 | draft / active / paused / deleted |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `secret_refs`

表注释：密钥引用表，只保存密钥系统引用，不保存真实密钥。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `secret_ref_id` | uuid | 是 | 密钥引用 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `secret_provider` | text | 是 | vault / env / cloud_secret_manager |
| `secret_external_ref` | text | 是 | 外部密钥引用 |
| `purpose` | text | 是 | 用途 |
| `status` | text | 是 | active / revoked |
| `created_at` | timestamptz | 是 | 创建时间 |

### `sync_policies`

表注释：数据源同步策略表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `sync_policy_id` | uuid | 是 | 同步策略 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `data_source_profile_id` | uuid | 是 | 数据源 profile ID |
| `schedule` | text | 否 | 同步计划 |
| `mode` | text | 是 | manual / incremental / full |
| `filters` | jsonb | 是 | 同步过滤条件 |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `ontology_profiles`

表注释：本体 profile 主表。RAG 图谱查询和关系校验必须引用它。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `ontology_profile_id` | uuid | 是 | 本体 profile ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `name` | text | 是 | 本体名称 |
| `description` | text | 否 | 描述 |
| `status` | text | 是 | draft / active / retired |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `ontology_versions`

表注释：本体版本表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `ontology_version_id` | uuid | 是 | 本体版本 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `ontology_profile_id` | uuid | 是 | 本体 profile ID |
| `version` | integer | 是 | 版本号 |
| `schema` | jsonb | 是 | 本体 schema |
| `status` | text | 是 | draft / active / retired |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `ontology_entity_types`

表注释：本体实体类型表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `entity_type_id` | uuid | 是 | 实体类型 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `ontology_version_id` | uuid | 是 | 本体版本 ID |
| `name` | text | 是 | 实体类型名称 |
| `properties_schema` | jsonb | 是 | 属性 schema |
| `created_at` | timestamptz | 是 | 创建时间 |

### `ontology_relation_types`

表注释：本体关系类型表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `relation_type_id` | uuid | 是 | 关系类型 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `ontology_version_id` | uuid | 是 | 本体版本 ID |
| `name` | text | 是 | 关系类型名称 |
| `source_entity_type_id` | uuid | 是 | 起点实体类型 |
| `target_entity_type_id` | uuid | 是 | 终点实体类型 |
| `properties_schema` | jsonb | 是 | 属性 schema |
| `created_at` | timestamptz | 是 | 创建时间 |

### `vector_collections`

表注释：向量集合注册表。Milvus / Chroma 是向量事实源，本表保存集合归属、维度、模型和状态。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `vector_collection_id` | uuid | 是 | 向量集合 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `knowledge_base_id` | uuid | 否 | 知识库 ID |
| `vector_provider` | text | 是 | milvus / chroma / pgvector |
| `collection_name` | text | 是 | 集合名 |
| `embedding_model` | text | 是 | embedding 模型 |
| `dimension` | integer | 是 | 向量维度 |
| `status` | text | 是 | building / active / retired / failed |
| `created_at` | timestamptz | 是 | 创建时间 |

### `graph_profiles`

表注释：图谱 profile 注册表。Neo4j / TuGraph 是图事实源，本表保存连接 profile、ontology 绑定和状态。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `graph_profile_id` | uuid | 是 | 图谱 profile ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `graph_provider` | text | 是 | neo4j / tugraph |
| `profile_name` | text | 是 | profile 名称 |
| `ontology_profile_id` | uuid | 否 | 本体 profile ID |
| `connection_config` | jsonb | 是 | 脱敏连接配置 |
| `secret_ref_id` | uuid | 否 | 密钥引用 ID |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `knowledge_bases`

表注释：统一知识库主表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `data_source_profile_id` | uuid | 否 | 默认数据源 profile |
| `ontology_profile_id` | uuid | 否 | 默认本体 profile |
| `name` | text | 是 | 知识库名称 |
| `description` | text | 否 | 描述 |
| `owner_user_id` | uuid | 是 | 所有人 |
| `status` | text | 是 | draft / active / archived / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `knowledge_documents`

表注释：知识库文档主表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `document_id` | uuid | 是 | 文档 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `file_id` | uuid | 否 | 来源文件 ID |
| `title` | text | 是 | 文档标题 |
| `source_uri` | text | 否 | 来源 URI |
| `content_sha256` | text | 是 | 正文 hash |
| `status` | text | 是 | uploaded / parsed / indexed / failed / deleted |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `knowledge_chunks`

表注释：文档切片表，Milvus / Chroma 只保存向量，正文以本表为准。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `chunk_id` | uuid | 是 | 切片 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `document_id` | uuid | 是 | 文档 ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `chunk_index` | integer | 是 | 文档内切片序号 |
| `content` | text | 是 | 切片正文 |
| `content_sha256` | text | 是 | 切片 hash |
| `token_count` | integer | 否 | token 数 |
| `metadata` | jsonb | 是 | 页码、段落、标题等信息 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `knowledge_versions`

表注释：知识库版本表，用于发布、回滚和审计。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `knowledge_version_id` | uuid | 是 | 知识版本 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `publish_batch_id` | uuid | 否 | 所属发布批次 |
| `version` | integer | 是 | 版本号 |
| `status` | text | 是 | draft / indexing / active / retired |
| `document_count` | integer | 是 | 文档数 |
| `chunk_count` | integer | 是 | 切片数 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `activated_at` | timestamptz | 否 | 激活时间 |

### `knowledge_publish_batches`

表注释：知识发布批次表。RAG 运行时 QA05 查询的 active batch 来自这里。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `publish_batch_id` | uuid | 是 | 发布批次 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `knowledge_version_id` | uuid | 是 | 知识版本 ID |
| `status` | text | 是 | draft / indexing / approved / active / retired / failed |
| `activated_at` | timestamptz | 否 | 激活时间 |
| `retired_at` | timestamptz | 否 | 退役时间 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `knowledge_index_jobs`

表注释：知识索引任务表，记录解析、切片、向量索引、图谱写入等任务。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `index_job_id` | uuid | 是 | 索引任务 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `publish_batch_id` | uuid | 是 | 发布批次 ID |
| `job_type` | text | 是 | parse / chunk / embed / graph / fulltext |
| `status` | text | 是 | queued / running / succeeded / failed |
| `input_ref` | jsonb | 是 | 输入引用 |
| `output_ref` | jsonb | 否 | 输出引用 |
| `error` | jsonb | 否 | 错误信息 |
| `started_at` | timestamptz | 否 | 开始时间 |
| `finished_at` | timestamptz | 否 | 结束时间 |

### `knowledge_permissions`

表注释：知识库访问控制表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `permission_id` | uuid | 是 | 权限记录 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `principal_type` | text | 是 | user / workspace / role / scene |
| `principal_id` | uuid | 是 | 主体 ID |
| `permission` | text | 是 | read / write / admin |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `knowledge_vector_refs`

表注释：知识切片到向量库记录的引用表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `vector_ref_id` | uuid | 是 | 向量引用 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `document_id` | uuid | 是 | 文档 ID |
| `chunk_id` | uuid | 是 | 切片 ID |
| `vector_provider` | text | 是 | milvus / chroma / pgvector |
| `collection_name` | text | 是 | 向量集合名 |
| `vector_external_ref` | text | 是 | 向量库返回的外部标识 |
| `embedding_model` | text | 是 | embedding 模型 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `knowledge_graph_refs`

表注释：知识文档或切片到图数据库实体/关系的引用表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `graph_ref_id` | uuid | 是 | 图谱引用 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `document_id` | uuid | 是 | 文档 ID |
| `chunk_id` | uuid | 否 | 切片 ID |
| `graph_provider` | text | 是 | neo4j / tugraph |
| `graph_profile` | text | 是 | 图谱 profile |
| `entity_external_ref` | text | 否 | 图数据库实体外部标识 |
| `relation_external_ref` | text | 否 | 图数据库关系外部标识 |
| `created_at` | timestamptz | 是 | 创建时间 |

## 6. Capability

### `model_profiles`

表注释：模型 profile 表。Scene 模型绑定必须引用已注册模型 profile 或明确记录 provider / model。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `model_profile_id` | uuid | 是 | 模型 profile ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `provider` | text | 是 | 模型供应商 |
| `model_name` | text | 是 | 模型名称 |
| `purpose` | text | 是 | router / answer / rewrite / eval / embedding |
| `params` | jsonb | 是 | 默认参数 |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `policy_profiles`

表注释：策略 profile 主表。输入安全、输出安全、ACL、工具审批都从这里解析。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `policy_profile_id` | uuid | 是 | 策略 profile ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `name` | text | 是 | 策略名称 |
| `policy_type` | text | 是 | input_guard / output_guard / acl / tool_approval / publish |
| `status` | text | 是 | draft / active / retired |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `policy_rules`

表注释：策略规则表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `policy_rule_id` | uuid | 是 | 策略规则 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `policy_profile_id` | uuid | 是 | 策略 profile ID |
| `rule_code` | text | 是 | 规则编号 |
| `condition` | jsonb | 是 | 触发条件 |
| `action` | text | 是 | allow / deny / require_approval / redact |
| `priority` | integer | 是 | 优先级 |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `policy_decisions`

表注释：策略裁决记录表。FW03、FW11、FW17、QA03、QA14、QA21 都必须写裁决结果。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `policy_decision_id` | uuid | 是 | 策略裁决 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 否 | Run ID |
| `app_run_id` | uuid | 否 | App Run ID |
| `flow_run_id` | uuid | 否 | Flow Run ID |
| `policy_profile_id` | uuid | 是 | 策略 profile ID |
| `node_code` | text | 是 | 触发节点编号 |
| `subject_user_id` | uuid | 否 | 被裁决用户 |
| `resource_ref` | jsonb | 是 | 被裁决资源引用 |
| `decision` | text | 是 | allow / deny / require_approval / redact |
| `reason` | text | 是 | 裁决原因 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `capability_registry`

表注释：Skill / Tool / Prompt 的统一注册主表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `capability_id` | uuid | 是 | 能力 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `name` | text | 是 | 能力名称 |
| `capability_type` | text | 是 | skill / tool / prompt |
| `description` | text | 否 | 描述 |
| `owner_user_id` | uuid | 是 | 所有人 |
| `status` | text | 是 | draft / active / retired |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `capability_versions`

表注释：能力版本表，保存内容、参数和发布状态。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `capability_version_id` | uuid | 是 | 能力版本 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `capability_id` | uuid | 是 | 能力 ID |
| `version` | integer | 是 | 版本号 |
| `content` | jsonb | 是 | 能力内容 |
| `input_schema` | jsonb | 否 | 输入契约 |
| `output_schema` | jsonb | 否 | 输出契约 |
| `status` | text | 是 | draft / testing / approved / active / retired |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `capability_permissions`

表注释：能力访问控制表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `permission_id` | uuid | 是 | 权限记录 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `capability_id` | uuid | 是 | 能力 ID |
| `principal_type` | text | 是 | user / workspace / role / scene |
| `principal_id` | uuid | 是 | 主体 ID |
| `permission` | text | 是 | read / execute / write / admin |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

## 7. App / Scene / Flow

### `app_registry`

表注释：可运行 App 注册表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `app_id` | uuid | 是 | App ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `name` | text | 是 | App 名称 |
| `description` | text | 否 | 描述 |
| `status` | text | 是 | draft / active / paused / retired |
| `default_router_version_id` | uuid | 否 | 默认 Router Workflow 版本 |
| `policy_profile_id` | uuid | 否 | 默认策略 profile |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `scene_registry`

表注释：业务 Scene 注册表，Router 只能选择 active Scene。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `scene_id` | uuid | 是 | Scene ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `app_id` | uuid | 是 | App ID |
| `name` | text | 是 | Scene 名称 |
| `description` | text | 是 | 业务说明 |
| `intent_description` | text | 是 | Router 可读意图说明 |
| `input_schema_ref` | text | 是 | 输入 schema 引用 |
| `output_schema_ref` | text | 是 | 输出 schema 引用 |
| `policy_profile_id` | uuid | 否 | 默认策略 profile |
| `status` | text | 是 | draft / testing / approved / active / paused / retired |
| `version` | integer | 是 | 元数据版本 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `updated_at` | timestamptz | 是 | 更新时间 |

### `scene_route_examples`

表注释：Scene 路由样例表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `example_id` | uuid | 是 | 样例 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `app_id` | uuid | 是 | App ID |
| `scene_id` | uuid | 是 | Scene ID |
| `text` | text | 是 | 用户输入样例 |
| `label` | text | 是 | positive / negative |
| `reason` | text | 是 | 命中或排除原因 |
| `status` | text | 是 | active / disabled |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_workflow_specs`

表注释：Scene Workflow 显式节点契约表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `workflow_spec_id` | uuid | 是 | Workflow Spec ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `app_id` | uuid | 是 | App ID |
| `scene_id` | uuid | 是 | Scene ID |
| `nodes` | jsonb | 是 | 显式节点列表 |
| `edges` | jsonb | 是 | 显式边列表 |
| `input_contract` | jsonb | 是 | 输入契约 |
| `output_contract` | jsonb | 是 | 输出契约 |
| `failure_policy` | jsonb | 是 | 失败策略 |
| `status` | text | 是 | draft / validated / retired |
| `schema_version` | integer | 是 | 契约版本 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_knowledge_bindings`

表注释：Scene 和知识库或知识版本的绑定表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `binding_id` | uuid | 是 | 绑定 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `scene_id` | uuid | 是 | Scene ID |
| `workflow_spec_id` | uuid | 否 | Scene Workflow Spec ID |
| `knowledge_base_id` | uuid | 是 | 知识库 ID |
| `knowledge_version_id` | uuid | 否 | 指定知识版本 |
| `status` | text | 是 | active / disabled |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_vector_bindings`

表注释：Scene 和向量集合的绑定表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `binding_id` | uuid | 是 | 绑定 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `scene_id` | uuid | 是 | Scene ID |
| `vector_collection_id` | uuid | 是 | 向量集合 ID |
| `vector_provider` | text | 是 | milvus / chroma / pgvector |
| `collection_name` | text | 是 | 向量集合名 |
| `embedding_model` | text | 是 | embedding 模型 |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_graph_bindings`

表注释：Scene 和图谱 profile 的绑定表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `binding_id` | uuid | 是 | 绑定 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `scene_id` | uuid | 是 | Scene ID |
| `graph_profile_id` | uuid | 是 | 图谱 profile ID |
| `ontology_profile_id` | uuid | 否 | 本体 profile ID |
| `graph_provider` | text | 是 | neo4j / tugraph |
| `graph_profile` | text | 是 | 图谱 profile |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_tool_bindings`

表注释：Scene 和 Tool / Skill 能力的绑定表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `binding_id` | uuid | 是 | 绑定 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `scene_id` | uuid | 是 | Scene ID |
| `capability_id` | uuid | 是 | 能力 ID |
| `capability_version_id` | uuid | 否 | 能力版本 ID |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_model_bindings`

表注释：Scene 和模型的绑定表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `binding_id` | uuid | 是 | 绑定 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `scene_id` | uuid | 是 | Scene ID |
| `model_profile_id` | uuid | 否 | 模型 profile ID |
| `model_provider` | text | 是 | 模型供应商 |
| `model_name` | text | 是 | 模型名称 |
| `purpose` | text | 是 | router / answer / rewrite / eval |
| `params` | jsonb | 是 | 模型参数 |
| `status` | text | 是 | active / disabled |
| `created_at` | timestamptz | 是 | 创建时间 |

### `router_versions`

表注释：Router Workflow 版本表。Router 版本是生产事实，不能由 chatbot 或 prompt 隐式决定。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `router_version_id` | uuid | 是 | Router 版本 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `app_id` | uuid | 是 | App ID |
| `version` | integer | 是 | 版本号 |
| `artifact_uri` | text | 是 | Router workflow artifact URI |
| `artifact_sha256` | text | 是 | Router artifact hash |
| `eval_run_id` | uuid | 否 | 评测运行 ID |
| `status` | text | 是 | draft / testing / approved / active / retired |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `flow_templates`

表注释：Flow 模板元数据表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `flow_template_id` | uuid | 是 | Flow 模板 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `name` | text | 是 | 模板名称 |
| `description` | text | 否 | 描述 |
| `template_type` | text | 是 | rag / router / tool / custom |
| `metadata` | jsonb | 是 | 扩展信息 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `flow_versions`

表注释：可发布 Flow 版本表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `flow_version_id` | uuid | 是 | Flow 版本 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `flow_template_id` | uuid | 否 | Flow 模板 ID |
| `studio_flow_external_ref` | text | 否 | studio-flow 外部 Flow 标识 |
| `version` | integer | 是 | 版本号 |
| `artifact_uri` | text | 是 | Flow artifact URI |
| `artifact_sha256` | text | 是 | Flow artifact hash |
| `status` | text | 是 | draft / testing / approved / active / retired |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `app_scene_flow_bindings`

表注释：App + Scene + Flow 的生产绑定表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `binding_id` | uuid | 是 | 绑定 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `app_id` | uuid | 是 | App ID |
| `scene_id` | uuid | 是 | Scene ID |
| `flow_version_id` | uuid | 是 | Flow 版本 ID |
| `status` | text | 是 | draft / testing / approved / active / retired |
| `approval_id` | uuid | 否 | 发布审批 ID |
| `effective_from` | timestamptz | 否 | 生效时间 |
| `effective_to` | timestamptz | 否 | 失效时间 |
| `activated_at` | timestamptz | 否 | 激活时间 |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

## 8. Eval / Approval

### `scene_eval_case_sets`

表注释：Scene 评测集主表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `case_set_id` | uuid | 是 | 评测集 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `scene_id` | uuid | 是 | Scene ID |
| `name` | text | 是 | 评测集名称 |
| `status` | text | 是 | draft / active / archived |
| `created_by_user_id` | uuid | 是 | 创建人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_eval_cases`

表注释：Scene 评测用例表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `case_id` | uuid | 是 | 用例 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `case_set_id` | uuid | 是 | 评测集 ID |
| `input` | jsonb | 是 | 输入 |
| `expected_output` | jsonb | 否 | 期望输出 |
| `assertions` | jsonb | 是 | 断言规则 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_eval_runs`

表注释：Scene 评测执行记录表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `eval_run_id` | uuid | 是 | 评测运行 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `case_set_id` | uuid | 是 | 评测集 ID |
| `flow_version_id` | uuid | 是 | Flow 版本 ID |
| `status` | text | 是 | running / succeeded / failed |
| `started_at` | timestamptz | 是 | 开始时间 |
| `finished_at` | timestamptz | 否 | 结束时间 |

### `scene_eval_results`

表注释：Scene 评测结果明细表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `eval_result_id` | uuid | 是 | 评测结果 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `eval_run_id` | uuid | 是 | 评测运行 ID |
| `case_id` | uuid | 是 | 用例 ID |
| `passed` | boolean | 是 | 是否通过 |
| `score` | numeric | 否 | 评分 |
| `details` | jsonb | 是 | 结果详情 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_approvals`

表注释：Scene / Flow 发布审批表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `approval_id` | uuid | 是 | 审批 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `target_type` | text | 是 | scene / flow_binding / knowledge_version |
| `target_id` | uuid | 是 | 审批对象 ID |
| `decision` | text | 是 | approved / rejected |
| `comment` | text | 否 | 审批意见 |
| `approved_by_user_id` | uuid | 是 | 审批人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `scene_activation_history`

表注释：Scene / Flow 绑定的激活、暂停、回滚、退役历史。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `history_id` | uuid | 是 | 历史记录 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `binding_id` | uuid | 是 | App Scene Flow 绑定 ID |
| `action` | text | 是 | activate / pause / rollback / retire |
| `from_status` | text | 否 | 变更前状态 |
| `to_status` | text | 是 | 变更后状态 |
| `created_by_user_id` | uuid | 是 | 操作人 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `approval_requests`

表注释：运行时人工审批请求表。FW11 或 R18 进入 waiting_approval 时写入。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `approval_request_id` | uuid | 是 | 审批请求 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `flow_run_id` | uuid | 否 | Flow Run ID |
| `request_type` | text | 是 | tool_call / policy_exception / high_risk_answer / publish |
| `target_ref` | jsonb | 是 | 审批对象引用 |
| `status` | text | 是 | pending / approved / rejected / expired / cancelled |
| `requested_by_node_code` | text | 是 | 触发审批的节点编号 |
| `requested_by_user_id` | uuid | 否 | 发起用户 |
| `created_at` | timestamptz | 是 | 创建时间 |
| `expires_at` | timestamptz | 否 | 过期时间 |

### `approval_events`

表注释：运行时审批事件表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `approval_event_id` | uuid | 是 | 审批事件 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `approval_request_id` | uuid | 是 | 审批请求 ID |
| `event_type` | text | 是 | requested / approved / rejected / expired / cancelled |
| `actor_user_id` | uuid | 否 | 操作用户 |
| `comment` | text | 否 | 说明 |
| `payload` | jsonb | 是 | 事件载荷 |
| `created_at` | timestamptz | 是 | 创建时间 |

## 9. Run / Trace / Evidence

### `app_runs`

表注释：一次用户请求的 App 级运行记录。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `app_run_id` | uuid | 是 | App Run ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `request_id` | uuid | 是 | 请求 ID |
| `trace_id` | uuid | 是 | Trace ID |
| `workspace_id` | uuid | 是 | workspace ID |
| `app_id` | uuid | 是 | App ID |
| `thread_id` | uuid | 否 | 聊天会话 ID |
| `user_id` | uuid | 是 | 用户 ID |
| `route_decision_id` | uuid | 否 | 路由决策 ID |
| `input` | jsonb | 是 | 请求输入 |
| `output` | jsonb | 否 | 请求输出 |
| `status` | text | 是 | received / running / waiting_approval / succeeded / failed / blocked / cancelled |
| `created_at` | timestamptz | 是 | 创建时间 |
| `finished_at` | timestamptz | 否 | 结束时间 |

### `route_decisions`

表注释：Router 决策记录表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `route_decision_id` | uuid | 是 | 路由决策 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `router_flow_version_id` | uuid | 否 | Router Flow 版本 |
| `candidate_scenes` | jsonb | 是 | 候选 Scene 列表 |
| `selected_scene_id` | uuid | 否 | 选中的 Scene |
| `validated_scene_id` | uuid | 否 | 校验通过的 Scene |
| `selected_binding_id` | uuid | 否 | 选中的 Flow 绑定 |
| `confidence` | numeric | 否 | 置信度 |
| `reason` | text | 否 | 路由理由 |
| `status` | text | 是 | candidate / validated / rejected / executed |
| `created_at` | timestamptz | 是 | 创建时间 |

### `flow_runs`

表注释：一次 Flow 执行记录。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `flow_run_id` | uuid | 是 | Flow Run ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `domain_id` | uuid | 是 | 业务域 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `trace_id` | uuid | 是 | Trace ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `scene_id` | uuid | 是 | Scene ID |
| `flow_version_id` | uuid | 是 | Flow 版本 ID |
| `studio_run_external_ref` | text | 否 | studio-flow 外部运行标识 |
| `status` | text | 是 | running / succeeded / failed / cancelled |
| `input` | jsonb | 是 | Flow 输入 |
| `output` | jsonb | 否 | Flow 输出 |
| `started_at` | timestamptz | 是 | 开始时间 |
| `finished_at` | timestamptz | 否 | 结束时间 |

### `run_steps`

表注释：运行节点明细表，记录框架节点执行。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `run_step_id` | uuid | 是 | 节点执行 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `flow_run_id` | uuid | 否 | Flow Run ID |
| `node_code` | text | 是 | 节点编号，如 FW00 / QA01 |
| `node_name` | text | 是 | 节点名称 |
| `status` | text | 是 | started / succeeded / failed / skipped |
| `input_ref` | jsonb | 否 | 输入引用 |
| `output_ref` | jsonb | 否 | 输出引用 |
| `input` | jsonb | 否 | 节点输入 |
| `output` | jsonb | 否 | 节点输出 |
| `error_code` | text | 否 | 错误码 |
| `error_detail_ref` | jsonb | 否 | 错误详情引用 |
| `error` | jsonb | 否 | 错误信息 |
| `started_at` | timestamptz | 是 | 开始时间 |
| `finished_at` | timestamptz | 否 | 结束时间 |

### `scene_node_events`

表注释：Scene 内部节点事件表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `event_id` | uuid | 是 | 事件 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `flow_run_id` | uuid | 是 | Flow Run ID |
| `scene_id` | uuid | 是 | Scene ID |
| `scene_node_code` | text | 是 | Scene 节点编号 |
| `event_type` | text | 是 | start / end / token / error / custom |
| `payload` | jsonb | 是 | 事件内容 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `data_access_events`

表注释：Internal Data API 数据访问审计表。所有 PostgreSQL / Milvus / Neo4j 查询都要记录。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `data_access_event_id` | uuid | 是 | 数据访问事件 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `flow_run_id` | uuid | 否 | Flow Run ID |
| `node_code` | text | 是 | 发起查询的节点编号 |
| `api_name` | text | 是 | Internal API 名称 |
| `source_store` | text | 是 | postgres / milvus / chroma / neo4j / tugraph |
| `query_ref` | jsonb | 是 | 查询引用或脱敏查询摘要 |
| `result_count` | integer | 是 | 返回数量 |
| `status` | text | 是 | succeeded / failed / skipped |
| `error` | jsonb | 否 | 错误信息 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `trace_events`

表注释：通用 trace 事件表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `trace_event_id` | uuid | 是 | Trace 事件 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `trace_id` | uuid | 是 | Trace ID |
| `run_id` | uuid | 是 | Run ID |
| `event_type` | text | 是 | request / route / flow / data / evidence / error |
| `node_code` | text | 否 | 节点编号 |
| `payload` | jsonb | 是 | 事件载荷 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `run_metrics`

表注释：Run 指标表，用于 FW20 写 latency、token、召回数等指标。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `metric_id` | uuid | 是 | 指标 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `flow_run_id` | uuid | 否 | Flow Run ID |
| `metric_name` | text | 是 | 指标名 |
| `metric_value` | numeric | 是 | 指标值 |
| `unit` | text | 否 | 单位 |
| `tags` | jsonb | 是 | 标签 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `evidence_records`

表注释：回答证据表，最终答案必须引用这里的证据。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `evidence_id` | uuid | 是 | 证据 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `flow_run_id` | uuid | 否 | Flow Run ID |
| `evidence_type` | text | 是 | chunk / graph_path / tool_result / sql_result |
| `source_type` | text | 是 | postgres / vector / graph / tool |
| `source_ref` | jsonb | 是 | 来源引用 |
| `document_id` | uuid | 否 | 文档 ID |
| `chunk_id` | uuid | 否 | 切片 ID |
| `graph_path_external_ref` | text | 否 | 图路径外部引用 |
| `acl_decision` | text | 是 | allow / deny / redacted |
| `selected_by_node_code` | text | 是 | 选择证据的节点编号 |
| `score` | numeric | 否 | 检索分数 |
| `content_snapshot` | text | 是 | 证据内容快照 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `evidence_citations`

表注释：答案片段和证据绑定表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `citation_id` | uuid | 是 | 引用 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `message_id` | uuid | 否 | 回答消息 ID |
| `evidence_id` | uuid | 是 | 证据 ID |
| `answer_span` | jsonb | 是 | 答案片段位置 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `no_answer_records`

表注释：无答案记录表，用于禁止模型无证据猜测。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `no_answer_id` | uuid | 是 | 无答案记录 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 是 | 全链路 Run ID |
| `app_run_id` | uuid | 是 | App Run ID |
| `reason_code` | text | 是 | no_evidence / low_confidence / policy_blocked |
| `details` | jsonb | 是 | 详细原因 |
| `created_at` | timestamptz | 是 | 创建时间 |

### `feedback_events`

表注释：用户反馈表。

| 字段 | 类型 | 必填 | 字段注释 |
|---|---|---|---|
| `feedback_id` | uuid | 是 | 反馈 ID |
| `tenant_id` | uuid | 是 | 租户 ID |
| `run_id` | uuid | 否 | 全链路 Run ID |
| `app_run_id` | uuid | 否 | App Run ID |
| `message_id` | uuid | 否 | 消息 ID |
| `user_id` | uuid | 是 | 用户 ID |
| `rating` | integer | 否 | 评分 |
| `feedback_type` | text | 是 | like / dislike / correction / issue |
| `comment` | text | 否 | 反馈内容 |
| `created_at` | timestamptz | 是 | 创建时间 |

## 10. Router View

### `active_scene_router_view`

视图注释：Router 唯一候选列表。Router 只读该视图，不直接拼多表。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `tenant_id` | uuid | 租户 ID |
| `domain_id` | uuid | 业务域 ID |
| `app_id` | uuid | App ID |
| `scene_id` | uuid | active Scene ID |
| `scene_name` | text | Scene 名称 |
| `intent_description` | text | Router 可读意图 |
| `route_examples` | jsonb | active 正反例 |
| `router_version_id` | uuid | active Router 版本 |
| `binding_id` | uuid | active App Scene Flow 绑定 |
| `flow_version_id` | uuid | active Flow 版本 |
| `policy_profile_id` | uuid | active 策略 profile |
