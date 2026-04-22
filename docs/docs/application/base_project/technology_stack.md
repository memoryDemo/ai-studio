---
title: AI Studio 技术栈
---

# AI Studio 技术栈

## 一、总览

`AI Studio` 的技术栈不是“哪个框架火就全量押上去”，而是按平台分层做技术落位。

一句话版本：

`FastAPI + LangGraph + PostgreSQL + Redis + Milvus + Neo4j + MinIO/S3 + MCP + Langfuse + OpenTelemetry`

## 二、按层拆分

### 2.1 API / BFF

- `Python 3.11+`
- `FastAPI`
- `Pydantic v2`
- `Uvicorn / Gunicorn`

职责：

- App API
- streaming
- upload
- runs / approvals / evidence

### 2.2 Agent Runtime

- `LangGraph`
- 可选 `LangChain` 适配层

职责：

- stateful orchestration
- checkpointer
- interrupt / resume
- HITL

原则：

- `LangGraph-first`
- 但不 `LangGraph-everywhere`

### 2.3 Knowledge / Retrieval

- `PostgreSQL`
- `Milvus`
- `Neo4j`
- `MinIO / S3`

职责：

- metadata / registry
- semantic retrieval
- graph retrieval
- artifacts / reports / files

### 2.4 Memory OS

- `LangGraph state + checkpointer`
- `MemoryGateway`
- `PostgreSQL`
- `Milvus`
- `Neo4j`

职责：

- working memory
- checkpoint memory
- episodic memory
- semantic memory
- graph / insight memory

### 2.5 Tool Mesh

- `MCP Gateway`
- `Tool Registry`
- `Sandbox Runtime`

职责：

- tool registration
- schema validation
- allowlist
- audit
- execution isolation

### 2.6 Observability

- `Langfuse`
- `OpenTelemetry`
- `Prometheus`
- `Grafana`
- `Loki / Tempo / Jaeger`

职责：

- LLM traces
- prompt / token / model cost
- platform trace / metric / log
- memory quality metrics

## 三、三库分工

### PostgreSQL

作为系统事实主库，保存：

- `runs`
- `run_steps`
- `approvals`
- `tool_audit`
- `knowledge_spaces`
- `skill_registry`
- `episodic_events`
- `semantic_memory_items`
- `evidence_index`

### Milvus

作为语义检索层，保存：

- knowledge chunk vectors
- semantic memory vectors
- related fact retrieval vectors

### Neo4j

作为图洞见层，保存：

- entity relation graph
- event relation graph
- support / contradiction edges
- GraphRAG structures

## 四、为什么不是 Mem0-first

`Mem0` 可以接，但 `AI Studio` 不以它作为主记忆底座。

原因：

- 平台需要自己的 `MemoryGateway`
- 平台要把 memory 和 knowledge / evidence / graph 一起治理
- 长期主线是 `PG + Milvus + Neo4j` 的组合，不是单 memory SDK

因此：

- `Mem0` 是可选 adapter
- 不是主技术栈核心

## 五、为什么是 LangGraph-first

选择 `LangGraph`，是因为它在 `AI Studio` 需要的那一层最强：

- durable execution
- thread state
- checkpoint
- interrupt / resume
- HITL

而 `AI Studio` 平台自身仍然负责：

- Run API
- Memory OS
- Knowledge / Skill 模型
- Tool Mesh
- Evidence / Audit

## 六、MVP vs Production

### MVP

- FastAPI
- LangGraph
- PostgreSQL
- Redis
- Milvus
- Langfuse

### Production

- FastAPI + LangGraph
- PostgreSQL + Redis + Milvus + Neo4j + MinIO/S3
- MCP Gateway + Sandbox
- Langfuse + OpenTelemetry + Prometheus/Grafana
- Kafka（异步规模化后再接）

## 七、最终结论

`AI Studio` 的技术栈不是靠单一框架兜底，而是：

- `FastAPI` 管平台入口
- `LangGraph` 管 agent runtime
- `PostgreSQL` 管系统事实
- `Milvus` 管语义召回
- `Neo4j` 管图洞见
- `Langfuse` 管 LLM 观测
- `OpenTelemetry` 管平台观测
