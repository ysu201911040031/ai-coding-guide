#!/usr/bin/env python3
"""开工卡：环境核对 + 基线 + 复用提醒。

默认只读：不执行任何版本命令，不写文件。
  python preflight.py                  打印开工卡（安全，可挂在会话开始）
  python preflight.py --init           建档：生成 .ai/env.json 与 .ai/env-log.md（不覆盖）
  python preflight.py --check          实测版本并与记录比对（会执行 env.json 里的 check 命令，需先获批）
  python preflight.py --apply-drift    把实测值写回 env.json，并在 env-log.md 追加变更行
  python preflight.py --age=30         核对阈值（默认 30 天）
  python preflight.py --proj=<路径>     指定项目根（默认当前目录）

退出码：0 正常；1 --check/--apply-drift 发现漂移；2 用法或文件错误。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "env.template.json"
LOG_TEMPLATE = HERE / "env-log.template.md"

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_env(proj):
    path = proj / ".ai" / "env.json"
    if not path.exists():
        return None, path
    return json.loads(path.read_text(encoding="utf-8")), path


def days_since(value):
    try:
        return (date.today() - datetime.strptime(value, "%Y-%m-%d").date()).days
    except (TypeError, ValueError):
        return None


def decode(raw):
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


def run_check(command, proj):
    """执行单条命令，返回第一行非空输出。调用前必须已获批。"""
    proc = subprocess.run(command, shell=True, cwd=str(proj), capture_output=True, timeout=20)
    text = decode(proc.stdout).strip() or decode(proc.stderr).strip()
    if not text and proc.returncode != 0:
        raise RuntimeError(f"命令失败，退出码 {proc.returncode}")
    return text.splitlines()[0].strip() if text else ""


def git_baseline(proj):
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(proj), "rev-parse", "--abbrev-ref", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        dirty = subprocess.check_output(
            ["git", "-C", str(proj), "status", "--porcelain"],
            text=True, stderr=subprocess.DEVNULL,
        ).splitlines()
        return branch, len(dirty)
    except Exception:
        return None, None


def fmt_env(env):
    lang = env.get("language", {})
    fw = env.get("framework", {})
    osv = env.get("os", {})
    lang_s = " ".join(x for x in (lang.get("name", ""), lang.get("standard", "")) if x)
    fw_s = " ".join(x for x in (fw.get("name", ""), fw.get("version", "")) if x)
    os_s = " ".join(x for x in (osv.get("name", ""), osv.get("arch", "")) if x)
    return " / ".join(x for x in (lang_s, fw_s, os_s) if x) or "未填写"


def cmd_init(proj, _args):
    ai = proj / ".ai"
    env_path = ai / "env.json"
    log_path = ai / "env-log.md"
    if env_path.exists():
        print(f"[SKIP] 已存在：{env_path}（本工具不覆盖）")
        return 0
    ai.mkdir(parents=True, exist_ok=True)
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    import platform

    template["os"] = {"name": platform.system(), "arch": platform.machine() or "<x64>"}
    template["recorded_at"] = date.today().isoformat()
    template["verified_at"] = date.today().isoformat()
    env_path.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log_path.write_text(LOG_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[OK] 已建档：{env_path}")
    print(f"[OK] 已建日志：{log_path}")
    print("     下一步：填 <占位符>；然后（获批后）运行 --check 记录实测值")
    return 0


def cmd_card(proj, args):
    env, path = load_env(proj)
    print(f"=== 开工卡 {date.today().isoformat()} ===")
    print(f"项目  : {proj}")
    branch, dirty = git_baseline(proj)
    if branch:
        print(f"基线  : {branch} ｜ 未提交 {dirty} 个文件")
    else:
        print("基线  : 不是 git 仓库（或 git 不可用）")
    if not env:
        print(f"环境  : 未建档（{path}）→ 先运行 python preflight.py --init")
        return 0

    print(f"环境  : {fmt_env(env)}")
    tools = [t.get("name", "?") + ("（已记录）" if str(t.get("observed", "")).strip() else "（未记录）")
             for t in env.get("toolchains", [])]
    if tools:
        print(f"工具链: {' ｜ '.join(tools)}")
    age = days_since(env.get("verified_at"))
    if age is None:
        print("核对  : 未核对（verified_at 无效）")
    elif age > args.age:
        print(f"核对  : {age} 天前 ⚠ 超过阈值 {args.age}，先确认环境再动手")
    else:
        print(f"核对  : {age} 天前（阈值 {args.age}）")
    print("复用  : 新功能 / 新模块 / 新依赖 → 先问「要不要搜现成实现」（默认 10 分钟，无果再写）；bug 修复不问")
    index = proj / "10-资源台账" / "提示词库索引.md"
    print(f"提示词: 复用无果 → {'查 ' + str(index) if index.exists() else '查项目提示词库索引'}")
    if args.checked:
        print("        （本轮已执行 --check）")
    else:
        print("        （--check 未执行：版本以记录为准）")
    return 0


def collect_checks(env, proj):
    rows = []
    for item in env.get("toolchains", []):
        name = item.get("name", "?")
        command = str(item.get("check", "")).strip()
        observed = str(item.get("observed", "")).strip()
        if not command or command.startswith("<"):
            rows.append((name, "SKIP", observed, "未配置 check 命令"))
            continue
        try:
            actual = run_check(command, proj)
        except Exception as exc:  # 超时 / 命令不存在
            rows.append((name, "ERROR", observed, str(exc).splitlines()[0]))
            continue
        if not observed or observed.startswith("<"):
            rows.append((name, "TODO", actual, "已实测，尚未记录；用 --apply-drift 写入"))
        elif observed == actual:
            rows.append((name, "MATCH", actual, ""))
        else:
            rows.append((name, "DRIFT", actual, f"记录值：{observed}"))
    return rows


def print_rows(rows):
    for name, status, actual, note in rows:
        line = f"[{status}] {name}: {actual or '（无输出）'}"
        if note:
            line += f"  ← {note}"
        print(line)


def cmd_check(proj, args):
    env, _ = load_env(proj)
    if not env:
        print("[FAIL] 未建档，先运行 --init")
        return 2
    rows = collect_checks(env, proj)
    print_rows(rows)
    drift = [r for r in rows if r[1] in ("DRIFT", "ERROR")]
    if drift:
        print(f"\n发现 {len(drift)} 项漂移。确认后运行：python preflight.py --apply-drift")
        return 1
    todo = [r for r in rows if r[1] == "TODO"]
    if todo:
        print(f"\n有 {len(todo)} 项已实测但未记录，运行 --apply-drift 写入。")
        return 0
    print("\n环境与记录一致。")
    return 0


def cmd_apply(proj, _args):
    env, path = load_env(proj)
    if not env:
        print("[FAIL] 未建档，先运行 --init")
        return 2
    rows = collect_checks(env, proj)
    print_rows(rows)
    changes = []
    for item in env.get("toolchains", []):
        name = item.get("name", "?")
        for r_name, status, actual, _note in rows:
            if r_name == name and status in ("DRIFT", "TODO") and actual:
                old = str(item.get("observed", "")).strip() or "（空）"
                item["observed"] = actual
                changes.append((name, old, actual))

    env["verified_at"] = date.today().isoformat()
    path.write_text(json.dumps(env, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    log_path = proj / ".ai" / "env-log.md"
    if changes:
        if not log_path.exists():
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(LOG_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
        existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        with log_path.open("a", encoding="utf-8") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            for name, old, new in changes:
                f.write(f"| {date.today().isoformat()} | {name} | {old} | {new} | 人工确认 | --check 输出 |\n")
        print(f"\n[OK] 已记录 {len(changes)} 项变更 → {log_path}")
    else:
        print("\n[OK] 无变更，仅更新核对日期")
    return 0


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply-drift", action="store_true")
    parser.add_argument("--age", type=int, default=30)
    parser.add_argument("--proj", default=os.getcwd())
    args = parser.parse_args()

    proj = Path(args.proj).expanduser().resolve()
    if not proj.exists():
        print(f"[FAIL] 项目根不存在：{proj}")
        return 2
    args.checked = args.check

    if args.init:
        return cmd_init(proj, args)
    if args.check:
        return cmd_check(proj, args)
    if args.apply_drift:
        return cmd_apply(proj, args)
    return cmd_card(proj, args)


if __name__ == "__main__":
    sys.exit(main())