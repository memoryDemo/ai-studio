---
title: Meyo Chatbot 数据库表字典
---

# Meyo Chatbot 数据库表字典

## 1. 服务归属

| 项 | 值 |
|---|---|
| 服务 | `chatbot` / `apps/meyo-chatbot` |
| 当前上游 | Open WebUI |
| 当前本地库 | `apps/meyo-chatbot/backend/open_webui/data/webui.db` |
| 内部 schema | `chatbot` |
| 内部表来源 | Open WebUI 自带刚需 |
| 是否生产事实源 | 否 |
| 生产事实源 | `meyo` |

## 2. Chatbot 对应的生产表

这些表归 `meyo` 拥有，chatbot 通过 Meyo API 使用。

| 表名 | 业务场景 | 归属服务 | 用途 |
|---|---|---|---|
| `meyo.users` | 系统 | meyo | 统一用户 |
| `meyo.user_identities` | 系统 | meyo | chatbot 用户和统一用户绑定 |
| `meyo.workspaces` | 系统 | meyo | 统一 workspace |
| `meyo.workspace_members` | 系统 | meyo | workspace 成员 |
| `meyo.files` | 文件 | meyo | 上传文件元数据 |
| `meyo.chat_threads` | 聊天 | meyo | 聊天会话 |
| `meyo.chat_messages` | 聊天 | meyo | 聊天消息 |
| `meyo.chat_message_attachments` | 聊天 | meyo | 聊天消息附件 |
| `meyo.knowledge_bases` | 知识库 | meyo | 统一知识库 |
| `meyo.knowledge_documents` | 知识库 | meyo | 知识文档 |
| `meyo.knowledge_chunks` | 知识库 | meyo | 知识切片 |
| `meyo.capability_registry` | 能力 | meyo | Skill / Tool / Prompt 统一能力 |

## 3. Chatbot 当前内部表总览

当前 Open WebUI 内部表 41 张。切 PostgreSQL 后由 Open WebUI migrations 创建。

