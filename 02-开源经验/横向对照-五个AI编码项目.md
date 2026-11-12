# 横向对照：五个 AI 编码项目（spec-kit / OpenSpec / Superpowers / Aider / GPT Engineer）

> 归档日期：2026-11-12 ｜ 证据：本机源码快照（`_extern/`，commit 见文末）+ GitHub API 元数据（同日查询）
> 对应手册：A2 / B1 / B2 / B3 / B4 / B7 / C1 / C2 / D1 / E4 / G4 / J6 / M1
> 一句话结论：**五家不是同一类东西**。它们分属执行工具、规格流程、技能方法三层；本手册是第四层——约束、证据与验证。可以借机制，不必换赛道。

---

## 0. 怎么读这份对照

- **事实**分两类：① 仓库里直接读到的（README、目录、模板、许可证文件）——A 级；② GitHub API 返回的许可、归档状态、最后提交——A 级；③ 厂商自述的"我们比谁好"——B/C 级，只当立场，不当结论。
- **star 数一律不引用**：易变，且本手册规定 star 不作成熟度判据。
- 本文件只写"它是什么、怎么运转、能借什么"，不写"谁更强"。

## 1. 四层模型（先定位，再比较）

| 层 | 解决什么 | 代表 |
|---|---|---|
| **L1 执行工具** | 把改动落到文件与 git | Aider（终端结对）、GPT Engineer（整仓生成） |
| **L2 规格流程** | 写代码前先对齐"做什么" | spec-kit、OpenSpec |
| **L3 技能方法** | 让 Agent 按固定套路走 | Superpowers |
| **L4 约束 + 证据 + 验证** | 凭什么信、什么时候停、装没装对 | **本手册 / 规则包 / checks + verify** |

五家都不提供 L4：没有证据分级、没有存疑清单、没有证伪路径、没有"安装后行为验证"。这是本项目的生态位。

## 2. 逐个体检

### 2.1 spec-kit（github/spec-kit，MIT，活跃）

**自我定位**（README 原文）：给编码 Agent 提供结构化流程、可复用模板与可记录产出的开源工具包。

**三条独立入口**（不是必须全跑的阶段）：
- **SDD**：`/speckit-constitution → -specify → -plan → -tasks → -implement → -converge`；重复 implement/converge 直到报告 `Converged`。
- **Bug 修复**（扩展 `specify extension add bug`）：`/speckit-bug-assess → -bug-fix → -bug-test`，报告落 `.specify/bugs/<slug>/`，结论只有 `verified / partial / failed`，**只有 verified 算修好**。
- **Idea 评估**（扩展 `add assess`）：intake → research → define → shape → decide，产出 go / needs-clarification / stop。

**机制**：`specify` CLI（Python 3.11+ / uv）+ 模板（constitution / spec / plan / tasks / checklist）+ 扩展、预设、工作流、bundle、catalog；支持多 Agent 接入，可按组织/合规定制预设。

**强制力**：流程与模板层。它规定"按什么顺序产出什么工件"，**不拦动作**——不会阻止 Agent 直接执行 `rm -rf`。

**与本手册对应**：B2（先工件后实现）、B3（计划与执行分离）、C2（缺验证不算完成，bug 三态是现成实现）。

**可借**：① bug 的 `assessed / fixed / verified` 三态；② "每个阶段一份工件"的硬性产物清单；③ 扩展/预设的分层，避免把流程写死。
**不借**：小任务跑完整流水线（撞 B8 的"3 轮不收敛就动手"与 M1 的注意力预算）。

### 2.2 OpenSpec（Fission-AI/OpenSpec，MIT，活跃）

**自我定位**：轻量规格层，让"规格"成为人与 Agent 的共同底稿；明确面向 brownfield。

**目录结构**：
```
openspec/
├── specs/                  # 系统当前行为（唯一事实来源，按能力分）
├── changes/<name>/         # 进行中的变更：proposal.md / specs/ / design.md / tasks.md
└── changes/archive/…       # 完成后归档，增量并回 specs
```

**流程**：`/openspec-explore`（先想清楚）→ `/openspec-propose`（生成变更目录）→ `/openspec-apply-change` → `/openspec-archive-change`。扩展档还有 new/continue/ff/verify/bulk-archive/onboard。

