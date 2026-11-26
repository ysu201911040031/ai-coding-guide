# 开工准备：GitHub 侧提案横向对照

> 归档日期：2026-11-17 ｜ 检索范围：GitHub 官方博客、arXiv、6 个仓库 README 原文 + API 元数据
> 对应手册：**A3 / A4 / A6**（新增 A6 之后的第一轮外部校验）
> Provenance：AI 生成（本会话调研与实测），人工未改动
> 一句话结论：**GitHub 侧对「开工前该准备什么」已收敛出一份高度一致的清单，但同一天发布的实测论文给这份清单泼了冷水——它证实了「精简 + 只写非默认」，否掉了「仓库概览」。**

---

## 0 · 怎么读这份对照

1. **等级只按「能不能回到原文」分**，不按 star 分。A = 一手可回查；B = 机构自报或大样本调查；C = 二手转述、需回锚。
2. **凡「同一来源不同版本」必须带版本号**。本轮实测到一篇博客的标题与正文口径互相打架（§3.1），一篇论文的三个版本结论方向不同（§3.2）。
3. **本文只回答「开工前准备什么、先准备哪个」**，不回答「AGENTS.md 每段怎么写」——后者在 `规则文件约定-AGENTS与CONVENTIONS.md`，不在这里重复。

---

## 1 · 结论先行

1. **「开工前」不是造脚手架，是开一次会**。Shree Mulay 的原话：`Day Zero should be a conversation before it becomes a diff`。这一条与 A6「项目骨架是人的判断，AI 只能给候选与理由」是同一个意思，但它给了更硬的机制：**plan mode 先行，任何 mutate 之前先批准**。
2. **清单本身收敛了**：AGENTS.md（规则）+ 规格/意图文件 + 持久化待办 + 契约测试 + 三层边界 + 命令前置。六家提案在这六项上几乎无分歧。
3. **清单的收益被高估了**。ETH Zurich 实测（138 实例 / 12 仓 / 5,694 PR）：上下文文件**不普遍提升**任务解决率，成本 **+20%~23%**（p<0.001%）；`repository overview` 这一项**被证否**。
4. **「一个文件存内容，其余只放指针」已从规范变成工程约束**。`johnpapa/ai-ready` 生成的三行指针文件（`CLAUDE.md` / `.cursorrules` / `copilot-instructions.md` 各三行，全部指向 `AGENTS.md`）理由写得很直白：`One file holds the content; everything else points at it, so nothing drifts.`——这正是 A6「同一事实存两份」禁令的外部实现。
5. **有一个硬上限手册没写**：Codex 默认 `project_doc_max_bytes = 32 KiB`，合并后**静默截断、无警告**。这不是「建议精简」，是超过就有一半内容根本没被读到。

---

## 2 · 六家提案横向对照

| 提案 | 提出什么 | 关键机制（可借的） | 等级 | 回查状态 |
|---|---|---|---|---|
| **GitHub 官方博客**《How to write a great agents.md》<br>Matt Nigh，2025-11-19 / 更新 11-25 | 六大核心区：commands / testing / project structure / code style / git workflow / **boundaries** | **三层边界**：`✅ Always do` / `⚠️ Ask first` / `🚫 Never do`；**命令前置**（带 flag，不只写工具名） | **A** | 全文已读 |
| **agents.md 官方规范** | 60k+ 项目采用；无必填字段、无 schema、就近覆盖 | **显式用户指令覆盖一切**；但 agent **会自动执行**列出的测试命令 | **A** | 全文已读 |
| **Shree Mulay**《Day Zero》<br>2026-07-08 | 四件套：`AGENTS.md` / `openspec/project.md` / `Beads` issues / **contract tests** | **纪律漏斗**：71/94 (75%) → 31/94 (33%)；**plan mode 在任何 mutate 之前** | **B**（个人审计，作者自认口径局限） | 全文已读 |
| **ETH Zurich** arXiv:2602.11988<br>v1 2026-02-12 / v3 2026-09-29 | 首次**受控测量**上下文文件到底有没有用 | 结论是「**只写代码里读不到的、超出默认的东西**」 | **A** | 摘要 + 正文数据已核 |
| **franklioxygen/agent-workflows**<br>MIT · 81★ · 2026-05-29 | **Preflight 八问** + **Triage Gate 三档** | 三档分诊：`Minimal`（跳过全套流程）/ `Standard` / `Complex`（跑满 Step 0–5） | **B** | README 已读 |
| **AntoGA/agents-contract**<br>MIT · 20★ · 2026-10-19 | 五节契约 + 零依赖 linter + SessionStart hook | 把「规则文件本身的质量」变成机器可查：`E030` 禁止残留占位符、`E040` 禁止类密钥串、`W050` 反引号路径必须真实存在、`W101` >32 KiB 警告 | **A**（实现可跑） | README 已读 |

