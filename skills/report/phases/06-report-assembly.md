# Phase 6: 报告组装 (HTML 图文报告)

> 来源：从 SKILL.md L881-950 抽取。
> 参考：src/shared/report_assembler/render_report_html.py — HTML 报告渲染器

将 Phase 1–5 的产物组装为一份单文件自包含的 HTML 图文报告。

**Step 6.1: AI 构建 JSON 骨架**

收集各阶段产物，构造 JSON 骨架 (`report_sections.json`)：

| 来源 | 产物 | JSON 章节类型 |
|------|------|--------------|
| Phase 1 | 结果解读文本 | `{"type": "text"}` |
| Phase 2 | 表格 (Markdown Table) | `{"type": "table"}` |
| Phase 3 | 已生成的 SVG+PNG | `{"type": "figure", "figure_file": "...", "figure_file_svg": "..."}` |
| Phase 4 | 方法学描述 | `{"type": "text"}` |
| Phase 5 | 合规检查结果 | `{"type": "checklist"}` |

JSON 骨架格式（`report_sections.json`）：

```json
{
  "title": "...", "study_type": "RCT",
  "sections": [
    {"id": "methods", "type": "text", "content": "..."},
    {"id": "table1", "type": "table", "content": "| 变量 | ... |"},
    {"id": "km_curve", "type": "figure", "figure_file": "km_curve.png", "caption": "..."},
    {"id": "compliance", "type": "checklist", "items": [{"passed": true, "label": "..."}]}
  ]
}
```

> section type: `text` | `table` | `figure`(需 figure_file+caption) | `checklist`(需 items[]) | `multi`(需 children[])

**Step 6.2: 调用渲染器生成 HTML**

```bash
# 完整 API 见 src/shared/report_assembler/render_report_html.py
python src/shared/report_assembler/render_report_html.py \
  --title "报告标题" \
  --sections reports/report_sections.json \
  --figures reports/figures/ \
  --output reports/final_report.html \
  --css-theme minimal
```

> 渲染失败时自动降级为 Markdown 拼接：将 JSON 骨架中各 section 按序拼接为 `final_report.md`。

**Step 6.3: 输出产物**

`final_report.html` + `final_report.md` + `figures/*.png` + `tables/*.docx` + `journal-template.json`

**报告组装异常处理**：

| 触发条件 | 一线处理 | 仍失败兜底 |
|---------|---------|-----------|
| JSON 骨架缺少必需章节（如 "methods" 未生成） | 检查缺失章节来源阶段是否完成 | 在骨架中补充空章节占位，标注"待补充"，生成缺失章节清单和补充指南 |
| 渲染脚本 `render_report_html.py` 不存在或报错 | 检查路径和依赖（python-docx / jinja2） | 用 Markdown 直接拼接替代 HTML 渲染，输出纯文本版，提供渲染错误日志和修复建议 |
| 产物路径冲突（png/docx 同名列） | 自动追加时间戳后缀（如 `table1_baseline_1600.docx`） | 提示用户选择：(1) 覆盖现有文件 (2) 重命名新文件 (3) 保留两个版本 |

**报告组装检查点**：

> 🔴 [MANDATORY-REPT-04] 报告组装完成后，必须展示以下内容给用户确认：
> 1. 最终报告文件路径（HTML + MD）
> 2. 图表文件清单
> 3. 表格文件清单
> 4. 合规检查最终结果
>
> 用户确认后才能交付最终报告。
