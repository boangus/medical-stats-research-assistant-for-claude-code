#!/usr/bin/env python3
"""
render_report_html.py — HTML 图文报告渲染器
==============================================
接收 JSON 骨架描述 + PNG 图片目录 → 输出单文件自包含 HTML 报告。

用法:
  python render_report_html.py \\
    --title "医学统计研究报告" \\
    --sections report_sections.json \\
    --figures ./figures/ \\
    --output final_report.html

JSON 骨架格式 (report_sections.json):
{
  "title": "...",
  "subtitle": "...",
  "report_guideline": "STROBE",
  "generated_at": "2026-05-29",
  "sections": [
    {"id": "methods", "title": "方法学", "type": "text",
     "content": "纯文本段落..."},
    {"id": "table1", "title": "基线特征", "type": "table",
     "content": "| 变量 | 组A | 组B |\\n|---|...|"},
    {"id": "km_curve", "title": "生存曲线", "type": "figure",
     "figure_file": "km_curve_survival.png",
     "caption": "图1. Kaplan-Meier 生存曲线"},
    {"id": "discussion", "title": "讨论", "type": "multi",
     "children": [
       {"type": "text", "content": "..."},
       {"type": "figure", "figure_file": "...", "caption": "..."}
     ]}
  ],
  "footnote": "...",
  "disclaimer": "..."
}

依赖: 无 (仅 Python 标准库)
作者: MSRA Team
版本: 0.1.0
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from html import escape


# ============================================================================
# CSS 主题
# ============================================================================

CSS_THEMES = {
    "minimal": """
/* ===== Minimal Theme for MSRA Report ===== */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 24px;
    color: #1a1a1a;
    background: #fff;
    line-height: 1.7;
    font-size: 15px;
}

/* Header */
.report-header {
    border-bottom: 2px solid #2563eb;
    padding-bottom: 20px;
    margin-bottom: 32px;
}
.report-header h1 {
    font-size: 26px;
    font-weight: 600;
    margin: 0 0 6px 0;
    color: #111;
}
.report-header .subtitle {
    font-size: 15px;
    color: #555;
    margin: 0;
}
.report-header .meta {
    margin-top: 10px;
    font-size: 13px;
    color: #777;
}

/* Sections */
.section {
    margin-bottom: 32px;
}
.section h2 {
    font-size: 19px;
    font-weight: 600;
    color: #111;
    border-left: 4px solid #2563eb;
    padding-left: 10px;
    margin: 28px 0 14px 0;
}
.section h3 {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin: 20px 0 10px 0;
}

/* Text */
.section p {
    margin: 10px 0;
    text-align: justify;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 13px;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px 10px;
    text-align: left;
}
th {
    background: #f8f9fa;
    font-weight: 600;
    color: #333;
}
tr:nth-child(even) {
    background: #f8f9fa;
}
caption {
    caption-side: bottom;
    font-size: 12px;
    color: #666;
    margin-top: 6px;
    text-align: left;
}

/* Figures */
.figure-wrapper {
    margin: 20px 0;
    text-align: center;
}
.figure-wrapper img {
    max-width: 100%;
    height: auto;
    border: 1px solid #eee;
    border-radius: 4px;
}
.figure-wrapper .caption {
    margin-top: 8px;
    font-size: 13px;
    color: #555;
    text-align: center;
}

/* Footer */
.report-footer {
    border-top: 1px solid #ddd;
    padding-top: 16px;
    margin-top: 40px;
    font-size: 12px;
    color: #999;
}
.report-footer .disclaimer {
    margin-top: 8px;
    color: #bbb;
    font-style: italic;
}

/* Checklist */
.checklist-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 4px 0;
    font-size: 13px;
}
.checklist-item .check {
    color: #16a34a;
    font-weight: bold;
}
.checklist-item .cross {
    color: #dc2626;
    font-weight: bold;
}

