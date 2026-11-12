# 开源经验④：协议、工具边界与最小权限（v2 新增）

> 归档日期：2026-11-11 ｜ 类别：开源经验 / 标准与治理
> 对应手册：H 章（H1–H4）、A3 修订、D7 修订
> **v1 的缺口**：只谈流程与规则，没谈 Agent 通过什么接口触达外部世界、授权该在哪一层做。

---

## 1. MCP 官方规范（A 级，已回查原文）

**来源**：`https://modelcontextprotocol.io/specification/2026-07-28`（MCP 是开放协议，借鉴 LSP 的思路标准化「LLM 应用 ↔ 外部数据源/工具」的集成）

**架构**：JSON-RPC 2.0；2026-07-28 修订把核心改为**无状态、自包含请求**、按请求协商能力（早期修订的 initialize 握手与会话被移除）。角色：Host（发起连接的 LLM 应用）/ Client（host 内的连接器）/ Server（提供上下文与能力）。Server 提供 Resources、Prompts、Tools；Client 可提供 Elicitation。扩展（Tasks、Skills over MCP、MCP Apps）一律 opt-in 且需双方协商。

**安全与信任章节的三条关键原则（原文要点）**
1. **用户同意与控制**：用户必须明确同意并理解所有数据访问与操作；必须保留对「共享哪些数据、执行哪些动作」的控制；实现者应提供清晰的审查与授权 UI。
2. **数据隐私**：Host 在把用户数据暴露给 Server 前必须取得明确同意；未经同意不得把资源数据传到别处；用户数据应有适当访问控制。
3. **工具安全**：**工具代表任意代码执行**，必须谨慎；**工具行为描述（如 annotations）应视为不可信**，除非来自可信 Server；**Host 调用任何工具前必须取得明确用户同意**；用户应在授权前理解工具做什么。

**最关键的一句（原文）**：
> "While MCP itself **cannot enforce these security principles at the protocol level**, implementors SHOULD ..."（协议本身无法在协议层强制这些原则）

→ 这直接支撑手册 A3：**审批必须是宿主/流程层的一等机制，不能指望协议或提示词兜底**。

### 1.1 版本治理（容易被忽略）

MCP 修订以 `YYYY-MM-DD` 命名，实现必须声明自己实现的是哪一版，因为生命周期、传输与特性语义差异很大：
`2024-11-05`（首发，HTTP+SSE）→ `2025-03-26`（Streamable HTTP / OAuth / tool annotations）→ `2025-06-18`（移除 JSON-RPC batching、结构化工具输出、elicitation）→ `2025-11-25`（OIDC Discovery、增量授权、实验性 tasks）→ `2026-07-28`（核心无状态、移除 initialize / 会话、要求 per-request 版本与能力元数据）。

> 工程含义：**「接了 MCP」不等于行为确定**。升级协议版本可能改变工具语义与授权路径，需要像升级依赖一样做回归。

### 1.2 已记录的威胁类型（B 级，来自社区与学术综述）

| 威胁 | 说明 | 对应控制 |
|---|---|---|
| Confused deputy | 代理把上游授权复用于用户未批准的客户端 | 把 consent 绑定到请求方客户端与目标资源 |
| Token passthrough | Server 把 MCP token 转发给另一 API | 校验 audience、另取下游 token |
| SSRF via metadata | 客户端跟随恶意授权元数据访问内网 | 校验 discovery URL、限制重定向与出网 |
| 本地代码执行 | 启动不可信的本地 Server 包即执行任意代码 | 校验命令与发布者、隔离进程、最小权限 |
| **Tool poisoning** | 工具元数据/输出里藏有欺骗模型的指令 | 保留来源、注解视为不可信、重大动作需批准 |
| Overbroad access | Server 拿到超出任务需要的文件/API 权限 | 窄凭据、资源级 scope、操作级确认 |

补一句很重要的：结构化消息能保留**类型与来源**，但**不会让内容变安全**；`serverInfo` 是自报的，`roots` 是描述性的而非沙箱，工具注解是「声明」而非「已验证行为」，OAuth 授予的是访问权而非判断力。

## 2. OWASP Top 10 for Agentic Applications 2026（B 级，三份独立解读交叉确认）

> OWASP GenAI Security Project 于 2025-12 发布（2026 版），经 100+ 行业专家评审；是首个面向自主 Agent 的分类法。本轮未逐条打开官方原文页，清单与 mitigations 来自三份独立解读，标 B 级。

