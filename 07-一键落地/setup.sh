#!/usr/bin/env bash
# ============================================================
#  通用 AI 配置安装器（与项目无关）
#  一个源头（core/00-协作铁律.md + project.local.md）→ 多个平台
#
#  bash setup.sh                  预览：会写哪些文件
#  bash setup.sh --list           列出平台与本机状态
#  bash setup.sh --apply          安装到已确认的平台
#  bash setup.sh --apply --proj=/path/to/repo
#  bash setup.sh --apply --only=workbuddy,codex,claude
#  bash setup.sh --apply --force  连未验证的平台也装（qoder/cursor/windsurf）
#  bash setup.sh --paste          只生成可粘贴文本（ChatGPT/DeepSeek/Kimi）
#  bash setup.sh --apply --with-memory   追加 WorkBuddy 的 MEMORY.md 记忆块
#
#  幂等 · 覆盖前备份 · 生成回滚脚本 · 不碰源码 · 不执行 git
# ============================================================
set -u

SRC="$(cd "$(dirname "$0")" && pwd)"
CORE="$SRC/core/00-协作铁律.md"
PROJ_RULES="$SRC/project.local.md"
TARGETS="$SRC/targets.tsv"
MEMBLOCK="$SRC/memory-block.md"
MEMFILE="$HOME/.workbuddy/MEMORY.md"

APPLY=0; LIST=0; FORCE=0; PASTE=0; WITH_MEMORY=0; ONLY=""; PROJ="$(pwd)"
for a in "$@"; do
  case "$a" in
    --apply)        APPLY=1 ;;
    --list)         LIST=1 ;;
    --force)        FORCE=1 ;;
    --paste)        PASTE=1 ;;
    --with-memory)  WITH_MEMORY=1 ;;
    --only=*)       ONLY="${a#--only=}" ;;
    --proj=*)       PROJ="${a#--proj=}" ;;
    --help|-h)      sed -n '3,16p' "$0"; exit 0 ;;
    *) printf '未知参数: %s（用 --help）\n' "$a"; exit 2 ;;
  esac
done

[ -f "$CORE" ] || { printf '[FATAL] 缺少源文件: %s\n' "$CORE"; exit 1; }
[ -f "$TARGETS" ] || { printf '[FATAL] 缺少平台表: %s\n' "$TARGETS"; exit 1; }

STAMP="$(date +%Y%m%d-%H%M%S)"
BAKDIR="$SRC/archive/backups/$STAMP"
BACKUPS=""          # 每行：<备份文件>\t<原路径>
ROLLBACK="$SRC/rollback-$STAMP.sh"

is_template() { head -3 "$PROJ_RULES" 2>/dev/null | grep -q '待填'; }
body() {
  cat "$CORE"
  if [ -s "$PROJ_RULES" ] && ! is_template; then
    printf '\n\n---\n\n# 项目约定（本项目）\n\n'
    # 跳过项目文件自己的 H1 与说明块，从第一个二级标题开始
    sed '1,/^## /{/^## /!d}' "$PROJ_RULES"
  fi
}
compose() {
  case "$1" in
    rule)
      printf -- '---\ndescription: 跨项目协作铁律（自检先请示 / 基线先报 / 破坏性动作先批 / 验收先写死）\nalwaysApply: true\n---\n\n'; body ;;
    mdc)
      printf -- '---\ndescription: 跨项目协作铁律\nglobs: **/*\nalwaysApply: true\n---\n\n'; body ;;
    md)
      printf '<!-- 由 setup.sh 生成，源：core/00-协作铁律.md（+ project.local.md）。改内容请改源头，重跑会覆盖本文件 -->\n\n'; body ;;
    paste)
      # 只取第一个 --- 之后的正体，去掉给人类看的说明，粘进网页版才干净
      if [ -f "$SRC/core/99-系统提示词.md" ]; then sed '1,/^---$/d' "$SRC/core/99-系统提示词.md"; else body; fi ;;
  esac
}
match() { [ -z "$ONLY" ] && return 0; case ",$ONLY," in *",$1,"*) return 0 ;; *) return 1 ;; esac; }
# 表可能被记事本之类写过（带 UTF-8 BOM），这里统一剥掉，避免表头被当成一行目标
rows() { sed '1s/^\xEF\xBB\xBF//' "$TARGETS" | grep -v '^[[:space:]]*#' | grep -v '^[[:space:]]*$'; }

# ---------- --list ----------
if [ "$LIST" -eq 1 ]; then
  printf '%-12s %-9s %-7s %s\n' 平台 作用域 状态 路径
  printf '%.0s-' {1..78}; printf '\n'
  while IFS=$'\t' read -r id scope rel fmt status label; do
    case "$scope" in user) full="$HOME/$rel" ;; project) full="$PROJ/$rel" ;; *) full="—" ;; esac
    [ "$full" != "—" ] && { [ -e "$full" ] && mark="已存在" || mark="未创建"; } || mark="—"
    printf '%-12s %-9s %-7s %s  [%s]\n' "$id" "$scope" "$status" "$full" "$mark"
  done < <(rows)
  printf '\n当前项目根：%s\n' "$PROJ"
  exit 0
fi

# ---------- --paste ----------
if [ "$PASTE" -eq 1 ]; then
  out="$SRC/out/系统提示词.txt"; mkdir -p "$SRC/out"
  compose paste > "$out"
  printf '[OK] 可粘贴文本：%s（%s 行）\n' "$out" "$(wc -l < "$out")"
  printf '     用法：整段粘进 ChatGPT 自定义指令 / DeepSeek 系统提示 / Kimi 偏好设置\n'
  exit 0
fi