/* Print */
@media print {
    body { padding: 0; font-size: 12pt; }
    .section h2 { break-after: avoid; }
    .figure-wrapper { break-inside: avoid; }
    table { font-size: 10pt; }
}

@media (max-width: 600px) {
    body { padding: 16px; font-size: 14px; }
    table { font-size: 12px; }
    th, td { padding: 5px 6px; }
}
"""
}


# ============================================================================
# Markdown 表格 → HTML 表格
# ============================================================================

def md_table_to_html(md_table: str) -> str:
    """将 Markdown 表格转换为 HTML <table>。"""
    lines = [l.strip() for l in md_table.strip().split("\n") if l.strip()]
    if not lines:
        return "<p><em>空表格</em></p>"

    # 找到表格起始行（以 | 开头）
    table_lines = [l for l in lines if l.startswith("|") or l.startswith("+")]
    if not table_lines:
        return f"<pre>{escape(md_table)}</pre>"

    # 过滤掉分隔行 (|---|)
    data_lines = [l for l in table_lines if not re.match(r'^[\s\|:\-+]+$', l) or ('-' in l and ':' in l)]

    # 更鲁棒的分隔行检测：检查是否主要为 - 和 |
    def is_separator(line):
        stripped = line.replace('|', '').replace('-', '').replace(':', '').replace('+', '').strip()
        return len(stripped) == 0

    header_done = False
    rows_html = []

    for line in table_lines:
        if is_separator(line):
            header_done = True
            continue

        # Parse cells
        cells = [c.strip() for c in line.strip('|').split('|')]

        if not header_done:
            row_html = "        <tr>\n" + "\n".join(
                f"          <th>{escape(c)}</th>" for c in cells
            ) + "\n        </tr>"
            rows_html.append(row_html)
            header_done = True  # 第一行数据行即表头
        else:
            row_html = "        <tr>\n" + "\n".join(
                f"          <td>{escape(c)}</td>" for c in cells
            ) + "\n        </tr>"
            rows_html.append(row_html)

    if not rows_html:
        # fallback: 没有分隔行，所有行当作数据行
        header_done = False
        rows_html = []
        for line in table_lines:
            cells = [c.strip() for c in line.strip('|').split('|')]
            if not header_done:
                row_html = "        <tr>\n" + "\n".join(
                    f"          <th>{escape(c)}</th>" for c in cells
                ) + "\n        </tr>"
                rows_html.append(row_html)
                header_done = True
            else:
                row_html = "        <tr>\n" + "\n".join(
                    f"          <td>{escape(c)}</td>" for c in cells
                ) + "\n        </tr>"
                rows_html.append(row_html)

    return (
        '      <table>\n'
        + "\n".join(rows_html) + "\n"
        '      </table>'
    )


# ============================================================================
# 图片嵌入 (base64)
# ============================================================================

def embed_image(figures_dir: Path, figure_file: str) -> str:
    """读取图片文件并返回 base64 嵌入的 HTML img 标签。

    如果文件不存在，返回占位文本。
    """
    # Try direct path first
    img_path = Path(figure_file)
    if not img_path.is_absolute():
        img_path = figures_dir / figure_file

    if not img_path.exists():
        # Fallback: search in figures_dir
        for ext in ('.png', '.jpg', '.jpeg', '.svg', '.pdf'):
            candidate = figures_dir / f"{Path(figure_file).stem}{ext}"
            if candidate.exists():
                img_path = candidate
                break

    if not img_path.exists():
        return f'<p style="color:#999;font-style:italic;">[图: {escape(figure_file)} 未找到]</p>'

    try:
        data = img_path.read_bytes()
        ext = img_path.suffix.lower()
        mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg',
                     '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml'}
        mime = mime_map.get(ext, 'image/png')
        b64 = base64.b64encode(data).decode('ascii')
        return f'<img src="data:{mime};base64,{b64}" alt="{escape(figure_file)}" />'
    except Exception as e:
        return f'<p style="color:#c00;font-style:italic;">[图加载失败: {escape(str(e))}]</p>'


# ============================================================================
# 章节渲染
# ============================================================================

def render_section(section: dict, figures_dir: Path) -> str:
    """渲染单个章节。"""
    html_parts = []
    sec_type = section.get("type", "text")
    sec_id = section.get("id", "")
    sec_title = section.get("title", "")

    if sec_title:
        html_parts.append(f'    <h2 id="{escape(sec_id)}">{escape(sec_title)}</h2>')

    if sec_type == "text":
        content = section.get("content", "")
        html_parts.append(f'    <p>{escape(content)}</p>')

    elif sec_type == "table":
        content = section.get("content", "")
        html_parts.append(f'    {md_table_to_html(content)}')
        table_caption = section.get("caption", "")
        if table_caption:
            html_parts.append(f'    <p class="caption">{escape(table_caption)}</p>')

    elif sec_type == "figure":
        figure_file = section.get("figure_file", "")
        caption = section.get("caption", "")
        img_tag = embed_image(figures_dir, figure_file)
        html_parts.append('    <div class="figure-wrapper">')
        html_parts.append(f'      {img_tag}')
        if caption:
            html_parts.append(f'      <div class="caption">{escape(caption)}</div>')
        html_parts.append('    </div>')

    elif sec_type == "multi":
        # 复合章节：包含多个子元素
        for child in section.get("children", []):
            # 子元素没有标题，只渲染内容
            child_type = child.get("type", "text")
            if child_type == "text":
                html_parts.append(f'    <p>{escape(child.get("content", ""))}</p>')
            elif child_type == "table":
                html_parts.append(f'    {md_table_to_html(child.get("content", ""))}')
                tc = child.get("caption", "")
                if tc:
                    html_parts.append(f'    <p class="caption">{escape(tc)}</p>')
            elif child_type == "figure":
                ff = child.get("figure_file", "")
                cap = child.get("caption", "")
                img_tag = embed_image(figures_dir, ff)
                fig_html = '    <div class="figure-wrapper">\n'
                fig_html += f'      {img_tag}\n'
                if cap:
                    fig_html += f'      <div class="caption">{escape(cap)}</div>\n'
                fig_html += '    </div>'
                html_parts.append(fig_html)

    elif sec_type == "checklist":
        # 合规检查清单
        items = section.get("items", [])
        html_parts.append('    <div class="checklist">')
        for item in items:
            passed = item.get("passed", False)
            label = item.get("label", "")
            detail = item.get("detail", "")
            mark = '<span class="check">✓</span>' if passed else '<span class="cross">✗</span>'
            detail_text = f' — {escape(detail)}' if detail else ''
            html_parts.append(
                f'      <div class="checklist-item">{mark} '
                f'<span>{escape(label)}{detail_text}</span></div>'
            )
        html_parts.append('    </div>')

    else:
        html_parts.append(f'    <p><em>未知章节类型: {escape(sec_type)}</em></p>')

    result = '\n'.join(html_parts)
    return f'    <div class="section">\n{result}\n    </div>'


# ============================================================================
# 报告组装
# ============================================================================

def build_report(skeleton: dict, figures_dir: Path, css_theme: str = "minimal") -> str:
    """根据 JSON 骨架构建完整 HTML 报告。"""
    title = skeleton.get("title", "医学统计研究报告")
    subtitle = skeleton.get("subtitle", "")
    guideline = skeleton.get("report_guideline", "")
    generated_at = skeleton.get("generated_at", "")
    footnote = skeleton.get("footnote", "")
    disclaimer = skeleton.get("disclaimer", "")

    # CSS
    css = CSS_THEMES.get(css_theme, CSS_THEMES["minimal"])

    # Header
    header_parts = [f'      <h1>{escape(title)}</h1>']
    if subtitle:
        header_parts.append(f'      <p class="subtitle">{escape(subtitle)}</p>')
    meta_parts = []
    if guideline:
        meta_parts.append(f'报告规范: {escape(guideline)}')
    if generated_at:
        meta_parts.append(f'生成日期: {escape(generated_at)}')
    if meta_parts:
        header_parts.append(f'      <p class="meta">{" | ".join(meta_parts)}</p>')
    header_html = '\n'.join(header_parts)

    # Sections
    sections_html = []
    for section in skeleton.get("sections", []):
        sections_html.append(render_section(section, figures_dir))
    body_html = '\n'.join(sections_html)

    # Footer
    footer_parts = []
    if footnote:
        footer_parts.append(f'      <p>{escape(footnote)}</p>')
    if disclaimer:
        footer_parts.append(f'      <p class="disclaimer">{escape(disclaimer)}</p>')
    footer_html = '\n'.join(footer_parts)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<style>
{css}
</style>
</head>
<body>
  <div class="report-header">
{header_html}
  </div>
  <div class="report-body">
{body_html}
  </div>
  <div class="report-footer">
{footer_html}
  </div>
</body>
</html>
"""
    return html


