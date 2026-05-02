---
title: Meyo Studio Flow 数据库表字典
---

# Meyo Studio Flow 数据库表字典

## 1. 服务归属

| 项 | 值 |
|---|---|
| 服务 | `flow` / `apps/meyo-studio-flow` |
| 当前上游 | Langflow |
| 当前本地库 | `apps/meyo-studio-flow/langflow.db` |
| 内部 schema | `flow` |
| 内部表来源 | Langflow 自带刚需 |
| 是否生产事实源 | 否 |
| 生产事实源 | `meyo` |

## 2. Flow 对应的生产表

这些表归 `meyo` 拥有，flow 通过 Meyo API 使用。

| 表名 | 业务场景 | 归属服务 | 用途 |
|---|---|---|---|
| `meyo.flow_templates` | Flow 编排 | meyo | Flow 模板 |
| `meyo.flow_versions` | Flow 编排 | meyo | 可发布 Flow 版本 |
| `meyo.app_scene_flow_bindings` | Flow 编排 | meyo | App + Scene + Flow 绑定 |
| `meyo.scene_workflow_specs` | Flow 编排 | meyo | Scene Workflow 显式节点契约 |
| `meyo.scene_approvals` | 评测发布 | meyo | 发布审批 |
| `meyo.scene_activation_history` | 评测发布 | meyo | 激活、暂停、回滚历史 |
| `meyo.flow_runs` | 运行审计 | meyo | Flow 执行记录 |
| `meyo.run_steps` | 运行审计 | meyo | 运行节点明细 |
| `meyo.scene_node_events` | 运行审计 | meyo | Scene 内部节点事件 |

## 3. Flow 当前内部表总览

当前 Langflow 主数据库内部表 19 张。切 PostgreSQL 后由 Langflow migrations 创建。

| 表名 | 业务场景 | 来源 | 是否刚需 | 表注释 | 表说明 |
|---|---|---|---|---|---|
| `alembic_version` | 系统迁移 | Langflow 自带 | 是 | Alembic 迁移版本 | Langflow 升级数据库时要看当前 migration 版本，业务代码不直接使用。 |
| `apikey` | 系统身份 | Langflow 自带 | 是 | Langflow API Key | 用户或服务直接调用 Langflow API 时用，生产入口仍由 meyo 统一控制。 |
| `deployment` | 部署 | Langflow 自带 | 是 | Flow 部署记录 | 使用 Langflow 原生部署功能时用，Meyo 线上执行版本以 `meyo.flow_versions` 为准。 |
| `deployment_provider_account` | 部署 | Langflow 自带 | 是 | 部署平台账号 | Langflow 要部署到外部平台时，用它保存平台账号连接信息。 |
| `file` | Studio 资产 | Langflow 自带 | 是 | Studio 文件元数据 | 用户在 Studio 上传组件文件、数据文件或调试附件时，Langflow 原生页面会用它。 |
| `flow` | Flow 编排 | Langflow 自带 | 是 | Flow 草稿 / 工作流主体 | 用户在 Studio 画布里编辑草稿时用，发布到生产前还不是 Meyo 的线上 Flow 真相。 |
| `flow_version` | Flow 编排 | Langflow 自带 | 是 | Langflow 内部 Flow 版本 | Langflow 原生版本管理要用，Meyo 生产可执行版本另存到 meyo。 |
| `flow_version_deployment_attachment` | 部署 | Langflow 自带 | 是 | Flow 版本和部署记录关联 | Langflow 原生版本被部署时，用它把内部版本和部署记录连起来。 |
| `folder` | Studio 资产 | Langflow 自带 | 是 | Flow 文件夹 / 项目 | 用户在 Studio 里按项目或文件夹整理 Flow 时用。 |
| `job` | 后台任务 | Langflow 自带 | 是 | 后台任务 | Langflow 执行导入、构建、运行等后台任务时，用它展示任务状态。 |
| `message` | Playground 调试 | Langflow 自带 | 是 | Playground / 会话消息 | 用户在 Langflow Playground 里调试 Flow 的问答消息时用。 |
| `span` | 运行调试 | Langflow 自带 | 是 | Trace span 明细 | 调试某次 Flow 为什么慢或哪一步失败时，用它看节点级 trace 明细。 |
| `sso_config` | 系统身份 | Langflow 自带 | 是 | SSO 配置 | Langflow 自己接企业 SSO 登录时，用它保存 SSO 参数。 |
| `sso_user_profile` | 系统身份 | Langflow 自带 | 是 | SSO 用户档案 | SSO 登录成功后，用它把外部身份和 Langflow 用户关联起来。 |
| `trace` | 运行调试 | Langflow 自带 | 是 | Flow 执行 trace | Playground 或 API 运行一次 Flow 后，用它保存 Langflow 原生执行 trace。 |
| `transaction` | 运行调试 | Langflow 自带 | 是 | 节点 transaction 记录 | Langflow 节点运行时的输入输出明细用它保存，方便 Studio 排障。 |
| `user` | 系统身份 | Langflow 自带 | 是 | Langflow 用户 | Langflow 原生登录、权限和页面展示要用，生产统一用户在 `meyo.users`。 |
| `variable` | Flow 编排 | Langflow 自带 | 是 | Langflow 变量 | Flow 调试或运行时需要变量配置时，Langflow 原生功能会读取它。 |
| `vertex_build` | Flow 编排 | Langflow 自带 | 是 | 节点构建结果 | 用户在画布上构建或校验节点时，用它保存构建产物和错误信息。 |

