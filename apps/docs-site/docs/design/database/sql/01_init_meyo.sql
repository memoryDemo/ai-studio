-- Meyo PostgreSQL initialization script
-- Schema: meyo
-- Source: apps/docs-site/docs/design/database/01_inference_scene_runtime_db.md
-- This script creates Meyo-owned production truth tables and comments.

BEGIN;

CREATE SCHEMA IF NOT EXISTS "meyo";

CREATE TABLE IF NOT EXISTS "meyo"."tenants" (
    "tenant_id" uuid NOT NULL,
    "name" text NOT NULL,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("tenant_id")
);
COMMENT ON TABLE "meyo"."tenants" IS '租户主表，所有生产事实表必须通过 `tenant_id` 隔离。';
COMMENT ON COLUMN "meyo"."tenants"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."tenants"."name" IS '租户名称';
COMMENT ON COLUMN "meyo"."tenants"."status" IS '状态：active / suspended / deleted';
COMMENT ON COLUMN "meyo"."tenants"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."tenants"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."tenants"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."domains" (
    "domain_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "name" text NOT NULL,
    "description" text,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("domain_id")
);
COMMENT ON TABLE "meyo"."domains" IS '业务域主表。RAG、Agent、Skill、Run、Knowledge 都必须能追溯到 `domain_id`。';
COMMENT ON COLUMN "meyo"."domains"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."domains"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."domains"."name" IS '业务域名称';
COMMENT ON COLUMN "meyo"."domains"."description" IS '业务域描述';
COMMENT ON COLUMN "meyo"."domains"."status" IS 'active / archived / deleted';
COMMENT ON COLUMN "meyo"."domains"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."domains"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."domains"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."domains"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."users" (
    "user_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "display_name" text NOT NULL,
    "email" text,
    "phone" text,
    "avatar_uri" text,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("user_id")
);
COMMENT ON TABLE "meyo"."users" IS 'Meyo 统一用户主表。chatbot 和 flow 的用户都映射到这里。';
COMMENT ON COLUMN "meyo"."users"."user_id" IS '统一用户 ID';
COMMENT ON COLUMN "meyo"."users"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."users"."display_name" IS '展示名';
COMMENT ON COLUMN "meyo"."users"."email" IS '邮箱';
COMMENT ON COLUMN "meyo"."users"."phone" IS '手机号';
COMMENT ON COLUMN "meyo"."users"."avatar_uri" IS '头像 URI';
COMMENT ON COLUMN "meyo"."users"."status" IS '状态：active / disabled / deleted';
COMMENT ON COLUMN "meyo"."users"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."users"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."users"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."user_identities" (
    "identity_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "user_id" uuid NOT NULL,
    "provider" text NOT NULL,
    "external_ref" text NOT NULL,
    "email" text,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("identity_id")
);
COMMENT ON TABLE "meyo"."user_identities" IS '外部账号绑定表，用于绑定 Open WebUI、Langflow、SSO、OIDC 等外部身份。';
COMMENT ON COLUMN "meyo"."user_identities"."identity_id" IS '绑定记录 ID';
COMMENT ON COLUMN "meyo"."user_identities"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."user_identities"."user_id" IS '统一用户 ID';
COMMENT ON COLUMN "meyo"."user_identities"."provider" IS '来源：chatbot / flow / oidc / saml';
COMMENT ON COLUMN "meyo"."user_identities"."external_ref" IS '外部系统用户标识，非 UUID 不命名为 `*_id`';
COMMENT ON COLUMN "meyo"."user_identities"."email" IS '外部身份邮箱';
COMMENT ON COLUMN "meyo"."user_identities"."status" IS '状态：active / disabled';
COMMENT ON COLUMN "meyo"."user_identities"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."user_identities"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."user_identities"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."workspaces" (
    "workspace_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "name" text NOT NULL,
    "description" text,
    "owner_user_id" uuid NOT NULL,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("workspace_id")
);
COMMENT ON TABLE "meyo"."workspaces" IS '统一 workspace 主表，chatbot 和 flow 只通过 Meyo API 使用它。';
COMMENT ON COLUMN "meyo"."workspaces"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."workspaces"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."workspaces"."name" IS 'workspace 名称';
COMMENT ON COLUMN "meyo"."workspaces"."description" IS '描述';
COMMENT ON COLUMN "meyo"."workspaces"."owner_user_id" IS '所有人';
COMMENT ON COLUMN "meyo"."workspaces"."status" IS '状态：active / archived / deleted';
COMMENT ON COLUMN "meyo"."workspaces"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."workspaces"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."workspaces"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."workspace_members" (
    "workspace_member_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "user_id" uuid NOT NULL,
    "role" text NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("workspace_member_id")
);
COMMENT ON TABLE "meyo"."workspace_members" IS 'workspace 成员关系和角色。';
COMMENT ON COLUMN "meyo"."workspace_members"."workspace_member_id" IS '成员关系 ID';
COMMENT ON COLUMN "meyo"."workspace_members"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."workspace_members"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."workspace_members"."user_id" IS '用户 ID';
COMMENT ON COLUMN "meyo"."workspace_members"."role" IS '角色：owner / admin / member / viewer';
COMMENT ON COLUMN "meyo"."workspace_members"."status" IS '状态：active / removed';
COMMENT ON COLUMN "meyo"."workspace_members"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."workspace_members"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."files" (
    "file_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "uploaded_by_user_id" uuid NOT NULL,
    "filename" text NOT NULL,
    "content_type" text,
    "byte_size" bigint NOT NULL,
    "storage_uri" text NOT NULL,
    "sha256" text NOT NULL,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("file_id")
);
COMMENT ON TABLE "meyo"."files" IS '统一文件元数据表。文件 bytes 放对象存储，本表保存 URI、hash、归属和状态。';
COMMENT ON COLUMN "meyo"."files"."file_id" IS '文件 ID';
COMMENT ON COLUMN "meyo"."files"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."files"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."files"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."files"."uploaded_by_user_id" IS '上传用户';
COMMENT ON COLUMN "meyo"."files"."filename" IS '原始文件名';
COMMENT ON COLUMN "meyo"."files"."content_type" IS 'MIME 类型';
COMMENT ON COLUMN "meyo"."files"."byte_size" IS '文件大小';
COMMENT ON COLUMN "meyo"."files"."storage_uri" IS '对象存储 URI';
COMMENT ON COLUMN "meyo"."files"."sha256" IS '文件 SHA256';
COMMENT ON COLUMN "meyo"."files"."status" IS '状态：uploaded / processing / ready / deleted';
COMMENT ON COLUMN "meyo"."files"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."files"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."files"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."chat_threads" (
    "thread_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "user_id" uuid NOT NULL,
    "app_id" uuid,
    "title" text NOT NULL,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("thread_id")
);
COMMENT ON TABLE "meyo"."chat_threads" IS '统一聊天会话主表，chatbot 的历史会话读取这里。';
COMMENT ON COLUMN "meyo"."chat_threads"."thread_id" IS '会话 ID';
COMMENT ON COLUMN "meyo"."chat_threads"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."chat_threads"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."chat_threads"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."chat_threads"."user_id" IS '发起用户';
COMMENT ON COLUMN "meyo"."chat_threads"."app_id" IS '关联 App';
COMMENT ON COLUMN "meyo"."chat_threads"."title" IS '会话标题';
COMMENT ON COLUMN "meyo"."chat_threads"."status" IS '状态：active / archived / deleted';
COMMENT ON COLUMN "meyo"."chat_threads"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."chat_threads"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."chat_threads"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."chat_messages" (
    "message_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "thread_id" uuid NOT NULL,
    "user_id" uuid,
    "parent_message_id" uuid,
    "role" text NOT NULL,
    "content" jsonb NOT NULL,
    "status" text NOT NULL,
    "app_run_id" uuid,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("message_id")
);
COMMENT ON TABLE "meyo"."chat_messages" IS '统一聊天消息明细表。';
COMMENT ON COLUMN "meyo"."chat_messages"."message_id" IS '消息 ID';
COMMENT ON COLUMN "meyo"."chat_messages"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."chat_messages"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."chat_messages"."thread_id" IS '会话 ID';
COMMENT ON COLUMN "meyo"."chat_messages"."user_id" IS '用户 ID，assistant/system 消息可为空';
COMMENT ON COLUMN "meyo"."chat_messages"."parent_message_id" IS '父消息';
COMMENT ON COLUMN "meyo"."chat_messages"."role" IS 'user / assistant / system / tool';
COMMENT ON COLUMN "meyo"."chat_messages"."content" IS '消息内容';
COMMENT ON COLUMN "meyo"."chat_messages"."status" IS 'created / streaming / completed / failed / deleted';
COMMENT ON COLUMN "meyo"."chat_messages"."app_run_id" IS '关联运行记录';
COMMENT ON COLUMN "meyo"."chat_messages"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."chat_messages"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."chat_message_attachments" (
    "attachment_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "message_id" uuid NOT NULL,
    "file_id" uuid NOT NULL,
    "attachment_type" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("attachment_id")
);
COMMENT ON TABLE "meyo"."chat_message_attachments" IS '聊天消息和文件附件关联表。';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."attachment_id" IS '附件关系 ID';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."message_id" IS '消息 ID';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."file_id" IS '文件 ID';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."attachment_type" IS 'input_file / citation_file / generated_file';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."chat_message_attachments"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."data_source_profiles" (
    "data_source_profile_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "name" text NOT NULL,
    "source_type" text NOT NULL,
    "connection_config" jsonb NOT NULL,
    "secret_ref_id" uuid,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("data_source_profile_id")
);
COMMENT ON TABLE "meyo"."data_source_profiles" IS '数据源 profile。用于记录数据来自哪里、由哪个同步策略维护。';
COMMENT ON COLUMN "meyo"."data_source_profiles"."data_source_profile_id" IS '数据源 profile ID';
COMMENT ON COLUMN "meyo"."data_source_profiles"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."data_source_profiles"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."data_source_profiles"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."data_source_profiles"."name" IS '数据源名称';
COMMENT ON COLUMN "meyo"."data_source_profiles"."source_type" IS 'file / web / database / api / sharepoint / manual';
COMMENT ON COLUMN "meyo"."data_source_profiles"."connection_config" IS '脱敏连接配置';
COMMENT ON COLUMN "meyo"."data_source_profiles"."secret_ref_id" IS '密钥引用 ID';
COMMENT ON COLUMN "meyo"."data_source_profiles"."status" IS 'draft / active / paused / deleted';
COMMENT ON COLUMN "meyo"."data_source_profiles"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."data_source_profiles"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."data_source_profiles"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."secret_refs" (
    "secret_ref_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "secret_provider" text NOT NULL,
    "secret_external_ref" text NOT NULL,
    "purpose" text NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("secret_ref_id")
);
COMMENT ON TABLE "meyo"."secret_refs" IS '密钥引用表，只保存密钥系统引用，不保存真实密钥。';
COMMENT ON COLUMN "meyo"."secret_refs"."secret_ref_id" IS '密钥引用 ID';
COMMENT ON COLUMN "meyo"."secret_refs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."secret_refs"."secret_provider" IS 'vault / env / cloud_secret_manager';
COMMENT ON COLUMN "meyo"."secret_refs"."secret_external_ref" IS '外部密钥引用';
COMMENT ON COLUMN "meyo"."secret_refs"."purpose" IS '用途';
COMMENT ON COLUMN "meyo"."secret_refs"."status" IS 'active / revoked';
COMMENT ON COLUMN "meyo"."secret_refs"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."sync_policies" (
    "sync_policy_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "data_source_profile_id" uuid NOT NULL,
    "schedule" text,
    "mode" text NOT NULL,
    "filters" jsonb NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("sync_policy_id")
);
COMMENT ON TABLE "meyo"."sync_policies" IS '数据源同步策略表。';
COMMENT ON COLUMN "meyo"."sync_policies"."sync_policy_id" IS '同步策略 ID';
COMMENT ON COLUMN "meyo"."sync_policies"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."sync_policies"."data_source_profile_id" IS '数据源 profile ID';
COMMENT ON COLUMN "meyo"."sync_policies"."schedule" IS '同步计划';
COMMENT ON COLUMN "meyo"."sync_policies"."mode" IS 'manual / incremental / full';
COMMENT ON COLUMN "meyo"."sync_policies"."filters" IS '同步过滤条件';
COMMENT ON COLUMN "meyo"."sync_policies"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."sync_policies"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."ontology_profiles" (
    "ontology_profile_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "name" text NOT NULL,
    "description" text,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("ontology_profile_id")
);
COMMENT ON TABLE "meyo"."ontology_profiles" IS '本体 profile 主表。RAG 图谱查询和关系校验必须引用它。';
COMMENT ON COLUMN "meyo"."ontology_profiles"."ontology_profile_id" IS '本体 profile ID';
COMMENT ON COLUMN "meyo"."ontology_profiles"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."ontology_profiles"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."ontology_profiles"."name" IS '本体名称';
COMMENT ON COLUMN "meyo"."ontology_profiles"."description" IS '描述';
COMMENT ON COLUMN "meyo"."ontology_profiles"."status" IS 'draft / active / retired';
COMMENT ON COLUMN "meyo"."ontology_profiles"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."ontology_profiles"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."ontology_profiles"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."ontology_versions" (
    "ontology_version_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "ontology_profile_id" uuid NOT NULL,
    "version" integer NOT NULL,
    "schema" jsonb NOT NULL,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("ontology_version_id")
);
COMMENT ON TABLE "meyo"."ontology_versions" IS '本体版本表。';
COMMENT ON COLUMN "meyo"."ontology_versions"."ontology_version_id" IS '本体版本 ID';
COMMENT ON COLUMN "meyo"."ontology_versions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."ontology_versions"."ontology_profile_id" IS '本体 profile ID';
COMMENT ON COLUMN "meyo"."ontology_versions"."version" IS '版本号';
COMMENT ON COLUMN "meyo"."ontology_versions"."schema" IS '本体 schema';
COMMENT ON COLUMN "meyo"."ontology_versions"."status" IS 'draft / active / retired';
COMMENT ON COLUMN "meyo"."ontology_versions"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."ontology_versions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."ontology_entity_types" (
    "entity_type_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "ontology_version_id" uuid NOT NULL,
    "name" text NOT NULL,
    "properties_schema" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("entity_type_id")
);
COMMENT ON TABLE "meyo"."ontology_entity_types" IS '本体实体类型表。';
COMMENT ON COLUMN "meyo"."ontology_entity_types"."entity_type_id" IS '实体类型 ID';
COMMENT ON COLUMN "meyo"."ontology_entity_types"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."ontology_entity_types"."ontology_version_id" IS '本体版本 ID';
COMMENT ON COLUMN "meyo"."ontology_entity_types"."name" IS '实体类型名称';
COMMENT ON COLUMN "meyo"."ontology_entity_types"."properties_schema" IS '属性 schema';
COMMENT ON COLUMN "meyo"."ontology_entity_types"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."ontology_relation_types" (
    "relation_type_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "ontology_version_id" uuid NOT NULL,
    "name" text NOT NULL,
    "source_entity_type_id" uuid NOT NULL,
    "target_entity_type_id" uuid NOT NULL,
    "properties_schema" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("relation_type_id")
);
COMMENT ON TABLE "meyo"."ontology_relation_types" IS '本体关系类型表。';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."relation_type_id" IS '关系类型 ID';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."ontology_version_id" IS '本体版本 ID';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."name" IS '关系类型名称';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."source_entity_type_id" IS '起点实体类型';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."target_entity_type_id" IS '终点实体类型';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."properties_schema" IS '属性 schema';
COMMENT ON COLUMN "meyo"."ontology_relation_types"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."vector_collections" (
    "vector_collection_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "knowledge_base_id" uuid,
    "vector_provider" text NOT NULL,
    "collection_name" text NOT NULL,
    "embedding_model" text NOT NULL,
    "dimension" integer NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("vector_collection_id")
);
COMMENT ON TABLE "meyo"."vector_collections" IS '向量集合注册表。Milvus / Chroma 是向量事实源，本表保存集合归属、维度、模型和状态。';
COMMENT ON COLUMN "meyo"."vector_collections"."vector_collection_id" IS '向量集合 ID';
COMMENT ON COLUMN "meyo"."vector_collections"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."vector_collections"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."vector_collections"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."vector_collections"."vector_provider" IS 'milvus / chroma / pgvector';
COMMENT ON COLUMN "meyo"."vector_collections"."collection_name" IS '集合名';
COMMENT ON COLUMN "meyo"."vector_collections"."embedding_model" IS 'embedding 模型';
COMMENT ON COLUMN "meyo"."vector_collections"."dimension" IS '向量维度';
COMMENT ON COLUMN "meyo"."vector_collections"."status" IS 'building / active / retired / failed';
COMMENT ON COLUMN "meyo"."vector_collections"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."graph_profiles" (
    "graph_profile_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "graph_provider" text NOT NULL,
    "profile_name" text NOT NULL,
    "ontology_profile_id" uuid,
    "connection_config" jsonb NOT NULL,
    "secret_ref_id" uuid,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("graph_profile_id")
);
COMMENT ON TABLE "meyo"."graph_profiles" IS '图谱 profile 注册表。Neo4j / TuGraph 是图事实源，本表保存连接 profile、ontology 绑定和状态。';
COMMENT ON COLUMN "meyo"."graph_profiles"."graph_profile_id" IS '图谱 profile ID';
COMMENT ON COLUMN "meyo"."graph_profiles"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."graph_profiles"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."graph_profiles"."graph_provider" IS 'neo4j / tugraph';
COMMENT ON COLUMN "meyo"."graph_profiles"."profile_name" IS 'profile 名称';
COMMENT ON COLUMN "meyo"."graph_profiles"."ontology_profile_id" IS '本体 profile ID';
COMMENT ON COLUMN "meyo"."graph_profiles"."connection_config" IS '脱敏连接配置';
COMMENT ON COLUMN "meyo"."graph_profiles"."secret_ref_id" IS '密钥引用 ID';
COMMENT ON COLUMN "meyo"."graph_profiles"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."graph_profiles"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_bases" (
    "knowledge_base_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "data_source_profile_id" uuid,
    "ontology_profile_id" uuid,
    "name" text NOT NULL,
    "description" text,
    "owner_user_id" uuid NOT NULL,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("knowledge_base_id")
);
COMMENT ON TABLE "meyo"."knowledge_bases" IS '统一知识库主表。';
COMMENT ON COLUMN "meyo"."knowledge_bases"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_bases"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_bases"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."knowledge_bases"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."knowledge_bases"."data_source_profile_id" IS '默认数据源 profile';
COMMENT ON COLUMN "meyo"."knowledge_bases"."ontology_profile_id" IS '默认本体 profile';
COMMENT ON COLUMN "meyo"."knowledge_bases"."name" IS '知识库名称';
COMMENT ON COLUMN "meyo"."knowledge_bases"."description" IS '描述';
COMMENT ON COLUMN "meyo"."knowledge_bases"."owner_user_id" IS '所有人';
COMMENT ON COLUMN "meyo"."knowledge_bases"."status" IS 'draft / active / archived / deleted';
COMMENT ON COLUMN "meyo"."knowledge_bases"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."knowledge_bases"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."knowledge_bases"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_documents" (
    "document_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "knowledge_base_id" uuid NOT NULL,
    "file_id" uuid,
    "title" text NOT NULL,
    "source_uri" text,
    "content_sha256" text NOT NULL,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("document_id")
);
COMMENT ON TABLE "meyo"."knowledge_documents" IS '知识库文档主表。';
COMMENT ON COLUMN "meyo"."knowledge_documents"."document_id" IS '文档 ID';
COMMENT ON COLUMN "meyo"."knowledge_documents"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_documents"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."knowledge_documents"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_documents"."file_id" IS '来源文件 ID';
COMMENT ON COLUMN "meyo"."knowledge_documents"."title" IS '文档标题';
COMMENT ON COLUMN "meyo"."knowledge_documents"."source_uri" IS '来源 URI';
COMMENT ON COLUMN "meyo"."knowledge_documents"."content_sha256" IS '正文 hash';
COMMENT ON COLUMN "meyo"."knowledge_documents"."status" IS 'uploaded / parsed / indexed / failed / deleted';
COMMENT ON COLUMN "meyo"."knowledge_documents"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."knowledge_documents"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."knowledge_documents"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."knowledge_documents"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_chunks" (
    "chunk_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "document_id" uuid NOT NULL,
    "knowledge_base_id" uuid NOT NULL,
    "chunk_index" integer NOT NULL,
    "content" text NOT NULL,
    "content_sha256" text NOT NULL,
    "token_count" integer,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("chunk_id")
);
COMMENT ON TABLE "meyo"."knowledge_chunks" IS '文档切片表，Milvus / Chroma 只保存向量，正文以本表为准。';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."chunk_id" IS '切片 ID';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."document_id" IS '文档 ID';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."chunk_index" IS '文档内切片序号';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."content" IS '切片正文';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."content_sha256" IS '切片 hash';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."token_count" IS 'token 数';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."metadata" IS '页码、段落、标题等信息';
COMMENT ON COLUMN "meyo"."knowledge_chunks"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_versions" (
    "knowledge_version_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "knowledge_base_id" uuid NOT NULL,
    "publish_batch_id" uuid,
    "version" integer NOT NULL,
    "status" text NOT NULL,
    "document_count" integer NOT NULL,
    "chunk_count" integer NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "activated_at" timestamptz,
    PRIMARY KEY ("knowledge_version_id")
);
COMMENT ON TABLE "meyo"."knowledge_versions" IS '知识库版本表，用于发布、回滚和审计。';
COMMENT ON COLUMN "meyo"."knowledge_versions"."knowledge_version_id" IS '知识版本 ID';
COMMENT ON COLUMN "meyo"."knowledge_versions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_versions"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_versions"."publish_batch_id" IS '所属发布批次';
COMMENT ON COLUMN "meyo"."knowledge_versions"."version" IS '版本号';
COMMENT ON COLUMN "meyo"."knowledge_versions"."status" IS 'draft / indexing / active / retired';
COMMENT ON COLUMN "meyo"."knowledge_versions"."document_count" IS '文档数';
COMMENT ON COLUMN "meyo"."knowledge_versions"."chunk_count" IS '切片数';
COMMENT ON COLUMN "meyo"."knowledge_versions"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."knowledge_versions"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."knowledge_versions"."activated_at" IS '激活时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_publish_batches" (
    "publish_batch_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "knowledge_base_id" uuid NOT NULL,
    "knowledge_version_id" uuid NOT NULL,
    "status" text NOT NULL,
    "activated_at" timestamptz,
    "retired_at" timestamptz,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("publish_batch_id")
);
COMMENT ON TABLE "meyo"."knowledge_publish_batches" IS '知识发布批次表。RAG 运行时 QA05 查询的 active batch 来自这里。';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."publish_batch_id" IS '发布批次 ID';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."knowledge_version_id" IS '知识版本 ID';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."status" IS 'draft / indexing / approved / active / retired / failed';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."activated_at" IS '激活时间';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."retired_at" IS '退役时间';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."knowledge_publish_batches"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_index_jobs" (
    "index_job_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "publish_batch_id" uuid NOT NULL,
    "job_type" text NOT NULL,
    "status" text NOT NULL,
    "input_ref" jsonb NOT NULL,
    "output_ref" jsonb,
    "error" jsonb,
    "started_at" timestamptz,
    "finished_at" timestamptz,
    PRIMARY KEY ("index_job_id")
);
COMMENT ON TABLE "meyo"."knowledge_index_jobs" IS '知识索引任务表，记录解析、切片、向量索引、图谱写入等任务。';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."index_job_id" IS '索引任务 ID';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."publish_batch_id" IS '发布批次 ID';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."job_type" IS 'parse / chunk / embed / graph / fulltext';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."status" IS 'queued / running / succeeded / failed';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."input_ref" IS '输入引用';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."output_ref" IS '输出引用';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."error" IS '错误信息';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."started_at" IS '开始时间';
COMMENT ON COLUMN "meyo"."knowledge_index_jobs"."finished_at" IS '结束时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_permissions" (
    "permission_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "knowledge_base_id" uuid NOT NULL,
    "principal_type" text NOT NULL,
    "principal_id" uuid NOT NULL,
    "permission" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("permission_id")
);
COMMENT ON TABLE "meyo"."knowledge_permissions" IS '知识库访问控制表。';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."permission_id" IS '权限记录 ID';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."principal_type" IS 'user / workspace / role / scene';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."principal_id" IS '主体 ID';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."permission" IS 'read / write / admin';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."knowledge_permissions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_vector_refs" (
    "vector_ref_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "knowledge_base_id" uuid NOT NULL,
    "document_id" uuid NOT NULL,
    "chunk_id" uuid NOT NULL,
    "vector_provider" text NOT NULL,
    "collection_name" text NOT NULL,
    "vector_external_ref" text NOT NULL,
    "embedding_model" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("vector_ref_id")
);
COMMENT ON TABLE "meyo"."knowledge_vector_refs" IS '知识切片到向量库记录的引用表。';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."vector_ref_id" IS '向量引用 ID';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."document_id" IS '文档 ID';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."chunk_id" IS '切片 ID';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."vector_provider" IS 'milvus / chroma / pgvector';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."collection_name" IS '向量集合名';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."vector_external_ref" IS '向量库返回的外部标识';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."embedding_model" IS 'embedding 模型';
COMMENT ON COLUMN "meyo"."knowledge_vector_refs"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."knowledge_graph_refs" (
    "graph_ref_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "knowledge_base_id" uuid NOT NULL,
    "document_id" uuid NOT NULL,
    "chunk_id" uuid,
    "graph_provider" text NOT NULL,
    "graph_profile" text NOT NULL,
    "entity_external_ref" text,
    "relation_external_ref" text,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("graph_ref_id")
);
COMMENT ON TABLE "meyo"."knowledge_graph_refs" IS '知识文档或切片到图数据库实体/关系的引用表。';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."graph_ref_id" IS '图谱引用 ID';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."document_id" IS '文档 ID';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."chunk_id" IS '切片 ID';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."graph_provider" IS 'neo4j / tugraph';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."graph_profile" IS '图谱 profile';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."entity_external_ref" IS '图数据库实体外部标识';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."relation_external_ref" IS '图数据库关系外部标识';
COMMENT ON COLUMN "meyo"."knowledge_graph_refs"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."model_profiles" (
    "model_profile_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "provider" text NOT NULL,
    "model_name" text NOT NULL,
    "purpose" text NOT NULL,
    "params" jsonb NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("model_profile_id")
);
COMMENT ON TABLE "meyo"."model_profiles" IS '模型 profile 表。Scene 模型绑定必须引用已注册模型 profile 或明确记录 provider / model。';
COMMENT ON COLUMN "meyo"."model_profiles"."model_profile_id" IS '模型 profile ID';
COMMENT ON COLUMN "meyo"."model_profiles"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."model_profiles"."provider" IS '模型供应商';
COMMENT ON COLUMN "meyo"."model_profiles"."model_name" IS '模型名称';
COMMENT ON COLUMN "meyo"."model_profiles"."purpose" IS 'router / answer / rewrite / eval / embedding';
COMMENT ON COLUMN "meyo"."model_profiles"."params" IS '默认参数';
COMMENT ON COLUMN "meyo"."model_profiles"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."model_profiles"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."policy_profiles" (
    "policy_profile_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "name" text NOT NULL,
    "policy_type" text NOT NULL,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("policy_profile_id")
);
COMMENT ON TABLE "meyo"."policy_profiles" IS '策略 profile 主表。输入安全、输出安全、ACL、工具审批都从这里解析。';
COMMENT ON COLUMN "meyo"."policy_profiles"."policy_profile_id" IS '策略 profile ID';
COMMENT ON COLUMN "meyo"."policy_profiles"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."policy_profiles"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."policy_profiles"."name" IS '策略名称';
COMMENT ON COLUMN "meyo"."policy_profiles"."policy_type" IS 'input_guard / output_guard / acl / tool_approval / publish';
COMMENT ON COLUMN "meyo"."policy_profiles"."status" IS 'draft / active / retired';
COMMENT ON COLUMN "meyo"."policy_profiles"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."policy_profiles"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."policy_profiles"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."policy_rules" (
    "policy_rule_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "policy_profile_id" uuid NOT NULL,
    "rule_code" text NOT NULL,
    "condition" jsonb NOT NULL,
    "action" text NOT NULL,
    "priority" integer NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("policy_rule_id")
);
COMMENT ON TABLE "meyo"."policy_rules" IS '策略规则表。';
COMMENT ON COLUMN "meyo"."policy_rules"."policy_rule_id" IS '策略规则 ID';
COMMENT ON COLUMN "meyo"."policy_rules"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."policy_rules"."policy_profile_id" IS '策略 profile ID';
COMMENT ON COLUMN "meyo"."policy_rules"."rule_code" IS '规则编号';
COMMENT ON COLUMN "meyo"."policy_rules"."condition" IS '触发条件';
COMMENT ON COLUMN "meyo"."policy_rules"."action" IS 'allow / deny / require_approval / redact';
COMMENT ON COLUMN "meyo"."policy_rules"."priority" IS '优先级';
COMMENT ON COLUMN "meyo"."policy_rules"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."policy_rules"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."policy_decisions" (
    "policy_decision_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid,
    "app_run_id" uuid,
    "flow_run_id" uuid,
    "policy_profile_id" uuid NOT NULL,
    "node_code" text NOT NULL,
    "subject_user_id" uuid,
    "resource_ref" jsonb NOT NULL,
    "decision" text NOT NULL,
    "reason" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("policy_decision_id")
);
COMMENT ON TABLE "meyo"."policy_decisions" IS '策略裁决记录表。FW03、FW11、FW17、QA03、QA14、QA21 都必须写裁决结果。';
COMMENT ON COLUMN "meyo"."policy_decisions"."policy_decision_id" IS '策略裁决 ID';
COMMENT ON COLUMN "meyo"."policy_decisions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."policy_decisions"."run_id" IS 'Run ID';
COMMENT ON COLUMN "meyo"."policy_decisions"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."policy_decisions"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."policy_decisions"."policy_profile_id" IS '策略 profile ID';
COMMENT ON COLUMN "meyo"."policy_decisions"."node_code" IS '触发节点编号';
COMMENT ON COLUMN "meyo"."policy_decisions"."subject_user_id" IS '被裁决用户';
COMMENT ON COLUMN "meyo"."policy_decisions"."resource_ref" IS '被裁决资源引用';
COMMENT ON COLUMN "meyo"."policy_decisions"."decision" IS 'allow / deny / require_approval / redact';
COMMENT ON COLUMN "meyo"."policy_decisions"."reason" IS '裁决原因';
COMMENT ON COLUMN "meyo"."policy_decisions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."capability_registry" (
    "capability_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "name" text NOT NULL,
    "capability_type" text NOT NULL,
    "description" text,
    "owner_user_id" uuid NOT NULL,
    "status" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("capability_id")
);
COMMENT ON TABLE "meyo"."capability_registry" IS 'Skill / Tool / Prompt 的统一注册主表。';
COMMENT ON COLUMN "meyo"."capability_registry"."capability_id" IS '能力 ID';
COMMENT ON COLUMN "meyo"."capability_registry"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."capability_registry"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."capability_registry"."name" IS '能力名称';
COMMENT ON COLUMN "meyo"."capability_registry"."capability_type" IS 'skill / tool / prompt';
COMMENT ON COLUMN "meyo"."capability_registry"."description" IS '描述';
COMMENT ON COLUMN "meyo"."capability_registry"."owner_user_id" IS '所有人';
COMMENT ON COLUMN "meyo"."capability_registry"."status" IS 'draft / active / retired';
COMMENT ON COLUMN "meyo"."capability_registry"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."capability_registry"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."capability_registry"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."capability_versions" (
    "capability_version_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "capability_id" uuid NOT NULL,
    "version" integer NOT NULL,
    "content" jsonb NOT NULL,
    "input_schema" jsonb,
    "output_schema" jsonb,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("capability_version_id")
);
COMMENT ON TABLE "meyo"."capability_versions" IS '能力版本表，保存内容、参数和发布状态。';
COMMENT ON COLUMN "meyo"."capability_versions"."capability_version_id" IS '能力版本 ID';
COMMENT ON COLUMN "meyo"."capability_versions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."capability_versions"."capability_id" IS '能力 ID';
COMMENT ON COLUMN "meyo"."capability_versions"."version" IS '版本号';
COMMENT ON COLUMN "meyo"."capability_versions"."content" IS '能力内容';
COMMENT ON COLUMN "meyo"."capability_versions"."input_schema" IS '输入契约';
COMMENT ON COLUMN "meyo"."capability_versions"."output_schema" IS '输出契约';
COMMENT ON COLUMN "meyo"."capability_versions"."status" IS 'draft / testing / approved / active / retired';
COMMENT ON COLUMN "meyo"."capability_versions"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."capability_versions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."capability_permissions" (
    "permission_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "capability_id" uuid NOT NULL,
    "principal_type" text NOT NULL,
    "principal_id" uuid NOT NULL,
    "permission" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("permission_id")
);
COMMENT ON TABLE "meyo"."capability_permissions" IS '能力访问控制表。';
COMMENT ON COLUMN "meyo"."capability_permissions"."permission_id" IS '权限记录 ID';
COMMENT ON COLUMN "meyo"."capability_permissions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."capability_permissions"."capability_id" IS '能力 ID';
COMMENT ON COLUMN "meyo"."capability_permissions"."principal_type" IS 'user / workspace / role / scene';
COMMENT ON COLUMN "meyo"."capability_permissions"."principal_id" IS '主体 ID';
COMMENT ON COLUMN "meyo"."capability_permissions"."permission" IS 'read / execute / write / admin';
COMMENT ON COLUMN "meyo"."capability_permissions"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."capability_permissions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."app_registry" (
    "app_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "name" text NOT NULL,
    "description" text,
    "status" text NOT NULL,
    "default_router_version_id" uuid,
    "policy_profile_id" uuid,
    "metadata" jsonb NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("app_id")
);
COMMENT ON TABLE "meyo"."app_registry" IS '可运行 App 注册表。';
COMMENT ON COLUMN "meyo"."app_registry"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."app_registry"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."app_registry"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."app_registry"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."app_registry"."name" IS 'App 名称';
COMMENT ON COLUMN "meyo"."app_registry"."description" IS '描述';
COMMENT ON COLUMN "meyo"."app_registry"."status" IS 'draft / active / paused / retired';
COMMENT ON COLUMN "meyo"."app_registry"."default_router_version_id" IS '默认 Router Workflow 版本';
COMMENT ON COLUMN "meyo"."app_registry"."policy_profile_id" IS '默认策略 profile';
COMMENT ON COLUMN "meyo"."app_registry"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."app_registry"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."app_registry"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."app_registry"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_registry" (
    "scene_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "app_id" uuid NOT NULL,
    "name" text NOT NULL,
    "description" text NOT NULL,
    "intent_description" text NOT NULL,
    "input_schema_ref" text NOT NULL,
    "output_schema_ref" text NOT NULL,
    "policy_profile_id" uuid,
    "status" text NOT NULL,
    "version" integer NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    "updated_at" timestamptz NOT NULL,
    PRIMARY KEY ("scene_id")
);
COMMENT ON TABLE "meyo"."scene_registry" IS '业务 Scene 注册表，Router 只能选择 active Scene。';
COMMENT ON COLUMN "meyo"."scene_registry"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_registry"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_registry"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."scene_registry"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."scene_registry"."name" IS 'Scene 名称';
COMMENT ON COLUMN "meyo"."scene_registry"."description" IS '业务说明';
COMMENT ON COLUMN "meyo"."scene_registry"."intent_description" IS 'Router 可读意图说明';
COMMENT ON COLUMN "meyo"."scene_registry"."input_schema_ref" IS '输入 schema 引用';
COMMENT ON COLUMN "meyo"."scene_registry"."output_schema_ref" IS '输出 schema 引用';
COMMENT ON COLUMN "meyo"."scene_registry"."policy_profile_id" IS '默认策略 profile';
COMMENT ON COLUMN "meyo"."scene_registry"."status" IS 'draft / testing / approved / active / paused / retired';
COMMENT ON COLUMN "meyo"."scene_registry"."version" IS '元数据版本';
COMMENT ON COLUMN "meyo"."scene_registry"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."scene_registry"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."scene_registry"."updated_at" IS '更新时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_route_examples" (
    "example_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "app_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "text" text NOT NULL,
    "label" text NOT NULL,
    "reason" text NOT NULL,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("example_id")
);
COMMENT ON TABLE "meyo"."scene_route_examples" IS 'Scene 路由样例表。';
COMMENT ON COLUMN "meyo"."scene_route_examples"."example_id" IS '样例 ID';
COMMENT ON COLUMN "meyo"."scene_route_examples"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_route_examples"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."scene_route_examples"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_route_examples"."text" IS '用户输入样例';
COMMENT ON COLUMN "meyo"."scene_route_examples"."label" IS 'positive / negative';
COMMENT ON COLUMN "meyo"."scene_route_examples"."reason" IS '命中或排除原因';
COMMENT ON COLUMN "meyo"."scene_route_examples"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."scene_route_examples"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."scene_route_examples"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_workflow_specs" (
    "workflow_spec_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "app_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "nodes" jsonb NOT NULL,
    "edges" jsonb NOT NULL,
    "input_contract" jsonb NOT NULL,
    "output_contract" jsonb NOT NULL,
    "failure_policy" jsonb NOT NULL,
    "status" text NOT NULL,
    "schema_version" integer NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("workflow_spec_id")
);
COMMENT ON TABLE "meyo"."scene_workflow_specs" IS 'Scene Workflow 显式节点契约表。';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."workflow_spec_id" IS 'Workflow Spec ID';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."nodes" IS '显式节点列表';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."edges" IS '显式边列表';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."input_contract" IS '输入契约';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."output_contract" IS '输出契约';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."failure_policy" IS '失败策略';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."status" IS 'draft / validated / retired';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."schema_version" IS '契约版本';
COMMENT ON COLUMN "meyo"."scene_workflow_specs"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_knowledge_bindings" (
    "binding_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "workflow_spec_id" uuid,
    "knowledge_base_id" uuid NOT NULL,
    "knowledge_version_id" uuid,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("binding_id")
);
COMMENT ON TABLE "meyo"."scene_knowledge_bindings" IS 'Scene 和知识库或知识版本的绑定表。';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."binding_id" IS '绑定 ID';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."workflow_spec_id" IS 'Scene Workflow Spec ID';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."knowledge_base_id" IS '知识库 ID';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."knowledge_version_id" IS '指定知识版本';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."scene_knowledge_bindings"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_vector_bindings" (
    "binding_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "vector_collection_id" uuid NOT NULL,
    "vector_provider" text NOT NULL,
    "collection_name" text NOT NULL,
    "embedding_model" text NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("binding_id")
);
COMMENT ON TABLE "meyo"."scene_vector_bindings" IS 'Scene 和向量集合的绑定表。';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."binding_id" IS '绑定 ID';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."vector_collection_id" IS '向量集合 ID';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."vector_provider" IS 'milvus / chroma / pgvector';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."collection_name" IS '向量集合名';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."embedding_model" IS 'embedding 模型';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."scene_vector_bindings"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_graph_bindings" (
    "binding_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "graph_profile_id" uuid NOT NULL,
    "ontology_profile_id" uuid,
    "graph_provider" text NOT NULL,
    "graph_profile" text NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("binding_id")
);
COMMENT ON TABLE "meyo"."scene_graph_bindings" IS 'Scene 和图谱 profile 的绑定表。';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."binding_id" IS '绑定 ID';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."graph_profile_id" IS '图谱 profile ID';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."ontology_profile_id" IS '本体 profile ID';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."graph_provider" IS 'neo4j / tugraph';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."graph_profile" IS '图谱 profile';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."scene_graph_bindings"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_tool_bindings" (
    "binding_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "capability_id" uuid NOT NULL,
    "capability_version_id" uuid,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("binding_id")
);
COMMENT ON TABLE "meyo"."scene_tool_bindings" IS 'Scene 和 Tool / Skill 能力的绑定表。';
COMMENT ON COLUMN "meyo"."scene_tool_bindings"."binding_id" IS '绑定 ID';
COMMENT ON COLUMN "meyo"."scene_tool_bindings"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_tool_bindings"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_tool_bindings"."capability_id" IS '能力 ID';
COMMENT ON COLUMN "meyo"."scene_tool_bindings"."capability_version_id" IS '能力版本 ID';
COMMENT ON COLUMN "meyo"."scene_tool_bindings"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."scene_tool_bindings"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_model_bindings" (
    "binding_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "model_profile_id" uuid,
    "model_provider" text NOT NULL,
    "model_name" text NOT NULL,
    "purpose" text NOT NULL,
    "params" jsonb NOT NULL,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("binding_id")
);
COMMENT ON TABLE "meyo"."scene_model_bindings" IS 'Scene 和模型的绑定表。';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."binding_id" IS '绑定 ID';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."model_profile_id" IS '模型 profile ID';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."model_provider" IS '模型供应商';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."model_name" IS '模型名称';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."purpose" IS 'router / answer / rewrite / eval';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."params" IS '模型参数';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."status" IS 'active / disabled';
COMMENT ON COLUMN "meyo"."scene_model_bindings"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."router_versions" (
    "router_version_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "app_id" uuid NOT NULL,
    "version" integer NOT NULL,
    "artifact_uri" text NOT NULL,
    "artifact_sha256" text NOT NULL,
    "eval_run_id" uuid,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("router_version_id")
);
COMMENT ON TABLE "meyo"."router_versions" IS 'Router Workflow 版本表。Router 版本是生产事实，不能由 chatbot 或 prompt 隐式决定。';
COMMENT ON COLUMN "meyo"."router_versions"."router_version_id" IS 'Router 版本 ID';
COMMENT ON COLUMN "meyo"."router_versions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."router_versions"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."router_versions"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."router_versions"."version" IS '版本号';
COMMENT ON COLUMN "meyo"."router_versions"."artifact_uri" IS 'Router workflow artifact URI';
COMMENT ON COLUMN "meyo"."router_versions"."artifact_sha256" IS 'Router artifact hash';
COMMENT ON COLUMN "meyo"."router_versions"."eval_run_id" IS '评测运行 ID';
COMMENT ON COLUMN "meyo"."router_versions"."status" IS 'draft / testing / approved / active / retired';
COMMENT ON COLUMN "meyo"."router_versions"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."router_versions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."flow_templates" (
    "flow_template_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "name" text NOT NULL,
    "description" text,
    "template_type" text NOT NULL,
    "metadata" jsonb NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("flow_template_id")
);
COMMENT ON TABLE "meyo"."flow_templates" IS 'Flow 模板元数据表。';
COMMENT ON COLUMN "meyo"."flow_templates"."flow_template_id" IS 'Flow 模板 ID';
COMMENT ON COLUMN "meyo"."flow_templates"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."flow_templates"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."flow_templates"."name" IS '模板名称';
COMMENT ON COLUMN "meyo"."flow_templates"."description" IS '描述';
COMMENT ON COLUMN "meyo"."flow_templates"."template_type" IS 'rag / router / tool / custom';
COMMENT ON COLUMN "meyo"."flow_templates"."metadata" IS '扩展信息';
COMMENT ON COLUMN "meyo"."flow_templates"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."flow_templates"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."flow_versions" (
    "flow_version_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "flow_template_id" uuid,
    "studio_flow_external_ref" text,
    "version" integer NOT NULL,
    "artifact_uri" text NOT NULL,
    "artifact_sha256" text NOT NULL,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("flow_version_id")
);
COMMENT ON TABLE "meyo"."flow_versions" IS '可发布 Flow 版本表。';
COMMENT ON COLUMN "meyo"."flow_versions"."flow_version_id" IS 'Flow 版本 ID';
COMMENT ON COLUMN "meyo"."flow_versions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."flow_versions"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."flow_versions"."flow_template_id" IS 'Flow 模板 ID';
COMMENT ON COLUMN "meyo"."flow_versions"."studio_flow_external_ref" IS 'studio-flow 外部 Flow 标识';
COMMENT ON COLUMN "meyo"."flow_versions"."version" IS '版本号';
COMMENT ON COLUMN "meyo"."flow_versions"."artifact_uri" IS 'Flow artifact URI';
COMMENT ON COLUMN "meyo"."flow_versions"."artifact_sha256" IS 'Flow artifact hash';
COMMENT ON COLUMN "meyo"."flow_versions"."status" IS 'draft / testing / approved / active / retired';
COMMENT ON COLUMN "meyo"."flow_versions"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."flow_versions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."app_scene_flow_bindings" (
    "binding_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "app_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "flow_version_id" uuid NOT NULL,
    "status" text NOT NULL,
    "approval_id" uuid,
    "effective_from" timestamptz,
    "effective_to" timestamptz,
    "activated_at" timestamptz,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("binding_id")
);
COMMENT ON TABLE "meyo"."app_scene_flow_bindings" IS 'App + Scene + Flow 的生产绑定表。';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."binding_id" IS '绑定 ID';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."flow_version_id" IS 'Flow 版本 ID';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."status" IS 'draft / testing / approved / active / retired';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."approval_id" IS '发布审批 ID';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."effective_from" IS '生效时间';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."effective_to" IS '失效时间';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."activated_at" IS '激活时间';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."app_scene_flow_bindings"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_eval_case_sets" (
    "case_set_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "name" text NOT NULL,
    "status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("case_set_id")
);
COMMENT ON TABLE "meyo"."scene_eval_case_sets" IS 'Scene 评测集主表。';
COMMENT ON COLUMN "meyo"."scene_eval_case_sets"."case_set_id" IS '评测集 ID';
COMMENT ON COLUMN "meyo"."scene_eval_case_sets"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_eval_case_sets"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_eval_case_sets"."name" IS '评测集名称';
COMMENT ON COLUMN "meyo"."scene_eval_case_sets"."status" IS 'draft / active / archived';
COMMENT ON COLUMN "meyo"."scene_eval_case_sets"."created_by_user_id" IS '创建人';
COMMENT ON COLUMN "meyo"."scene_eval_case_sets"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_eval_cases" (
    "case_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "case_set_id" uuid NOT NULL,
    "input" jsonb NOT NULL,
    "expected_output" jsonb,
    "assertions" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("case_id")
);
COMMENT ON TABLE "meyo"."scene_eval_cases" IS 'Scene 评测用例表。';
COMMENT ON COLUMN "meyo"."scene_eval_cases"."case_id" IS '用例 ID';
COMMENT ON COLUMN "meyo"."scene_eval_cases"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_eval_cases"."case_set_id" IS '评测集 ID';
COMMENT ON COLUMN "meyo"."scene_eval_cases"."input" IS '输入';
COMMENT ON COLUMN "meyo"."scene_eval_cases"."expected_output" IS '期望输出';
COMMENT ON COLUMN "meyo"."scene_eval_cases"."assertions" IS '断言规则';
COMMENT ON COLUMN "meyo"."scene_eval_cases"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_eval_runs" (
    "eval_run_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "case_set_id" uuid NOT NULL,
    "flow_version_id" uuid NOT NULL,
    "status" text NOT NULL,
    "started_at" timestamptz NOT NULL,
    "finished_at" timestamptz,
    PRIMARY KEY ("eval_run_id")
);
COMMENT ON TABLE "meyo"."scene_eval_runs" IS 'Scene 评测执行记录表。';
COMMENT ON COLUMN "meyo"."scene_eval_runs"."eval_run_id" IS '评测运行 ID';
COMMENT ON COLUMN "meyo"."scene_eval_runs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_eval_runs"."case_set_id" IS '评测集 ID';
COMMENT ON COLUMN "meyo"."scene_eval_runs"."flow_version_id" IS 'Flow 版本 ID';
COMMENT ON COLUMN "meyo"."scene_eval_runs"."status" IS 'running / succeeded / failed';
COMMENT ON COLUMN "meyo"."scene_eval_runs"."started_at" IS '开始时间';
COMMENT ON COLUMN "meyo"."scene_eval_runs"."finished_at" IS '结束时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_eval_results" (
    "eval_result_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "eval_run_id" uuid NOT NULL,
    "case_id" uuid NOT NULL,
    "passed" boolean NOT NULL,
    "score" numeric,
    "details" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("eval_result_id")
);
COMMENT ON TABLE "meyo"."scene_eval_results" IS 'Scene 评测结果明细表。';
COMMENT ON COLUMN "meyo"."scene_eval_results"."eval_result_id" IS '评测结果 ID';
COMMENT ON COLUMN "meyo"."scene_eval_results"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_eval_results"."eval_run_id" IS '评测运行 ID';
COMMENT ON COLUMN "meyo"."scene_eval_results"."case_id" IS '用例 ID';
COMMENT ON COLUMN "meyo"."scene_eval_results"."passed" IS '是否通过';
COMMENT ON COLUMN "meyo"."scene_eval_results"."score" IS '评分';
COMMENT ON COLUMN "meyo"."scene_eval_results"."details" IS '结果详情';
COMMENT ON COLUMN "meyo"."scene_eval_results"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_approvals" (
    "approval_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "target_type" text NOT NULL,
    "target_id" uuid NOT NULL,
    "decision" text NOT NULL,
    "comment" text,
    "approved_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("approval_id")
);
COMMENT ON TABLE "meyo"."scene_approvals" IS 'Scene / Flow 发布审批表。';
COMMENT ON COLUMN "meyo"."scene_approvals"."approval_id" IS '审批 ID';
COMMENT ON COLUMN "meyo"."scene_approvals"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_approvals"."target_type" IS 'scene / flow_binding / knowledge_version';
COMMENT ON COLUMN "meyo"."scene_approvals"."target_id" IS '审批对象 ID';
COMMENT ON COLUMN "meyo"."scene_approvals"."decision" IS 'approved / rejected';
COMMENT ON COLUMN "meyo"."scene_approvals"."comment" IS '审批意见';
COMMENT ON COLUMN "meyo"."scene_approvals"."approved_by_user_id" IS '审批人';
COMMENT ON COLUMN "meyo"."scene_approvals"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_activation_history" (
    "history_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "binding_id" uuid NOT NULL,
    "action" text NOT NULL,
    "from_status" text,
    "to_status" text NOT NULL,
    "created_by_user_id" uuid NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("history_id")
);
COMMENT ON TABLE "meyo"."scene_activation_history" IS 'Scene / Flow 绑定的激活、暂停、回滚、退役历史。';
COMMENT ON COLUMN "meyo"."scene_activation_history"."history_id" IS '历史记录 ID';
COMMENT ON COLUMN "meyo"."scene_activation_history"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_activation_history"."binding_id" IS 'App Scene Flow 绑定 ID';
COMMENT ON COLUMN "meyo"."scene_activation_history"."action" IS 'activate / pause / rollback / retire';
COMMENT ON COLUMN "meyo"."scene_activation_history"."from_status" IS '变更前状态';
COMMENT ON COLUMN "meyo"."scene_activation_history"."to_status" IS '变更后状态';
COMMENT ON COLUMN "meyo"."scene_activation_history"."created_by_user_id" IS '操作人';
COMMENT ON COLUMN "meyo"."scene_activation_history"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."approval_requests" (
    "approval_request_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "flow_run_id" uuid,
    "request_type" text NOT NULL,
    "target_ref" jsonb NOT NULL,
    "status" text NOT NULL,
    "requested_by_node_code" text NOT NULL,
    "requested_by_user_id" uuid,
    "created_at" timestamptz NOT NULL,
    "expires_at" timestamptz,
    PRIMARY KEY ("approval_request_id")
);
COMMENT ON TABLE "meyo"."approval_requests" IS '运行时人工审批请求表。FW11 或 R18 进入 waiting_approval 时写入。';
COMMENT ON COLUMN "meyo"."approval_requests"."approval_request_id" IS '审批请求 ID';
COMMENT ON COLUMN "meyo"."approval_requests"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."approval_requests"."run_id" IS 'Run ID';
COMMENT ON COLUMN "meyo"."approval_requests"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."approval_requests"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."approval_requests"."request_type" IS 'tool_call / policy_exception / high_risk_answer / publish';
COMMENT ON COLUMN "meyo"."approval_requests"."target_ref" IS '审批对象引用';
COMMENT ON COLUMN "meyo"."approval_requests"."status" IS 'pending / approved / rejected / expired / cancelled';
COMMENT ON COLUMN "meyo"."approval_requests"."requested_by_node_code" IS '触发审批的节点编号';
COMMENT ON COLUMN "meyo"."approval_requests"."requested_by_user_id" IS '发起用户';
COMMENT ON COLUMN "meyo"."approval_requests"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."approval_requests"."expires_at" IS '过期时间';