# ============================================================================
# CLI
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="MSRA HTML 图文报告渲染器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python render_report_html.py --title \"统计报告\" --sections sec.json --figures ./figs/\n"
    )
    parser.add_argument("--title", default="医学统计研究报告",
                        help="报告标题")
    parser.add_argument("--sections", required=True,
                        help="JSON 骨架文件路径")
    parser.add_argument("--figures", default="./figures/",
                        help="PNG 图片目录路径")
    parser.add_argument("--output", default="final_report.html",
                        help="输出 HTML 文件路径")
    parser.add_argument("--css-theme", default="minimal",
                        choices=list(CSS_THEMES.keys()),
                        help="CSS 主题 (默认: minimal)")
    return parser.parse_args()


def generate_table_semantic_description(table_content: str) -> Dict:
    """
    生成表格的语义化描述
    
    使用TableMaster方法提取表格关键信息
    
    Parameters
    ----------
    table_content : str
        Markdown格式的表格内容
        
    Returns
    -------
    Dict
        表格语义化描述
    """
    try:
        # 导入表格理解模块
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from table_understanding import TableMasterExtractor
        
        # 解析表格数据
        lines = [l.strip() for l in table_content.strip().split("\n") if l.strip()]
        if not lines:
            return {'error': '空表格'}
        
        # 提取表头和数据行
        table_lines = [l for l in lines if l.startswith("|")]
        if not table_lines:
            return {'error': '无法解析表格'}
        
        # 简单的表格解析
        headers = []
        rows = []
        for i, line in enumerate(table_lines):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if i == 0:
                headers = cells
            elif not all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                rows.append(cells)
        
        table_data = {
            'headers': headers,
            'rows': rows
        }
        
        # 使用TableMaster提取语义信息
        extractor = TableMasterExtractor(table_data)
        semantic_info = extractor.extract()
        
        return {
            'table_structure': {
                'headers': headers,
                'row_count': len(rows),
                'column_count': len(headers)
            },
            'semantic_info': semantic_info,
            'summary': f"表格包含{len(headers)}列{len(rows)}行数据"
        }
        
    except Exception as e:
        return {'error': f"表格语义描述生成失败: {e}"}


