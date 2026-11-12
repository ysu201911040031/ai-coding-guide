# 开源经验③：Agent 架构、工作流模式与上下文工程

> 归档日期：2026-11-11 ｜ 可信等级：**A** 为主（Anthropic 官方工程博客、12-Factor Agents 项目、SWE-agent / Agentless 论文）；文中标注「C」的排行榜/分数来自社区汇总，不引用。
> 对应手册：B1 / B3 / B5 / C1 / C3 / C5 / D7

---

## 1. Anthropic《Building Effective Agents》（2024-12，官方工程博客，A）

**开篇结论**：与数十个团队合作后，最成功的实现**不是复杂框架，而是简单、可组合的模式**。

### 1.1 关键定义

| 概念 | 定义 |
|---|---|
| **Workflow（工作流）** | LLM 与工具通过**预定义代码路径**编排；人写控制流，模型填决策 |
| **Agent（智能体）** | LLM **动态决定自己的过程与工具使用**，掌握如何完成任务；= 循环 + 工具调用 + 环境反馈 + 停止条件 |

**默认建议**：先找最简单的方案，很多应用「单次 LLM 调用 + 检索 + 上下文示例」就够；只有在简单方案不够时才增加复杂度。工作流给可预测性，Agent 给灵活性，代价是延迟、成本与错误累积。

### 1.2 五种工作流模式

| 模式 | 做什么 | 适用 |
|---|---|---|
| Prompt chaining | 任务拆成固定顺序的 LLM 调用，中间可加**程序化 gate** 校验 | 可干净线性分解、准确率优先于延迟 |
| Routing | 分类输入、分派到专门提示/模型 | 输入类型差异大，优化一类会伤另一类 |
| Parallelization | sectioning（独立子任务并发）/ voting（同一任务多次跑取共识） | 子任务独立，或单次可靠性不够 |
| Orchestrator-workers | 中心模型**运行时动态**拆解任务并分派 | 子任务集合无法预先确定 |
| Evaluator-optimizer | 一个生成、一个批评，循环到达标 | **评估标准清晰且迭代有可测提升**时 |

> 对应手册 C3：evaluator-optimizer 不是万能；标准模糊时每轮只是换个说法，是在烧钱买心理安慰。

### 1.3 三条实现原则

1. **设计简洁**（simplicity）。
2. **透明**：展示 Agent 的计划步骤。
3. **精心设计 Agent-Computer Interface（ACI）**：工具定义值得和主提示同等程度的打磨——清晰文档、示例、自然的格式、参数设计成「难以用错」。

### 1.4 关于框架

框架（Claude Agent SDK、AWS Strands、Rivet、Vellum 等）能简化底层调用，但**额外的抽象层会遮蔽底层 prompt 与响应，使调试变难**，也诱使人加复杂度。建议先用原生 LLM API 起步；若用框架，务必理解其底层代码——「对底层假设错误是客户常见错误来源」。

> 对应手册 D7：分层/抽象边界要看清，不要靠猜测底层行为。

## 2. SWE-agent 与 Agentless：harness 比模型更影响结果

### 2.1 SWE-agent（NeurIPS 2024，A）

- 论文：*SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*（Yang, Jimenez, Wettig, Lieret, Yao, Narasimhan, Press 等，Princeton/Stanford）。
- 核心主张：**「LM agents 是一类新的终端用户，需要为其专门设计的界面」**——把 HCI 的方法论用在 Agent 与计算机之间。
- ACI 不是提示词，而是环境层设计：结构化的搜索/浏览命令、带行号的文件查看器、专用编辑命令、紧凑输出格式、**每一步给出该命令效果的简明反馈**、编译错误等护栏。
- 它解决的三类「界面失败」：搜索结果淹没上下文、导航状态丢失、静默编辑失败（sed 改错直到几步后才以无关错误暴露）。
- 论文报告：GPT-4 Turbo 在原始 SWE-bench 上 **12.5% pass@1**（早期非交互式 RAG 基线约 3.8%），HumanEvalFix 87.7%；**模型没变，界面变了**。

### 2.2 Agentless（arXiv 2407.01489，A）

- 反向做法：**删掉 agent loop**，用固定三阶段 pipeline：
  1. **Localization**：层级收窄（仓库结构 → 文件 → 类/函数 → 具体行）。
  2. **Repair**：生成多个 diff 格式候选补丁。
  3. **Patch validation**：生成复现测试 + 回归测试 + 多数投票选最终补丁。
