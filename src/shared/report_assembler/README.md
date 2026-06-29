# Report Assembler — 图文报告组装器

将分析结果、表格、图表图片组装为**单文件自包含 HTML 图文报告**。

## 用法

```bash
python render_report_html.py \
  --title "医学统计研究报告" \
  --sections report_sections.json \
  --figures ./figures/ \
  --output final_report.html \
  --css-theme minimal
```

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--title` | 医学统计研究报告 | 报告标题 |
| `--sections` | (必填) | JSON 骨架文件路径 |
| `--figures` | ./figures/ | PNG 图片目录 |
| `--output` | final_report.html | 输出 HTML 路径 |
| `--css-theme` | minimal | 主题: minimal |

## JSON 骨架格式

```json
{
  "title": "报告标题",
  "subtitle": "副标题（可选）",
  "report_guideline": "CONSORT/STROBE/PRISMA 等",
  "generated_at": "2026-05-29",
  "sections": [
    {"id": "sec1", "title": "方法学", "type": "text", "content": "..."},
    {"id": "sec2", "title": "基线特征", "type": "table", "content": "|...|...|"},
    {"id": "sec3", "title": "生存曲线", "type": "figure",
     "figure_file": "km.png", "caption": "图1. KM曲线"},
    {"id": "sec4", "title": "复合章节", "type": "multi",
     "children": [
       {"type": "text", "content": "..."},
       {"type": "figure", "figure_file": "...", "caption": "..."}
     ]},
    {"id": "sec5", "title": "合规检查", "type": "checklist",
     "items": [
       {"passed": true, "label": "项目1", "detail": "通过"},
       {"passed": false, "label": "项目2", "detail": "待补充"}
     ]}
  ],
  "footnote": "页脚说明（可选）",
  "disclaimer": "免责声明（可选）"
}
```

## 章节类型

| type | 说明 | 必填字段 |
|------|------|---------|
| `text` | 纯文本段落 | content |
| `table` | Markdown 表格 → HTML table | content, caption(可选) |
| `figure` | 嵌入图片 (base64) | figure_file, caption(可选) |
| `multi` | 复合章节（图文混排） | children |
| `checklist` | 合规检查清单 | items[] |

## 图片处理

- PNG/JPG/SVG 自动检测格式
- base64 嵌入，输出为单文件
- 查找顺序: 绝对路径 → figures_dir/{filename} → figures_dir/{stem}.png/.jpg

## 流水线集成

报告生成阶段 (report/SKILL.md Phase 7) 的工作流：

1. AI 构建 JSON 骨架（引用 Phase 1–6 产物）
2. 调用 `render_report_html.py` 渲染 HTML
3. 生成最终报告: `final_report.html` + `final_report.md`

## 依赖

无。仅 Python 标准库 (json, base64, pathlib, argparse, html.escape)。