| 表名 | 业务场景 | 来源 | 是否刚需 | 表注释 | 表说明 |
|---|---|---|---|---|---|
| `access_grant` | 系统权限 | Open WebUI 自带 | 是 | 资源授权关系 | Open WebUI 自己的资源共享和授权功能要用，过渡期保留它避免原生权限页面失效。 |
| `alembic_version` | 系统迁移 | Open WebUI 自带 | 是 | Alembic 迁移版本 | Open WebUI 升级数据库时要看当前 migration 版本，业务代码不直接使用。 |
| `api_key` | 系统身份 | Open WebUI 自带 | 是 | 用户 API Key | 用户在 Open WebUI 里创建 API Key 调接口时用，生产 API Key 后续可迁到 meyo。 |
| `auth` | 系统身份 | Open WebUI 自带 | 是 | 登录认证信息 | Open WebUI 本地账号密码和认证流程要用，接统一身份前不能删。 |
| `automation` | 自动化 | Open WebUI 自带 | 是 | 自动化任务定义 | 用户在 Open WebUI 配自动化任务时用，Meyo 不把它当生产 workflow 真相。 |
| `automation_run` | 自动化 | Open WebUI 自带 | 是 | 自动化执行记录 | Open WebUI 自动化任务每次执行后，用它给原生页面展示运行历史。 |
| `calendar` | 日历 | Open WebUI 自带 | 是 | 用户日历 | Open WebUI 日历页面保存用户日历源时用，不是 Meyo 主日程事实。 |
| `calendar_event` | 日历 | Open WebUI 自带 | 是 | 日历事件 | 用户在 Open WebUI 日历里创建或同步日程时用，Meyo 不依赖它做业务调度。 |
| `calendar_event_attendee` | 日历 | Open WebUI 自带 | 是 | 日历事件参与人 | Open WebUI 日历展示邀请人和参与状态时用。 |
| `channel` | 频道协作 | Open WebUI 自带 | 是 | 频道 | Open WebUI 团队频道功能用它表示一个群聊或协作空间。 |
| `channel_file` | 频道协作 | Open WebUI 自带 | 是 | 频道文件关联 | 用户在频道里共享文件时，用它把频道和文件连起来。 |
| `channel_member` | 频道协作 | Open WebUI 自带 | 是 | 频道成员 | Open WebUI 判断哪些用户在某个频道里，以及他们的角色和状态时用。 |
| `channel_webhook` | 频道协作 | Open WebUI 自带 | 是 | 频道 Webhook | 外部系统往 Open WebUI 频道推消息时，用它保存 webhook 配置。 |
| `chat` | 聊天 | Open WebUI 自带 | 是 | Open WebUI 聊天会话 | Open WebUI 原生聊天列表和历史页要用，生产会话真相在 `meyo.chat_threads`。 |
| `chat_file` | 聊天 | Open WebUI 自带 | 是 | 聊天文件关联 | Open WebUI 原生聊天带文件时用，生产附件关系在 `meyo.chat_message_attachments`。 |
| `chat_message` | 聊天 | Open WebUI 自带 | 是 | Open WebUI 聊天消息 | Open WebUI 原生消息列表要用，生产消息真相在 `meyo.chat_messages`。 |
| `chatidtag` | 聊天 | Open WebUI 自带 | 是 | 旧版聊天标签关系 | 旧版聊天标签迁移或查询时用，保留是为了兼容历史数据。 |
| `config` | 系统配置 | Open WebUI 自带 | 是 | Open WebUI 持久配置 | Open WebUI 页面设置、功能开关、默认参数要落库时用。 |
| `document` | 知识库 | Open WebUI 自带 | 是 | 旧版文档 collection 元数据 | Open WebUI 旧版文档 collection 还在运行或迁移时用，生产知识文档在 meyo。 |
| `feedback` | 反馈 | Open WebUI 自带 | 是 | 用户反馈 | 用户在 Open WebUI 原生界面点反馈时用，生产反馈在 `meyo.feedback_events`。 |
| `file` | 文件 | Open WebUI 自带 | 是 | Open WebUI 文件元数据 | Open WebUI 文件上传和原生页面引用时用，生产文件元数据在 meyo。 |
| `folder` | 聊天 | Open WebUI 自带 | 是 | 聊天文件夹 | 用户把聊天整理到文件夹时用，只影响 Open WebUI 原生会话管理。 |
| `function` | 能力模型 | Open WebUI 自带 | 是 | Function 配置 | Open WebUI 原生 function 配置用，生产 Skill、Tool、Prompt 统一进 meyo 能力表。 |
| `group` | 系统权限 | Open WebUI 自带 | 是 | 用户组 | Open WebUI 原生用户组权限用，Meyo 统一权限以 workspace 和 meyo 为准。 |
| `group_member` | 系统权限 | Open WebUI 自带 | 是 | 用户组成员 | Open WebUI 原生用户组判断成员关系时用。 |
| `knowledge` | 知识库 | Open WebUI 自带 | 是 | Open WebUI 知识库元数据 | Open WebUI 原生知识库页面要用，生产知识库真相在 meyo。 |
| `knowledge_file` | 知识库 | Open WebUI 自带 | 是 | 知识库文件关联 | Open WebUI 原生知识库挂文件时用，生产文档归属在 meyo。 |
| `memory` | 记忆 | Open WebUI 自带 | 是 | 用户记忆 | Open WebUI 个人记忆功能用，是否进入生产长期记忆要由 meyo 另行设计。 |
| `message` | 频道协作 | Open WebUI 自带 | 是 | 频道消息 | Open WebUI 频道聊天消息用，不是 chatbot 一对一 RAG 会话真相。 |
| `message_reaction` | 频道协作 | Open WebUI 自带 | 是 | 频道消息反应 | Open WebUI 频道消息点赞等 reaction 展示用。 |
| `migratehistory` | 系统迁移 | Open WebUI 自带 | 是 | Peewee 迁移历史 | Open WebUI 老迁移系统判断哪些 migration 跑过，业务代码不直接使用。 |
| `model` | 能力模型 | Open WebUI 自带 | 是 | 模型配置 | Open WebUI 原生模型配置页用，生产模型配置在 `meyo.model_profiles`。 |
| `note` | 笔记 | Open WebUI 自带 | 是 | 用户笔记 | 用户在 Open WebUI 写笔记时用，不作为 RAG 知识源，除非显式同步到 meyo。 |
| `oauth_session` | 系统身份 | Open WebUI 自带 | 是 | OAuth Session | OAuth 登录流程中保存临时 session，用于完成第三方登录。 |
| `prompt` | 能力模型 | Open WebUI 自带 | 是 | Prompt 主表 | Open WebUI 原生 Prompt 管理用，生产 Prompt 能力在 meyo 能力表。 |
| `prompt_history` | 能力模型 | Open WebUI 自带 | 是 | Prompt 历史版本 | Open WebUI Prompt 修改历史展示和回滚用。 |
| `shared_chat` | 聊天 | Open WebUI 自带 | 是 | 分享聊天 | 用户把某段聊天分享出去时，用它保存分享快照。 |
| `skill` | 能力模型 | Open WebUI 自带 | 是 | Skill 配置 | Open WebUI 原生 Skill 管理用，生产 Skill 在 meyo 能力表。 |
| `tag` | 内容管理 | Open WebUI 自带 | 是 | 标签 | 用户给聊天、文档或内容打标签时，Open WebUI 原生页面用它展示筛选。 |
| `tool` | 能力模型 | Open WebUI 自带 | 是 | Tool 配置 | Open WebUI 原生 Tool 管理用，生产 Tool 在 meyo 能力表。 |
| `user` | 系统身份 | Open WebUI 自带 | 是 | Open WebUI 用户 | Open WebUI 原生登录和页面用户对象用，生产统一用户在 `meyo.users`。 |

