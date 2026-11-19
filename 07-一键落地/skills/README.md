# Skills：把流程做成可触发的制品

> 三个流程 skill：`project-kickoff`（开工对齐）/ `diagnose`（诊断）/ `session-close`（收尾）。
> **它们不复述规则**，只负责"什么时候触发、按什么步骤走、什么算完成"；硬约束仍以 `../core/00-协作铁律.md` 为准。

## 为什么是 skill，不是再加三条准则

规则是散文，读不读、读没读进去，不可观测。skill 有 frontmatter 里的 `description`，工具会在任务开始时按描述判断是否加载；正文只在触发后进上下文。**这正好绕开规则文件越写越长的老路**（M1 / A1）。

## 结构（每个 SKILL.md 六段）

```
---
name: lowercase-hyphen-name
description: 做什么 + Use when ...（触发条件写全，工具靠它匹配）
---
Overview        这是什么、产出什么
When to Use     什么时候触发；什么时候不触发
Process         步骤 + 检查点；不是参考资料
Rationalizations 常见借口 → 逐条反驳
Red Flags       出现这些信号说明流程被跳过
Verification    出口证据；"看起来对"不算
```

## 安装

各工具的 skill 目录不同，**装之前先实测一次，不猜路径**。已知两个：

| 工具 | 路径 | 证据等级 |
|---|---|---|
| Qoder Desktop（用户级） | `~/.qoder-cn/skills/<name>/SKILL.md` | A（本会话已加载同目录下的 skill） |
| Claude Code（用户级） | `~/.claude/skills/<name>/SKILL.md` | C（官方文档口径，未在本机实测） |

复制整个目录即可，不改内容：

```bash
cp -r 07-一键落地/skills/project-kickoff ~/.qoder-cn/skills/
```

## 验收（三条，缺一不可）

1. **能触发**：新会话里只说"开工做一个 X"，不点名 skill，它应被加载。
2. **有出口**：触发后产出任务卡 / 复现证据 / 交接五行，而不是一段泛泛建议。
3. **删除正文即失效**：把 Process 段临时删掉，触发后不再产生上述产物——证明起作用的是流程，不是描述。

## 与规则、开工卡的分工

| 层 | 管什么 | 位置 |
|---|---|---|
| 规则 | 不可违背的硬约束 | `core/00-协作铁律.md` |
| 开工卡 | 每个会话一次的环境/基线/复用提醒 | `preflight/preflight.py` |
| skill | 具体任务的流程触发与出口条件 | 本目录 |

三层不互相复述。改动任何一层，先问"这条是不是已经在另一层写过"。
