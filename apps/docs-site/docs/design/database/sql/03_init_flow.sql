-- Flow PostgreSQL initialization script
-- Schema: flow
-- Source: apps/docs-site/docs/design/database/03_meyo_studio_flow.md
-- This script creates upstream application tables and comments for compatibility.

BEGIN;

CREATE SCHEMA IF NOT EXISTS "flow";

CREATE TABLE IF NOT EXISTS "flow"."alembic_version" (
    "version_num" varchar(32) NOT NULL,
    PRIMARY KEY ("version_num")
);
COMMENT ON TABLE "flow"."alembic_version" IS 'Alembic 迁移版本。';
COMMENT ON COLUMN "flow"."alembic_version"."version_num" IS '当前 Alembic revision';

CREATE TABLE IF NOT EXISTS "flow"."apikey" (
    "id" char(32) NOT NULL,
    "name" varchar,
    "api_key" varchar,
    "api_key_hash" varchar,
    "user_id" char(32),
    "last_used_at" timestamptz,
    "total_uses" integer,
    "is_active" boolean,
    "created_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."apikey" IS 'Langflow API Key。';
COMMENT ON COLUMN "flow"."apikey"."id" IS 'API Key ID';
COMMENT ON COLUMN "flow"."apikey"."name" IS '名称';
COMMENT ON COLUMN "flow"."apikey"."api_key" IS 'API Key 值';
COMMENT ON COLUMN "flow"."apikey"."api_key_hash" IS 'API Key hash';
COMMENT ON COLUMN "flow"."apikey"."user_id" IS 'Langflow 用户 ID';
COMMENT ON COLUMN "flow"."apikey"."last_used_at" IS '最近使用时间';
COMMENT ON COLUMN "flow"."apikey"."total_uses" IS '使用次数';
COMMENT ON COLUMN "flow"."apikey"."is_active" IS '是否启用';
COMMENT ON COLUMN "flow"."apikey"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "flow"."deployment" (
    "id" char(32) NOT NULL,
    "resource_key" varchar,
    "user_id" char(32),
    "project_id" char(32),
    "deployment_provider_account_id" char(32),
    "name" varchar,
    "description" text,
    "deployment_type" varchar(5),
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."deployment" IS 'Langflow Flow 部署记录。';
COMMENT ON COLUMN "flow"."deployment"."id" IS '部署 ID';
COMMENT ON COLUMN "flow"."deployment"."resource_key" IS '部署资源键';
COMMENT ON COLUMN "flow"."deployment"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."deployment"."project_id" IS '项目 / folder ID';
COMMENT ON COLUMN "flow"."deployment"."deployment_provider_account_id" IS '部署平台账号 ID';
COMMENT ON COLUMN "flow"."deployment"."name" IS '部署名称';
COMMENT ON COLUMN "flow"."deployment"."description" IS '描述';
COMMENT ON COLUMN "flow"."deployment"."deployment_type" IS '部署类型';
COMMENT ON COLUMN "flow"."deployment"."created_at" IS '创建时间';
COMMENT ON COLUMN "flow"."deployment"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."deployment_provider_account" (
    "id" char(32) NOT NULL,
    "user_id" char(32),
    "provider_tenant_id" varchar,
    "name" varchar,
    "provider_url" varchar,
    "api_key" varchar,
    "provider_key" varchar(19),
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."deployment_provider_account" IS 'Langflow 部署平台账号。';
COMMENT ON COLUMN "flow"."deployment_provider_account"."id" IS '部署账号 ID';
COMMENT ON COLUMN "flow"."deployment_provider_account"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."deployment_provider_account"."provider_tenant_id" IS '平台租户 ID';
COMMENT ON COLUMN "flow"."deployment_provider_account"."name" IS '账号名称';
COMMENT ON COLUMN "flow"."deployment_provider_account"."provider_url" IS '平台 URL';
COMMENT ON COLUMN "flow"."deployment_provider_account"."api_key" IS '平台 API Key';
COMMENT ON COLUMN "flow"."deployment_provider_account"."provider_key" IS '平台类型';
COMMENT ON COLUMN "flow"."deployment_provider_account"."created_at" IS '创建时间';
COMMENT ON COLUMN "flow"."deployment_provider_account"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."file" (
    "id" char(32) NOT NULL,
    "user_id" char(32),
    "name" varchar,
    "path" varchar,
    "size" integer,
    "provider" varchar,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."file" IS 'Langflow Studio 文件元数据。';
COMMENT ON COLUMN "flow"."file"."id" IS '文件 ID';
COMMENT ON COLUMN "flow"."file"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."file"."name" IS '文件名';
COMMENT ON COLUMN "flow"."file"."path" IS '文件路径';
COMMENT ON COLUMN "flow"."file"."size" IS '文件大小';
COMMENT ON COLUMN "flow"."file"."provider" IS '文件存储 provider';
COMMENT ON COLUMN "flow"."file"."created_at" IS '创建时间';
COMMENT ON COLUMN "flow"."file"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."flow" (
    "id" char(32) NOT NULL,
    "user_id" char(32),
    "folder_id" char(32),
    "name" varchar,
    "description" text,
    "data" jsonb,
    "tags" jsonb,
    "icon" varchar,
    "icon_bg_color" varchar,
    "gradient" varchar,
    "is_component" boolean,
    "webhook" boolean,
    "endpoint_name" varchar,
    "mcp_enabled" boolean,
    "action_name" varchar,
    "action_description" text,
    "access_type" varchar(7),
    "locked" boolean,
    "fs_path" varchar,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."flow" IS 'Langflow 内部 Flow 草稿 / 工作流主体。生产发布事实应写入 `meyo.flow_versions`。';
COMMENT ON COLUMN "flow"."flow"."id" IS 'Langflow Flow ID';
COMMENT ON COLUMN "flow"."flow"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."flow"."folder_id" IS '文件夹 ID';
COMMENT ON COLUMN "flow"."flow"."name" IS 'Flow 名称';
COMMENT ON COLUMN "flow"."flow"."description" IS '描述';
COMMENT ON COLUMN "flow"."flow"."data" IS 'Flow 画布数据';
COMMENT ON COLUMN "flow"."flow"."tags" IS '标签';
COMMENT ON COLUMN "flow"."flow"."icon" IS '图标';
COMMENT ON COLUMN "flow"."flow"."icon_bg_color" IS '图标背景色';
COMMENT ON COLUMN "flow"."flow"."gradient" IS '渐变配置';
COMMENT ON COLUMN "flow"."flow"."is_component" IS '是否组件';
COMMENT ON COLUMN "flow"."flow"."webhook" IS '是否启用 webhook';
COMMENT ON COLUMN "flow"."flow"."endpoint_name" IS 'endpoint 名称';
COMMENT ON COLUMN "flow"."flow"."mcp_enabled" IS '是否启用 MCP';
COMMENT ON COLUMN "flow"."flow"."action_name" IS 'Action 名称';
COMMENT ON COLUMN "flow"."flow"."action_description" IS 'Action 描述';
COMMENT ON COLUMN "flow"."flow"."access_type" IS '访问类型';
COMMENT ON COLUMN "flow"."flow"."locked" IS '是否锁定';
COMMENT ON COLUMN "flow"."flow"."fs_path" IS '文件系统路径';
COMMENT ON COLUMN "flow"."flow"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."flow_version" (
    "id" char(32) NOT NULL,
    "flow_id" char(32),
    "user_id" char(32),
    "data" jsonb,
    "version_number" integer,
    "description" varchar(500),
    "created_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."flow_version" IS 'Langflow 内部 Flow 版本。';
COMMENT ON COLUMN "flow"."flow_version"."id" IS '版本 ID';
COMMENT ON COLUMN "flow"."flow_version"."flow_id" IS 'Flow ID';
COMMENT ON COLUMN "flow"."flow_version"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."flow_version"."data" IS '版本 Flow 数据';
COMMENT ON COLUMN "flow"."flow_version"."version_number" IS '版本号';
COMMENT ON COLUMN "flow"."flow_version"."description" IS '版本描述';
COMMENT ON COLUMN "flow"."flow_version"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "flow"."flow_version_deployment_attachment" (
    "id" char(32) NOT NULL,
    "user_id" char(32),
    "flow_version_id" char(32),
    "deployment_id" char(32),
    "provider_snapshot_id" varchar,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."flow_version_deployment_attachment" IS 'Langflow Flow 版本和部署记录关联。';
COMMENT ON COLUMN "flow"."flow_version_deployment_attachment"."id" IS '关联 ID';
COMMENT ON COLUMN "flow"."flow_version_deployment_attachment"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."flow_version_deployment_attachment"."flow_version_id" IS 'Flow 版本 ID';
COMMENT ON COLUMN "flow"."flow_version_deployment_attachment"."deployment_id" IS '部署 ID';
COMMENT ON COLUMN "flow"."flow_version_deployment_attachment"."provider_snapshot_id" IS '平台快照 ID';
COMMENT ON COLUMN "flow"."flow_version_deployment_attachment"."created_at" IS '创建时间';
COMMENT ON COLUMN "flow"."flow_version_deployment_attachment"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."folder" (
    "id" char(32) NOT NULL,
    "parent_id" char(32),
    "user_id" char(32),
    "name" varchar,
    "description" text,
    "auth_settings" jsonb,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."folder" IS 'Langflow Flow 文件夹 / 项目。';
COMMENT ON COLUMN "flow"."folder"."id" IS '文件夹 ID';
COMMENT ON COLUMN "flow"."folder"."parent_id" IS '父文件夹 ID';
COMMENT ON COLUMN "flow"."folder"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."folder"."name" IS '文件夹名称';
COMMENT ON COLUMN "flow"."folder"."description" IS '描述';
COMMENT ON COLUMN "flow"."folder"."auth_settings" IS '认证设置';

CREATE TABLE IF NOT EXISTS "flow"."job" (
    "job_id" char(32) NOT NULL,
    "flow_id" char(32),
    "status" varchar(11),
    "type" varchar(10),
    "user_id" char(32),
    "asset_id" char(32),
    "asset_type" varchar,
    "created_timestamp" timestamptz,
    "finished_timestamp" timestamptz,
    PRIMARY KEY ("job_id")
);
COMMENT ON TABLE "flow"."job" IS 'Langflow 后台任务。';
COMMENT ON COLUMN "flow"."job"."job_id" IS 'Job ID';
COMMENT ON COLUMN "flow"."job"."flow_id" IS 'Flow ID';
COMMENT ON COLUMN "flow"."job"."status" IS '任务状态';
COMMENT ON COLUMN "flow"."job"."type" IS '任务类型';
COMMENT ON COLUMN "flow"."job"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."job"."asset_id" IS '资产 ID';
COMMENT ON COLUMN "flow"."job"."asset_type" IS '资产类型';
COMMENT ON COLUMN "flow"."job"."created_timestamp" IS '创建时间';
COMMENT ON COLUMN "flow"."job"."finished_timestamp" IS '完成时间';

CREATE TABLE IF NOT EXISTS "flow"."message" (
    "id" char(32) NOT NULL,
    "flow_id" char(32),
    "session_id" varchar,
    "sender" varchar,
    "sender_name" varchar,
    "text" text,
    "files" jsonb,
    "error" boolean,
    "edit" boolean,
    "properties" jsonb,
    "category" text,
    "content_blocks" jsonb,
    "context_id" varchar,
    "session_metadata" jsonb,
    "timestamp" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."message" IS 'Langflow Playground / 会话消息。';
COMMENT ON COLUMN "flow"."message"."id" IS '消息 ID';
COMMENT ON COLUMN "flow"."message"."flow_id" IS 'Flow ID';
COMMENT ON COLUMN "flow"."message"."session_id" IS '会话 ID';
COMMENT ON COLUMN "flow"."message"."sender" IS '发送方';
COMMENT ON COLUMN "flow"."message"."sender_name" IS '发送方名称';
COMMENT ON COLUMN "flow"."message"."text" IS '文本';
COMMENT ON COLUMN "flow"."message"."files" IS '文件列表';
COMMENT ON COLUMN "flow"."message"."error" IS '是否错误';
COMMENT ON COLUMN "flow"."message"."edit" IS '是否编辑消息';
COMMENT ON COLUMN "flow"."message"."properties" IS '消息属性';
COMMENT ON COLUMN "flow"."message"."category" IS '消息分类';
COMMENT ON COLUMN "flow"."message"."content_blocks" IS '内容块';
COMMENT ON COLUMN "flow"."message"."context_id" IS '上下文 ID';
COMMENT ON COLUMN "flow"."message"."session_metadata" IS '会话元数据';
COMMENT ON COLUMN "flow"."message"."timestamp" IS '时间戳';

CREATE TABLE IF NOT EXISTS "flow"."span" (
    "id" char(32) NOT NULL,
    "trace_id" char(32),
    "parent_span_id" char(32),
    "name" varchar,
    "span_type" varchar(9),
    "span_kind" varchar(8),
    "status" varchar(5),
    "start_time" timestamptz,
    "end_time" timestamptz,
    "latency_ms" integer,
    "inputs" jsonb,
    "outputs" jsonb,
    "error" text,
    "attributes" jsonb,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."span" IS 'Langflow trace span 明细。';
COMMENT ON COLUMN "flow"."span"."id" IS 'Span ID';
COMMENT ON COLUMN "flow"."span"."trace_id" IS 'Trace ID';
COMMENT ON COLUMN "flow"."span"."parent_span_id" IS '父 Span ID';
COMMENT ON COLUMN "flow"."span"."name" IS 'Span 名称';
COMMENT ON COLUMN "flow"."span"."span_type" IS 'Span 类型';
COMMENT ON COLUMN "flow"."span"."span_kind" IS 'Span kind';
COMMENT ON COLUMN "flow"."span"."status" IS '状态';
COMMENT ON COLUMN "flow"."span"."start_time" IS '开始时间';
COMMENT ON COLUMN "flow"."span"."end_time" IS '结束时间';
COMMENT ON COLUMN "flow"."span"."latency_ms" IS '耗时毫秒';
COMMENT ON COLUMN "flow"."span"."inputs" IS '输入';
COMMENT ON COLUMN "flow"."span"."outputs" IS '输出';
COMMENT ON COLUMN "flow"."span"."error" IS '错误';
COMMENT ON COLUMN "flow"."span"."attributes" IS '属性';

CREATE TABLE IF NOT EXISTS "flow"."sso_config" (
    "id" char(32) NOT NULL,
    "provider" varchar,
    "provider_name" varchar,
    "enabled" boolean,
    "enforce_sso" boolean,
    "client_id" varchar,
    "client_secret_encrypted" varchar,
    "discovery_url" varchar,
    "redirect_uri" varchar,
    "scopes" varchar,
    "email_claim" varchar,
    "username_claim" varchar,
    "user_id_claim" varchar,
    "token_endpoint" varchar,
    "authorization_endpoint" varchar,
    "jwks_uri" varchar,
    "issuer" varchar,
    "created_by" char(32),
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."sso_config" IS 'Langflow SSO 配置。';
COMMENT ON COLUMN "flow"."sso_config"."id" IS 'SSO 配置 ID';
COMMENT ON COLUMN "flow"."sso_config"."provider" IS 'Provider';
COMMENT ON COLUMN "flow"."sso_config"."provider_name" IS 'Provider 名称';
COMMENT ON COLUMN "flow"."sso_config"."enabled" IS '是否启用';
COMMENT ON COLUMN "flow"."sso_config"."enforce_sso" IS '是否强制 SSO';
COMMENT ON COLUMN "flow"."sso_config"."client_id" IS 'Client ID';
COMMENT ON COLUMN "flow"."sso_config"."client_secret_encrypted" IS '加密后的 Client Secret';
COMMENT ON COLUMN "flow"."sso_config"."discovery_url" IS 'Discovery URL';
COMMENT ON COLUMN "flow"."sso_config"."redirect_uri" IS 'Redirect URI';
COMMENT ON COLUMN "flow"."sso_config"."scopes" IS 'Scopes';
COMMENT ON COLUMN "flow"."sso_config"."email_claim" IS '邮箱 claim';
COMMENT ON COLUMN "flow"."sso_config"."username_claim" IS '用户名 claim';
COMMENT ON COLUMN "flow"."sso_config"."user_id_claim" IS '用户 ID claim';
COMMENT ON COLUMN "flow"."sso_config"."token_endpoint" IS 'Token endpoint';
COMMENT ON COLUMN "flow"."sso_config"."authorization_endpoint" IS 'Authorization endpoint';
COMMENT ON COLUMN "flow"."sso_config"."jwks_uri" IS 'JWKS URI';
COMMENT ON COLUMN "flow"."sso_config"."issuer" IS 'Issuer';
COMMENT ON COLUMN "flow"."sso_config"."created_by" IS '创建人';
COMMENT ON COLUMN "flow"."sso_config"."created_at" IS '创建时间';
COMMENT ON COLUMN "flow"."sso_config"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."sso_user_profile" (
    "id" char(32) NOT NULL,
    "user_id" char(32),
    "sso_provider" varchar,
    "sso_user_id" varchar,
    "email" varchar,
    "sso_last_login_at" timestamptz,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."sso_user_profile" IS 'Langflow SSO 用户档案。';
COMMENT ON COLUMN "flow"."sso_user_profile"."id" IS 'SSO 用户档案 ID';
COMMENT ON COLUMN "flow"."sso_user_profile"."user_id" IS 'Langflow 用户 ID';
COMMENT ON COLUMN "flow"."sso_user_profile"."sso_provider" IS 'SSO provider';
COMMENT ON COLUMN "flow"."sso_user_profile"."sso_user_id" IS 'SSO 用户 ID';
COMMENT ON COLUMN "flow"."sso_user_profile"."email" IS '邮箱';
COMMENT ON COLUMN "flow"."sso_user_profile"."sso_last_login_at" IS '最近 SSO 登录时间';
COMMENT ON COLUMN "flow"."sso_user_profile"."created_at" IS '创建时间';
COMMENT ON COLUMN "flow"."sso_user_profile"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."trace" (
    "id" char(32) NOT NULL,
    "flow_id" char(32),
    "name" varchar,
    "status" varchar(5),
    "start_time" timestamptz,
    "end_time" timestamptz,
    "total_latency_ms" integer,
    "total_tokens" integer,
    "session_id" varchar,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."trace" IS 'Langflow Flow 执行 trace。';
COMMENT ON COLUMN "flow"."trace"."id" IS 'Trace ID';
COMMENT ON COLUMN "flow"."trace"."flow_id" IS 'Flow ID';
COMMENT ON COLUMN "flow"."trace"."name" IS 'Trace 名称';
COMMENT ON COLUMN "flow"."trace"."status" IS '状态';
COMMENT ON COLUMN "flow"."trace"."start_time" IS '开始时间';
COMMENT ON COLUMN "flow"."trace"."end_time" IS '结束时间';
COMMENT ON COLUMN "flow"."trace"."total_latency_ms" IS '总耗时毫秒';
COMMENT ON COLUMN "flow"."trace"."total_tokens" IS 'token 总数';
COMMENT ON COLUMN "flow"."trace"."session_id" IS '会话 ID';

CREATE TABLE IF NOT EXISTS "flow"."transaction" (
    "id" char(32) NOT NULL,
    "flow_id" char(32),
    "vertex_id" varchar,
    "target_id" varchar,
    "inputs" jsonb,
    "outputs" jsonb,
    "status" varchar,
    "error" varchar,
    "timestamp" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."transaction" IS 'Langflow 节点 transaction 记录。';
COMMENT ON COLUMN "flow"."transaction"."id" IS 'Transaction ID';
COMMENT ON COLUMN "flow"."transaction"."flow_id" IS 'Flow ID';
COMMENT ON COLUMN "flow"."transaction"."vertex_id" IS '节点 ID';
COMMENT ON COLUMN "flow"."transaction"."target_id" IS '目标节点 ID';
COMMENT ON COLUMN "flow"."transaction"."inputs" IS '输入';
COMMENT ON COLUMN "flow"."transaction"."outputs" IS '输出';
COMMENT ON COLUMN "flow"."transaction"."status" IS '状态';
COMMENT ON COLUMN "flow"."transaction"."error" IS '错误';
COMMENT ON COLUMN "flow"."transaction"."timestamp" IS '时间戳';

CREATE TABLE IF NOT EXISTS "flow"."user" (
    "id" char(32) NOT NULL,
    "username" varchar,
    "password" varchar,
    "profile_image" varchar,
    "is_active" boolean,
    "is_superuser" boolean,
    "store_api_key" varchar,
    "optins" jsonb,
    "create_at" timestamptz,
    "updated_at" timestamptz,
    "last_login_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."user" IS 'Langflow 用户。生产用户真相应迁移到 `meyo.users`。';
COMMENT ON COLUMN "flow"."user"."id" IS 'Langflow 用户 ID';
COMMENT ON COLUMN "flow"."user"."username" IS '用户名';
COMMENT ON COLUMN "flow"."user"."password" IS '密码 hash';
COMMENT ON COLUMN "flow"."user"."profile_image" IS '头像';
COMMENT ON COLUMN "flow"."user"."is_active" IS '是否启用';
COMMENT ON COLUMN "flow"."user"."is_superuser" IS '是否超级用户';
COMMENT ON COLUMN "flow"."user"."store_api_key" IS 'API Key 存储字段';
COMMENT ON COLUMN "flow"."user"."optins" IS '用户 opt-in 设置';
COMMENT ON COLUMN "flow"."user"."create_at" IS '创建时间';
COMMENT ON COLUMN "flow"."user"."updated_at" IS '更新时间';
COMMENT ON COLUMN "flow"."user"."last_login_at" IS '最近登录时间';

CREATE TABLE IF NOT EXISTS "flow"."variable" (
    "id" char(32) NOT NULL,
    "user_id" char(32),
    "name" varchar,
    "value" varchar,
    "type" varchar,
    "default_fields" jsonb,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."variable" IS 'Langflow 变量。';
COMMENT ON COLUMN "flow"."variable"."id" IS '变量 ID';
COMMENT ON COLUMN "flow"."variable"."user_id" IS '用户 ID';
COMMENT ON COLUMN "flow"."variable"."name" IS '变量名';
COMMENT ON COLUMN "flow"."variable"."value" IS '变量值';
COMMENT ON COLUMN "flow"."variable"."type" IS '变量类型';
COMMENT ON COLUMN "flow"."variable"."default_fields" IS '默认字段';
COMMENT ON COLUMN "flow"."variable"."created_at" IS '创建时间';
COMMENT ON COLUMN "flow"."variable"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "flow"."vertex_build" (
    "build_id" char(32) NOT NULL,
    "id" varchar,
    "flow_id" char(32),
    "job_id" char(32),
    "data" jsonb,
    "artifacts" jsonb,
    "params" text,
    "valid" boolean,
    "timestamp" timestamptz,
    PRIMARY KEY ("build_id")
);
COMMENT ON TABLE "flow"."vertex_build" IS 'Langflow 节点构建结果。';
COMMENT ON COLUMN "flow"."vertex_build"."build_id" IS '构建 ID';
COMMENT ON COLUMN "flow"."vertex_build"."id" IS '节点 ID';
COMMENT ON COLUMN "flow"."vertex_build"."flow_id" IS 'Flow ID';
COMMENT ON COLUMN "flow"."vertex_build"."job_id" IS 'Job ID';
COMMENT ON COLUMN "flow"."vertex_build"."data" IS '构建数据';
COMMENT ON COLUMN "flow"."vertex_build"."artifacts" IS '构建产物';
COMMENT ON COLUMN "flow"."vertex_build"."params" IS '参数';
COMMENT ON COLUMN "flow"."vertex_build"."valid" IS '是否有效';
COMMENT ON COLUMN "flow"."vertex_build"."timestamp" IS '时间戳';

CREATE TABLE IF NOT EXISTS "flow"."full_llm_cache" (
    "prompt" varchar NOT NULL,
    "llm" varchar NOT NULL,
    "idx" integer NOT NULL,
    "response" varchar,
    PRIMARY KEY ("prompt", "llm", "idx")
);
COMMENT ON TABLE "flow"."full_llm_cache" IS 'LangChain LLM 缓存。本地调试重复调用 LLM 时使用，可删除重建，不作为生产事实。';
COMMENT ON COLUMN "flow"."full_llm_cache"."prompt" IS '提示词内容';
COMMENT ON COLUMN "flow"."full_llm_cache"."llm" IS 'LLM 配置标识';
COMMENT ON COLUMN "flow"."full_llm_cache"."idx" IS '缓存响应序号';
COMMENT ON COLUMN "flow"."full_llm_cache"."response" IS '缓存响应内容';

CREATE TABLE IF NOT EXISTS "flow"."full_md5_llm_cache" (
    "id" varchar NOT NULL,
    "prompt_md5" varchar,
    "llm" varchar,
    "idx" integer,
    "prompt" varchar,
    "response" varchar,
    PRIMARY KEY ("id")
);
COMMENT ON TABLE "flow"."full_md5_llm_cache" IS 'LangChain LLM 缓存索引。本地调试按 MD5 查找缓存结果时使用，可删除重建，不作为生产事实。';
COMMENT ON COLUMN "flow"."full_md5_llm_cache"."id" IS '缓存记录 ID';
COMMENT ON COLUMN "flow"."full_md5_llm_cache"."prompt_md5" IS '提示词 MD5';
COMMENT ON COLUMN "flow"."full_md5_llm_cache"."llm" IS 'LLM 配置标识';
COMMENT ON COLUMN "flow"."full_md5_llm_cache"."idx" IS '缓存响应序号';
COMMENT ON COLUMN "flow"."full_md5_llm_cache"."prompt" IS '提示词内容';
COMMENT ON COLUMN "flow"."full_md5_llm_cache"."response" IS '缓存响应内容';

COMMIT;