## 4. 内部表字段

字段类型来自当前 SQLite 快照；切 PostgreSQL 后以 Open WebUI migrations 生成结果为准。

### `access_grant`

表注释：Open WebUI 资源授权关系。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 授权记录 ID |
| `resource_type` | TEXT | 资源类型 |
| `resource_id` | TEXT | 资源 ID |
| `principal_type` | TEXT | 主体类型 |
| `principal_id` | TEXT | 主体 ID |
| `permission` | TEXT | 权限 |
| `created_at` | BIGINT | 创建时间 |

### `alembic_version`

表注释：Alembic 迁移版本。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `version_num` | VARCHAR(32) | 当前 Alembic revision |

### `api_key`

表注释：Open WebUI 用户 API Key。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | API Key ID |
| `user_id` | TEXT | Open WebUI 用户 ID |
| `key` | TEXT | API Key 明文或密钥值 |
| `data` | JSON | 扩展数据 |
| `expires_at` | BIGINT | 过期时间 |
| `last_used_at` | BIGINT | 最近使用时间 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `auth`

表注释：Open WebUI 登录认证信息。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | VARCHAR(255) | 用户 ID |
| `email` | VARCHAR(255) | 登录邮箱 |
| `password` | TEXT | 密码 hash |
| `active` | INTEGER | 是否启用 |

### `automation`

表注释：Open WebUI 自动化任务定义。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 自动化 ID |
| `user_id` | TEXT | 用户 ID |
| `name` | TEXT | 自动化名称 |
| `data` | JSON | 自动化配置 |
| `meta` | JSON | 元数据 |
| `is_active` | BOOLEAN | 是否启用 |
| `last_run_at` | BIGINT | 最近运行时间 |
| `next_run_at` | BIGINT | 下次运行时间 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `automation_run`

表注释：Open WebUI 自动化执行记录。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 执行 ID |
| `automation_id` | TEXT | 自动化 ID |
| `chat_id` | TEXT | 关联聊天 ID |
| `status` | TEXT | 执行状态 |
| `error` | TEXT | 错误信息 |
| `created_at` | BIGINT | 创建时间 |

### `calendar`

