---
title: 基座项目总览
---

# 基座项目总览

这组文档用于定义 `Meyo` 的平台级设计基线，而不是某个 demo 页面的使用说明。

当前这套文档现在分两组：

1. 架构基线
2. 开发指南

## 一、项目定位

`Meyo` 是一个 **LangGraph-first 的 AgentOS 平台工程**，目标是为上层 AI 应用提供统一的：

- agent runtime
- knowledge / skill
- tool mesh
- memory OS
- observability

它不是一个“多工具聊天 demo”，而是一个可长期演进的企业级 AI 基座。

## 二、当前三条核心判断

1. `LangGraph` 作为首选 agent runtime，只进入 `orchestrator/runtime` 层。
2. 记忆系统采用 `LangGraph primitives + MemoryGateway + PostgreSQL/Milvus/Neo4j` 的分层模型。
3. 平台对业务暴露的是稳定的 `Run API / Gateway API`，不是底层框架内部对象。

## 三、推荐阅读顺序

建议按下面顺序阅读：

1. [Meyo 企业级 AgentOS 架构设计文档（实施蓝图版）](./architecture_design.md)
2. [Meyo 功能设计](./functional_design.md)
3. [Meyo 技术栈](./technology_stack.md)
4. [Meyo Memory OS 设计](./memory_os_design.md)
5. [快速上手：当前工程骨架与最短阅读路径](./quick_code_onboarding.md)
6. [从零开始上手：uv、Workspace 与包加载链路](./from_zero_to_running.md)
7. [目录结构与模块职责](./directory_and_module_map.md)
8. [Packages 架构与包间分层设计](./packages_architecture.md)
9. [开发 Playbooks 与使用方式](./development_playbooks.md)

## 四、目录结构说明

这套 docs 站点保留了 `Umber Studio/docs` 的 Docusaurus 工程壳，同时把文档资产收敛到了 `application/base_project` 这条线。

另外还预建了与 `Umber Studio` 顶层一致的 docs 目录骨架，作为后续文档扩展的占位：

- `agents/`
- `api/`
- `application/`
- `awel/`
- `changelog/`
- `config-reference/`
- `cookbook/`
- `dbgpts/`
- `faq/`
- `getting-started/`
- `installation/`
- `modules/`
- `studios/`
- `tutorials/`
- `upgrade/`

当前这些目录大多还只有占位文件，不承载正式内容。

## 五、开发指南

当前已经迁入并适配 `Meyo` 的开发指南包括：

- [快速上手：当前工程骨架与最短阅读路径](./quick_code_onboarding.md)
- [从零开始上手：uv、Workspace 与包加载链路](./from_zero_to_running.md)
- [目录结构与模块职责](./directory_and_module_map.md)
- [Packages 架构与包间分层设计](./packages_architecture.md)
- [开发 Playbooks 与使用方式](./development_playbooks.md)

仓库级 playbooks 位于：

- `docs/playbooks/README.md`
- `docs/playbooks/add-new-api-endpoint.md`
- `docs/playbooks/add-new-scene.md`