## 4. 内部表字段

字段类型来自当前 SQLite 快照；切 PostgreSQL 后以 Langflow migrations 生成结果为准。

### `alembic_version`

表注释：Alembic 迁移版本。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `version_num` | VARCHAR(32) | 当前 Alembic revision |

### `apikey`

表注释：Langflow API Key。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | API Key ID |
| `name` | VARCHAR | 名称 |
| `api_key` | VARCHAR | API Key 值 |
| `api_key_hash` | VARCHAR | API Key hash |
| `user_id` | CHAR(32) | Langflow 用户 ID |
| `last_used_at` | DATETIME | 最近使用时间 |
| `total_uses` | INTEGER | 使用次数 |
| `is_active` | BOOLEAN | 是否启用 |
| `created_at` | DATETIME | 创建时间 |

### `deployment`

表注释：Langflow Flow 部署记录。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 部署 ID |
| `resource_key` | VARCHAR | 部署资源键 |
| `user_id` | CHAR(32) | 用户 ID |
| `project_id` | CHAR(32) | 项目 / folder ID |
| `deployment_provider_account_id` | CHAR(32) | 部署平台账号 ID |
| `name` | VARCHAR | 部署名称 |
| `description` | TEXT | 描述 |
| `deployment_type` | VARCHAR(5) | 部署类型 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `deployment_provider_account`

表注释：Langflow 部署平台账号。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 部署账号 ID |
| `user_id` | CHAR(32) | 用户 ID |
| `provider_tenant_id` | VARCHAR | 平台租户 ID |
| `name` | VARCHAR | 账号名称 |
| `provider_url` | VARCHAR | 平台 URL |
| `api_key` | VARCHAR | 平台 API Key |
| `provider_key` | VARCHAR(19) | 平台类型 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `file`

表注释：Langflow Studio 文件元数据。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 文件 ID |
| `user_id` | CHAR(32) | 用户 ID |
| `name` | VARCHAR | 文件名 |
| `path` | VARCHAR | 文件路径 |
| `size` | INTEGER | 文件大小 |
| `provider` | VARCHAR | 文件存储 provider |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `flow`

表注释：Langflow 内部 Flow 草稿 / 工作流主体。生产发布事实应写入 `meyo.flow_versions`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | Langflow Flow ID |
| `user_id` | CHAR(32) | 用户 ID |
| `folder_id` | CHAR(32) | 文件夹 ID |
| `name` | VARCHAR | Flow 名称 |
| `description` | TEXT | 描述 |
| `data` | JSON | Flow 画布数据 |
| `tags` | JSON | 标签 |
| `icon` | VARCHAR | 图标 |
| `icon_bg_color` | VARCHAR | 图标背景色 |
| `gradient` | VARCHAR | 渐变配置 |
| `is_component` | BOOLEAN | 是否组件 |
| `webhook` | BOOLEAN | 是否启用 webhook |
| `endpoint_name` | VARCHAR | endpoint 名称 |
| `mcp_enabled` | BOOLEAN | 是否启用 MCP |
| `action_name` | VARCHAR | Action 名称 |
| `action_description` | TEXT | Action 描述 |
| `access_type` | VARCHAR(7) | 访问类型 |
| `locked` | BOOLEAN | 是否锁定 |
| `fs_path` | VARCHAR | 文件系统路径 |
| `updated_at` | DATETIME | 更新时间 |

