# Contributing to MSRA

感谢你对本项目的兴趣！以下是参与贡献的指南。

## 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/boangus/medical-stats-research-assistant-for-claude-code.git
cd medical-stats-research-assistant

# 2. 创建 Python 虚拟环境
python -m venv venv
source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 运行安装脚本（创建 symlink/junction）
# Mac/Linux:
chmod +x install.sh && ./install.sh
# Windows:
.\install.ps1
```

## 编码规范

### Python
- 遵循 PEP 8
- 使用 `ruff` 进行 lint: `ruff check shared/ tests/`
- 所有公开函数必须有 docstring（Google style）
- 文件编码统一为 UTF-8，open() 时显式指定 `encoding="utf-8"`

### R
- 使用 `<-` 赋值（不用 `=`）
- 文件编码统一为 UTF-8

### SKILL.md
- 必须包含 YAML frontmatter（name, description, version, works_with, depends_on, tags）
- 必须包含 IRON RULES 章节
- 失败模式使用"触发条件 / 一线处理 / 仍失败兜底"三列表
- 检查点使用 🔴/🟡/🟢 视觉标记

## 提交规范

```
<type>: <description>

类型:
- feat:     新功能
- fix:      修复
- docs:     文档
- style:    格式
- refactor: 重构
- test:     测试
- chore:    构建/工具
```

## Pull Request 流程

1. Fork 仓库，创建 feature 分支
2. 确保 `pytest tests/ -v` 全部通过
3. 确保 `ruff check shared/ tests/` 无错误
4. 更新 CHANGELOG.md
5. 提交 PR，描述变更内容和原因

## 报告问题

- 使用 GitHub Issues
- 包含复现步骤、期望行为、实际行为
- 标注操作系统和 Python/R 版本

## 许可

本项目采用双许可证模式（详见 [LICENSE](LICENSE)）：

- **代码贡献** (.py, .R, .sh, .ps1 等) 默认使用 **MIT 许可证**
- **知识库贡献** (SKILL.md, 文档, 模板, 检查清单等) 默认使用 **CC BY-NC-SA 4.0**

提交 PR 即表示你同意将贡献内容按上述对应许可证授权。