**交叉共识（六家里 ≥4 家提到）**：命令要给**可执行原文**、边界要**分档**、规则要**短**、开工前**先出计划再动手**。

**分歧点只有一个**：规格/意图文件放哪。Day Zero 说 `openspec/project.md`，spec-kit 说 `.specify/memory/constitution.md`，而 OpenSpec 自己在 2.0 里已经把这个文件废了（§3.3）。

---

## 3 · 三处二手转述与一手原文不符

> 这一节比 §2 值钱。**三处全部来自中文技术社区与 AI 摘要**，且都能在原文里找到反例。

### 3.1 「分析了 2,500 个仓库」→ 实际是 **2,500 份文件**

**流传版本**（多篇中文解读、连 GitHub 自己的副标题都这么写）：

> `from analyzing 2,500+ repositories`

**正文原文**（同一页面，出现两次）：

> `I analyzed over 2,500 agents.md files across public repos to understand how developers were using agents.md files.`
> `My analysis of over 2,500 agents.md files revealed a clear divide between the ones that fail and the ones that work.`

**为什么这条要紧**：仓库数与文件数差一个量级。一个 monorepo 可以放 88 份 AGENTS.md（该文另一处自己举的例子），所以 2,500 份文件可能只覆盖几百个仓库。**用它论证「多数项目都这么干」会把样本量吹大一个数量级。**

**处置**：引用只写「2,500+ 份 `agents.md` 文件」，并注明来自副标题的「repositories」与正文冲突。已登记 `06-来源索引/存疑与待核实.md`。

### 3.2 「人类写的文件提升 4%」→ 实际 **+2.4%，p=0.21，不显著**

**流传版本**（至少 3 篇英文解读，中文区已开始转）：

| 宣称 | 实际情况 |
|---|---|
| `Developer-written AGENTS.md: +4% improvement` | 论文 4.2 节：`improve agent performance by 2.4% on average (p=21%)` |
| `LLM-generated: −3%` | SWE-bench `−0.5%`（p=0.87）、CTXbench `−2%`（p=0.37），**两者都不显著** |
| 基准名 `AGENTbench` | 论文里叫 **`CTXbench`** |

**更关键的方向偏差**：这些解读的叙事是「人类写的有小幅收益，机器写的倒扣」。而**论文 v1 摘要的措辞严厉得多**：

> `we find that context files tend to reduce task success rates compared to providing no repository context, while also increasing inference cost by over 20%`

即 v1 说的是**两类都倾向降低**，不是「人类写的有 +4%」。到 v3 摘要才改成较中性的 `does not generally improve`。

**论文自身也有一处不一致**：引言写 `outperform LLM-generated ones by a significant margin of 7% on average`，4.2 节却是 +2.4% vs −2%（差值约 4.4%）。引用应以 4.2 节与表 3 为准。

**处置**：手册与本文只引 v3 摘要的定性结论 + 4.2 节的数字，并注明「p 值均不显著，样本 138 实例、12 个 Python 仓库」。**不引 4% 这个数**。

### 3.3 `openspec/project.md` 已被 OpenSpec 自己废弃

Day Zero 那篇（2026-07-08）把 `openspec/project.md` 列为四件套之一。而**本机快照的 OpenSpec 2.0.0** 里，这个文件已是 legacy：

> `The old project.md was passive—agents might read it, might not, might forget what they read. We found reliability was inconsistent.`
> 新机制：`openspec/config.yaml` 的 context 段，`actively injected into every OpenSpec planning request`
> 代价原文：`Because context is injected into every request, you'll want to be concise.`

