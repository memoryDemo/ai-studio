# AI Studio

AI Studio 是一个 `LangGraph-first` 的 AgentOS 平台项目，目标是为上层 AI 应用提供统一的：

- agent runtime
- knowledge / skill
- memory OS
- tool mesh
- observability

## 项目分层

当前仓库采用一个 **向 `Umber Studio` 对齐的多 package 分层**，学习它的包边界设计，但实现规模先保持克制。

当前包结构：

- `packages/ai-studio-core`
  - 放稳定 contracts、gateway 协议、运行时输入输出模型
- `packages/ai-studio-ext`
  - 放具体实现、runtime 适配、基础扩展能力
- `packages/ai-studio-client`
  - 放未来 SDK / API client 边界
- `packages/ai-studio-serve`
  - 放服务层与应用服务编排
- `packages/ai-studio-app`
  - 放启动、装配与未来 API 入口
- `packages/ai-studio-sandbox`
  - 放受控执行与沙箱能力边界
- `packages/ai-studio-accelerator/ai-studio-acc-auto`
  - 放可选推理加速依赖矩阵与自动安装壳
- `packages/ai-studio-accelerator/ai-studio-acc-flash-attn`
  - 放 `flash-attn` 这类单独安装策略的适配壳

依赖方向固定为：

`ai-studio-core <- ai-studio-ext / ai-studio-client / ai-studio-sandbox / ai-studio-serve <- ai-studio-app`

另外，`ai-studio-app` 会侧向依赖 `ai-studio-acc-auto`，把 GPU / 推理加速能力保持在独立附属层，而不是混进核心包。

这意味着：

- `core` 不写业务 I/O
- `ext` 承担实现，不反向污染 `core`
- `serve` 不依赖 `app`
- `app` 负责装配，不承载底层 contracts

## 文档

文档工作区位于 [docs](/Users/memory/CodeRepository/PycharmProjects/ai-studio/docs)，已复刻 `Umber Studio/docs` 的 Docusaurus 工程结构。

当前已补入的核心文档：

- [基座项目总览](/Users/memory/CodeRepository/PycharmProjects/ai-studio/docs/docs/application/base_project/index.md)
- [AI Studio 企业级 AgentOS 架构设计文档（实施蓝图版）](/Users/memory/CodeRepository/PycharmProjects/ai-studio/docs/docs/application/base_project/architecture_design.md)
- [AI Studio 功能设计](/Users/memory/CodeRepository/PycharmProjects/ai-studio/docs/docs/application/base_project/functional_design.md)
- [AI Studio 技术栈](/Users/memory/CodeRepository/PycharmProjects/ai-studio/docs/docs/application/base_project/technology_stack.md)
- [AI Studio Memory OS 设计](/Users/memory/CodeRepository/PycharmProjects/ai-studio/docs/docs/application/base_project/memory_os_design.md)

## 最小启动

先同步 workspace：

```bash
uv sync --all-packages
```

然后启动当前最小 webserver：

```bash
uv run ai-studio start webserver --config /my/dev.toml
```

`--config` 会优先按以下规则解析：

- 真实存在的绝对路径，直接使用
- 以 `/` 开头但不是实际绝对文件时，按 `configs/` 根目录解析
- 普通相对路径找不到时，也回退到 `configs/` 下查找

所以这条命令等价于：

```bash
uv run ai-studio start webserver --config configs/my/dev.toml
```