CREATE TABLE IF NOT EXISTS "meyo"."approval_events" (
    "approval_event_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "approval_request_id" uuid NOT NULL,
    "event_type" text NOT NULL,
    "actor_user_id" uuid,
    "comment" text,
    "payload" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("approval_event_id")
);
COMMENT ON TABLE "meyo"."approval_events" IS '运行时审批事件表。';
COMMENT ON COLUMN "meyo"."approval_events"."approval_event_id" IS '审批事件 ID';
COMMENT ON COLUMN "meyo"."approval_events"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."approval_events"."approval_request_id" IS '审批请求 ID';
COMMENT ON COLUMN "meyo"."approval_events"."event_type" IS 'requested / approved / rejected / expired / cancelled';
COMMENT ON COLUMN "meyo"."approval_events"."actor_user_id" IS '操作用户';
COMMENT ON COLUMN "meyo"."approval_events"."comment" IS '说明';
COMMENT ON COLUMN "meyo"."approval_events"."payload" IS '事件载荷';
COMMENT ON COLUMN "meyo"."approval_events"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."app_runs" (
    "app_run_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "request_id" uuid NOT NULL,
    "trace_id" uuid NOT NULL,
    "workspace_id" uuid NOT NULL,
    "app_id" uuid NOT NULL,
    "thread_id" uuid,
    "user_id" uuid NOT NULL,
    "route_decision_id" uuid,
    "input" jsonb NOT NULL,
    "output" jsonb,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    "finished_at" timestamptz,
    PRIMARY KEY ("app_run_id")
);
COMMENT ON TABLE "meyo"."app_runs" IS '一次用户请求的 App 级运行记录。';
COMMENT ON COLUMN "meyo"."app_runs"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."app_runs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."app_runs"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."app_runs"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."app_runs"."request_id" IS '请求 ID';
COMMENT ON COLUMN "meyo"."app_runs"."trace_id" IS 'Trace ID';
COMMENT ON COLUMN "meyo"."app_runs"."workspace_id" IS 'workspace ID';
COMMENT ON COLUMN "meyo"."app_runs"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."app_runs"."thread_id" IS '聊天会话 ID';
COMMENT ON COLUMN "meyo"."app_runs"."user_id" IS '用户 ID';
COMMENT ON COLUMN "meyo"."app_runs"."route_decision_id" IS '路由决策 ID';
COMMENT ON COLUMN "meyo"."app_runs"."input" IS '请求输入';
COMMENT ON COLUMN "meyo"."app_runs"."output" IS '请求输出';
COMMENT ON COLUMN "meyo"."app_runs"."status" IS 'received / running / waiting_approval / succeeded / failed / blocked / cancelled';
COMMENT ON COLUMN "meyo"."app_runs"."created_at" IS '创建时间';
COMMENT ON COLUMN "meyo"."app_runs"."finished_at" IS '结束时间';

