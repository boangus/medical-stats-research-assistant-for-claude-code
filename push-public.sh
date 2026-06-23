#!/bin/bash
# 推送到公共仓库（从 main 分支创建独立公开版本）
# 用法：./push-public.sh
#
# 工作原理：
# 1. 检查当前在 main 分支且工作区干净
# 2. 基于 main 创建临时的 clean-main 分支
# 3. 强推 clean-main 到 public 仓库的 main 分支
# 4. 清理本地 clean-main 分支
#
# 这样 public 仓库永远只有 main 分支，且与 origin/main 保持同步

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

# 创建临时 clean-main 分支
git branch -f clean-main main
git checkout clean-main

# 强推到 public 仓库
if git push public clean-main:main --force-with-lease --quiet 2>/dev/null; then
  echo "✅ 已推送到公共仓库"
else
  echo "❌ 推送失败"
  git checkout main
  git branch -D clean-main
  exit 1
fi

# 切换回 main 并清理临时分支
git checkout main
git branch -D clean-main 2>/dev/null || true

echo "✅ 完成"
