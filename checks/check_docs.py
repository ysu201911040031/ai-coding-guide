#!/usr/bin/env python3
"""仓库对账检查（只读）。

检查项：
  1. 正文条目数 / 速查表行数 / P0 数 / 表-文差集 —— 与 checks/expected.json 比对
  2. 行数上限（速查卡、个人卡、提炼版）
  3. Markdown 相对链接是否指向真实文件
  4. 编码：UTF-8 无 BOM
  5. 敏感串：本机用户路径 / 邮箱 / 私网 IP / 64 位哈希

用法（仓库根目录）：
  python checks/check_docs.py
  python checks/check_docs.py --update     # 有意变更后刷新基线（不碰 caps）

退出码：0 全部通过；1 有 FAIL；2 运行错误。
"""
import io
import json
import os
import re
import subprocess
import sys
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANDBOOK = os.path.join(ROOT, "AI编程建议清单与准则手册.md")
EXPECT_PATH = os.path.join(ROOT, "checks", "expected.json")
SKIP_DIRS = {".git", "out", "archive", "dist", "__pycache__", "对话", "脱敏前原稿-20261112-1049", "脱敏前原稿-20261112-1111"}

FAIL, WARN = [], []


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def md_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(base, name)


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def check_counts(expected):
    text = read(HANDBOOK)
    entries = re.findall(r"^#### ([A-N]\d+) ·", text, re.M)
    rows = re.findall(r"^\| ([A-N]\d+) \|", text, re.M)
    p0 = re.findall(r"^\| ([A-N]\d+) \|.*\*\*P0\*\*", text, re.M)
    dup = sorted({x for x in entries if entries.count(x) > 1})

    missing = sorted(set(entries) - set(rows))
    exp = expected["handbook"]

    if len(entries) != exp["entries"]:
        FAIL.append(f"正文条目 {len(entries)} ≠ 基线 {exp['entries']}")
    if len(rows) != exp["table_rows"]:
        FAIL.append(f"速查表条目 {len(rows)} ≠ 基线 {exp['table_rows']}")
    if len(p0) != exp["p0"]:
        FAIL.append(f"P0 {len(p0)} ≠ 基线 {exp['p0']}")
    if missing != sorted(exp["missing_from_table"]):
        FAIL.append(f"表-文差集变了：{missing} ≠ 基线 {sorted(exp['missing_from_table'])}")
    if dup:
        FAIL.append(f"正文条目重复：{dup}")
    if sorted(set(rows) - set(entries)):
        FAIL.append(f"表内出现正文没有的条目：{sorted(set(rows) - set(entries))}")

    return len(entries), len(rows), len(p0), missing


def check_caps(expected):
    for name, cap in expected["caps"].items():
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            FAIL.append(f"上限检查找不到文件：{name}")
            continue
        n = len(read(path).splitlines())
        if n > cap:
            FAIL.append(f"{name} 已 {n} 行，超上限 {cap}")


def check_links():
    link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
    for path in md_files():
        for m in link_re.finditer(read(path)):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = urllib.parse.unquote(target.split("#")[0].strip("<>"))
            if not target:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(resolved):
                FAIL.append(f"断链：{rel(path)} → {target}")


def check_encoding_and_hygiene():
    pat_userdir = re.compile(r"(Users[\\/][^\\/\s]|/home/[^/\s])")
    pat_winpath = re.compile(r"(?<![A-Za-z])[A-Za-z]:\\[^\s<>]")
    pat_email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
    pat_ip = re.compile(r"\b(?:10|127|192\.168|172\.(?:1[6-9]|2\d|3[01]))(?:\.\d{1,3}){2,3}\b")
    pat_sha = re.compile(r"\b[0-9a-f]{64}\b")

    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith((".md", ".sh", ".tsv", ".txt")):
                continue
            path = os.path.join(base, name)
            raw = open(path, "rb").read()
            if raw.startswith(b"\xef\xbb\xbf"):
                FAIL.append(f"带 BOM：{rel(path)}")
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                FAIL.append(f"不是合法 UTF-8：{rel(path)}")
                continue
            for i, line in enumerate(text.splitlines(), 1):
                where = f"{rel(path)}:{i}"
                if pat_userdir.search(line) or pat_winpath.search(line):
                    FAIL.append(f"本机绝对路径：{where}")
                if pat_sha.search(line):
                    WARN.append(f"疑似哈希：{where}")
                if pat_email.search(line):
                    WARN.append(f"疑似邮箱：{where}")
                if "http" not in line and pat_ip.search(line):
                    WARN.append(f"疑似私网 IP：{where}")


def tracked_text_files():
    try:
        out = subprocess.check_output(
            ["git", "-c", "core.quotepath=false", "ls-files"], cwd=ROOT, text=True, encoding="utf-8"
        )
        return [f for f in out.split("\n") if f.endswith(".md")]
    except Exception:
        return [rel(p) for p in md_files()]


def main():
    if not os.path.exists(EXPECT_PATH):
        print(f"[FATAL] 缺少基线文件：{EXPECT_PATH}")
        return 2
    expected = json.loads(read(EXPECT_PATH))

    entries, rows, p0, missing = check_counts(expected)
    check_caps(expected)
    check_links()
    check_encoding_and_hygiene()

    print("=" * 60)
    print(f" 文件：{len(tracked_text_files())} 个 Markdown ｜ 正文 {entries} 条 ｜ 速查表 {rows} 条 ｜ P0 {p0} 条")
    print(f" 表-文差集（{len(missing)}）：{' '.join(missing)}")
    print("=" * 60)

    for msg in FAIL:
        print(f"[FAIL] {msg}")
    for msg in WARN:
        print(f"[WARN] {msg}")

    print("-" * 60)
    if FAIL:
        print(f" 结果：FAIL（{len(FAIL)} 项错误，{len(WARN)} 项警告）")
        return 1
    print(f" 结果：PASS（{len(WARN)} 项警告）")
    return 0


if __name__ == "__main__":
    if "--update" in sys.argv:
        text = read(HANDBOOK)
        entries = re.findall(r"^#### ([A-N]\d+) ·", text, re.M)
        rows = re.findall(r"^\| ([A-N]\d+) \|", text, re.M)
        p0 = re.findall(r"^\| ([A-N]\d+) \|.*\*\*P0\*\*", text, re.M)
        data = json.loads(read(EXPECT_PATH))
        data["handbook"] = {
            "entries": len(entries),
            "table_rows": len(rows),
            "p0": len(p0),
            "missing_from_table": sorted(set(entries) - set(rows)),
        }
        with open(EXPECT_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("[OK] 基线已更新（caps 未动）")
        sys.exit(0)
    sys.exit(main())