CREATE TABLE IF NOT EXISTS "meyo"."route_decisions" (
    "route_decision_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "router_flow_version_id" uuid,
    "candidate_scenes" jsonb NOT NULL,
    "selected_scene_id" uuid,
    "validated_scene_id" uuid,
    "selected_binding_id" uuid,
    "confidence" numeric,
    "reason" text,
    "status" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("route_decision_id")
);
COMMENT ON TABLE "meyo"."route_decisions" IS 'Router 决策记录表。';
COMMENT ON COLUMN "meyo"."route_decisions"."route_decision_id" IS '路由决策 ID';
COMMENT ON COLUMN "meyo"."route_decisions"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."route_decisions"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."route_decisions"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."route_decisions"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."route_decisions"."router_flow_version_id" IS 'Router Flow 版本';
COMMENT ON COLUMN "meyo"."route_decisions"."candidate_scenes" IS '候选 Scene 列表';
COMMENT ON COLUMN "meyo"."route_decisions"."selected_scene_id" IS '选中的 Scene';
COMMENT ON COLUMN "meyo"."route_decisions"."validated_scene_id" IS '校验通过的 Scene';
COMMENT ON COLUMN "meyo"."route_decisions"."selected_binding_id" IS '选中的 Flow 绑定';
COMMENT ON COLUMN "meyo"."route_decisions"."confidence" IS '置信度';
COMMENT ON COLUMN "meyo"."route_decisions"."reason" IS '路由理由';
COMMENT ON COLUMN "meyo"."route_decisions"."status" IS 'candidate / validated / rejected / executed';
COMMENT ON COLUMN "meyo"."route_decisions"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."flow_runs" (
    "flow_run_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "domain_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "trace_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "flow_version_id" uuid NOT NULL,
    "studio_run_external_ref" text,
    "status" text NOT NULL,
    "input" jsonb NOT NULL,
    "output" jsonb,
    "started_at" timestamptz NOT NULL,
    "finished_at" timestamptz,
    PRIMARY KEY ("flow_run_id")
);
COMMENT ON TABLE "meyo"."flow_runs" IS '一次 Flow 执行记录。';
COMMENT ON COLUMN "meyo"."flow_runs"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."flow_runs"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."flow_runs"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."flow_runs"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."flow_runs"."trace_id" IS 'Trace ID';
COMMENT ON COLUMN "meyo"."flow_runs"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."flow_runs"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."flow_runs"."flow_version_id" IS 'Flow 版本 ID';
COMMENT ON COLUMN "meyo"."flow_runs"."studio_run_external_ref" IS 'studio-flow 外部运行标识';
COMMENT ON COLUMN "meyo"."flow_runs"."status" IS 'running / succeeded / failed / cancelled';
COMMENT ON COLUMN "meyo"."flow_runs"."input" IS 'Flow 输入';
COMMENT ON COLUMN "meyo"."flow_runs"."output" IS 'Flow 输出';
COMMENT ON COLUMN "meyo"."flow_runs"."started_at" IS '开始时间';
COMMENT ON COLUMN "meyo"."flow_runs"."finished_at" IS '结束时间';