**两件事同时成立**：文章没写错（当时 `project.md` 确实是官方推荐），但只过了 4 个月就作废。**这是「引用必带版本口径」最便宜的一个例子**——同一句话，带不带版本号，可信度差一个量级。

---

## 4 · ETH Zurich 的冷水：它到底打的是谁

先说**它没打的东西**：论文只测**任务解决率**（issue 是否被关掉），不含代码效率与安全性（作者自列局限）；只测 **Python**，且是 12 个「小众、本来就带开发者上下文文件」的仓库；138 个实例、p 值全不显著。**样本量不足以支撑「AGENTS.md 没用」这种强结论。**

再说**它确实打中的东西**——三条，都能对上手册：

| 打中的是什么 | 原文 | 手册哪条要改 |
|---|---|---|
| **仓库概览 / 目录树没用** | `repository overviews, although popular and recommended by model providers, are not helpful`；效果指标是「碰到 PR 实际修改文件之前的步数」，**没有下降** | **A6 要改**：不能把目录结构表写进 `AGENTS.md` 正文 |
| **规则被良好遵守，但遵守本身是成本** | `coding agents tend to respect their instructions`；提到 `uv` 时使用率 1.6 次/实例 vs 未提及 <0.01 次 | A1 已有（上下文预算），A4 要加强「删掉 AI 本来就会做的事」 |
| **只在「超出代码已有信息」时有用** | v1：`human-written context files should describe only minimal requirements`；v3：`useful for specifying non-standard coding practices` | A4 的「只写非默认」从偏好升级为**实测支撑** |

**一个反证细节值得记**：把测试仓库里所有文档（`.md`、示例、`docs/`）删掉后，LLM 生成的上下文文件**反而平均提升 2.7%**，并超过开发者版本。说明这类文件的内容**大部分是在复述 README**——README 在，它就是冗余；README 不在，它才补位。

> **据此的推论（标为推测，需实测）**：本仓库已有 `README.md` + 手册 + 速查表，再写一份 `AGENTS.md` 概述目录，大概率是重复。**A6 的 `docs/ai/` 应只放「代码里读不到的判据」（如「不许用 X，因为 2026-xx 踩过坑」），不放结构说明。**

---

## 5 · 与 A6 的对照：印证 / 修正 / 还缺

### 5.1 印证（三处，A6 不用改）

| A6 的写法 | 外部印证 |
|---|---|
| 「项目骨架是**人的判断**，AI 只能给候选与理由」 | Day Zero：`Day Zero should be a conversation before it becomes a diff`；`plan mode first: read-only inspection, explicit assumptions, a narrow first milestone, and approval before anything mutates` |
| 「同一事实存两份 → 应规避」 | `ai-ready` 的实测做法：`One file holds the content; everything else points at it, so nothing drifts`，且指针文件**硬性三行** |
| 「记忆归口一处，其余都是镜像」 | `ai-ready` 的重跑机制：`On subsequent runs, it audits your existing AI-ready files against the current state of your codebase — flagging drift`，但 `It never overwrites your files` |

### 5.2 修正（两处，A6 需要动）

**修正一：`docs/ai/` 不能放「目录结构说明」。**

A6 现写「`docs/ai/` 只放索引与 3–5 篇专题，不放大段规范」。这句本身没错，但**没说清「索引索引的是什么」**。按 §4，索引**不能索引目录结构**（论文证否），只能索引**判据**：为什么这么选、否决过什么、哪里不能碰。

建议改法（最小改动，不动条目结构）：把「索引」二字具体化为「索引**判据**，不索引**结构**」。

**修正二：加一条硬上限。**

A6 没有量化「短」。Codex 的实测上限是合并后 32 KiB 静默截断。这与 A6 现有的「`docs/ai/` 只放 3–5 篇」是同一件事的**机器侧依据**，值得写进去——因为它把「建议」变成了「超了就有一半读不到」。

### 5.3 还缺（两处，A6 未覆盖，但属「开工前」范畴）

**缺一：没有「按项目规模分诊」。**