### `flow_version`

表注释：Langflow 内部 Flow 版本。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 版本 ID |
| `flow_id` | CHAR(32) | Flow ID |
| `user_id` | CHAR(32) | 用户 ID |
| `data` | JSON | 版本 Flow 数据 |
| `version_number` | INTEGER | 版本号 |
| `description` | VARCHAR(500) | 版本描述 |
| `created_at` | DATETIME | 创建时间 |

### `flow_version_deployment_attachment`

表注释：Langflow Flow 版本和部署记录关联。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 关联 ID |
| `user_id` | CHAR(32) | 用户 ID |
| `flow_version_id` | CHAR(32) | Flow 版本 ID |
| `deployment_id` | CHAR(32) | 部署 ID |
| `provider_snapshot_id` | VARCHAR | 平台快照 ID |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `folder`

表注释：Langflow Flow 文件夹 / 项目。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 文件夹 ID |
| `parent_id` | CHAR(32) | 父文件夹 ID |
| `user_id` | CHAR(32) | 用户 ID |
| `name` | VARCHAR | 文件夹名称 |
| `description` | TEXT | 描述 |
| `auth_settings` | JSON | 认证设置 |

### `job`

表注释：Langflow 后台任务。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `job_id` | CHAR(32) | Job ID |
| `flow_id` | CHAR(32) | Flow ID |
| `status` | VARCHAR(11) | 任务状态 |
| `type` | VARCHAR(10) | 任务类型 |
| `user_id` | CHAR(32) | 用户 ID |
| `asset_id` | CHAR(32) | 资产 ID |
| `asset_type` | VARCHAR | 资产类型 |
| `created_timestamp` | DATETIME | 创建时间 |
| `finished_timestamp` | DATETIME | 完成时间 |

### `message`

表注释：Langflow Playground / 会话消息。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 消息 ID |
| `flow_id` | CHAR(32) | Flow ID |
| `session_id` | VARCHAR | 会话 ID |
| `sender` | VARCHAR | 发送方 |
| `sender_name` | VARCHAR | 发送方名称 |
| `text` | TEXT | 文本 |
| `files` | JSON | 文件列表 |
| `error` | BOOLEAN | 是否错误 |
| `edit` | BOOLEAN | 是否编辑消息 |
| `properties` | JSON | 消息属性 |
| `category` | TEXT | 消息分类 |
| `content_blocks` | JSON | 内容块 |
| `context_id` | VARCHAR | 上下文 ID |
| `session_metadata` | JSON | 会话元数据 |
| `timestamp` | DATETIME | 时间戳 |

### `span`

表注释：Langflow trace span 明细。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | Span ID |
| `trace_id` | CHAR(32) | Trace ID |
| `parent_span_id` | CHAR(32) | 父 Span ID |
| `name` | VARCHAR | Span 名称 |
| `span_type` | VARCHAR(9) | Span 类型 |
| `span_kind` | VARCHAR(8) | Span kind |
| `status` | VARCHAR(5) | 状态 |
| `start_time` | DATETIME | 开始时间 |
| `end_time` | DATETIME | 结束时间 |
| `latency_ms` | INTEGER | 耗时毫秒 |
| `inputs` | JSON | 输入 |
| `outputs` | JSON | 输出 |
| `error` | TEXT | 错误 |
| `attributes` | JSON | 属性 |

### `sso_config`

