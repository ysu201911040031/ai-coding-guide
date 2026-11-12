# 通用 AI 配置包（与项目无关 · 多平台）

> 一个源头，安装到所有 AI 工具。**不绑定任何项目**——换个仓库只改 `project.local.md`，脚本不用动。
> 2026-11-11 / 上游：`../速查卡.md`、`../速查卡-个人版.md`、`../AI编程建议清单与准则手册.md`

## 一句话原理

```
core/00-协作铁律.md  +  project.local.md  ──setup.sh──▶  各平台认的格式
      （通用，改一次）      （项目，可空）                    （自动生成，别手改）
```

生成出来的文件顶部都有注释：**改内容请改源头，重跑会覆盖**。

## 三步

```bash
cd "<档案根>/07-一键落地"          # 换成你本机存放本包的实际目录

bash setup.sh --list                      # ① 看会装到哪、本机存不存在
bash setup.sh --apply --proj=/你的/仓库     # ② 装（先备份，覆盖前）
bash setup.sh --paste                     # ③ 给网页版生成可粘贴文本
```

只装某几个：`--only=workbuddy,codex,claude`
连未验证平台也装：`--force`

装完必须验证，别问它「记住了吗」——那是自报：

```bash
bash verify.sh            # 静态：已装文件是否与源头一致 + 关键条款是否都在
bash verify.sh --probe    # 行为：生成 4 个探针，粘进新会话，按判据打勾
bash verify.sh --score=out/probes/<时间戳>/记录.md
```

## 支持哪些平台（`targets.tsv` 可自己加行）

| id | 装到哪 | 状态 |
|---|---|---|
| `workbuddy` | `~/.workbuddy/rules/00-协作铁律.md` | ✅ 已确认 |
| `codebuddy` | `~/.codebuddy/rules/00-协作铁律.md` | ✅ 已确认 |
| `claude` | `~/.claude/CLAUDE.md` | ✅ 约定 |
| `claude-proj` | `<仓库>/CLAUDE.md` | ✅ 约定 |
| `codex` | `<仓库>/AGENTS.md` | ✅ 约定（多数 Agent 工具都读） |
| `copilot` | `<仓库>/.github/copilot-instructions.md` | ✅ 约定 |
| `qoder` | `<仓库>/.qoder/rules/general.md` | ⚠️ 未验证，需 `--force` |
| `cursor` | `<仓库>/.cursor/rules/general.mdc` | ⚠️ 未验证，需 `--force` |
| `windsurf` | `<仓库>/.windsurfrules` | ⚠️ 未验证，需 `--force` |
| `paste` | `out/系统提示词.txt` | ✅ 给 ChatGPT / DeepSeek / Kimi 网页版 |

> **为什么有「未验证」**：`~/.qoder`、`~/.claude`、`~/.codex` 这台机器上确实存在，但没找到它们的规则目录样本；Cursor 根本没装。所以这三个标 `prob`——**目录已存在才装**，否则跳过并提示，不猜路径。
> 你确认了正确路径后，直接改 `targets.tsv` 那一行，把 `prob` 改成 `ok` 即可。

## 「自己调」怎么调

| 想改什么 | 改哪 |
|---|---|
| 通用铁律（跨项目都要） | `core/00-协作铁律.md` |
| 本项目命令 / 硬约束 / 已知坑 | `project.local.md`（出厂是通用基线，`<...>` 待填） |
| 加一个平台 | `targets.tsv` 加一行，不用碰脚本 |
| 网页版粘贴文本 | `core/99-系统提示词.md` |
| 5 条日常提示词 | `prompts.md` |

> `project.local.md` 里带「待填」标记时，脚本只装通用铁律、并提示你去填——**占位符不会被塞进规则文件**。
> 填完去掉标记，项目段才会拼进去。

`project.local.md` 出厂是模板状态（脚本会提示「仅装入了通用铁律」）。填好后重跑，项目段才会拼进去。

## 安全设计

- 默认 dry-run，`--apply` 才写
- 幂等：内容相同则 `[SAME]` 跳过
- 覆盖前备份到 **`archive/backups/<时间戳>/<id>.bak`**（刻意不放在目标旁边——否则会在你的仓库里留下一堆 `.bak-*` 污染 `git status`）
- 生成 `rollback-<时间戳>.sh`，一条命令还原
- 不碰源码、不执行 git、不写 `.git`、不删任何文件

## 目录

```
07-一键落地/
├── setup.sh                  ← 安装器（多平台、幂等、可回滚）
├── targets.tsv               ← 平台 → 路径映射（自己加行）
├── core/
│   ├── 00-协作铁律.md          ← 唯一源头（通用）
│   └── 99-系统提示词.md        ← 无文件约定平台的粘贴版
├── project.local.md          ← 项目约定（出厂通用基线，`<...>` 待填）
├── VERSION                   ← 包版本号
├── memory-block.md           ← 可选：WorkBuddy MEMORY.md 记忆块
└── prompts.md                ← 5 条可复制提示词
```

> `archive/`（旧的单平台版本）与 `archive/backups/`（安装时的备份）都是**运行后才产生**的目录，
> 出厂包里不存在。旧的单平台版本已被 `core/` 取代，不再分发。

## 项目专用内容去哪了

本包已与项目解耦：**这里只有跨项目通用的铁律**，任何项目专名、构建命令、硬件约束、框架版本都不在本包内。

项目专用内容一律放在 `../05-项目落地/<项目名>/` 下，每个项目一个子目录：

- `<项目名>项目规则.md` —— 填好的 `project.local.md` 长什么样，可直接改名复用
- `<项目名>-AGENTS示例.md` —— 该项目的 `AGENTS.md` 成品

> 换项目＝**换一个子目录**，本包一个字都不用改。
> 这些子目录**不随通用包分发**（打包时整块排除），所以别人拿到的包里没有你的项目信息。
