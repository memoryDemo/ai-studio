# Meyo Docs Workspace

## 快速开始

先进入 docs 工作区：

```bash
cd <repo-root>/docs
```

安装依赖：

```bash
bun install
```

本地启动：

```bash
bun run start
```

构建静态站点：

```bash
bun run build
```

默认端口是 `3000`。

## 当前文档范围

这个 docs 工作区复用了 `Umber Studio/docs` 的 Docusaurus 工程壳，但当前文档资产已经切到 `Meyo` 自己的内容。

当前站内重点文档：

- `docs/docs/application/base_project/index.md`
- `docs/docs/application/base_project/architecture_design.md`
- `docs/docs/application/base_project/functional_design.md`
- `docs/docs/application/base_project/technology_stack.md`
- `docs/docs/application/base_project/memory_os_design.md`
- `docs/docs/application/base_project/quick_code_onboarding.md`
- `docs/docs/application/base_project/directory_and_module_map.md`
- `docs/docs/application/base_project/packages_architecture.md`
- `docs/docs/application/base_project/development_playbooks.md`

仓库级 playbooks 位于：

- `docs/playbooks/README.md`
- `docs/playbooks/add-new-api-endpoint.md`
- `docs/playbooks/add-new-scene.md`
