# 开源经验①：仓库级规则文件约定

> 归档日期：2026-11-11 ｜ 可信等级：**A**（`agents.md` 官方站点、OpenAI Codex / Apache Airflow 官方示例、aider 官方 FAQ）
> 对应手册：A1 / A4 / A5 / B5

---

## 1. AGENTS.md：跨工具的「给 Agent 看的 README」

**定位**（官方表述）：`AGENTS.md` 是标准 Markdown 文件，放在仓库根，给编码 Agent 提供构建命令、测试指令、代码约定、安全注意事项等上下文。它与人类 README 互补：README 面向「理解与上手」，AGENTS.md 面向「让 Agent 可靠地做对事」。

**规模与治理**（官方站点口径）：
- 被 **60k+ 开源项目**采用；由 OpenAI Codex、Amp、Google Jules、Cursor、Factory 等共同推动。
- 现由 **Linux Foundation 旗下的 Agentic AI Foundation** 托管，定位为开放格式而非厂商配置。
- 官方给出的示例仓库：`openai/codex`、`apache/airflow`、`temporalio/sdk-java`、`PlutoLang/Pluto`。

**四条硬规则（FAQ 原文要点）**：
1. **没有必填字段**，没有 frontmatter，没有 schema——就是 Markdown，标题随便起，Agent 直接读文本。
2. **就近优先**：目录树中离被编辑文件最近的 `AGENTS.md` 生效，嵌套文件覆盖父级；**显式用户聊天指令覆盖一切**。
3. Agent **会尝试执行** `AGENTS.md` 里列出的测试命令，并在完成任务前修复失败——所以写进去的命令必须是你想让它跑的（这一点与「自检先请示」纪律冲突时需由人覆盖）。
4. 视为 **living documentation**，可随时更新。

**Monorepo 做法**：官方明确建议按子包放多份，而不是一个巨型根文件；「写作时 OpenAI 主仓有 88 份 AGENTS.md」。

**迁移与兼容**：
```bash
# 旧格式收敛
mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md
```
```yaml
# aider: .aider.conf.yml
read: AGENTS.md
```
```json
// Gemini CLI: .gemini/settings.json
{ "context": { "fileName": "AGENTS.md" } }
```
官方列出的兼容工具包括：Codex、Jules、Warp、VS Code、Windsurf、GitHub Copilot coding agent、Gemini CLI、Cursor、Devin、opencode 等。工具专属文件（`CLAUDE.md` / `GEMINI.md` / `.github/copilot-instructions.md` / `.cursor/rules/`）仅在需要 AGENTS.md 表达不了的行为时使用。

## 2. 官方推荐的章节

| 章节 | 内容 |
|---|---|
| Project overview | 项目是做什么的（简短） |
| Build and test commands | **确切命令**，可复制执行 |
| Code style guidelines | 清单式硬规则 |
| Testing instructions | 如何跑单测、哪些必须通过 |
| Security considerations | 安全注意事项、禁止操作 |
| 其他 | 提交信息 / PR 规范、部署步骤、大数据集坑、「任何你会告诉新同事的事」 |

## 3. 优秀写法的三个特征（来自 Codex / Airflow 示例与社区归纳）

1. **祈使、可执行，不是描述**：写 `pnpm vitest run -t "<test name>"`，不写「注意测试规范」。
2. **代码风格是清单**：Codex 的示例几乎全是规则条目（遵守特定 clippy lint、exhaustive match、argument-comment lint），每条链接到它所约束的规则。
3. **写明环境/沙箱契约**：例如 Codex 文档说明 `CODEX_SANDBOX_NETWORK_DISABLED=1` 以及为什么某些测试会提前退出——**防止 Agent 去「修」本来正确的测试**。

## 4. 反模式（社区明确点名）

- 复述人类 README，而不是告诉 Agent 该做什么。
- 「写整洁代码」这类不改变任何决策的模糊指导。
- 只给精确命令之外的东西：提到工具却不写怎么安装、怎么写命令。
- 一份超长根文件覆盖所有子项目（应拆分）。
- 让 `AGENTS.md` 膨胀——其中每个 token 都在挤占理解真实代码的上下文预算（见 12-Factor Agents / Lost in the Middle）。

## 5. aider 的 CONVENTIONS.md

- 一个纯 Markdown 文件，用 `--read CONVENTIONS.md` 或 `/read` 加载，作为**只读上下文**。
- 典型内容：指定优先使用的库（如 `httpx` 而非 `requests`）、强制类型标注、命名约定。
- 若 provider 支持 prompt caching，该文件会被缓存，多轮对话中几乎不增加成本。
- 价值：把「每次都要口头纠正」变成一次性、可版本化的约束。与 `AGENTS.md` 的区别是它是**工具级只读上下文**，不是跨工具约定；现在推荐统一收敛到 `AGENTS.md`。

## 6. 其他同类约定（收敛关系）

| 文件 | 归属 | 现状 |
|---|---|---|
| `AGENTS.md` | 跨工具开放格式 | 推荐作为唯一真相来源 |
| `CLAUDE.md` | Claude Code | 常软链或 `@import` 到 AGENTS.md |
| `GEMINI.md` / `QWEN.md` / `WARP.md` | 各工具 | 同上 |
| `.github/copilot-instructions.md` | GitHub Copilot | 工具专属行为时用 |
| `.cursor/rules/`、`.clinerules/` | 按 glob 激活的规则 | 适合窄范围按文件/模型触发 |
| `CONVENTIONS.md` | aider | 只读约定，可迁移 |

> 对应手册 A5：规则是配置，不是文档——要能 diff、能 review、能回滚，与代码同仓同版本。

## 7. 可复制的最小骨架

见主手册 `4.1 规则文件骨架`，或 `05-项目落地/AGENTS.md骨架草案.md`。

## 8. 来源

- `https://agents.md/`（官方规范站点，A）
- OpenAI Codex `AGENTS.md`、Apache Airflow `AGENTS.md` 官方示例（A）
- `awesome-agent-conventions` 的 AGENTS.md 条目与反模式归纳（A/B）
- aider FAQ（`https://github.com/Aider-AI/aider/blob/main/docs/faq.md`，A）与 conventions 文档（A）
