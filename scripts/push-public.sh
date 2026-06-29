#!/bin/bash
# 推送到公共仓库 (origin = medical-stats-research-assistant-for-claude-code)
# 用法：./push-public.sh
#
# 注意：origin 已指向 public 仓库，直接 git push 即可。
# 本脚本仅做安全检查 + 推送。

set -e

cd "$(dirname "$0")"

# 检查当前分支
CURRENT=$(git branch --show-current)
if [ "$CURRENT" != "main" ]; then
  echo "❌ 请先切换到 main 分支"
  exit 1
fi

# 检查工作区是否干净
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ 工作区有未提交的变更，请先处理"
  exit 1
fi

# 推送到 origin（即 public 仓库）
git push origin main
echo "✅ 已推送到公共仓库"