def generate_chart_structured_description(chart_data: Dict) -> Dict:
    """
    生成图表的结构化描述
    
    使用FDV方法将图表转化为结构化文本描述
    
    Parameters
    ----------
    chart_data : Dict
        图表数据，包含类型、数据点、坐标轴等信息
        
    Returns
    -------
    Dict
        图表结构化描述
    """
    try:
        # 导入图表理解模块
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from chart_understanding import ChartFDVGenerator
        
        # 使用FDV生成结构化描述
        generator = ChartFDVGenerator(chart_data)
        fdv_description = generator.generate_description()
        
        return {
            'chart_type': chart_data.get('type', 'unknown'),
            'fdv_description': fdv_description,
            'data_summary': {
                'data_points': len(chart_data.get('data_points', [])),
                'has_confidence_interval': 'confidence_interval' in chart_data,
                'has_p_value': 'p_value' in chart_data,
                'has_sample_size': 'sample_size' in chart_data
            }
        }
        
    except Exception as e:
        return {'error': f"图表结构化描述生成失败: {e}"}


def generate_table_chart_verification_report(skeleton: Dict) -> Dict:
    """
    生成表格和图表的自动化核查报告
    
    Parameters
    ----------
    skeleton : Dict
        报告JSON骨架
        
    Returns
    -------
    Dict
        核查报告
    """
    report = {
        'table_verification': [],
        'chart_verification': [],
        'overall_score': 0.0,
        'recommendations': []
    }
    
    # 遍历所有章节
    for section in skeleton.get('sections', []):
        section_type = section.get('type', '')
        
        # 检查表格
        if section_type == 'table':
            table_content = section.get('content', '')
            if table_content:
                table_desc = generate_table_semantic_description(table_content)
                report['table_verification'].append({
                    'section_id': section.get('id', ''),
                    'section_title': section.get('title', ''),
                    'description': table_desc
                })
        
        # 检查图表
        elif section_type == 'figure':
            figure_file = section.get('figure_file', '')
            if figure_file:
                # 这里可以添加图表文件分析逻辑
                chart_data = {
                    'type': 'figure',
                    'file': figure_file,
                    'caption': section.get('caption', '')
                }
                chart_desc = generate_chart_structured_description(chart_data)
                report['chart_verification'].append({
                    'section_id': section.get('id', ''),
                    'section_title': section.get('title', ''),
                    'description': chart_desc
                })
        
        # 检查复合章节
        elif section_type == 'multi':
            for child in section.get('children', []):
                child_type = child.get('type', '')
                if child_type == 'table':
                    table_content = child.get('content', '')
                    if table_content:
                        table_desc = generate_table_semantic_description(table_content)
                        report['table_verification'].append({
                            'section_id': section.get('id', ''),
                            'section_title': section.get('title', ''),
                            'child_title': child.get('caption', ''),
                            'description': table_desc
                        })
                elif child_type == 'figure':
                    figure_file = child.get('figure_file', '')
                    if figure_file:
                        chart_data = {
                            'type': 'figure',
                            'file': figure_file,
                            'caption': child.get('caption', '')
                        }
                        chart_desc = generate_chart_structured_description(chart_data)
                        report['chart_verification'].append({
                            'section_id': section.get('id', ''),
                            'section_title': section.get('title', ''),
                            'child_title': child.get('caption', ''),
                            'description': chart_desc
                        })
    
    return report


def main():
    args = parse_args()

    # 读取 JSON 骨架
    sec_path = Path(args.sections)
    if not sec_path.exists():
        print(f"错误: 骨架文件不存在: {sec_path}", file=sys.stderr)
        sys.exit(1)
    with open(sec_path, encoding="utf-8") as f:
        skeleton = json.load(f)

    # 覆盖 title (CLI 优先级更高)
    skeleton["title"] = args.title

    # 图片目录
    figures_dir = Path(args.figures)

    # 构建 HTML
    html = build_report(skeleton, figures_dir, args.css_theme)

    # 写文件
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML 报告已生成: {output_path.resolve()}")
    print(f"   文件大小: {output_path.stat().st_size / 1024:.1f} KB")
    
    # 生成表格和图表核查报告
    verification_report = generate_table_chart_verification_report(skeleton)
    verification_path = output_path.with_suffix('.verification.json')
    with open(verification_path, "w", encoding="utf-8") as f:
        json.dump(verification_report, f, ensure_ascii=False, indent=2)
    print(f"📊 表格图表核查报告已生成: {verification_path}")


if __name__ == "__main__":
    main()