CREATE TABLE IF NOT EXISTS "meyo"."run_steps" (
    "run_step_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "flow_run_id" uuid,
    "node_code" text NOT NULL,
    "node_name" text NOT NULL,
    "status" text NOT NULL,
    "input_ref" jsonb,
    "output_ref" jsonb,
    "input" jsonb,
    "output" jsonb,
    "error_code" text,
    "error_detail_ref" jsonb,
    "error" jsonb,
    "started_at" timestamptz NOT NULL,
    "finished_at" timestamptz,
    PRIMARY KEY ("run_step_id")
);
COMMENT ON TABLE "meyo"."run_steps" IS '运行节点明细表，记录框架节点执行。';
COMMENT ON COLUMN "meyo"."run_steps"."run_step_id" IS '节点执行 ID';
COMMENT ON COLUMN "meyo"."run_steps"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."run_steps"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."run_steps"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."run_steps"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."run_steps"."node_code" IS '节点编号，如 FW00 / QA01';
COMMENT ON COLUMN "meyo"."run_steps"."node_name" IS '节点名称';
COMMENT ON COLUMN "meyo"."run_steps"."status" IS 'started / succeeded / failed / skipped';
COMMENT ON COLUMN "meyo"."run_steps"."input_ref" IS '输入引用';
COMMENT ON COLUMN "meyo"."run_steps"."output_ref" IS '输出引用';
COMMENT ON COLUMN "meyo"."run_steps"."input" IS '节点输入';
COMMENT ON COLUMN "meyo"."run_steps"."output" IS '节点输出';
COMMENT ON COLUMN "meyo"."run_steps"."error_code" IS '错误码';
COMMENT ON COLUMN "meyo"."run_steps"."error_detail_ref" IS '错误详情引用';
COMMENT ON COLUMN "meyo"."run_steps"."error" IS '错误信息';
COMMENT ON COLUMN "meyo"."run_steps"."started_at" IS '开始时间';
COMMENT ON COLUMN "meyo"."run_steps"."finished_at" IS '结束时间';