表注释：Open WebUI 用户日历。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 日历 ID |
| `user_id` | TEXT | 用户 ID |
| `name` | TEXT | 日历名称 |
| `color` | TEXT | 颜色 |
| `is_default` | BOOLEAN | 是否默认日历 |
| `data` | JSON | 日历数据 |
| `meta` | JSON | 元数据 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `calendar_event`

表注释：Open WebUI 日历事件。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 事件 ID |
| `calendar_id` | TEXT | 日历 ID |
| `user_id` | TEXT | 用户 ID |
| `title` | TEXT | 标题 |
| `description` | TEXT | 描述 |
| `start_at` | BIGINT | 开始时间 |
| `end_at` | BIGINT | 结束时间 |
| `all_day` | BOOLEAN | 是否全天 |
| `rrule` | TEXT | 重复规则 |
| `color` | TEXT | 颜色 |
| `location` | TEXT | 地点 |
| `data` | JSON | 事件数据 |
| `meta` | JSON | 元数据 |
| `is_cancelled` | BOOLEAN | 是否取消 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `calendar_event_attendee`

表注释：Open WebUI 日历事件参与人。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 参与记录 ID |
| `event_id` | TEXT | 事件 ID |
| `user_id` | TEXT | 用户 ID |
| `status` | TEXT | 参与状态 |
| `meta` | JSON | 元数据 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `channel`

表注释：Open WebUI 频道。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 频道 ID |
| `user_id` | TEXT | 创建用户 ID |
| `name` | TEXT | 频道名称 |
| `description` | TEXT | 描述 |
| `data` | JSON | 频道数据 |
| `meta` | JSON | 元数据 |
| `type` | TEXT | 频道类型 |
| `is_private` | BOOLEAN | 是否私有 |
| `archived_at` | BIGINT | 归档时间 |
| `archived_by` | TEXT | 归档人 |
| `deleted_at` | BIGINT | 删除时间 |
| `deleted_by` | TEXT | 删除人 |
| `updated_by` | TEXT | 更新人 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `channel_file`

表注释：Open WebUI 频道和文件关联。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 关联 ID |
| `user_id` | TEXT | 用户 ID |
| `channel_id` | TEXT | 频道 ID |
| `file_id` | TEXT | 文件 ID |
| `message_id` | TEXT | 消息 ID |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `channel_member`

表注释：Open WebUI 频道成员。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 成员记录 ID |
| `channel_id` | TEXT | 频道 ID |
| `user_id` | TEXT | 用户 ID |
| `status` | TEXT | 成员状态 |
| `is_active` | BOOLEAN | 是否有效 |
| `is_channel_muted` | BOOLEAN | 是否静音 |
| `is_channel_pinned` | BOOLEAN | 是否置顶 |
| `data` | JSON | 成员数据 |
| `meta` | JSON | 元数据 |
| `joined_at` | BIGINT | 加入时间 |
| `left_at` | BIGINT | 离开时间 |
| `last_read_at` | BIGINT | 最近已读时间 |
| `role` | TEXT | 频道角色 |
| `invited_by` | TEXT | 邀请人 |
| `invited_at` | BIGINT | 邀请时间 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `channel_webhook`

表注释：Open WebUI 频道 Webhook。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | Webhook ID |
| `user_id` | TEXT | 用户 ID |
| `channel_id` | TEXT | 频道 ID |
| `name` | TEXT | Webhook 名称 |
| `profile_image_url` | TEXT | 头像 URL |
| `token` | TEXT | Webhook token |
| `last_used_at` | BIGINT | 最近使用时间 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `chat`

表注释：Open WebUI 聊天会话。生产聊天真相应迁移到 `meyo.chat_threads`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | VARCHAR(255) | 聊天 ID |
| `user_id` | VARCHAR(255) | 用户 ID |
| `title` | TEXT | 标题 |
| `share_id` | VARCHAR(255) | 分享 ID |
| `archived` | INTEGER | 是否归档 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |
| `chat` | JSON | 聊天内容快照 |
| `pinned` | BOOLEAN | 是否置顶 |
| `meta` | JSON | 元数据 |
| `folder_id` | TEXT | 文件夹 ID |
| `tasks` | JSON | 任务数据 |
| `summary` | TEXT | 摘要 |
| `last_read_at` | BIGINT | 最近已读时间 |

