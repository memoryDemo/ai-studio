-- Chatbot PostgreSQL initialization script
-- Schema: chatbot
-- Source: apps/docs-site/docs/design/database/02_meyo_chatbot.md
-- This script creates upstream application tables and comments for compatibility.

BEGIN;

CREATE SCHEMA IF NOT EXISTS "chatbot";

CREATE TABLE IF NOT EXISTS "chatbot"."access_grant" (
    "id" text NOT NULL,
    "resource_type" text,
    "resource_id" text,
    "principal_type" text,
    "principal_id" text,
    "permission" text,
    "created_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."access_grant" IS 'Open WebUI 资源授权关系。';
COMMENT ON COLUMN "chatbot"."access_grant"."id" IS '授权记录 ID';
COMMENT ON COLUMN "chatbot"."access_grant"."resource_type" IS '资源类型';
COMMENT ON COLUMN "chatbot"."access_grant"."resource_id" IS '资源 ID';
COMMENT ON COLUMN "chatbot"."access_grant"."principal_type" IS '主体类型';
COMMENT ON COLUMN "chatbot"."access_grant"."principal_id" IS '主体 ID';
COMMENT ON COLUMN "chatbot"."access_grant"."permission" IS '权限';
COMMENT ON COLUMN "chatbot"."access_grant"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "chatbot"."alembic_version" (
    "version_num" varchar(32) NOT NULL,
    PRIMARY KEY ("version_num")
);
COMMENT ON TABLE "chatbot"."alembic_version" IS 'Alembic 迁移版本。';
COMMENT ON COLUMN "chatbot"."alembic_version"."version_num" IS '当前 Alembic revision';

CREATE TABLE IF NOT EXISTS "chatbot"."api_key" (
    "id" text NOT NULL,
    "user_id" text,
    "key" text,
    "data" jsonb,
    "expires_at" bigint,
    "last_used_at" bigint,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."api_key" IS 'Open WebUI 用户 API Key。';
COMMENT ON COLUMN "chatbot"."api_key"."id" IS 'API Key ID';
COMMENT ON COLUMN "chatbot"."api_key"."user_id" IS 'Open WebUI 用户 ID';
COMMENT ON COLUMN "chatbot"."api_key"."key" IS 'API Key 明文或密钥值';
COMMENT ON COLUMN "chatbot"."api_key"."data" IS '扩展数据';
COMMENT ON COLUMN "chatbot"."api_key"."expires_at" IS '过期时间';
COMMENT ON COLUMN "chatbot"."api_key"."last_used_at" IS '最近使用时间';
COMMENT ON COLUMN "chatbot"."api_key"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."api_key"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."auth" (
    "id" varchar(255) NOT NULL,
    "email" varchar(255),
    "password" text,
    "active" integer,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."auth" IS 'Open WebUI 登录认证信息。';
COMMENT ON COLUMN "chatbot"."auth"."id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."auth"."email" IS '登录邮箱';
COMMENT ON COLUMN "chatbot"."auth"."password" IS '密码 hash';
COMMENT ON COLUMN "chatbot"."auth"."active" IS '是否启用';

CREATE TABLE IF NOT EXISTS "chatbot"."automation" (
    "id" text NOT NULL,
    "user_id" text,
    "name" text,
    "data" jsonb,
    "meta" jsonb,
    "is_active" boolean,
    "last_run_at" bigint,
    "next_run_at" bigint,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."automation" IS 'Open WebUI 自动化任务定义。';
COMMENT ON COLUMN "chatbot"."automation"."id" IS '自动化 ID';
COMMENT ON COLUMN "chatbot"."automation"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."automation"."name" IS '自动化名称';
COMMENT ON COLUMN "chatbot"."automation"."data" IS '自动化配置';
COMMENT ON COLUMN "chatbot"."automation"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."automation"."is_active" IS '是否启用';
COMMENT ON COLUMN "chatbot"."automation"."last_run_at" IS '最近运行时间';
COMMENT ON COLUMN "chatbot"."automation"."next_run_at" IS '下次运行时间';
COMMENT ON COLUMN "chatbot"."automation"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."automation"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."automation_run" (
    "id" text NOT NULL,
    "automation_id" text,
    "chat_id" text,
    "status" text,
    "error" text,
    "created_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."automation_run" IS 'Open WebUI 自动化执行记录。';
COMMENT ON COLUMN "chatbot"."automation_run"."id" IS '执行 ID';
COMMENT ON COLUMN "chatbot"."automation_run"."automation_id" IS '自动化 ID';
COMMENT ON COLUMN "chatbot"."automation_run"."chat_id" IS '关联聊天 ID';
COMMENT ON COLUMN "chatbot"."automation_run"."status" IS '执行状态';
COMMENT ON COLUMN "chatbot"."automation_run"."error" IS '错误信息';
COMMENT ON COLUMN "chatbot"."automation_run"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "chatbot"."calendar" (
    "id" text NOT NULL,
    "user_id" text,
    "name" text,
    "color" text,
    "is_default" boolean,
    "data" jsonb,
    "meta" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."calendar" IS 'Open WebUI 用户日历。';
COMMENT ON COLUMN "chatbot"."calendar"."id" IS '日历 ID';
COMMENT ON COLUMN "chatbot"."calendar"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."calendar"."name" IS '日历名称';
COMMENT ON COLUMN "chatbot"."calendar"."color" IS '颜色';
COMMENT ON COLUMN "chatbot"."calendar"."is_default" IS '是否默认日历';
COMMENT ON COLUMN "chatbot"."calendar"."data" IS '日历数据';
COMMENT ON COLUMN "chatbot"."calendar"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."calendar"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."calendar"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."calendar_event" (
    "id" text NOT NULL,
    "calendar_id" text,
    "user_id" text,
    "title" text,
    "description" text,
    "start_at" bigint,
    "end_at" bigint,
    "all_day" boolean,
    "rrule" text,
    "color" text,
    "location" text,
    "data" jsonb,
    "meta" jsonb,
    "is_cancelled" boolean,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."calendar_event" IS 'Open WebUI 日历事件。';
COMMENT ON COLUMN "chatbot"."calendar_event"."id" IS '事件 ID';
COMMENT ON COLUMN "chatbot"."calendar_event"."calendar_id" IS '日历 ID';
COMMENT ON COLUMN "chatbot"."calendar_event"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."calendar_event"."title" IS '标题';
COMMENT ON COLUMN "chatbot"."calendar_event"."description" IS '描述';
COMMENT ON COLUMN "chatbot"."calendar_event"."start_at" IS '开始时间';
COMMENT ON COLUMN "chatbot"."calendar_event"."end_at" IS '结束时间';
COMMENT ON COLUMN "chatbot"."calendar_event"."all_day" IS '是否全天';
COMMENT ON COLUMN "chatbot"."calendar_event"."rrule" IS '重复规则';
COMMENT ON COLUMN "chatbot"."calendar_event"."color" IS '颜色';
COMMENT ON COLUMN "chatbot"."calendar_event"."location" IS '地点';
COMMENT ON COLUMN "chatbot"."calendar_event"."data" IS '事件数据';
COMMENT ON COLUMN "chatbot"."calendar_event"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."calendar_event"."is_cancelled" IS '是否取消';
COMMENT ON COLUMN "chatbot"."calendar_event"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."calendar_event"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."calendar_event_attendee" (
    "id" text NOT NULL,
    "event_id" text,
    "user_id" text,
    "status" text,
    "meta" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."calendar_event_attendee" IS 'Open WebUI 日历事件参与人。';
COMMENT ON COLUMN "chatbot"."calendar_event_attendee"."id" IS '参与记录 ID';
COMMENT ON COLUMN "chatbot"."calendar_event_attendee"."event_id" IS '事件 ID';
COMMENT ON COLUMN "chatbot"."calendar_event_attendee"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."calendar_event_attendee"."status" IS '参与状态';
COMMENT ON COLUMN "chatbot"."calendar_event_attendee"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."calendar_event_attendee"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."calendar_event_attendee"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."channel" (
    "id" text NOT NULL,
    "user_id" text,
    "name" text,
    "description" text,
    "data" jsonb,
    "meta" jsonb,
    "type" text,
    "is_private" boolean,
    "archived_at" bigint,
    "archived_by" text,
    "deleted_at" bigint,
    "deleted_by" text,
    "updated_by" text,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."channel" IS 'Open WebUI 频道。';
COMMENT ON COLUMN "chatbot"."channel"."id" IS '频道 ID';
COMMENT ON COLUMN "chatbot"."channel"."user_id" IS '创建用户 ID';
COMMENT ON COLUMN "chatbot"."channel"."name" IS '频道名称';
COMMENT ON COLUMN "chatbot"."channel"."description" IS '描述';
COMMENT ON COLUMN "chatbot"."channel"."data" IS '频道数据';
COMMENT ON COLUMN "chatbot"."channel"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."channel"."type" IS '频道类型';
COMMENT ON COLUMN "chatbot"."channel"."is_private" IS '是否私有';
COMMENT ON COLUMN "chatbot"."channel"."archived_at" IS '归档时间';
COMMENT ON COLUMN "chatbot"."channel"."archived_by" IS '归档人';
COMMENT ON COLUMN "chatbot"."channel"."deleted_at" IS '删除时间';
COMMENT ON COLUMN "chatbot"."channel"."deleted_by" IS '删除人';
COMMENT ON COLUMN "chatbot"."channel"."updated_by" IS '更新人';
COMMENT ON COLUMN "chatbot"."channel"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."channel"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."channel_file" (
    "id" text NOT NULL,
    "user_id" text,
    "channel_id" text,
    "file_id" text,
    "message_id" text,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."channel_file" IS 'Open WebUI 频道和文件关联。';
COMMENT ON COLUMN "chatbot"."channel_file"."id" IS '关联 ID';
COMMENT ON COLUMN "chatbot"."channel_file"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."channel_file"."channel_id" IS '频道 ID';
COMMENT ON COLUMN "chatbot"."channel_file"."file_id" IS '文件 ID';
COMMENT ON COLUMN "chatbot"."channel_file"."message_id" IS '消息 ID';
COMMENT ON COLUMN "chatbot"."channel_file"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."channel_file"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."channel_member" (
    "id" text NOT NULL,
    "channel_id" text,
    "user_id" text,
    "status" text,
    "is_active" boolean,
    "is_channel_muted" boolean,
    "is_channel_pinned" boolean,
    "data" jsonb,
    "meta" jsonb,
    "joined_at" bigint,
    "left_at" bigint,
    "last_read_at" bigint,
    "role" text,
    "invited_by" text,
    "invited_at" bigint,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."channel_member" IS 'Open WebUI 频道成员。';
COMMENT ON COLUMN "chatbot"."channel_member"."id" IS '成员记录 ID';
COMMENT ON COLUMN "chatbot"."channel_member"."channel_id" IS '频道 ID';
COMMENT ON COLUMN "chatbot"."channel_member"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."channel_member"."status" IS '成员状态';
COMMENT ON COLUMN "chatbot"."channel_member"."is_active" IS '是否有效';
COMMENT ON COLUMN "chatbot"."channel_member"."is_channel_muted" IS '是否静音';
COMMENT ON COLUMN "chatbot"."channel_member"."is_channel_pinned" IS '是否置顶';
COMMENT ON COLUMN "chatbot"."channel_member"."data" IS '成员数据';
COMMENT ON COLUMN "chatbot"."channel_member"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."channel_member"."joined_at" IS '加入时间';
COMMENT ON COLUMN "chatbot"."channel_member"."left_at" IS '离开时间';
COMMENT ON COLUMN "chatbot"."channel_member"."last_read_at" IS '最近已读时间';
COMMENT ON COLUMN "chatbot"."channel_member"."role" IS '频道角色';
COMMENT ON COLUMN "chatbot"."channel_member"."invited_by" IS '邀请人';
COMMENT ON COLUMN "chatbot"."channel_member"."invited_at" IS '邀请时间';
COMMENT ON COLUMN "chatbot"."channel_member"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."channel_member"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."channel_webhook" (
    "id" text NOT NULL,
    "user_id" text,
    "channel_id" text,
    "name" text,
    "profile_image_url" text,
    "token" text,
    "last_used_at" bigint,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."channel_webhook" IS 'Open WebUI 频道 Webhook。';
COMMENT ON COLUMN "chatbot"."channel_webhook"."id" IS 'Webhook ID';
COMMENT ON COLUMN "chatbot"."channel_webhook"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."channel_webhook"."channel_id" IS '频道 ID';
COMMENT ON COLUMN "chatbot"."channel_webhook"."name" IS 'Webhook 名称';
COMMENT ON COLUMN "chatbot"."channel_webhook"."profile_image_url" IS '头像 URL';
COMMENT ON COLUMN "chatbot"."channel_webhook"."token" IS 'Webhook token';
COMMENT ON COLUMN "chatbot"."channel_webhook"."last_used_at" IS '最近使用时间';
COMMENT ON COLUMN "chatbot"."channel_webhook"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."channel_webhook"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."chat" (
    "id" varchar(255) NOT NULL,
    "user_id" varchar(255),
    "title" text,
    "share_id" varchar(255),
    "archived" integer,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    "chat" jsonb,
    "pinned" boolean,
    "meta" jsonb,
    "folder_id" text,
    "tasks" jsonb,
    "summary" text,
    "last_read_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."chat" IS 'Open WebUI 聊天会话。生产聊天真相应迁移到 `meyo.chat_threads`。';
COMMENT ON COLUMN "chatbot"."chat"."id" IS '聊天 ID';
COMMENT ON COLUMN "chatbot"."chat"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."chat"."title" IS '标题';
COMMENT ON COLUMN "chatbot"."chat"."share_id" IS '分享 ID';
COMMENT ON COLUMN "chatbot"."chat"."archived" IS '是否归档';
COMMENT ON COLUMN "chatbot"."chat"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."chat"."updated_at" IS '更新时间';
COMMENT ON COLUMN "chatbot"."chat"."chat" IS '聊天内容快照';
COMMENT ON COLUMN "chatbot"."chat"."pinned" IS '是否置顶';
COMMENT ON COLUMN "chatbot"."chat"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."chat"."folder_id" IS '文件夹 ID';
COMMENT ON COLUMN "chatbot"."chat"."tasks" IS '任务数据';
COMMENT ON COLUMN "chatbot"."chat"."summary" IS '摘要';
COMMENT ON COLUMN "chatbot"."chat"."last_read_at" IS '最近已读时间';

CREATE TABLE IF NOT EXISTS "chatbot"."chat_file" (
    "id" text NOT NULL,
    "user_id" text,
    "chat_id" text,
    "file_id" text,
    "message_id" text,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."chat_file" IS 'Open WebUI 聊天和文件关联。';
COMMENT ON COLUMN "chatbot"."chat_file"."id" IS '关联 ID';
COMMENT ON COLUMN "chatbot"."chat_file"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."chat_file"."chat_id" IS '聊天 ID';
COMMENT ON COLUMN "chatbot"."chat_file"."file_id" IS '文件 ID';
COMMENT ON COLUMN "chatbot"."chat_file"."message_id" IS '消息 ID';
COMMENT ON COLUMN "chatbot"."chat_file"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."chat_file"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."chat_message" (
    "id" text NOT NULL,
    "chat_id" text,
    "user_id" text,
    "role" text,
    "parent_id" text,
    "content" jsonb,
    "output" jsonb,
    "model_id" text,
    "files" jsonb,
    "sources" jsonb,
    "embeds" jsonb,
    "done" boolean,
    "status_history" jsonb,
    "error" jsonb,
    "usage" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."chat_message" IS 'Open WebUI 聊天消息。生产消息真相应迁移到 `meyo.chat_messages`。';
COMMENT ON COLUMN "chatbot"."chat_message"."id" IS '消息 ID';
COMMENT ON COLUMN "chatbot"."chat_message"."chat_id" IS '聊天 ID';
COMMENT ON COLUMN "chatbot"."chat_message"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."chat_message"."role" IS '消息角色';
COMMENT ON COLUMN "chatbot"."chat_message"."parent_id" IS '父消息 ID';
COMMENT ON COLUMN "chatbot"."chat_message"."content" IS '消息内容';
COMMENT ON COLUMN "chatbot"."chat_message"."output" IS '输出内容';
COMMENT ON COLUMN "chatbot"."chat_message"."model_id" IS '模型 ID';
COMMENT ON COLUMN "chatbot"."chat_message"."files" IS '文件列表';
COMMENT ON COLUMN "chatbot"."chat_message"."sources" IS '来源列表';
COMMENT ON COLUMN "chatbot"."chat_message"."embeds" IS '嵌入内容';
COMMENT ON COLUMN "chatbot"."chat_message"."done" IS '是否完成';
COMMENT ON COLUMN "chatbot"."chat_message"."status_history" IS '状态历史';
COMMENT ON COLUMN "chatbot"."chat_message"."error" IS '错误信息';
COMMENT ON COLUMN "chatbot"."chat_message"."usage" IS 'token / 调用用量';
COMMENT ON COLUMN "chatbot"."chat_message"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."chat_message"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."chatidtag" (
    "id" varchar(255) NOT NULL,
    "tag_name" varchar(255),
    "chat_id" varchar(255),
    "user_id" varchar(255),
    "timestamp" integer,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."chatidtag" IS 'Open WebUI 旧版聊天标签关联。';
COMMENT ON COLUMN "chatbot"."chatidtag"."id" IS '关联 ID';
COMMENT ON COLUMN "chatbot"."chatidtag"."tag_name" IS '标签名';
COMMENT ON COLUMN "chatbot"."chatidtag"."chat_id" IS '聊天 ID';
COMMENT ON COLUMN "chatbot"."chatidtag"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."chatidtag"."timestamp" IS '时间戳';

CREATE TABLE IF NOT EXISTS "chatbot"."config" (
    "id" integer NOT NULL,
    "data" jsonb,
    "version" integer,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."config" IS 'Open WebUI 持久配置。';
COMMENT ON COLUMN "chatbot"."config"."id" IS '配置 ID';
COMMENT ON COLUMN "chatbot"."config"."data" IS '配置内容';
COMMENT ON COLUMN "chatbot"."config"."version" IS '配置版本';
COMMENT ON COLUMN "chatbot"."config"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."config"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."document" (
    "id" integer NOT NULL,
    "collection_name" varchar(255),
    "name" varchar(255),
    "title" text,
    "filename" text,
    "content" text,
    "user_id" varchar(255),
    "timestamp" integer,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."document" IS 'Open WebUI 旧版文档 collection 元数据。';
COMMENT ON COLUMN "chatbot"."document"."id" IS '文档记录 ID';
COMMENT ON COLUMN "chatbot"."document"."collection_name" IS 'collection 名称';
COMMENT ON COLUMN "chatbot"."document"."name" IS '文档名称';
COMMENT ON COLUMN "chatbot"."document"."title" IS '标题';
COMMENT ON COLUMN "chatbot"."document"."filename" IS '文件名';
COMMENT ON COLUMN "chatbot"."document"."content" IS '文档内容';
COMMENT ON COLUMN "chatbot"."document"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."document"."timestamp" IS '时间戳';

CREATE TABLE IF NOT EXISTS "chatbot"."feedback" (
    "id" text NOT NULL,
    "user_id" text,
    "version" bigint,
    "type" text,
    "data" jsonb,
    "meta" jsonb,
    "snapshot" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."feedback" IS 'Open WebUI 用户反馈。';
COMMENT ON COLUMN "chatbot"."feedback"."id" IS '反馈 ID';
COMMENT ON COLUMN "chatbot"."feedback"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."feedback"."version" IS '反馈版本';
COMMENT ON COLUMN "chatbot"."feedback"."type" IS '反馈类型';
COMMENT ON COLUMN "chatbot"."feedback"."data" IS '反馈数据';
COMMENT ON COLUMN "chatbot"."feedback"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."feedback"."snapshot" IS '快照';
COMMENT ON COLUMN "chatbot"."feedback"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."feedback"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."file" (
    "id" text NOT NULL,
    "user_id" text,
    "filename" text,
    "meta" jsonb,
    "created_at" integer,
    "hash" text,
    "data" jsonb,
    "updated_at" bigint,
    "path" text,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."file" IS 'Open WebUI 文件元数据。生产文件真相应迁移到 `meyo.files`。';
COMMENT ON COLUMN "chatbot"."file"."id" IS '文件 ID';
COMMENT ON COLUMN "chatbot"."file"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."file"."filename" IS '文件名';
COMMENT ON COLUMN "chatbot"."file"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."file"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."file"."hash" IS '文件 hash';
COMMENT ON COLUMN "chatbot"."file"."data" IS '文件数据';
COMMENT ON COLUMN "chatbot"."file"."updated_at" IS '更新时间';
COMMENT ON COLUMN "chatbot"."file"."path" IS '本地路径';

CREATE TABLE IF NOT EXISTS "chatbot"."folder" (
    "id" text NOT NULL,
    "parent_id" text,
    "user_id" text,
    "name" text,
    "items" jsonb,
    "meta" jsonb,
    "is_expanded" boolean,
    "data" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."folder" IS 'Open WebUI 聊天文件夹。';
COMMENT ON COLUMN "chatbot"."folder"."id" IS '文件夹 ID';
COMMENT ON COLUMN "chatbot"."folder"."parent_id" IS '父文件夹 ID';
COMMENT ON COLUMN "chatbot"."folder"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."folder"."name" IS '文件夹名称';
COMMENT ON COLUMN "chatbot"."folder"."items" IS '子项';
COMMENT ON COLUMN "chatbot"."folder"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."folder"."is_expanded" IS '是否展开';
COMMENT ON COLUMN "chatbot"."folder"."data" IS '扩展数据';
COMMENT ON COLUMN "chatbot"."folder"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."folder"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."function" (
    "id" text NOT NULL,
    "user_id" text,
    "name" text,
    "type" text,
    "content" text,
    "meta" text,
    "valves" text,
    "is_active" integer,
    "is_global" integer,
    "created_at" integer,
    "updated_at" integer,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."function" IS 'Open WebUI function 配置。生产能力真相应迁移到 `meyo.capability_registry`。';
COMMENT ON COLUMN "chatbot"."function"."id" IS 'Function ID';
COMMENT ON COLUMN "chatbot"."function"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."function"."name" IS '名称';
COMMENT ON COLUMN "chatbot"."function"."type" IS '类型';
COMMENT ON COLUMN "chatbot"."function"."content" IS '内容';
COMMENT ON COLUMN "chatbot"."function"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."function"."valves" IS '参数';
COMMENT ON COLUMN "chatbot"."function"."is_active" IS '是否启用';
COMMENT ON COLUMN "chatbot"."function"."is_global" IS '是否全局';
COMMENT ON COLUMN "chatbot"."function"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."function"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."group" (
    "id" text NOT NULL,
    "user_id" text,
    "name" text,
    "description" text,
    "data" jsonb,
    "meta" jsonb,
    "permissions" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."group" IS 'Open WebUI 用户组。';
COMMENT ON COLUMN "chatbot"."group"."id" IS '用户组 ID';
COMMENT ON COLUMN "chatbot"."group"."user_id" IS '创建用户 ID';
COMMENT ON COLUMN "chatbot"."group"."name" IS '用户组名称';
COMMENT ON COLUMN "chatbot"."group"."description" IS '描述';
COMMENT ON COLUMN "chatbot"."group"."data" IS '数据';
COMMENT ON COLUMN "chatbot"."group"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."group"."permissions" IS '权限';
COMMENT ON COLUMN "chatbot"."group"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."group"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."group_member" (
    "id" text NOT NULL,
    "group_id" text,
    "user_id" text,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."group_member" IS 'Open WebUI 用户组成员。';
COMMENT ON COLUMN "chatbot"."group_member"."id" IS '成员关系 ID';
COMMENT ON COLUMN "chatbot"."group_member"."group_id" IS '用户组 ID';
COMMENT ON COLUMN "chatbot"."group_member"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."group_member"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."group_member"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."knowledge" (
    "id" text NOT NULL,
    "user_id" text,
    "name" text,
    "description" text,
    "meta" jsonb,
    "data" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."knowledge" IS 'Open WebUI 知识库元数据。生产知识真相应迁移到 `meyo.knowledge_bases`。';
COMMENT ON COLUMN "chatbot"."knowledge"."id" IS '知识库 ID';
COMMENT ON COLUMN "chatbot"."knowledge"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."knowledge"."name" IS '名称';
COMMENT ON COLUMN "chatbot"."knowledge"."description" IS '描述';
COMMENT ON COLUMN "chatbot"."knowledge"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."knowledge"."data" IS '知识库数据';
COMMENT ON COLUMN "chatbot"."knowledge"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."knowledge"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."knowledge_file" (
    "id" text NOT NULL,
    "user_id" text,
    "knowledge_id" text,
    "file_id" text,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."knowledge_file" IS 'Open WebUI 知识库和文件关联。';
COMMENT ON COLUMN "chatbot"."knowledge_file"."id" IS '关联 ID';
COMMENT ON COLUMN "chatbot"."knowledge_file"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."knowledge_file"."knowledge_id" IS '知识库 ID';
COMMENT ON COLUMN "chatbot"."knowledge_file"."file_id" IS '文件 ID';
COMMENT ON COLUMN "chatbot"."knowledge_file"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."knowledge_file"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."memory" (
    "id" varchar(255) NOT NULL,
    "user_id" varchar(255),
    "content" text,
    "updated_at" integer,
    "created_at" integer,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."memory" IS 'Open WebUI 用户记忆。';
COMMENT ON COLUMN "chatbot"."memory"."id" IS '记忆 ID';
COMMENT ON COLUMN "chatbot"."memory"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."memory"."content" IS '记忆内容';
COMMENT ON COLUMN "chatbot"."memory"."updated_at" IS '更新时间';
COMMENT ON COLUMN "chatbot"."memory"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "chatbot"."message" (
    "id" text NOT NULL,
    "user_id" text,
    "channel_id" text,
    "content" text,
    "data" jsonb,
    "meta" jsonb,
    "parent_id" text,
    "reply_to_id" text,
    "is_pinned" boolean,
    "pinned_at" bigint,
    "pinned_by" text,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."message" IS 'Open WebUI 频道消息。';
COMMENT ON COLUMN "chatbot"."message"."id" IS '消息 ID';
COMMENT ON COLUMN "chatbot"."message"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."message"."channel_id" IS '频道 ID';
COMMENT ON COLUMN "chatbot"."message"."content" IS '消息内容';
COMMENT ON COLUMN "chatbot"."message"."data" IS '消息数据';
COMMENT ON COLUMN "chatbot"."message"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."message"."parent_id" IS '父消息 ID';
COMMENT ON COLUMN "chatbot"."message"."reply_to_id" IS '回复消息 ID';
COMMENT ON COLUMN "chatbot"."message"."is_pinned" IS '是否置顶';
COMMENT ON COLUMN "chatbot"."message"."pinned_at" IS '置顶时间';
COMMENT ON COLUMN "chatbot"."message"."pinned_by" IS '置顶人';
COMMENT ON COLUMN "chatbot"."message"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."message"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."message_reaction" (
    "id" text NOT NULL,
    "user_id" text,
    "message_id" text,
    "name" text,
    "created_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."message_reaction" IS 'Open WebUI 频道消息反应。';
COMMENT ON COLUMN "chatbot"."message_reaction"."id" IS '反应 ID';
COMMENT ON COLUMN "chatbot"."message_reaction"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."message_reaction"."message_id" IS '消息 ID';
COMMENT ON COLUMN "chatbot"."message_reaction"."name" IS '反应名称';
COMMENT ON COLUMN "chatbot"."message_reaction"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "chatbot"."migratehistory" (
    "id" integer NOT NULL,
    "name" varchar(255),
    "migrated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."migratehistory" IS 'Peewee 迁移历史。';
COMMENT ON COLUMN "chatbot"."migratehistory"."id" IS '迁移历史 ID';
COMMENT ON COLUMN "chatbot"."migratehistory"."name" IS '迁移名称';
COMMENT ON COLUMN "chatbot"."migratehistory"."migrated_at" IS '迁移时间';

CREATE TABLE IF NOT EXISTS "chatbot"."model" (
    "id" text NOT NULL,
    "user_id" text,
    "base_model_id" text,
    "name" text,
    "meta" text,
    "params" text,
    "is_active" boolean,
    "created_at" integer,
    "updated_at" integer,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."model" IS 'Open WebUI 模型配置。';
COMMENT ON COLUMN "chatbot"."model"."id" IS '模型 ID';
COMMENT ON COLUMN "chatbot"."model"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."model"."base_model_id" IS '基础模型 ID';
COMMENT ON COLUMN "chatbot"."model"."name" IS '模型名称';
COMMENT ON COLUMN "chatbot"."model"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."model"."params" IS '参数';
COMMENT ON COLUMN "chatbot"."model"."is_active" IS '是否启用';
COMMENT ON COLUMN "chatbot"."model"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."model"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."note" (
    "id" text NOT NULL,
    "user_id" text,
    "title" text,
    "data" jsonb,
    "meta" jsonb,
    "is_pinned" boolean,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."note" IS 'Open WebUI 用户笔记。';
COMMENT ON COLUMN "chatbot"."note"."id" IS '笔记 ID';
COMMENT ON COLUMN "chatbot"."note"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."note"."title" IS '标题';
COMMENT ON COLUMN "chatbot"."note"."data" IS '笔记数据';
COMMENT ON COLUMN "chatbot"."note"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."note"."is_pinned" IS '是否置顶';
COMMENT ON COLUMN "chatbot"."note"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."note"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."oauth_session" (
    "id" text NOT NULL,
    "user_id" text,
    "provider" text,
    "token" text,
    "expires_at" bigint,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."oauth_session" IS 'Open WebUI OAuth Session。';
COMMENT ON COLUMN "chatbot"."oauth_session"."id" IS 'Session ID';
COMMENT ON COLUMN "chatbot"."oauth_session"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."oauth_session"."provider" IS 'OAuth provider';
COMMENT ON COLUMN "chatbot"."oauth_session"."token" IS 'OAuth token';
COMMENT ON COLUMN "chatbot"."oauth_session"."expires_at" IS '过期时间';
COMMENT ON COLUMN "chatbot"."oauth_session"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."oauth_session"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."prompt" (
    "id" text NOT NULL,
    "command" varchar,
    "user_id" varchar,
    "name" text,
    "content" text,
    "data" jsonb,
    "meta" jsonb,
    "is_active" boolean,
    "version_id" text,
    "tags" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."prompt" IS 'Open WebUI Prompt 主表。生产能力真相应迁移到 `meyo.capability_registry`。';
COMMENT ON COLUMN "chatbot"."prompt"."id" IS 'Prompt ID';
COMMENT ON COLUMN "chatbot"."prompt"."command" IS 'Prompt 命令';
COMMENT ON COLUMN "chatbot"."prompt"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."prompt"."name" IS '名称';
COMMENT ON COLUMN "chatbot"."prompt"."content" IS '内容';
COMMENT ON COLUMN "chatbot"."prompt"."data" IS '数据';
COMMENT ON COLUMN "chatbot"."prompt"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."prompt"."is_active" IS '是否启用';
COMMENT ON COLUMN "chatbot"."prompt"."version_id" IS '当前版本 ID';
COMMENT ON COLUMN "chatbot"."prompt"."tags" IS '标签';
COMMENT ON COLUMN "chatbot"."prompt"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."prompt"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."prompt_history" (
    "id" text NOT NULL,
    "prompt_id" text,
    "parent_id" text,
    "snapshot" jsonb,
    "user_id" text,
    "commit_message" text,
    "created_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."prompt_history" IS 'Open WebUI Prompt 历史版本。';
COMMENT ON COLUMN "chatbot"."prompt_history"."id" IS '历史版本 ID';
COMMENT ON COLUMN "chatbot"."prompt_history"."prompt_id" IS 'Prompt ID';
COMMENT ON COLUMN "chatbot"."prompt_history"."parent_id" IS '父版本 ID';
COMMENT ON COLUMN "chatbot"."prompt_history"."snapshot" IS '版本快照';
COMMENT ON COLUMN "chatbot"."prompt_history"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."prompt_history"."commit_message" IS '提交说明';
COMMENT ON COLUMN "chatbot"."prompt_history"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "chatbot"."shared_chat" (
    "id" text NOT NULL,
    "chat_id" text,
    "user_id" text,
    "title" text,
    "chat" jsonb,
    "created_at" bigint,
    "updated_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."shared_chat" IS 'Open WebUI 分享聊天快照。';
COMMENT ON COLUMN "chatbot"."shared_chat"."id" IS '分享 ID';
COMMENT ON COLUMN "chatbot"."shared_chat"."chat_id" IS '聊天 ID';
COMMENT ON COLUMN "chatbot"."shared_chat"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."shared_chat"."title" IS '标题';
COMMENT ON COLUMN "chatbot"."shared_chat"."chat" IS '聊天快照';
COMMENT ON COLUMN "chatbot"."shared_chat"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."shared_chat"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."skill" (
    "id" varchar NOT NULL,
    "user_id" varchar,
    "name" text,
    "description" text,
    "content" text,
    "meta" jsonb,
    "is_active" boolean,
    "updated_at" bigint,
    "created_at" bigint,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."skill" IS 'Open WebUI Skill 配置。生产能力真相应迁移到 `meyo.capability_registry`。';
COMMENT ON COLUMN "chatbot"."skill"."id" IS 'Skill ID';
COMMENT ON COLUMN "chatbot"."skill"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."skill"."name" IS 'Skill 名称';
COMMENT ON COLUMN "chatbot"."skill"."description" IS '描述';
COMMENT ON COLUMN "chatbot"."skill"."content" IS '内容';
COMMENT ON COLUMN "chatbot"."skill"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."skill"."is_active" IS '是否启用';
COMMENT ON COLUMN "chatbot"."skill"."updated_at" IS '更新时间';
COMMENT ON COLUMN "chatbot"."skill"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "chatbot"."tag" (
    "id" varchar(255) NOT NULL,
    "name" varchar(255),
    "user_id" varchar(255),
    "meta" jsonb,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."tag" IS 'Open WebUI 标签。';
COMMENT ON COLUMN "chatbot"."tag"."id" IS '标签 ID';
COMMENT ON COLUMN "chatbot"."tag"."name" IS '标签名';
COMMENT ON COLUMN "chatbot"."tag"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."tag"."meta" IS '元数据';

CREATE TABLE IF NOT EXISTS "chatbot"."tool" (
    "id" text NOT NULL,
    "user_id" text,
    "name" text,
    "content" text,
    "specs" text,
    "meta" text,
    "valves" text,
    "created_at" integer,
    "updated_at" integer,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."tool" IS 'Open WebUI Tool 配置。生产能力真相应迁移到 `meyo.capability_registry`。';
COMMENT ON COLUMN "chatbot"."tool"."id" IS 'Tool ID';
COMMENT ON COLUMN "chatbot"."tool"."user_id" IS '用户 ID';
COMMENT ON COLUMN "chatbot"."tool"."name" IS 'Tool 名称';
COMMENT ON COLUMN "chatbot"."tool"."content" IS '内容';
COMMENT ON COLUMN "chatbot"."tool"."specs" IS '工具规格';
COMMENT ON COLUMN "chatbot"."tool"."meta" IS '元数据';
COMMENT ON COLUMN "chatbot"."tool"."valves" IS '参数';
COMMENT ON COLUMN "chatbot"."tool"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."tool"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "chatbot"."user" (
    "id" varchar(255) NOT NULL,
    "name" varchar(255),
    "email" varchar(255),
    "role" varchar(255),
    "profile_image_url" text,
    "created_at" integer,
    "updated_at" integer,
    "last_active_at" integer,
    "username" varchar(50),
    "bio" text,
    "gender" text,
    "date_of_birth" date,
    "profile_banner_image_url" text,
    "timezone" varchar,
    "presence_state" varchar,
    "status_emoji" varchar,
    "status_message" text,
    "status_expires_at" bigint,
    "oauth" jsonb,
    "info" jsonb,
    "settings" jsonb,
    "scim" jsonb,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "chatbot"."user" IS 'Open WebUI 用户表。生产用户真相应迁移到 `meyo.users`。';
COMMENT ON COLUMN "chatbot"."user"."id" IS 'Open WebUI 用户 ID';
COMMENT ON COLUMN "chatbot"."user"."name" IS '姓名';
COMMENT ON COLUMN "chatbot"."user"."email" IS '邮箱';
COMMENT ON COLUMN "chatbot"."user"."role" IS '角色';
COMMENT ON COLUMN "chatbot"."user"."profile_image_url" IS '头像 URL';
COMMENT ON COLUMN "chatbot"."user"."created_at" IS '创建时间';
COMMENT ON COLUMN "chatbot"."user"."updated_at" IS '更新时间';
COMMENT ON COLUMN "chatbot"."user"."last_active_at" IS '最近活跃时间';
COMMENT ON COLUMN "chatbot"."user"."username" IS '用户名';
COMMENT ON COLUMN "chatbot"."user"."bio" IS '简介';
COMMENT ON COLUMN "chatbot"."user"."gender" IS '性别';
COMMENT ON COLUMN "chatbot"."user"."date_of_birth" IS '出生日期';
COMMENT ON COLUMN "chatbot"."user"."profile_banner_image_url" IS '主页横幅';
COMMENT ON COLUMN "chatbot"."user"."timezone" IS '时区';
COMMENT ON COLUMN "chatbot"."user"."presence_state" IS '在线状态';
COMMENT ON COLUMN "chatbot"."user"."status_emoji" IS '状态 emoji';
COMMENT ON COLUMN "chatbot"."user"."status_message" IS '状态文案';
COMMENT ON COLUMN "chatbot"."user"."status_expires_at" IS '状态过期时间';
COMMENT ON COLUMN "chatbot"."user"."oauth" IS 'OAuth 数据';
COMMENT ON COLUMN "chatbot"."user"."info" IS '用户信息';
COMMENT ON COLUMN "chatbot"."user"."settings" IS '用户设置';
COMMENT ON COLUMN "chatbot"."user"."scim" IS 'SCIM 数据';

COMMIT;