CREATE TABLE IF NOT EXISTS "meyo"."scene_node_events" (
    "event_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "flow_run_id" uuid NOT NULL,
    "scene_id" uuid NOT NULL,
    "scene_node_code" text NOT NULL,
    "event_type" text NOT NULL,
    "payload" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("event_id")
);
COMMENT ON TABLE "meyo"."scene_node_events" IS 'Scene 内部节点事件表。';
COMMENT ON COLUMN "meyo"."scene_node_events"."event_id" IS '事件 ID';
COMMENT ON COLUMN "meyo"."scene_node_events"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."scene_node_events"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."scene_node_events"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."scene_node_events"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."scene_node_events"."scene_id" IS 'Scene ID';
COMMENT ON COLUMN "meyo"."scene_node_events"."scene_node_code" IS 'Scene 节点编号';
COMMENT ON COLUMN "meyo"."scene_node_events"."event_type" IS 'start / end / token / error / custom';
COMMENT ON COLUMN "meyo"."scene_node_events"."payload" IS '事件内容';
COMMENT ON COLUMN "meyo"."scene_node_events"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."data_access_events" (
    "data_access_event_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "flow_run_id" uuid,
    "node_code" text NOT NULL,
    "api_name" text NOT NULL,
    "source_store" text NOT NULL,
    "query_ref" jsonb NOT NULL,
    "result_count" integer NOT NULL,
    "status" text NOT NULL,
    "error" jsonb,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("data_access_event_id")
);
COMMENT ON TABLE "meyo"."data_access_events" IS 'Internal Data API 数据访问审计表。所有 PostgreSQL / Milvus / Neo4j 查询都要记录。';
COMMENT ON COLUMN "meyo"."data_access_events"."data_access_event_id" IS '数据访问事件 ID';
COMMENT ON COLUMN "meyo"."data_access_events"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."data_access_events"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."data_access_events"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."data_access_events"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."data_access_events"."node_code" IS '发起查询的节点编号';
COMMENT ON COLUMN "meyo"."data_access_events"."api_name" IS 'Internal API 名称';
COMMENT ON COLUMN "meyo"."data_access_events"."source_store" IS 'postgres / milvus / chroma / neo4j / tugraph';
COMMENT ON COLUMN "meyo"."data_access_events"."query_ref" IS '查询引用或脱敏查询摘要';
COMMENT ON COLUMN "meyo"."data_access_events"."result_count" IS '返回数量';
COMMENT ON COLUMN "meyo"."data_access_events"."status" IS 'succeeded / failed / skipped';
COMMENT ON COLUMN "meyo"."data_access_events"."error" IS '错误信息';
COMMENT ON COLUMN "meyo"."data_access_events"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."trace_events" (
    "trace_event_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "trace_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "event_type" text NOT NULL,
    "node_code" text,
    "payload" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("trace_event_id")
);
COMMENT ON TABLE "meyo"."trace_events" IS '通用 trace 事件表。';
COMMENT ON COLUMN "meyo"."trace_events"."trace_event_id" IS 'Trace 事件 ID';
COMMENT ON COLUMN "meyo"."trace_events"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."trace_events"."trace_id" IS 'Trace ID';
COMMENT ON COLUMN "meyo"."trace_events"."run_id" IS 'Run ID';
COMMENT ON COLUMN "meyo"."trace_events"."event_type" IS 'request / route / flow / data / evidence / error';
COMMENT ON COLUMN "meyo"."trace_events"."node_code" IS '节点编号';
COMMENT ON COLUMN "meyo"."trace_events"."payload" IS '事件载荷';
COMMENT ON COLUMN "meyo"."trace_events"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."run_metrics" (
    "metric_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "flow_run_id" uuid,
    "metric_name" text NOT NULL,
    "metric_value" numeric NOT NULL,
    "unit" text,
    "tags" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("metric_id")
);
COMMENT ON TABLE "meyo"."run_metrics" IS 'Run 指标表，用于 FW20 写 latency、token、召回数等指标。';
COMMENT ON COLUMN "meyo"."run_metrics"."metric_id" IS '指标 ID';
COMMENT ON COLUMN "meyo"."run_metrics"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."run_metrics"."run_id" IS 'Run ID';
COMMENT ON COLUMN "meyo"."run_metrics"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."run_metrics"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."run_metrics"."metric_name" IS '指标名';
COMMENT ON COLUMN "meyo"."run_metrics"."metric_value" IS '指标值';
COMMENT ON COLUMN "meyo"."run_metrics"."unit" IS '单位';
COMMENT ON COLUMN "meyo"."run_metrics"."tags" IS '标签';
COMMENT ON COLUMN "meyo"."run_metrics"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."evidence_records" (
    "evidence_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "flow_run_id" uuid,
    "evidence_type" text NOT NULL,
    "source_type" text NOT NULL,
    "source_ref" jsonb NOT NULL,
    "document_id" uuid,
    "chunk_id" uuid,
    "graph_path_external_ref" text,
    "acl_decision" text NOT NULL,
    "selected_by_node_code" text NOT NULL,
    "score" numeric,
    "content_snapshot" text NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("evidence_id")
);
COMMENT ON TABLE "meyo"."evidence_records" IS '回答证据表，最终答案必须引用这里的证据。';
COMMENT ON COLUMN "meyo"."evidence_records"."evidence_id" IS '证据 ID';
COMMENT ON COLUMN "meyo"."evidence_records"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."evidence_records"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."evidence_records"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."evidence_records"."flow_run_id" IS 'Flow Run ID';
COMMENT ON COLUMN "meyo"."evidence_records"."evidence_type" IS 'chunk / graph_path / tool_result / sql_result';
COMMENT ON COLUMN "meyo"."evidence_records"."source_type" IS 'postgres / vector / graph / tool';
COMMENT ON COLUMN "meyo"."evidence_records"."source_ref" IS '来源引用';
COMMENT ON COLUMN "meyo"."evidence_records"."document_id" IS '文档 ID';
COMMENT ON COLUMN "meyo"."evidence_records"."chunk_id" IS '切片 ID';
COMMENT ON COLUMN "meyo"."evidence_records"."graph_path_external_ref" IS '图路径外部引用';
COMMENT ON COLUMN "meyo"."evidence_records"."acl_decision" IS 'allow / deny / redacted';
COMMENT ON COLUMN "meyo"."evidence_records"."selected_by_node_code" IS '选择证据的节点编号';
COMMENT ON COLUMN "meyo"."evidence_records"."score" IS '检索分数';
COMMENT ON COLUMN "meyo"."evidence_records"."content_snapshot" IS '证据内容快照';
COMMENT ON COLUMN "meyo"."evidence_records"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."evidence_citations" (
    "citation_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "message_id" uuid,
    "evidence_id" uuid NOT NULL,
    "answer_span" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("citation_id")
);
COMMENT ON TABLE "meyo"."evidence_citations" IS '答案片段和证据绑定表。';
COMMENT ON COLUMN "meyo"."evidence_citations"."citation_id" IS '引用 ID';
COMMENT ON COLUMN "meyo"."evidence_citations"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."evidence_citations"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."evidence_citations"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."evidence_citations"."message_id" IS '回答消息 ID';
COMMENT ON COLUMN "meyo"."evidence_citations"."evidence_id" IS '证据 ID';
COMMENT ON COLUMN "meyo"."evidence_citations"."answer_span" IS '答案片段位置';
COMMENT ON COLUMN "meyo"."evidence_citations"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."no_answer_records" (
    "no_answer_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid NOT NULL,
    "app_run_id" uuid NOT NULL,
    "reason_code" text NOT NULL,
    "details" jsonb NOT NULL,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("no_answer_id")
);
COMMENT ON TABLE "meyo"."no_answer_records" IS '无答案记录表，用于禁止模型无证据猜测。';
COMMENT ON COLUMN "meyo"."no_answer_records"."no_answer_id" IS '无答案记录 ID';
COMMENT ON COLUMN "meyo"."no_answer_records"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."no_answer_records"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."no_answer_records"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."no_answer_records"."reason_code" IS 'no_evidence / low_confidence / policy_blocked';
COMMENT ON COLUMN "meyo"."no_answer_records"."details" IS '详细原因';
COMMENT ON COLUMN "meyo"."no_answer_records"."created_at" IS '创建时间';