### `chat_file`

表注释：Open WebUI 聊天和文件关联。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 关联 ID |
| `user_id` | TEXT | 用户 ID |
| `chat_id` | TEXT | 聊天 ID |
| `file_id` | TEXT | 文件 ID |
| `message_id` | TEXT | 消息 ID |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `chat_message`

表注释：Open WebUI 聊天消息。生产消息真相应迁移到 `meyo.chat_messages`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 消息 ID |
| `chat_id` | TEXT | 聊天 ID |
| `user_id` | TEXT | 用户 ID |
| `role` | TEXT | 消息角色 |
| `parent_id` | TEXT | 父消息 ID |
| `content` | JSON | 消息内容 |
| `output` | JSON | 输出内容 |
| `model_id` | TEXT | 模型 ID |
| `files` | JSON | 文件列表 |
| `sources` | JSON | 来源列表 |
| `embeds` | JSON | 嵌入内容 |
| `done` | BOOLEAN | 是否完成 |
| `status_history` | JSON | 状态历史 |
| `error` | JSON | 错误信息 |
| `usage` | JSON | token / 调用用量 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `chatidtag`

表注释：Open WebUI 旧版聊天标签关联。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | VARCHAR(255) | 关联 ID |
| `tag_name` | VARCHAR(255) | 标签名 |
| `chat_id` | VARCHAR(255) | 聊天 ID |
| `user_id` | VARCHAR(255) | 用户 ID |
| `timestamp` | INTEGER | 时间戳 |

### `config`

表注释：Open WebUI 持久配置。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | INTEGER | 配置 ID |
| `data` | JSON | 配置内容 |
| `version` | INTEGER | 配置版本 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

### `document`

表注释：Open WebUI 旧版文档 collection 元数据。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | INTEGER | 文档记录 ID |
| `collection_name` | VARCHAR(255) | collection 名称 |
| `name` | VARCHAR(255) | 文档名称 |
| `title` | TEXT | 标题 |
| `filename` | TEXT | 文件名 |
| `content` | TEXT | 文档内容 |
| `user_id` | VARCHAR(255) | 用户 ID |
| `timestamp` | INTEGER | 时间戳 |

### `feedback`

表注释：Open WebUI 用户反馈。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 反馈 ID |
| `user_id` | TEXT | 用户 ID |
| `version` | BIGINT | 反馈版本 |
| `type` | TEXT | 反馈类型 |
| `data` | JSON | 反馈数据 |
| `meta` | JSON | 元数据 |
| `snapshot` | JSON | 快照 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `file`

表注释：Open WebUI 文件元数据。生产文件真相应迁移到 `meyo.files`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 文件 ID |
| `user_id` | TEXT | 用户 ID |
| `filename` | TEXT | 文件名 |
| `meta` | JSON | 元数据 |
| `created_at` | INTEGER | 创建时间 |
| `hash` | TEXT | 文件 hash |
| `data` | JSON | 文件数据 |
| `updated_at` | BIGINT | 更新时间 |
| `path` | TEXT | 本地路径 |

### `folder`

表注释：Open WebUI 聊天文件夹。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 文件夹 ID |
| `parent_id` | TEXT | 父文件夹 ID |
| `user_id` | TEXT | 用户 ID |
| `name` | TEXT | 文件夹名称 |
| `items` | JSON | 子项 |
| `meta` | JSON | 元数据 |
| `is_expanded` | BOOLEAN | 是否展开 |
| `data` | JSON | 扩展数据 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `function`

表注释：Open WebUI function 配置。生产能力真相应迁移到 `meyo.capability_registry`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | Function ID |
| `user_id` | TEXT | 用户 ID |
| `name` | TEXT | 名称 |
| `type` | TEXT | 类型 |
| `content` | TEXT | 内容 |
| `meta` | TEXT | 元数据 |
| `valves` | TEXT | 参数 |
| `is_active` | INTEGER | 是否启用 |
| `is_global` | INTEGER | 是否全局 |
| `created_at` | INTEGER | 创建时间 |
| `updated_at` | INTEGER | 更新时间 |