A6 的六条勾选项对「一个 300 行的脚本」和「一个多服务系统」一视同仁。`franklioxygen/agent-workflows` 给了现成的三档：

| 档 | 判据 | 流程 |
|---|---|---|
| `Minimal` | 单入口脚本 / CLI / 小库，无服务无数据库 | **跳过全套**，直接脚手架 |
| `Standard` | 有服务、数据库、API、前端或构建流水线 | 从「收集需求」开始，可省的节省掉 |
| `Complex` | 多组件、monorepo、多部署目标、跨团队 | 跑满全流程 |

**缺二：没有「契约测试」这一件。**

Day Zero 的四件套里，`contract tests` 是**唯一一件 A6 完全没有的**——A6 管布局（东西放哪），不管验证（怎么算开工成功）。而 Day Zero 的数据恰好说这是最常被漏的一件：**31/94（33%）**，比规则文件低 42 个百分点。

> 但**不建议**塞进 A6。理由：A6 已 33 行，且「契约测试」是**验证**问题，属 F 组（证据与验收），不是布局问题。按 A6 自己写的「与 A5 的分界」同理，应该由 F 组某条承担，或新开一条。

---

## 6 · 开工前的准备清单（按规模，可直接抄）

> 取自上述六家的交集，不引入任何单一来源的独家主张。**三档只用一档**，不要全做。

**三档通用（3 分钟，任何项目都做）**
- [ ] 写一行：这个项目**不做什么**（非目标）。Shree Mulay：`If the repo does not say what is out of scope, the agent will expand.`
- [ ] 写**可执行**的构建/测试命令原文，带 flag（不是「按规范构建」）。
- [ ] 列 `🚫 Never` 三条：不碰的目录、不提交的凭据、不改的生成文件。

**`Standard` 追加**
- [ ] `AGENTS.md` 分三层边界（✅/⚠️/🚫），**不写目录树**（§4）。
- [ ] 一份意图文件：项目为什么存在、第一个能力是什么。放 `docs/ai/` 或工具自己的位置，**只此一份**。
- [ ] 待办落在仓库里（issue / `TODO.md` 都行），不留在对话里。

**`Complex` 追加**
- [ ] `plan mode` 先出计划，批准后才允许 mutate。
- [ ] 一条契约测试：锁住「第一个公开行为」（路由存在 / 文件有必需字段 / parser 拒绝坏输入）。
- [ ] 每个子包一份短 `AGENTS.md`，就近覆盖；总数控制在合并后 32 KiB 以内。

---

## 7 · 实测元数据与淘汰名单

> 全部 2026-11-17 经 `api.github.com` 直查。**不登记 star 作成熟度判据**，此处只为说明「这个仓有多新」。

| 仓库 | ★ | 许可 | 最近提交 | 结论 |
|---|---|---|---|---|
| `johnpapa/ai-ready` | 239 | MIT | 2026-09-27 | ✅ 可读可借（指针文件 + 行数预算 `AGENTS.md` 150 行） |
| `franklioxygen/agent-workflows` | 81 | MIT | 2026-05-29 | ✅ 可读（Preflight 八问 + 三档分诊） |
| `Taiizor/agents-md-cookbook` | 29 | MIT | 2026-08-08 | ✅ 可用（`agents-md-lint` + `agents-md-migrate`） |
| `AntoGA/agents-contract` | 20 | MIT | 2026-10-19 | ✅ 可用（零依赖 linter，规则最硬） |
| **`michaelshimeles/rstack`** | 1,525 | **NO-LICENSE** | 2026-11-05 | ⚠️ **只读不可抄**。保留所有权利；内容是「worktree 隔离 + 证据前置 + before/after 证明」，值得看，**一个字都不能搬** |
| `mattpocock/skills` | 326,097 | MIT | 2026-11-13 | 可参考，但与本主题弱相关 |
| `obra/superpowers` | 318,788 | MIT | 2026-11-03 | 已在 `02-开源经验/横向对照` 覆盖 |
| `github/spec-kit` | 150,153 | MIT | 2026-11-16 | 已有；`constitution-template.md` 带 **Version / Ratified / Last Amended**，是 A5 的外部印证 |
| `Fission-AI/OpenSpec` | 75,026 | MIT | 2026-11-17 | 已有；2.0 废弃 `project.md`（§3.3） |
| `gastownhall/beads` | 28,793 | MIT | 2026-11-15 | Day Zero 四件套之一；**注意已从 `steveyegge/beads` 迁移到 `gastownhall/beads`**，旧地址 301 |
| **`jbuz/pre-flight-check`** | **0** | MIT | 2025-11-25 | ❌ **淘汰**：创建当天唯一一次提交，一年未动 |
| **`tokwalabs/claude-code-playground`** | **0** | Apache-2.0 | 2026-10-01 | ❌ **淘汰**：`pushed_at` 早于 `created_at`，元数据不自洽 |
| **`YuanyuanMa03/awesome-agents-md`** | **0** | — | 创建日 = 检索日 | ❌ **淘汰**：当天创建，疑刷榜 |
| **`polarislin19/Memory-Keel`** | **0** | — | 创建日 = 检索日 | ❌ **淘汰**：同上 |