**关键差异**：**增量 + 归档合并**。只规范这次要改的部分，不用给存量代码补全量文档；完成后变更归档、规格更新，而不是留在 PR 里。

**强制力**：技能与文本约定，同样不拦动作。官方自述"no rigid phase gates"（B/C，厂商立场）。

**与本手册对应**：B2、E4（教训回流成规则——它是"变更回流成规格"）、D6（存量维护）。

**可借**：`change → archive → specs 合并` 这条闭环，正好补 B2 缺的"变更完成后如何沉淀"。
**不借**：Stores（跨仓规划，beta）对单人过重；多套 profile 容易变成"流程选项疲劳"。

### 2.3 Superpowers（obra/superpowers，MIT，活跃）

**自我定位**：一套完整的软件开发方法论，以可组合技能（skills）实现，并靠初始指令确保 Agent 真的会用。

**主链路**（README 自述）：
```
问清你到底要做什么 → 分块给出规格 → 设计签字
 → 写实现计划（细到"一个没品味、没判断、没项目上下文、讨厌测试的初级工程师也能照做"）
 → subagent-driven development：每个任务派新子代理，逐个检查与评审
 → 红/绿 TDD、YAGNI、DRY
```
技能自动触发，共 15 个（本地快照）：brainstorming、writing-plans、executing-plans、subagent-driven-development、test-driven-development、systematic-debugging、requesting-code-review、receiving-code-review、verification-before-completion、using-git-worktrees、dispatching-parallel-agents、finishing-a-development-branch、writing-skills、diagnosing-superpowers、using-superpowers。

**强制力**：技能触发 + 评审流程；跨 harness（Claude Code、Codex、Cursor、Gemini CLI 等，按各自插件机制安装）。**不是安全边界**。

**与本手册对应**：B3/B4、B7（并行只在读密集、独立任务）、C1/C2、G3/G4、J6。

**可借**：① **两阶段审查**（先查是否符合规格，再查代码质量，顺序不可反）；② **verification-before-completion**（完工前必须跑验证）；③ "测试前写的代码要删"比"先红后绿"更硬。
**不借**：技能全量自动触发（15 个技能常驻会挤上下文，撞 M1）；子代理默认并行（撞 B7 与 J5 的审查带宽）。

### 2.4 Aider（Aider-AI/aider，Apache-2.0，活跃）

**自我定位**：终端里的 AI 结对编程。

**机制**：git 自动提交（可 diff / undo）｜repo map（tree-sitter 符号图）｜100+ 语言｜architect/editor 双模型｜IDE watch（注释触发）｜图片与网页上下文｜语音｜每次改动后跑 lint/test｜可接本地模型。

**强制力**：工具行为层——它真的会 commit、真的会跑 lint/test（是否放行由你配置）。**自动 commit 是安全网，不是审查替代品**（D1）。

**与本手册对应**：A2（dirty 检查 + 干净基线）、B4（小批量可回溯）、D1（产出当待审 PR）。

**可借**：把"每次请求前检查工作区是否干净"做成机械习惯（A2 已有，但常靠人记）；`/undo` 式回滚体验。
**不借**：把自动 commit 当审查通过；大重构时的 token 成本要提前估（单次改动可能吃掉大量预算）。

### 2.5 GPT Engineer（AntonOsika/gpt-engineer，MIT，**已归档**）

**自我定位**（README 原文）："The OG code generation experimentation platform"——并明确让读者去看 aider（"well maintained hackable CLI"）和 gptengineer.app（托管服务）。

**机制**：`prompt` 文件 → `gpte <dir>` 生成整个代码库；`-i` 改进存量；`preprompts` 定义 Agent 身份；支持视觉输入与 `bench` 基准。

**状态**：GitHub API 显示 **archived: true**，最后提交 2025-05-14。属于历史项目，不是当前工具链。

**与本手册对应**：B1 的 UAM（无约束自动化）——**只适合一次性原型，生产禁用**；与"先修坏模式再让 Agent 进去"（M4/额外建议 15）直接冲突。

**结论**：只作历史参考，不纳入日常流程。

## 3. 横向矩阵