### `group`

表注释：Open WebUI 用户组。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 用户组 ID |
| `user_id` | TEXT | 创建用户 ID |
| `name` | TEXT | 用户组名称 |
| `description` | TEXT | 描述 |
| `data` | JSON | 数据 |
| `meta` | JSON | 元数据 |
| `permissions` | JSON | 权限 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `group_member`

表注释：Open WebUI 用户组成员。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 成员关系 ID |
| `group_id` | TEXT | 用户组 ID |
| `user_id` | TEXT | 用户 ID |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `knowledge`

表注释：Open WebUI 知识库元数据。生产知识真相应迁移到 `meyo.knowledge_bases`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 知识库 ID |
| `user_id` | TEXT | 用户 ID |
| `name` | TEXT | 名称 |
| `description` | TEXT | 描述 |
| `meta` | JSON | 元数据 |
| `data` | JSON | 知识库数据 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `knowledge_file`

表注释：Open WebUI 知识库和文件关联。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 关联 ID |
| `user_id` | TEXT | 用户 ID |
| `knowledge_id` | TEXT | 知识库 ID |
| `file_id` | TEXT | 文件 ID |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `memory`

表注释：Open WebUI 用户记忆。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | VARCHAR(255) | 记忆 ID |
| `user_id` | VARCHAR(255) | 用户 ID |
| `content` | TEXT | 记忆内容 |
| `updated_at` | INTEGER | 更新时间 |
| `created_at` | INTEGER | 创建时间 |

### `message`

表注释：Open WebUI 频道消息。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 消息 ID |
| `user_id` | TEXT | 用户 ID |
| `channel_id` | TEXT | 频道 ID |
| `content` | TEXT | 消息内容 |
| `data` | JSON | 消息数据 |
| `meta` | JSON | 元数据 |
| `parent_id` | TEXT | 父消息 ID |
| `reply_to_id` | TEXT | 回复消息 ID |
| `is_pinned` | BOOLEAN | 是否置顶 |
| `pinned_at` | BIGINT | 置顶时间 |
| `pinned_by` | TEXT | 置顶人 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `message_reaction`

表注释：Open WebUI 频道消息反应。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 反应 ID |
| `user_id` | TEXT | 用户 ID |
| `message_id` | TEXT | 消息 ID |
| `name` | TEXT | 反应名称 |
| `created_at` | BIGINT | 创建时间 |

### `migratehistory`

表注释：Peewee 迁移历史。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | INTEGER | 迁移历史 ID |
| `name` | VARCHAR(255) | 迁移名称 |
| `migrated_at` | DATETIME | 迁移时间 |

### `model`

表注释：Open WebUI 模型配置。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 模型 ID |
| `user_id` | TEXT | 用户 ID |
| `base_model_id` | TEXT | 基础模型 ID |
| `name` | TEXT | 模型名称 |
| `meta` | TEXT | 元数据 |
| `params` | TEXT | 参数 |
| `is_active` | BOOLEAN | 是否启用 |
| `created_at` | INTEGER | 创建时间 |
| `updated_at` | INTEGER | 更新时间 |

### `note`

表注释：Open WebUI 用户笔记。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 笔记 ID |
| `user_id` | TEXT | 用户 ID |
| `title` | TEXT | 标题 |
| `data` | JSON | 笔记数据 |
| `meta` | JSON | 元数据 |
| `is_pinned` | BOOLEAN | 是否置顶 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `oauth_session`

表注释：Open WebUI OAuth Session。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | Session ID |
| `user_id` | TEXT | 用户 ID |
| `provider` | TEXT | OAuth provider |
| `token` | TEXT | OAuth token |
| `expires_at` | BIGINT | 过期时间 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `prompt`

