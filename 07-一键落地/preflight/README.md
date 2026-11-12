# 开工卡（preflight）

> 解决三件事：**环境每会话报一次**、**漂移了先确认再动手**、**新功能先问要不要复用**。
> 默认只读；只有 `--check` 会执行命令，跑之前必须先获批。

## 三步接入

1. 把本目录复制到项目根，脚本放进 `.ai/`：
   ```
   <项目>/.ai/preflight.py
   <项目>/.ai/env.template.json
   <项目>/.ai/env-log.template.md
   ```
2. 建档并填占位符（框架版本、语言标准、工具链的 `check` 命令）：
   ```
   python .ai/preflight.py --init
   ```
   然后（**获批后**）实测一次并写入记录：
   ```
   python .ai/preflight.py --check
   python .ai/preflight.py --apply-drift
   ```
3. 在 AI 工具里挂 SessionStart hook 执行 `python .ai/preflight.py`。
   本会话已存在 SessionStart hook 注入，说明机制可用；**具体配置文件位置按你的工具实测一次，不猜路径**。
   挂不上 hook 也行：会话第一句手动跑一次。

## 命令

| 命令 | 做什么 | 会跑命令吗 |
|---|---|---|
| `python .ai/preflight.py` | 打印开工卡：基线 / 环境 / 核对天数 / 复用提醒 | 否 |
| `python .ai/preflight.py --init` | 生成 `env.json` 与 `env-log.md`，不覆盖已存在文件 | 否 |
| `python .ai/preflight.py --check` | 跑 `toolchains[].check`，与 `observed` 比对 | **是**，先获批 |
| `python .ai/preflight.py --apply-drift` | 把实测值写回 `env.json`，并在 `env-log.md` 追加一行 | **是**，先获批 |

`check` 只写单条命令，不要管道和重定向；版本行由脚本取第一条非空输出，跨平台行为一致。

## 环境变动的记录方式

- 漂移判定只认**命令输出**，不认「我记得」。
- 每次变更在 `env-log.md` 追加：日期 / 字段 / 旧值 / 新值 / 触发 / 证据。
- 换机器、升级编译器、换框架版本，都算变更；`verified_at` 只表示「核对过」，不表示「没变」。

## 验收（三条，缺一不可）

1. 新项目 `--init` 后，`env.json` 与 `env-log.md` 都存在，且 `env.json` 是合法 JSON。
2. 故意改一处 `observed`，`--check` 必须报 `DRIFT` 并返回非 0。
3. 新会话（或手动跑默认命令）的输出里，必须同时出现**环境摘要**和**复用提醒**两行。

## 与现有规则的关系

- A2 基线：开工卡顺带报路径 / 分支 / 未提交数。
- C6 / D3：环境结论来自命令输出，不从静态代码推断；版本锁定写进记录。
- D8 复用：开工卡只负责"提醒 + 询问触发"，候选与止损仍按 D8 三档闸门走。
- 不新增第五份规则：行为写进 `project.local.md`，脚本只做提示与对账。

## 不做什么

- 不联网、不自动搜索、不装依赖。
- 不自动执行版本命令（只在 `--check` / `--apply-drift` 时）。
- 不在环境未变时反复追问——每会话一次，超过 30 天才提示复核。