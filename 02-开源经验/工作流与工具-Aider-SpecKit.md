# 开源经验②：可回溯工作流与规格驱动工具

> 归档日期：2026-11-11 ｜ 可信等级：**A**（aider 官方 FAQ/文档、GitHub Spec Kit 官方文档）
> 对应手册：A2 / B2 / B3 / B4 / C2 / D1

---

## 1. aider：把模型放进仍由开发者掌握的工程流程

### 1.1 Git 集成（最值得抄的一条）

aider 官方 FAQ 明确：**建议在 git 仓库中使用 aider，这本身就是安全机制**。具体行为：

- 在非 git 目录启动时会询问是否创建仓库。
- 把文件加入会话时，若文件未被 git 跟踪，会请求许可后加入。
- **启动时、以及每次发请求前检查工作区是否 dirty**，并提议先提交人的改动，确保 AI 的改动落在干净基线上、不与人的改动混杂。
- AI 每次改动后**自动生成一个描述性 commit**。
- 提供 `/diff` 与 `/undo`，可撤销上一次 AI 改动。
- 可在会话外开分支、用 `git reset` 回滚一整串不成功的改动。
- 可用 `--no-auto-commits` / `--no-dirty-commits` / `--no-git` 关闭，但官方不推荐，并提醒「务必自己保留备份」。

> 对应手册 A2（开工先对基线）、B4（小批量可回溯）、D1（产出当待审 PR）。**注意「自动 commit 是安全网，不是审查替代品」**——每次改完仍要检查 diff 范围、是否碰了无关文件、是否有对应验证。

### 1.2 Repository Map：压缩的架构地图

- 用 tree-sitter 抽取文件清单、关键符号（类/方法/函数签名），随修改请求一起给模型，让它看到「这个文件之外有哪些可复用结构」。
- 目的：降低上下文成本、保留跨文件关系；**不等于完整源码，也不等于模型理解了运行期行为**。
- 官方 usage 建议：**只把需要编辑的文件加入会话**，不要一上来把整个仓库塞进上下文。
- 社区 harness 总结的一条关键纪律：**「找文件」和「改文件」分两步**——LLM 负责命名候选，写集合只由人/显式规则声明，地图仅作参考；让 LLM 在地图上「任意编辑」是实测最常翻车的姿势。

### 1.3 Architect 模式：计划与执行分离

- `/chat-mode architect`：由 **architect 模型**分析请求、提出高层改动方案；再由独立的 **editor 模型**把方案翻译成逐行文件编辑。
- 推荐工作流：`/ask` 讨论方案、给反馈、确认计划 → 切 `/code` 说「go ahead」执行已商定的实现。
- 价值：避免模型在没理解系统架构前就冲进实现，尤其适合复杂重构。

### 1.4 其他可借鉴点

- `CONVENTIONS.md` 作为只读上下文（见同目录另一份档案）。
- `--watch-files`：在源码里写 `// AI!` 或 `AI?` 注释触发编辑或解释，把交互留在编辑器内。
- 修改后可自动跑 lint / test，让「看起来对」至少过一轮机器检查。
- 官方维护 polyglot benchmark（225 道 Exercism 练习，覆盖 C++/Go/Java/JS/Python/Rust），强调**用真实编辑任务而不是营销说法选模型**。

## 2. GitHub Spec Kit：把意图与证据放在实现前面

### 2.1 核心流程（SDD，Spec-Driven Development）

```
Constitution（项目原则，一次）
   → Specify（做什么、为什么）
   → Plan（技术栈与架构）
   → Tasks（可执行任务清单）
   → Implement（实现）
   → Converge（收敛验证，重复 implement → converge 直到报告 Converged）
```

- **每个阶段产出一份 Markdown 工件，喂给下一阶段**，给 Agent 结构化上下文而不是临时 prompt。
- 自带模板、质量检查清单与跨工件一致性分析。
- 需求澄清时**直接改已有 Markdown 工件**，不要重新生成整个阶段。
- 支持多款编码 Agent（Copilot / Gemini / Codex / Claude / Cursor / Zed / Qwen Code / CodeBuddy CLI 等），强调无锁定。

### 2.2 Bug 修复流程（与手册 C2 直接对应）

```
/speckit-bug-assess  →  /speckit-bug-fix  →  /speckit-bug-test
```

- 把「诊断原因」「限定范围的修复」「验证」拆成三个独立动作，避免 Agent 直接改现象而不改根因。
- 产物落在 `.specify/bugs/<slug>/`，最终结论为 **verified / partial / failed** 三态。
- 官方明确：**「Missing verification is not a successful fix」**（缺验证不算修复成功）。

### 2.3 决策前先取证（Idea assessment）

`intake → research → define → shape → decide`，产物以 `go / needs-clarification / kill` 结束；**「带书面理由地停止」也是一个有用结果**。对应手册 B2 与额外建议中「保留不用 AI 的选项」。

### 2.4 既有代码库

官方提供专门的 existing-project 指南，强调**不要把存量工程当绿地项目**开始。这对长周期、有历史包袱的项目尤其重要。

## 3. 两者的共同工程哲学

| 共同点 | 含义 | 手册条目 |
|---|---|---|
| 中间产物工件化 | 每一步产生可审阅的 Markdown / diff，而不是一次性长回答 | B2 |
| 计划与执行分离 | 先决定「改哪些」，再决定「怎么改」 | B3 |
| 可回溯性优先 | git commit / `/undo` / 分阶段工件 | A2 / B4 / D1 |
| 验证是独立阶段 | 缺验证即未完成 | C2 |
| 上下文要精简 | 只加需要的文件、地图只给骨架 | B5 |

## 4. 来源

- aider FAQ：`https://github.com/Aider-AI/aider/blob/main/docs/faq.md`；aider 官方 chat modes / conventions / usage 文档（A）
- GitHub Spec Kit 官方文档与 README：`https://github.com/github/spec-kit`（A）
- 中文/繁中的 aider 工作流解读（B，仅作旁证）
