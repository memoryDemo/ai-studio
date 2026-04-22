---
title: 基座项目总览
---

# 基座项目总览

这组文档用于定义 `AI Studio` 的平台级设计基线，而不是某个 demo 页面的使用说明。

当前这套文档只保留 4 篇核心资产：

1. [AI Studio 企业级 AgentOS 架构设计文档（实施蓝图版）](./architecture_design.md)
2. [AI Studio 技术栈](./technology_stack.md)
3. [AI Studio Memory OS 设计](./memory_os_design.md)

## 一、项目定位

`AI Studio` 是一个 **LangGraph-first 的 AgentOS 平台工程**，目标是为上层 AI 应用提供统一的：

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

1. [AI Studio 企业级 AgentOS 架构设计文档（实施蓝图版）](./architecture_design.md)
2. [AI Studio 技术栈](./technology_stack.md)
3. [AI Studio Memory OS 设计](./memory_os_design.md)

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