| 编号 | 风险 | 首要控制 |
|---|---|---|
| ASI01 | Agent Goal Hijack（不可信内容里的隐藏指令改写目标） | 指令与数据分离；目标变化前做策略校验；高影响动作人工批准 |
| ASI02 | Tool Misuse（合法工具被以危险方式使用） | 工具最小权限、参数校验、隔离沙箱、高影响调用审批 |
| ASI03 | Identity & Privilege Abuse | 用户/Agent/服务身份分离；短时、任务级凭据；每次动作重新授权 |
| ASI04 | Agentic Supply Chain（MCP server / 插件 / prompt / 模型被投毒） | 批准来源、版本与内容哈希固定、变更评审与吊销 |
| ASI05 | Unexpected Code Execution | 沙箱容器、无「模型直通 shell」、受限解释器、不以 root 运行 |
| ASI06 | Memory & Context Poisoning | 来源标记、会话/租户隔离、未验证记忆随时间衰减、不自摄入 |
| ASI07 | Insecure Inter-Agent Communication | Agent 间认证、消息 schema 校验、防重放 |
| ASI08 | Cascading Failures | 限制爆炸半径、熔断器、回滚与恢复路径 |
| ASI09 | Human-Agent Trust Exploitation | 审批界面展示影响与数据、避免紧迫感与暗模式 |
| ASI10 | Rogue Agents | 清单、行为监控、kill switch、凭据吊销 |

**上位原则：least agency（最小自主权）**——在不需要自主行为的地方部署自主性，只会扩大攻击面而不增加价值。它与可观测性必须成对出现：只有约束没有观测是「盲约束」，只有观测没有约束是「对正在发生的损害做录像」。

**控制点位置**：风险最高的 ASI01/02/05 都发生在「模型推理 → 系统动作」的边界上；**无论什么安全控制，都必须挂在这个边界**，而不是挂在提示词里。

## 3. 官方机构指引（B 级）

- 五国（澳/加/新/英/美）网络安全机构 2026-05 联合发布《Careful adoption of agentic AI services》：**从小处着手、只用于低风险任务、从一开始就施加既有安全控制**。
- NCSC 设计规则：处理外部随机邮件的 LLM 不应同时拥有特权工具；**「如果你无法理解、监控或限制一个 Agent 的行为，它就还没准备好部署」**。
- CISA《Careful Adoption of Agentic AI Services》（2026-05）：**清点每一个 Agent 与 connector、最小权限、全量日志、重大影响动作需人工批准**。
- OpenSSF《Security-Focused Guide for AI Code Assistant Instructions》（2025-08）：可直接作为 `AGENTS.md` 安全规则起步块——输入校验、输出编码、参数化查询、不得把密钥写进代码、依赖固定版本。
- NIST NCCoE 2026-02 概念稿：考虑 OAuth 2.0 / OIDC / SPIFFE-SPIRE / SCIM 做 Agent 身份与授权委派。

## 4. LSP / DAP 的位置（A/B 级）

- MCP 自述「借鉴 Language Server Protocol」；LSP 标准化的是「编辑器 ↔ 语言能力」，DAP 标准化「调试器 ↔ 前端」，MCP 标准化「Agent ↔ 上下文/工具」。
- 三者都是**能力接口**，不是信任边界。Vibe Coding 综述把 MCP / LSP / DAP 归为「交互式开发接口」层，同层还有隔离执行运行时（容器、gVisor 沙箱、云环境）与分布式编排（CI/CD 集成）。
- 实践含义：给 Agent 接 LSP 让它「看懂代码」是低风险能力；给它接 shell / 写文件 / 部署工具才是高影响动作，**两者应在权限上分开**。

## 5. 对准则的贡献

| 结论 | 手册条目 |
|---|---|
| 工具描述/注解不可信、调用前须明确同意、协议本身不强制 | A3 修订、H1 |
| least agency + 全量日志 + 独立身份 + 短时凭据 | H2、H3 |
| 高影响控制挂在「推理→动作」边界，不靠提示词 | A3、H1 |
| 协议版本要声明并做回归 | H4、D3（版本敏感） |
| 读能力（LSP/检索）与写能力（shell/部署）权限分离 | H2、A3 |
| OpenSSF 起步块可直接写进规则文件 | 4.1 / `05-项目落地/AGENTS.md骨架草案.md` |

## 6. 待补

见 `06-来源索引/存疑与待核实.md`：OWASP ASI 官方原文页、五国联合指引原文、OpenSSF 指南全文。