表注释：Langflow SSO 配置。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | SSO 配置 ID |
| `provider` | VARCHAR | Provider |
| `provider_name` | VARCHAR | Provider 名称 |
| `enabled` | BOOLEAN | 是否启用 |
| `enforce_sso` | BOOLEAN | 是否强制 SSO |
| `client_id` | VARCHAR | Client ID |
| `client_secret_encrypted` | VARCHAR | 加密后的 Client Secret |
| `discovery_url` | VARCHAR | Discovery URL |
| `redirect_uri` | VARCHAR | Redirect URI |
| `scopes` | VARCHAR | Scopes |
| `email_claim` | VARCHAR | 邮箱 claim |
| `username_claim` | VARCHAR | 用户名 claim |
| `user_id_claim` | VARCHAR | 用户 ID claim |
| `token_endpoint` | VARCHAR | Token endpoint |
| `authorization_endpoint` | VARCHAR | Authorization endpoint |
| `jwks_uri` | VARCHAR | JWKS URI |
| `issuer` | VARCHAR | Issuer |
| `created_by` | CHAR(32) | 创建人 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `sso_user_profile`

表注释：Langflow SSO 用户档案。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | SSO 用户档案 ID |
| `user_id` | CHAR(32) | Langflow 用户 ID |
| `sso_provider` | VARCHAR | SSO provider |
| `sso_user_id` | VARCHAR | SSO 用户 ID |
| `email` | VARCHAR | 邮箱 |
| `sso_last_login_at` | DATETIME | 最近 SSO 登录时间 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `trace`

表注释：Langflow Flow 执行 trace。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | Trace ID |
| `flow_id` | CHAR(32) | Flow ID |
| `name` | VARCHAR | Trace 名称 |
| `status` | VARCHAR(5) | 状态 |
| `start_time` | DATETIME | 开始时间 |
| `end_time` | DATETIME | 结束时间 |
| `total_latency_ms` | INTEGER | 总耗时毫秒 |
| `total_tokens` | INTEGER | token 总数 |
| `session_id` | VARCHAR | 会话 ID |

### `transaction`

表注释：Langflow 节点 transaction 记录。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | Transaction ID |
| `flow_id` | CHAR(32) | Flow ID |
| `vertex_id` | VARCHAR | 节点 ID |
| `target_id` | VARCHAR | 目标节点 ID |
| `inputs` | JSON | 输入 |
| `outputs` | JSON | 输出 |
| `status` | VARCHAR | 状态 |
| `error` | VARCHAR | 错误 |
| `timestamp` | DATETIME | 时间戳 |

### `user`

表注释：Langflow 用户。生产用户真相应迁移到 `meyo.users`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | Langflow 用户 ID |
| `username` | VARCHAR | 用户名 |
| `password` | VARCHAR | 密码 hash |
| `profile_image` | VARCHAR | 头像 |
| `is_active` | BOOLEAN | 是否启用 |
| `is_superuser` | BOOLEAN | 是否超级用户 |
| `store_api_key` | VARCHAR | API Key 存储字段 |
| `optins` | JSON | 用户 opt-in 设置 |
| `create_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |
| `last_login_at` | DATETIME | 最近登录时间 |

### `variable`

表注释：Langflow 变量。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | CHAR(32) | 变量 ID |
| `user_id` | CHAR(32) | 用户 ID |
| `name` | VARCHAR | 变量名 |
| `value` | VARCHAR | 变量值 |
| `type` | VARCHAR | 变量类型 |
| `default_fields` | JSON | 默认字段 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `vertex_build`

表注释：Langflow 节点构建结果。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `build_id` | CHAR(32) | 构建 ID |
| `id` | VARCHAR | 节点 ID |
| `flow_id` | CHAR(32) | Flow ID |
| `job_id` | CHAR(32) | Job ID |
| `data` | JSON | 构建数据 |
| `artifacts` | JSON | 构建产物 |
| `params` | TEXT | 参数 |
| `valid` | BOOLEAN | 是否有效 |
| `timestamp` | DATETIME | 时间戳 |

## 5. 本地缓存库

当前本地还存在：

```text
apps/meyo-studio-flow/.langchain.db
```

| 表名 | 业务场景 | 来源 | 是否刚需 | 表注释 | 表说明 |
|---|---|---|---|---|---|
| `full_llm_cache` | 本地调试 | LangChain cache 自带 | 否 | LLM 缓存 | 本地调试重复调用 LLM 时用它缓存结果，加速开发，可删除重建，不作为生产事实。 |
| `full_md5_llm_cache` | 本地调试 | LangChain cache 自带 | 否 | LLM 缓存索引 | 本地调试查 LLM 缓存时用它按 MD5 找结果，可删除重建，不作为生产事实。 |