CREATE TABLE IF NOT EXISTS "meyo"."feedback_events" (
    "feedback_id" uuid NOT NULL,
    "tenant_id" uuid NOT NULL,
    "run_id" uuid,
    "app_run_id" uuid,
    "message_id" uuid,
    "user_id" uuid NOT NULL,
    "rating" integer,
    "feedback_type" text NOT NULL,
    "comment" text,
    "created_at" timestamptz NOT NULL,
    PRIMARY KEY ("feedback_id")
);
COMMENT ON TABLE "meyo"."feedback_events" IS '用户反馈表。';
COMMENT ON COLUMN "meyo"."feedback_events"."feedback_id" IS '反馈 ID';
COMMENT ON COLUMN "meyo"."feedback_events"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."feedback_events"."run_id" IS '全链路 Run ID';
COMMENT ON COLUMN "meyo"."feedback_events"."app_run_id" IS 'App Run ID';
COMMENT ON COLUMN "meyo"."feedback_events"."message_id" IS '消息 ID';
COMMENT ON COLUMN "meyo"."feedback_events"."user_id" IS '用户 ID';
COMMENT ON COLUMN "meyo"."feedback_events"."rating" IS '评分';
COMMENT ON COLUMN "meyo"."feedback_events"."feedback_type" IS 'like / dislike / correction / issue';
COMMENT ON COLUMN "meyo"."feedback_events"."comment" IS '反馈内容';
COMMENT ON COLUMN "meyo"."feedback_events"."created_at" IS '创建时间';