表注释：Open WebUI Prompt 主表。生产能力真相应迁移到 `meyo.capability_registry`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | Prompt ID |
| `command` | VARCHAR | Prompt 命令 |
| `user_id` | VARCHAR | 用户 ID |
| `name` | TEXT | 名称 |
| `content` | TEXT | 内容 |
| `data` | JSON | 数据 |
| `meta` | JSON | 元数据 |
| `is_active` | BOOLEAN | 是否启用 |
| `version_id` | TEXT | 当前版本 ID |
| `tags` | JSON | 标签 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `prompt_history`

表注释：Open WebUI Prompt 历史版本。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 历史版本 ID |
| `prompt_id` | TEXT | Prompt ID |
| `parent_id` | TEXT | 父版本 ID |
| `snapshot` | JSON | 版本快照 |
| `user_id` | TEXT | 用户 ID |
| `commit_message` | TEXT | 提交说明 |
| `created_at` | BIGINT | 创建时间 |

### `shared_chat`

表注释：Open WebUI 分享聊天快照。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | 分享 ID |
| `chat_id` | TEXT | 聊天 ID |
| `user_id` | TEXT | 用户 ID |
| `title` | TEXT | 标题 |
| `chat` | JSON | 聊天快照 |
| `created_at` | BIGINT | 创建时间 |
| `updated_at` | BIGINT | 更新时间 |

### `skill`

表注释：Open WebUI Skill 配置。生产能力真相应迁移到 `meyo.capability_registry`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | VARCHAR | Skill ID |
| `user_id` | VARCHAR | 用户 ID |
| `name` | TEXT | Skill 名称 |
| `description` | TEXT | 描述 |
| `content` | TEXT | 内容 |
| `meta` | JSON | 元数据 |
| `is_active` | BOOLEAN | 是否启用 |
| `updated_at` | BIGINT | 更新时间 |
| `created_at` | BIGINT | 创建时间 |

### `tag`

表注释：Open WebUI 标签。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | VARCHAR(255) | 标签 ID |
| `name` | VARCHAR(255) | 标签名 |
| `user_id` | VARCHAR(255) | 用户 ID |
| `meta` | JSON | 元数据 |

### `tool`

表注释：Open WebUI Tool 配置。生产能力真相应迁移到 `meyo.capability_registry`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | TEXT | Tool ID |
| `user_id` | TEXT | 用户 ID |
| `name` | TEXT | Tool 名称 |
| `content` | TEXT | 内容 |
| `specs` | TEXT | 工具规格 |
| `meta` | TEXT | 元数据 |
| `valves` | TEXT | 参数 |
| `created_at` | INTEGER | 创建时间 |
| `updated_at` | INTEGER | 更新时间 |

### `user`

表注释：Open WebUI 用户表。生产用户真相应迁移到 `meyo.users`。

| 字段 | 类型 | 字段注释 |
|---|---|---|
| `id` | VARCHAR(255) | Open WebUI 用户 ID |
| `name` | VARCHAR(255) | 姓名 |
| `email` | VARCHAR(255) | 邮箱 |
| `role` | VARCHAR(255) | 角色 |
| `profile_image_url` | TEXT | 头像 URL |
| `created_at` | INTEGER | 创建时间 |
| `updated_at` | INTEGER | 更新时间 |
| `last_active_at` | INTEGER | 最近活跃时间 |
| `username` | VARCHAR(50) | 用户名 |
| `bio` | TEXT | 简介 |
| `gender` | TEXT | 性别 |
| `date_of_birth` | DATE | 出生日期 |
| `profile_banner_image_url` | TEXT | 主页横幅 |
| `timezone` | VARCHAR | 时区 |
| `presence_state` | VARCHAR | 在线状态 |
| `status_emoji` | VARCHAR | 状态 emoji |
| `status_message` | TEXT | 状态文案 |
| `status_expires_at` | BIGINT | 状态过期时间 |
| `oauth` | JSON | OAuth 数据 |
| `info` | JSON | 用户信息 |
| `settings` | JSON | 用户设置 |
| `scim` | JSON | SCIM 数据 |
