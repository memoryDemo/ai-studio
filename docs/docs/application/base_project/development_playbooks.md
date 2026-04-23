---
title: 开发 Playbooks 与使用方式
---

# 开发 Playbooks 与使用方式

`AI Studio` 当前保留了一组仓库级 playbooks，位置在：

```text
docs/playbooks/
```

这些文档不是站内“产品说明”，而是给开发者的**填空式操作手册**。

## 当前为什么需要 playbooks

`AI Studio` 现在还在从“文档基线”向“真实可运行系统”过渡。

这个阶段最怕两种问题：

- 一边写代码一边临时拍脑袋改边界
- 直接沿用 `Umber Studio` 的旧做法，忘了当前仓库其实还没长到那一步

## 当前有哪些 playbooks

| Playbook | 路径 | 当前状态 |
|---|---|---|
| 索引 | `docs/playbooks/README.md` | 已适配 `AI Studio` |
| 新增一个 HTTP 接口 | `docs/playbooks/add-new-api-endpoint.md` | 已改成 `AI Studio` 现状版本 |
| 新增一个 Agent 场景 | `docs/playbooks/add-new-scene.md` | 已改成“预置 playbook” |

## 这些 playbooks 和 Umber Studio 的主要差别

最大的差别只有一个：

**`AI Studio` 当前还没有完整的 `openapi/`、`scene/` 和前端工作台。**

所以这里的 playbooks 都做了两类调整：

1. 把 `Umber` 里那些“默认目录已存在”的表述改掉
2. 把现在还没落地的部分明确标成“前提条件”或“预置 playbook”

## 当前最适合使用的开发切片

如果你现在在 `AI Studio` 里写代码，最适合按下面顺序推进：

1. 新增 `core` contract
2. 新增 `ext` adapter
3. 新增 `serve` service
4. 新增 `app` wiring
5. 之后再补 FastAPI / Scene / Frontend

## 当前最低限度验证

因为仓库还在骨架阶段，所以当前最实用的验证是：

```bash
python -m compileall packages
cd docs && bun run build
```

如果你补了测试，再执行：

```bash
uv run pytest
```

## 一句话收口

`AI Studio` 的 playbooks 不是为了复制 `Umber Studio` 的现状，而是为了：

**把 `Umber` 那套开发方法论迁进来，同时诚实地反映 `AI Studio` 当前真实阶段。**
