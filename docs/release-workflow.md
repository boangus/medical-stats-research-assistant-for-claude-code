# 发布工作流

## 仓库架构

```
本地仓库
├── origin (私有)  boangus/medical-stats-research-assistant
│   └── 完整开发历史，所有 commit
│
└── public (公开)  boangus/medical-stats-research-assistant-for-claude-code
    └── 仅版本发布记录，每个 release 一个 commit
```

## 日常开发

```bash
# 正常开发，推送到私有仓库
git push origin <branch>
```

## 发布新版本

```bash
# 1. 确保当前在工作分支，所有改动已提交
git status

# 2. 切换到 release 分支，用 orphan 方式重建干净历史
git checkout --orphan release
git rm -rf .

# 3. 从工作分支复制全部文件
git checkout <工作分支> -- .

# 4. 提交版本（这是公开仓库唯一能看到的 commit）
git add -A
git commit -m "v0.9.1 — 版本说明"

# 5. 强制推送到公开仓库（替换历史为仅此一个 commit）
git push public release:main --force

# 6. 打 tag
git tag v0.9.1
git push public v0.9.1

# 7. 切回工作分支
git checkout <工作分支>
```

## 效果

| 仓库 | 历史记录 |
|------|---------|
| 私有 | `commit-1 → commit-2 → ... → commit-N` (完整开发过程) |
| 公开 | `v0.9.0` (首次发布) → `v0.9.1` (第二次发布) → ... |

## 注意事项

- 公开仓库使用 `--force` 推送，历史不可恢复（但本地私有仓库保留完整历史）
- 每次发布时，release 分支的 commit message 就是版本说明
- tag 会保留在公开仓库，方便用户下载特定版本
