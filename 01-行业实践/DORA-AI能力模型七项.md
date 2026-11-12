# DORA AI Capabilities Model：七项能力（v2 回查补齐）

> 归档日期：2026-11-11 ｜ 类别：行业实践 / 官方研究
> 可信等级：**A**（`dora.dev` 官方 2025 infographic PDF、Google 官方博客、dora.dev 上 companion guide 的介绍）；第三方解读标 B。
> v1 只写了「提出七项能力模型」而未列全，本档补齐，并修正 v1 中证据强度过高的表述。

---

## 1. 七项能力（官方 infographic 原文顺序）

| # | 能力 | DORA 的含义 | 与手册的映射 |
|---|---|---|---|
| 1 | **Clear and communicated AI stance**（清晰且已沟通的 AI 立场） | 组织对 AI 辅助工具的立场必须明确并传达；模糊会抑制采纳并制造风险；清晰的政策给开发者试验所需的心理安全 | E3、A1 |
| 2 | **Healthy data ecosystems**（健康的数据生态） | 内部数据质量足够高、统一、可访问，AI 才用得上 | B5、E3 |
| 3 | **AI-accessible internal data**（AI 可访问的内部数据） | 把内部文档、代码库、风格指南、API 文档、安全策略接给 AI；DORA 称这是从 **prompt engineering 走向 context engineering** | A1、B5、CEM |
| 4 | **Strong version control practices**（强版本控制） | AI 提高代码变更的量与速度，版本控制成为关键安全网：频繁提交、可用回滚 | A2、B4、D1 |
| 5 | **Working in small batches**（小批量工作） | DORA 长期原则，在 AI 辅助环境里「尤其有力」；大改动难评审、难测试、难集成 | **B4** |
| 6 | **User-centric focus**（以用户为中心） | **带警告的一项**：用户中心强的团队采用 AI 后效能提升；缺用户中心的团队采用 AI 后**团队绩效下降** | E1、场景决策 |
| 7 | **Quality internal platforms**（高质量内部平台） | 提供自动化、安全的「paved road」，让 AI 收益跨组织放大，避免个体收益被下游瓶颈吸收 | C4、B6 |

官方 infographic 的顶部结论原文：**"AI's primary role in software development is that of an amplifier"**（AI 的首要角色是放大器）。

### 1.1 平台侧配套数字（A 级官方 infographic）

- 90% 组织已采用至少一个内部平台；29% 处于多平台环境；76% 有专职平台团队。
- 但决定 AI 收益的是**平台质量**，不是平台存在与否 —— 这与 v1 的判断一致。
- 官方给技术领导者的三条：① 用系统视角解决对的问题；② 投资基础系统（内部平台、数据生态、核心工程纪律）；③ **聚焦有效使用，以指导、评估与验证 AI 产出的工作**。

### 1.2 companion guide 提供的方法（B 级，dora.dev 与官方转载）

- 对七项能力逐项给出：实施策略、团队起步的具体战术、监控进展与持续改进的方法。
- 七种**团队原型**（cluster analysis，从 Harmonious high-achievers 到 Legacy bottleneck / foundational challenges），用于定位改进优先级。
- **Value Stream Mapping（VSM）**分步引导：可视化从想法到客户的流动，找出工作在哪里等待，确保 AI 带来的局部提速不变成下游堆积。
- 90 分钟团队工作坊格式，用于排定先修哪项能力。
- 三阶段 context engineering 路径：**手工组装 briefing packets → RAG / MCP server 试点 → 组织级铺开**。

## 2. 对 v1 的两处修正

### 2.1 「小批量 + 测试是止血机制」→ 降级为「DORA 的解释与建议」

DORA 2024 的数据是**横断面调查的建模关联**（每 25% 采纳率 ↔ 吞吐量 −1.5%、稳定性 −7.2%，89% 不确定区间），不是「团队采用 AI 后观测到的下降」，更没有做干预实验。因此：

- ✅ 可以说：DORA **提出**变更集变大是可能机制，并**建议**恪守小批量与稳健测试。
- ❌ 不可以说：治理/评审/小批量已被证明能消除 AI 带来的不稳定性。
- 合适的表述：**「我们预期这有帮助，并会去测量」**（prompt-to-prototype 对证据性质的梳理，B 级）。

DORA 2025 官方博客进一步称吞吐量关联「较去年正向反转」，但强调「确保软件在交付用户前按预期工作仍是持续挑战」。两年结论方向不同，**共同且稳定的是下游验证与稳定性承压**。

### 2.2 「验证税」不是本手册自创

DORA 2026-03 的指引中已有 **verification tax** 提法：「生成阶段省下的时间常被重新分配到 verification overhead 与 prompting overhead」。同一指引要求停止依赖 output-based metrics（代码行、license、token、原始 PR 数）。
⚠ 目前该表述来自 B/C 级转述（re:cinq 等），**未回查 DORA 原文**，故手册沿用术语但标注「行业已有提法（待回查）」，不声称原创、不作为硬结论。

## 3. 与其他来源的交叉印证

| DORA 能力 | 独立佐证 |
|---|---|
| 强版本控制 / 可回滚 | aider git 集成（A2/B4） |
| 小批量 | DORA 2024 机制解释（A）、GitClear churn 趋势（B） |
| AI 可访问内部数据 / context engineering | Anthropic 官方 context engineering（A）、aider repo map（A）、`AGENTS.md`（A） |
| 清晰 AI 立场 | OpenSSF / CISA 指引、OWASP least agency（B） |
| 高质量平台与快速反馈 | 亚信三团队实证（B/C）、METR 边界讨论（A） |
| 用户中心 | Vibe Coding 综述的「质量仲裁者」角色（A） |

## 4. 来源

- `https://dora.dev/research/2025/2025-DORA-Report-Infographic.pdf`（**A**，官方 infographic，七项名称与顶部结论）
- `https://dora.dev/`（**A**，AI Capabilities Model companion guide 介绍）
- `https://blog.google/innovation-and-ai/technology/developers-tools/dora-report-2025/`（**A**，Google 官方博客）
- Storer & DeBellis, *Introducing DORA's inaugural AI Capabilities Model*, Google Cloud, 2025-09-23（**A/B**，本轮通过 re:cinq 与 roboticcontent 的引用核对，未直接打开原文）
- `https://roboticcontent.com/from-adoption-to-impact-putting-the-dora-ai-capabilities-model-to-work`（B，DORA 团队内容的转载/解读）
- `https://re-cinq.com/topics/dora-metrics`（B/C，DORA 2026-03 verification tax 与指标口径转述）
- `https://prompt-to-prototype.com/evidence/productivity-studies`（B，对 DORA 相关性性质的方法论梳理）

## 5. 待补

companion guide 全文（每项的实施策略与监控方法）、Storer & DeBellis 原文、DORA 2026-03 指引原文。见 `06-来源索引/存疑与待核实.md`。
