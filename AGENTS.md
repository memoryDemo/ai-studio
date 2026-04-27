# AGENTS.md

## 作用域
- 本文件作用于整个仓库。
- 如果某个子目录下存在更深层的 `AGENTS.md`，以更深层文件为准。

## 仓库定位
- 本仓库是 `Meyo`：一个私有化的、`LangGraph-first` 的 AgentOS 框架壳。
- 根目录的 `pyproject.toml` 主要承担 `uv workspace` 容器职责，不直接承载运行时业务依赖。
- 当前 Python 基线为 `>=3.12`。

## 目录分工
- `packages/`：共享 Python 能力与框架层代码，包含 `meyo`、`meyo_ext`、`meyo_client`、`meyo_serve`、`meyo_app`、`meyo_sandbox`、`meyo_accelerator`。
- `apps/meyo-chatbot`：独立的 Open WebUI 应用，包含 SvelteKit 前端与 FastAPI 后端；默认不应随意直接耦合 `packages/meyo-*`。
- `apps/meyo-studio-flow`：独立的 Langflow 工作流实验台；不属于根 `uv workspace` 的常规包成员，不要默认按根工作区结构改造它。
- `apps/docs-site`：Docusaurus 文档站。
- `configs/`：运行配置与示例配置，常用默认配置位于 `configs/meyo.toml`。
- `tests/`：根工作区测试；新增测试应贴近被测 package 或现有测试结构。
- `logs/`、`output/`、`tmp/`：运行输出和临时结果，不应作为源码事实来源，也不要把其中内容作为持久配置。

## 修改原则
- 优先做最小且完整的改动，避免顺手大范围重构。
- 优先修根因，不做临时性表面补丁。
- 除非用户明确要求，不要随意移动目录、重命名模块、调整 package 边界。
- 保持现有命名风格、分层方式与脚本入口一致。
- 不要编辑生成物、依赖目录或缓存目录，例如 `node_modules/`、`.venv/`、构建产物、覆盖率产物、`.pytest_cache/`、临时输出目录等。

## 分层与依赖边界
- 跨应用复用、框架能力、运行时主链路逻辑优先放在 `packages/`。
- 仅服务某个应用的行为、页面、适配逻辑留在对应 `apps/...` 目录内。
- 根 README 中定义的主依赖方向是 `meyo <- meyo-ext / meyo-client / meyo-serve <- meyo-app`；`meyo-app` 是最终装配层，可依赖 `meyo-sandbox` 与 `meyo-accelerator`。
- 不要让底层核心包反向依赖上层装配层或具体应用；如果确实需要跨层调用，优先抽象接口或把共享逻辑下沉到合适 package。
- 新增 Python 依赖时，优先加到最具体的 package 或 app；只有在确实被多个模块共享时才考虑放到更上层。
- 不要默认让 `apps/meyo-chatbot` 或 `apps/meyo-studio-flow` 直接 import `packages/meyo-*`；如果要改变这个边界，必须有明确任务背景。
- 不要在无明确需求时把 `apps/meyo-studio-flow` 重新纳入根 `uv workspace`，也不要顺手改造它的原有 Langflow 结构。

## 配置与安全
- 不要把真实密钥、token、cookie、数据库密码或私有服务凭据写入代码、文档、测试快照或示例配置。
- 需要新增环境变量时，优先更新对应 `.env.example`、示例 TOML 或 README，并说明默认值与本地开发取值。
- 读取 `.env`、本地配置或日志排障时，只引用必要字段名和脱敏后的值；不要在回复中完整暴露敏感内容。

## 工具与工作方式
- Python 命令优先使用 `uv run ...`。
- 优先复用现有 `package.json` scripts、`Makefile` 目标和仓库已有命令，不要凭空发明新入口。
- 搜索优先使用 `rg`；如果环境没有 `rg`，再退回到最小范围的替代方案。
- 阅读大文件时按片段读取，只看完成任务所需的上下文。
- 在大范围搜索、重构或新增抽象前，先查看本地 `README.md`、相关 manifest 和相邻代码，确认当前模式。

## 验证原则
- 验证从最小闭环开始，先跑与你改动最相关的检查，再逐步扩大范围。
- 不要为了完成局部任务而顺手修复无关失败项；如果发现无关失败，在结果里说明即可。

## 常用验证命令
- 根工作区 / CLI / WebServer：
  - `uv run meyo --help`
  - `uv run meyo start webserver --config configs/meyo.toml`
- Python 代码质量（按需执行最小范围目标）：
  - `uv run ruff check .`
  - `uv run ruff format .`
- `apps/meyo-chatbot`：
  - `cd apps/meyo-chatbot && npm run check`
  - `cd apps/meyo-chatbot && npm run test:frontend`
  - `cd apps/meyo-chatbot && npm run format:backend`
- `apps/docs-site`：
  - `cd apps/docs-site && npm run build`
- `apps/meyo-studio-flow`：
  - `cd apps/meyo-studio-flow && make run_cli open_browser=false`
  - `cd apps/meyo-studio-flow && make format_backend`

## 文档与配置同步
- 如果改动影响启动方式、端口、环境变量、配置字段或系统行为，尽量在同一任务内同步更新相关文档与示例。
- 保持 `README.md`、`configs/*.toml`、示例配置、以及 app 侧 `.env.example` 一致。
- 涉及 Meyo 与各应用的对接链路时，优先核对配置说明是否仍与代码一致，不要只改代码不改说明。

## Agent 协作建议
- 需要理解历史意图时，可先看 `git log`、`git blame`，避免误改架构边界。
- 若某个 app 或 package 的约束已经明显复杂到超出根文件承载范围，应在对应子目录补充更细的 `AGENTS.md`，而不是把所有细节都堆到根文件。