printf '==============================================\n'
printf ' 通用 AI 配置包 v%s\n' "$([ -f "$SRC/VERSION" ] && head -1 "$SRC/VERSION" || echo dev)"
printf ' 项目根 : %s\n' "$PROJ"
printf ' 模式   : %s\n' "$([ "$APPLY" -eq 1 ] && echo 'APPLY（写盘）' || echo 'DRY-RUN（只预览）')"
[ -n "$ONLY" ] && printf ' 限定   : %s\n' "$ONLY"
printf '==============================================\n\n'

n_ok=0; n_skip=0
while IFS=$'\t' read -r id scope rel fmt status label; do
  match "$id" || continue
  [ "$fmt" = "paste" ] && continue
  case "$scope" in
    user)    dst="$HOME/$rel" ;;
    project) dst="$PROJ/$rel" ;;
    *)       continue ;;
  esac
  parent="$(dirname "$dst")"

  if [ "$status" = "prob" ] && [ "$FORCE" -eq 0 ]; then
    # 未验证的平台：只有它专属的目录已经存在才装；根目录下的文件(.windsurfrules 这种)不算证据
    if [ ! -d "$parent" ] || [ "$parent" = "$PROJ" ] || [ "$parent" = "$HOME" ] || [ "$parent" = "${PROJ%/}" ]; then
      printf '[SKIP] %-12s 未验证的平台且无目录证据（确认路径后把 targets.tsv 的 prob 改成 ok，或加 --force）\n' "$id"
      n_skip=$((n_skip+1)); continue
    fi
  fi

  tmp="$SRC/.compose.$$.$(printf '%s' "$id" | tr -c 'a-zA-Z0-9' '_')"; compose "$fmt" > "$tmp"
  if [ -f "$dst" ] && cmp -s "$tmp" "$dst"; then
    printf '[SAME] %-12s %s\n' "$id" "$dst"; rm -f "$tmp"; continue
  fi
  if [ "$APPLY" -eq 0 ]; then
    if [ -f "$dst" ]; then printf '[PLAN] %-12s 覆盖(先备份) -> %s\n' "$id" "$dst"
    else printf '[PLAN] %-12s 新建         -> %s\n' "$id" "$dst"; fi
    rm -f "$tmp"; n_ok=$((n_ok+1)); continue
  fi
  mkdir -p "$parent" || { printf '[FAIL] %-12s 建不了目录 %s\n' "$id" "$parent"; rm -f "$tmp"; continue; }
  if [ -f "$dst" ]; then
    # 备份统一放到包内 archive/backups/，不要落在项目仓库里污染 git status
    mkdir -p "$BAKDIR" 2>/dev/null
    bak="$BAKDIR/$id.bak"
    cp "$dst" "$bak" && {
      BACKUPS="${BACKUPS}${bak}	${dst}
"
      printf '[BACK] %-12s %s\n' "$id" "$bak"; }
  fi
  if cp "$tmp" "$dst"; then printf '[OK]   %-12s %s\n' "$id" "$dst"; n_ok=$((n_ok+1))
  else printf '[FAIL] %-12s %s\n' "$id" "$dst"; fi
  rm -f "$tmp"
done < <(rows)

# ---------- 可选：WorkBuddy 记忆块 ----------
printf '\n'
if [ "$WITH_MEMORY" -eq 0 ]; then
  printf '[SKIP] 记忆块未启用（需要时加 --with-memory）\n'
elif grep -q 'AI-RULES-BEGIN' "$MEMFILE" 2>/dev/null; then
  printf '[SAME] MEMORY.md 已含标记块，跳过\n'
elif [ "$APPLY" -eq 0 ]; then
  printf '[PLAN] 追加记忆块 -> %s\n' "$MEMFILE"
else
  mkdir -p "$BAKDIR" 2>/dev/null
  cp "$MEMFILE" "$BAKDIR/MEMORY.md.bak" 2>/dev/null && \
    BACKUPS="${BACKUPS}${BAKDIR}/MEMORY.md.bak	${MEMFILE}
"
  printf '\n' >> "$MEMFILE" && cat "$MEMBLOCK" >> "$MEMFILE" \
    && printf '[OK]   记忆块已追加 -> %s\n' "$MEMFILE" || printf '[FAIL] 记忆块写入失败\n'
fi

if is_template; then
  printf '\n[!] project.local.md 还是模板 —— 仅装入了通用铁律。\n'
  printf '    填好项目命令/硬约束再重跑，才会带上项目段。\n'
fi

printf '\n'
if [ "$APPLY" -eq 1 ] && [ -n "$BACKUPS" ]; then
  { printf '#!/usr/bin/env bash\nset -u\n'
    printf '%s' "$BACKUPS" | while IFS="$(printf '\t')" read -r bak dst; do
      [ -z "$bak" ] && continue
      printf 'cp "%s" "%s" && echo "restored: %s"\n' "$bak" "$dst" "$dst"
    done
    printf 'echo 回滚完成\n'; } > "$ROLLBACK"
  chmod +x "$ROLLBACK" 2>/dev/null
  printf '[OK] 回滚脚本: %s\n' "$ROLLBACK"
fi

printf '\n==============================================\n'
if [ "$APPLY" -eq 1 ]; then
  printf ' 处理 %d 个目标（跳过 %d 个）\n' "$n_ok" "$n_skip"
  printf ' ① 多数工具需【新开会话】才读取新规则\n'
  printf ' ② 验证：新会话问「列出你能复述的硬约束」\n'
  [ -n "$BACKUPS" ] && printf ' ③ 撤销：bash %s\n' "$(basename "$ROLLBACK")"
else
  printf ' 预览结束，未写入任何文件（%d 个待处理）\n' "$n_ok"
  printf ' 确认后执行：bash setup.sh --apply\n'
fi
printf '==============================================\n'
