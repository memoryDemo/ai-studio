---
title: Playbooks 索引
---

# Umber Studio Playbooks — 填空式操作手册

## 这是什么

这个目录下每一份文档都是一份**填空题**:告诉你改哪几个文件、贴什么模板、跑什么验证命令。

目标是:**基础再弱的人,照着第 1 步做到最后一步,也能提出一个合格的 PR**。

Lead 评审时不用看他懂不懂架构,只看:

- 是不是按 playbook 每一步都做了
- 有没有违反 `.cursor/rules/` 和 `AGENTS.md` 里的红线
- PR 描述有没有回答 `90-pr-checklist.mdc` 的 5 个问题

## 现有 Playbook

| # | 场景 | Playbook |
|---|---|---|
| 1 | 新增一个 HTTP 接口(给前端或第三方调用) | [add-new-api-endpoint.md](./add-new-api-endpoint.md) |
| 2 | 新增一个 Chat 场景(新的 chat_mode) | [add-new-scene.md](./add-new-scene.md) |

接下来要补的(按优先级):

- `add-new-datasource.md` — 接一个新数据源
- `add-new-skill.md` — 新增一个 Skill
- `add-frontend-page.md` — 新增一个前端页面

## 怎么使用

1. 找到最接近你需求的 playbook(上面表格里按业务场景分)。
2. **从头到尾读一遍**,不要跳读。
3. 按"改动清单"一步步做,每做一步对照一次"自检"。
4. 做完后把"自检清单"和"影响面说明"贴进 PR 描述。

## 如果找不到对应的 playbook

说明这是一个非常规需求,必须 **先找 Lead 讨论**,不要自己闯。原因有二:

- 没有 playbook 意味着 Lead 还没把它标准化,需要 Lead 判断它应该落在 5 条主干的哪一段
- 如果讨论之后定下来了,Lead 会让你顺手把这份 playbook 补出来,变成团队资产

## 写新 Playbook 的格式

所有 playbook 统一 5 段:

1. **什么时候用这份 playbook**(匹配条件,越具体越好)
2. **主干定位**(明确告诉读者落在 5 条主干的哪一段)
3. **改动清单**(编号步骤,每步说明改哪个文件、贴什么模板)
4. **验证**(跑哪些命令、手动触发什么路径)
5. **PR 描述模板**(直接可复制到 PR body)