DROP VIEW IF EXISTS "meyo"."active_scene_router_view";
CREATE VIEW "meyo"."active_scene_router_view" AS
SELECT
    s."tenant_id",
    s."domain_id",
    s."app_id",
    s."scene_id",
    s."name" AS "scene_name",
    s."intent_description",
    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'example_id', e."example_id",
                'text', e."text",
                'label', e."label",
                'reason', e."reason"
            ) ORDER BY e."created_at"
        ) FILTER (WHERE e."example_id" IS NOT NULL),
        '[]'::jsonb
    ) AS "route_examples",
    rv."router_version_id",
    b."binding_id",
    b."flow_version_id",
    COALESCE(s."policy_profile_id", a."policy_profile_id") AS "policy_profile_id"
FROM "meyo"."scene_registry" s
JOIN "meyo"."app_registry" a
    ON a."tenant_id" = s."tenant_id"
   AND a."app_id" = s."app_id"
JOIN "meyo"."app_scene_flow_bindings" b
    ON b."tenant_id" = s."tenant_id"
   AND b."app_id" = s."app_id"
   AND b."scene_id" = s."scene_id"
   AND b."status" = 'active'
LEFT JOIN "meyo"."router_versions" rv
    ON rv."tenant_id" = s."tenant_id"
   AND rv."app_id" = s."app_id"
   AND rv."status" = 'active'