**淘汰判据（可复用）**：`star=0` 且 `created_at` 与 `pushed_at` 同日 → 一次提交后放弃，必须先看提交数再看内容。

---

## 8 · 来源

| 编号 | 来源 | URL | 版本 / 口径 | 等级 |
|---|---|---|---|---|
| L-13 | GitHub 博客《How to write a great agents.md》 | https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/ | 2025-11-19 发布 / 2025-11-25 更新；**2,500+ 份文件**（副标题误作 repositories） | **A** |
| L-14 | Gloaguen et al.《Evaluating AGENTS.md》 | https://arxiv.org/abs/2602.11988 | **v3 2026-09-29**（v1 2026-02-12，两版结论措辞不同）；CTXbench 138 实例 / 12 仓 / 5,694 PR | **A** |
| L-15 | Codex `AGENTS.md` Discovery 文档 | https://github.com/kexinoh/codex/raw/refs/heads/main/docs/agents_md.md | 镜像非官方域；`project_doc_max_bytes` 默认 32 KiB，静默截断 | **A/B**（内容一级，域名二级） |
| L-16 | Shree Mulay《Day Zero: I Audited How My AI Projects Actually Begin》 | https://shreemulay.com/writing/how-my-projects-begin | 2026-07-08；**94 个本人项目目录**，作者自认「非同类产品」 | **B** |
| L-17 | OpenSpec 迁移指南（本机快照） | `_extern/openspec/docs/migration-guide.md`，commit `d12c281` | `package.json` version **2.0.0**；`project.md` → `config.yaml` | **A** |
| L-18 | spec-kit `constitution-template.md`（本机快照） | `_extern/spec-kit/templates/constitution-template.md`，commit `979b0a3` | 含 Version / Ratified / Last Amended 三字段 | **A** |
| L-19 | `johnpapa/ai-ready` README | https://github.com/johnpapa/ai-ready | 239★ / MIT / 2026-09-27 | **A**（仓库自述） |
| L-20 | `franklioxygen/agent-workflows` § Preflight + Triage Gate | https://github.com/franklioxygen/agent-workflows/blob/master/project-initialization-agent-workflow.md | 81★ / MIT / 2026-05-29 | **B** |
| L-21 | `AntoGA/agents-contract` README（lint 规则表） | https://github.com/AntoGA/agents-contract | 20★ / MIT / 2026-10-19；规则码 E001–W101 | **A** |

---

## 9 · 本文没做的事（留给下一轮）

1. **没测本仓库自己的 `AGENTS.md` 是否真的改变行为**。§4 的推论是推测，要验需 A/B：同一任务，带与不带 `AGENTS.md` 各跑一次，比 `diff` 与返工次数。
2. **没核 Day Zero 的 71/65/49/47/31 五个数是怎么数出来的**。作者只说「看了 94 个目录」，未给计数脚本。**五个数只能当方向，不能当比例引用。**
3. **没评估 `Beads` 本身**。它已从 `steveyegge/beads` 迁移到 `gastownhall/beads`（旧地址 301），迁移原因与治理变化未查。