| 维度 | spec-kit | OpenSpec | Superpowers | Aider | GPT Engineer |
|---|---|---|---|---|---|
| 层 | L2 规格流程 | L2 规格流程 | L3 技能方法 | L1 执行工具 | L1 生成工具 |
| 入口 | `specify` CLI + skills | `openspec` CLI + skills | 插件/技能，自动触发 | 终端 CLI | `gpte` CLI |
| 核心产物 | constitution/spec/plan/tasks/bugs | specs + changes + archive | 计划、子任务、审查记录 | commit + repo map | 整个 workspace |
| 强制力 | 流程/模板 | 技能/文本 | 技能触发/评审 | 工具行为 | 几乎无 |
| 许可 | MIT | MIT | MIT | Apache-2.0 | MIT |
| 活跃度（API） | 2026-11-11 | 2026-11-11 | 2026-11-03 | 2026-05-22 | 已归档 |
| 单人日常 | 中大型才值 | 中等改动合适 | Claude Code 下强 | 可直接用 | 不建议 |
| 提供证据分级 | 否 | 否 | 否 | 否 | 否 |

## 4. 可吸收的四个机制（落进现有条目，不新开章）

| 机制 | 来源 | 落到哪 | 具体改法 |
|---|---|---|---|
| 变更完成后归档并合并回规格 | OpenSpec | B2 / E4 | 任务收尾多一步："这次改动更新了哪条规则/约定？"没有就写"无" |
| 两阶段审查：先规格后质量 | Superpowers | C2 / D1 | 验收顺序写死：① 做的是不是这件事 ② 做得好不好 |
| 只有 verified 算修好 | spec-kit | C2 | 缺陷修复结论只允许 verified / partial / failed 三态 |
| 测试前写的代码要删 | Superpowers | G4 | 先红后绿再加一条：没先写测试就写的实现，回退重来 |

**明确不吸收**：九命令全流水线用于小任务；15 个技能全量常驻；整仓一次性生成；把自动 commit 当审查。

## 5. 选型建议

```
单人 + Qoder（当前）：
  规则层用自己的（已覆盖）→ 想要规格痕迹：OpenSpec
  → 终端结对/回滚体验：Aider（可选）
  → 不建议：GPT Engineer（归档）、spec-kit 全流程

团队 / 跨仓：
  OpenSpec Stores（beta）或 spec-kit（扩展/预设可定制）二选一，别同时上

原型 / 一次性：
  直接用现有 Agent，标"不可上线"并隔离目录；不必引入任何框架
```

判断标准不是"谁功能多"，而是：**它补的是你缺的那一层吗？** 你现在缺的是真实使用证据，不是更多流程。

## 6. 未采信与待核

- **厂商对比**：OpenSpec README 称 spec-kit "thorough but heavyweight. Rigid phase gates"——这是竞品自述（B/C），本文件只记录，不采信为结论。
- **Aider 自报"88% 代码由自己写"**：来自 README 徽章，自报数据，按 E2 不作质量证据。
- **star / 下载量**：一律未引用。
- **Superpowers 的"能自主工作数小时"**：README 自述，未独立复现；按 B7 与 J5，默认不信"长时自主"的收益。
- **OpenSpec Stores**：README 标 beta，未实测。

## 7. 来源与快照

GitHub API 查询日期：2026-11-12。源码为本机 `_extern/` 下的 tarball 快照（无 `.git`）。

| 项目 | 仓库 | commit | 许可 |
|---|---|---|---|
| spec-kit | github/spec-kit | `979b0a3c1277283371c9901ad0eed04b64a99997` | MIT |
| OpenSpec | Fission-AI/OpenSpec | `d12c2817776779e06891d68230773b3bb673b106` | MIT |
| Superpowers | obra/superpowers | `22f0b463e7a5e579904dd6211a520321035526f7` | MIT |
| Aider | Aider-AI/aider | `5dc9490bb35f9729ef2c95d00a19ccd30c26339c` | Apache-2.0 |
| GPT Engineer | AntonOsika/gpt-engineer | `a90fcd543eedcc0ff2c34561bc0785d2ba83c47e` | MIT（仓库已归档） |

对应目录：`_extern/<项目>/README.md`、`LICENSE`；本文件引用的命令与目录名均可在快照内逐条核对。