LEFT JOIN "meyo"."scene_route_examples" e
    ON e."tenant_id" = s."tenant_id"
   AND e."app_id" = s."app_id"
   AND e."scene_id" = s."scene_id"
   AND e."status" = 'active'
WHERE s."status" = 'active'
  AND a."status" = 'active'
GROUP BY
    s."tenant_id", s."domain_id", s."app_id", s."scene_id",
    s."name", s."intent_description", rv."router_version_id",
    b."binding_id", b."flow_version_id", s."policy_profile_id", a."policy_profile_id";
COMMENT ON VIEW "meyo"."active_scene_router_view" IS 'Router 唯一候选列表。Router 只读该视图，不直接拼多表。';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."tenant_id" IS '租户 ID';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."domain_id" IS '业务域 ID';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."app_id" IS 'App ID';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."scene_id" IS 'active Scene ID';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."scene_name" IS 'Scene 名称';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."intent_description" IS 'Router 可读意图';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."route_examples" IS 'active 正反例';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."router_version_id" IS 'active Router 版本';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."binding_id" IS 'active App Scene Flow 绑定';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."flow_version_id" IS 'active Flow 版本';
COMMENT ON COLUMN "meyo"."active_scene_router_view"."policy_profile_id" IS 'active 策略 profile';

COMMIT;
