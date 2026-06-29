# Third-Party Notices

## stat-method-selector

This skill incorporates code and data from the **stat-method-selector** project.

- **Repository**: https://github.com/ApintLin/stat-method-selector
- **Author**: ApintLin
- **Version**: v2.2
- **License**: MIT License
- **Copyright**: Copyright (c) 2025
- **Commit**: bbe7994 (2026-06-17)

### Description

统计方法选择器 — 基于53篇已发表方法学论文构建的统计方法决策树，覆盖15个研究目标分支、112个统计方法叶子节点。支持问卷式引导和自然语言描述两种输入方式。

### Files from this project

| File | Description |
|------|-------------|
| `SKILL.md` | Claude Code skill 定义文件 |
| `decision-tree.json` | 15-goal, 112-method 决策树数据 |
| `references.md` | 53篇方法学论文的结构化摘要 |

> Web 界面文件（`server.js`、`start-server.bat`、`index.html`、`article.html`）已迁移至 `tools/stat-method-selector-server/`；决策树审计脚本（`audit.py` → `audit_stat_method_selector.py`、`audit_result.txt`）已迁移至 `scripts/audit/`。

### MIT License

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Citation

若在学术研究中使用本决策树或引用其方法学依据，请引用原始项目：

> ApintLin/stat-method-selector: 基于53篇方法学论文的统计方法选择器. GitHub. https://github.com/ApintLin/stat-method-selector

---

## Academic Literature

本技能引用的53篇方法学论文均为已发表的同行评审学术文献。论文本身的使用遵循学术引用规范，不属于软件许可范畴。完整的文献列表和引用格式见 `references.md`。
