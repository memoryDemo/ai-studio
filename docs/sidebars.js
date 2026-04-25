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
      ],
    },
  ],
};

module.exports = sidebars;
