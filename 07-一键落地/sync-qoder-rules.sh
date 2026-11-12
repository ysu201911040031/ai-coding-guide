#!/usr/bin/env bash
# ============================================================
#  同步 Qoder 用户级规则：项目源文件 → 规则目录
#
#  bash sync-qoder-rules.sh                预览（默认 dry-run，不写盘）
#  bash sync-qoder-rules.sh --apply        写入（覆盖前备份）
#  bash sync-qoder-rules.sh --check        有漂移就退出 1（给检查脚本用）
#  bash sync-qoder-rules.sh --only=00,10   只同步指定 id
#  QODER_RULES=/path bash ...              改目标目录（默认 ~/.qoder-cn/rules）
#
#  清单在同目录 qoder-rules.tsv；源文件里的 {{ROOT}} 会替换成本机项目根。
#  备份写到 07-一键落地/archive/qoder-rules-backups/<时间戳>/（不进规则目录，
#  否则 .md 备份会被当成规则加载）。
# ============================================================
set -u

SRC="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SRC/.." && pwd)"
MANIFEST="$SRC/qoder-rules.tsv"
DEST="${QODER_RULES:-$HOME/.qoder-cn/rules}"

APPLY=0
CHECK=0
ONLY=""
for a in "$@"; do
  case "$a" in
    --apply)        APPLY=1 ;;
    --check)        CHECK=1 ;;
    --only=*)       ONLY="${a#--only=}" ;;
    --help|-h)      sed -n '2,15p' "$0"; exit 0 ;;
    *) printf '未知参数: %s（用 --help）\n' "$a"; exit 2 ;;
  esac
done

[ -f "$MANIFEST" ] || { printf '[FATAL] 缺少清单: %s\n' "$MANIFEST"; exit 2; }

ROOT_WIN="$(cygpath -w "$ROOT" 2>/dev/null || printf '%s' "$ROOT")"
STAMP="$(date +%Y%m%d-%H%M%S)"
BAK="$SRC/archive/qoder-rules-backups/$STAMP"

match() { [ -z "$ONLY" ] && return 0; case ",$ONLY," in *",$1,"*) return 0 ;; *) return 1 ;; esac; }
listed() { awk -F'\t' -v id="$1" '$1==id{found=1} END{exit(found?0:1)}' "$MANIFEST"; }

printf '==============================================\n'
printf ' Qoder 规则同步 v1\n'
printf ' 项目根 : %s\n' "$ROOT_WIN"
printf ' 目标   : %s\n' "$DEST"
printf ' 模式   : %s\n' "$([ "$APPLY" -eq 1 ] && echo 'APPLY（写盘）' || echo 'DRY-RUN（只预览）')"
printf '==============================================\n\n'

n_same=0; n_plan=0; n_fail=0
while IFS=$'\t' read -r id relsrc always desc || [ -n "${id:-}" ]; do
  case "$id" in ''|\#*) continue ;; esac
  match "$id" || continue

  src="$ROOT/$relsrc"
  dst="$DEST/$id.md"
  if [ ! -f "$src" ]; then
    printf '[FAIL] %-24s 源文件缺失: %s\n' "$id" "$src"
    n_fail=$((n_fail+1)); continue
  fi

  body="$(cat "$src")"
  body="${body//\{\{ROOT\}\}/$ROOT_WIN}"
  tmp="$SRC/.qoder-sync.$$"
  {
    printf -- '---\ndescription: %s\nalwaysApply: %s\n---\n\n' "$desc" "$always"
    printf '%s\n' "$body"
  } > "$tmp"

  if [ -f "$dst" ] && cmp -s "$tmp" "$dst"; then
    printf '[SAME] %-24s %s\n' "$id" "$dst"
    n_same=$((n_same+1)); rm -f "$tmp"; continue
  fi

  if [ "$APPLY" -eq 0 ]; then
    if [ -f "$dst" ]; then
      printf '[PLAN] %-24s 更新（先备份）\n' "$id"
    else
      printf '[PLAN] %-24s 新建\n' "$id"
    fi
    n_plan=$((n_plan+1)); rm -f "$tmp"; continue
  fi

  mkdir -p "$DEST" || { printf '[FAIL] %-24s 建不了目录 %s\n' "$id" "$DEST"; rm -f "$tmp"; n_fail=$((n_fail+1)); continue; }
  if [ -f "$dst" ]; then
    mkdir -p "$BAK" 2>/dev/null && cp "$dst" "$BAK/$id.md" 2>/dev/null
  fi
  if cp "$tmp" "$dst"; then
    printf '[OK]   %-24s %s\n' "$id" "$dst"
    n_plan=$((n_plan+1))
  else
    printf '[FAIL] %-24s 写入失败\n' "$id"; n_fail=$((n_fail+1))
  fi
  rm -f "$tmp"
done < "$MANIFEST"

# 规则目录里存在但清单未登记的文件：只提示，不删
if [ -d "$DEST" ]; then
  for f in "$DEST"/*.md; do
    [ -e "$f" ] || continue
    id="$(basename "$f" .md)"
    listed "$id" || printf '[WARN] 未登记（不处理）: %s\n' "$f"
  done
fi

printf '\n'
if [ "$APPLY" -eq 1 ]; then
  printf ' 结果：写入 %d ｜ 一致 %d ｜ 失败 %d\n' "$n_plan" "$n_same" "$n_fail"
  [ -d "$BAK" ] && printf ' 备份：%s\n' "$BAK"
  printf ' 生效：新会话，或等下一轮刷新；手动规则用 @<id> 引入。\n'
else
  printf ' 结果：待更新 %d ｜ 一致 %d ｜ 失败 %d\n' "$n_plan" "$n_same" "$n_fail"
  printf ' 确认后执行：bash sync-qoder-rules.sh --apply\n'
fi
printf '==============================================\n'

[ "$n_fail" -gt 0 ] && exit 1
[ "$CHECK" -eq 1 ] && [ "$n_plan" -gt 0 ] && exit 1
exit 0