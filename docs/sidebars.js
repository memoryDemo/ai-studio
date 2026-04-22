// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    {
      type: "category",
      label: "平台框架",
      collapsed: false,
      collapsible: false,
      link: { type: "doc", id: "application/base_project/index" },
      items: [
        { type: "doc", id: "application/base_project/index", label: "基座项目总览" },
        {
          type: "doc",
          id: "application/base_project/architecture_design",
          label: "AI Studio 企业级 AgentOS 架构设计文档（实施蓝图版）",
        },
        { type: "doc", id: "application/base_project/technology_stack", label: "AI Studio 技术栈" },
        { type: "doc", id: "application/base_project/memory_os_design", label: "AI Studio Memory OS 设计" },
      ],
    },
  ],
};

module.exports = sidebars;
