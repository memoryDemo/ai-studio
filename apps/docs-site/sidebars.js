// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    {
      type: "category",
      label: "平台框架",
      collapsed: false,
      collapsible: true,
      link: { type: "doc", id: "application/base_project/index" },
      items: [
        { type: "doc", id: "application/base_project/index", label: "基座项目总览" },
        {
          type: "doc",
          id: "application/base_project/architecture_design",
          label: "Meyo 企业级 AgentOS 架构设计文档（实施蓝图版）",
        },
        { type: "doc", id: "application/base_project/functional_design", label: "Meyo 功能设计" },
        { type: "doc", id: "application/base_project/technology_stack", label: "Meyo 技术栈" },
        { type: "doc", id: "application/base_project/memory_os_design", label: "Meyo Memory OS 设计" },
      ],
    },
    {
      type: "category",
      label: "开发指南",
      collapsed: false,
      collapsible: true,
      items: [
        { type: "doc", id: "application/base_project/quick_code_onboarding", label: "快速上手" },
        { type: "doc", id: "application/base_project/from_zero_to_running", label: "从零开始上手" },
        { type: "doc", id: "application/base_project/directory_and_module_map", label: "目录结构与模块职责" },
        { type: "doc", id: "application/base_project/packages_architecture", label: "Packages 架构与分层" },
        { type: "doc", id: "application/base_project/development_playbooks", label: "开发 Playbooks" },
      ],
    },
    {
      type: "category",
      label: "设计文档",
      collapsed: false,
      collapsible: true,
      items: [
        { type: "doc", id: "design/project_architecture_dependency_design", label: "项目架构与按需依赖设计" },
        { type: "doc", id: "design/model_provider_manager_design", label: "Model Provider Manager 详细设计" },
        { type: "doc", id: "design/logging_system_design", label: "日志系统设计" },
        { type: "doc", id: "design/meyo_chatbot_migration_design", label: "Meyo Chatbot 迁移与改造设计" },
        { type: "doc", id: "design/meyo_studio_flow_migration_design", label: "Meyo Studio Flow 迁移与改造设计" },
      ],
    },
    {
      type: "category",
      label: "前沿专题",
      collapsed: false,
      collapsible: true,
      items: [
        { type: "doc", id: "feature/enterprise-ai-methodology-radar", label: "企业 AI App 前沿技术方法论雷达" },
        { type: "doc", id: "feature/ontology-graphrag-enterprise-ai", label: "Ontology + GraphRAG 企业落地说明" },
        { type: "doc", id: "feature/opentelemetry-genai-observability", label: "OpenTelemetry GenAI 可观测架构说明" },
        { type: "doc", id: "feature/ap2-ucp-agent-commerce", label: "AP2 / UCP Agent Commerce 协议说明" },
        { type: "doc", id: "feature/harness-engineering-agentos-development", label: "Harness Engineering：AgentOS 壳项目的开发方法" },
        { type: "doc", id: "feature/google-design-md-methodology", label: "Google DESIGN.md 设计思路与 Meyo 落地说明" },
      ],
    },
    {
      type: "category",
      label: "部署运维",
      collapsed: false,
      collapsible: true,
      items: [
        { type: "doc", id: "deploy/deployment_process", label: "部署流程" },
        { type: "doc", id: "deploy/deployment_faq", label: "部署常见问题" },
      ],
    },
  ],
};

module.exports = sidebars;