- 结果：**32.0% SWE-bench Lite（96 个修复），约 $0.70/issue**，当时在分数与成本上胜过所有开源 agent。
- 论文的隐含前提：LLM 不宜使用过多动作或复杂工具。

### 2.3 两条相反路径的共同结论

> 「软件外壳（harness）的设计对结果的影响，可以大于模型本身」——这是手册 1.3 的立论基础。
> 后续 mini-swe-agent 把控制循环压到「约 100 行 Python」，并指出「随着 LM 变强，很多复杂 scaffold 不再必要」；**但控制循环商品化后，上下文管理、状态管理、错误处理仍是工程重点**。

**⚠ 不引用**：社区 wiki 与媒体给出的 2025–2026 模型排行榜分数、模型命名与横向对比表（C 级，版本口径无法核实）。

## 3. 12-Factor Agents（Dex Horthy / HumanLayer，开源项目，A）

**核心洞察**：生产环境跑得好的「AI Agent」**大多不是自主循环，而是确定性软件 + 关键节点上的 LLM 决策**。作者访谈 100+ 开发者后总结出 12 条原则，致敬 Heroku 12-Factor App。

| # | 原则 | 要点 |
|---|---|---|
| 1 | Natural Language to Tool Calls | LLM 把自然语言转成结构化 JSON，确定性代码执行 |
| 2 | Own Your Prompts | 提示词是一等公民代码，不被框架默认提示遮蔽 |
| 3 | Own Your Context Window | 上下文是**注意力预算**，自定义高信号格式 |
| 4 | Tools are Just Structured Outputs | 工具调用本质是结构化输出；模型提议，代码处置 |
| 5 | Unify Execution State and Business State | 一个真相来源，便于调试/恢复/分叉 |
| 6 | Launch / Pause / Resume | 支持在**工具选择与执行之间**暂停，等待人工审批 |
| 7 | Contact Humans with Tool Calls | 把「联系人」建模成工具，human-in-the-loop 是一等步骤 |
| 8 | Own Your Control Flow | 自己写 while 循环与 switch，不把控制流外包给框架 |
| 9 | Compact Errors into Context | 错误压缩成短信号回灌，成功后清理失败轨迹，限制重试 |
| 10 | Small, Focused Agents | 小而专，每个 Agent 3–10 步（最多约 20 步） |
| 11 | Trigger from Anywhere | 可由 webhook / cron / 消息触发，不止聊天窗口 |
| 12 | Stateless Reducer | Agent 是 (state, event) → next state 的纯函数 |
| 附录 13 | Pre-fetch Context | 上下文前置取好，别在执行中反复查 |

**三条底层逻辑**：反框架主义（不是不用库，是别被通用性锁死质量上限）；确定性代码 + LLM 在关键节点决策；小步快跑。

**风险分档（社区对 Factor 1/4 的延伸解读，B 级）**：读取/分析可放行；发送、改配置需确定性代码校验权限与依赖；支付、删除、部署生产必须结构化请求 + 人工审批。对应手册 A3。

**Dumb zone 与上下文**：作者分析大量开发会话后指出，大上下文中间 40–60% 区间模型召回与推理退化；工具越多、上下文越长，Agent 越「笨」。Anthropic 的上下文工程表述为「找到能最大化目标结果概率的**最小高信号 token 集**」。对应手册 B5。

## 4. 对本手册的直接映射

| 开源结论 | 手册条目 |
|---|---|
| workflow vs agent 的划分、先简后繁 | B1（按风险选模式）、B3 |
| ACI：每步给简明反馈、防静默失败 | C1（外部信号）、C5（错误压缩） |
| Agentless 固定三阶段 + 验证 | B2（工件化）、C2（验收标准） |
| Factor 6/7：可暂停、人是一等工具 | A3（不可自动执行清单） |
| Factor 3/9/10 + dumb zone | B5（上下文最小化）、C3（停止条件） |
| Factor 5/12：状态外置、纯函数 | A2 / A5 / 额外建议 6（隔离执行） |
| 框架抽象遮蔽底层 | D7（分层与链接依赖） |
| Anthropic evaluator-optimizer 适用边界 | C3（循环必须划算） |

## 5. 来源

- Anthropic Engineering, *Building effective agents*, 2024-12-19：`https://www.anthropic.com/engineering/building-effective-agents`（A）
- SWE-agent, NeurIPS 2024 / arXiv:2405.15793（A）；Agentless, arXiv:2407.01489（A）
- 12-Factor Agents（HumanLayer）开源项目与多个独立解读（A/B）
- Anthropic 上下文工程相关表述（A，经 12-Factor 解读转引）
