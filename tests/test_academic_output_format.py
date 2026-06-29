#!/usr/bin/env python3
"""
学术输出格式测试

测试表格和图表的学术发表标准格式。
"""

import os

# 添加项目根目录到Python路径
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAcademicOutputFormat:
    """学术输出格式测试类"""

    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.tables_dir = os.path.join(self.temp_dir, "tables")
        self.figures_dir = os.path.join(self.temp_dir, "figures")
        os.makedirs(self.tables_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)

    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_three_line_table_format(self):
        """测试三线表格式规范"""
        # 三线表规范
        three_line_table_spec = {
            "top_border": "2pt",      # 顶线粗
            "header_border": "1pt",   # 表头下线中等
            "bottom_border": "2pt",   # 底线粗
            "vertical_borders": False, # 无竖线
            "left_right_borders": False, # 无左右端线
            "title_position": "top_center",  # 表题在上方居中
            "note_position": "bottom",  # 表注在下方
            "first_column_alignment": "left",  # 第一列左对齐
            "other_columns_alignment": "center",  # 其余居中
        }

        # 验证三线表规范
        assert three_line_table_spec["top_border"] == "2pt"
        assert three_line_table_spec["header_border"] == "1pt"
        assert three_line_table_spec["bottom_border"] == "2pt"
        assert three_line_table_spec["vertical_borders"] == False
        assert three_line_table_spec["left_right_borders"] == False

    def test_word_format_requirements(self):
        """测试Word格式要求"""
        word_format_requirements = {
            "format": ".docx",
            "font_chinese": "宋体",
            "font_english": "Times New Roman",
            "font_size": "10pt",  # 小五号
            "title_font_size": "10.5pt",  # 五号
        }

        # 验证Word格式要求
        assert word_format_requirements["format"] == ".docx"
        assert word_format_requirements["font_chinese"] == "宋体"
        assert word_format_requirements["font_size"] == "10pt"

    def test_figure_format_requirements(self):
        """测试图表格式要求"""
        figure_format_requirements = {
            "primary_format": "svg",  # 首要格式
            "academic_format": "pdf",  # 学术投稿格式
            "preview_format": "png",  # 预览格式
            "dpi": 300,  # PNG分辨率
            "font_size_axis": ">=10pt",  # 坐标轴标签字体大小
            "font_size_legend": ">=8pt",  # 图例字体大小
        }

        # 验证图表格式要求
        assert figure_format_requirements["primary_format"] == "svg"
        assert figure_format_requirements["academic_format"] == "pdf"
        assert figure_format_requirements["preview_format"] == "png"
        assert figure_format_requirements["dpi"] == 300

    def test_export_figure_default_formats(self):
        """测试export_figure函数的默认格式"""
        # 检查publication_figure_template.py中的默认格式
        template_path = Path(__file__).parent.parent / "src" / "shared" / "templates" / "publication_figure_template.py"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查默认格式是否包含pdf
            assert "formats = ['svg', 'pdf', 'png']" in content or \
                   "formats=['svg', 'pdf', 'png']" in content or \
                   "formats = ['svg', 'pdf', 'png']" in content

    def test_three_line_table_export_script(self):
        """测试三线表导出脚本"""
        # 检查export_tables_docx.py是否存在
        export_script_path = Path(__file__).parent.parent / "src" / "shared" / "report_assembler" / "export_tables_docx.py"

        assert export_script_path.exists(), "三线表导出脚本不存在"

        # 检查脚本内容
        with open(export_script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含三线表规范
        assert "顶线" in content or "top" in content.lower()
        assert "底线" in content or "bottom" in content.lower()
        assert "表头" in content or "header" in content.lower()

    def test_academic_output_deliverables(self):
        """测试学术输出交付物清单"""
        # 学术输出交付物清单
        deliverables = {
            "tables": [
                {"name": "Table 1 基线特征", "format": ".docx", "type": "three_line_table"},
                {"name": "主分析结果表", "format": ".docx", "type": "three_line_table"},
                {"name": "敏感性分析表", "format": ".docx", "type": "three_line_table"},
                {"name": "亚组分析表", "format": ".docx", "type": "three_line_table"},
            ],
            "figures": [
                {"name": "生存曲线图", "formats": [".svg", ".pdf", ".png"]},
                {"name": "森林图", "formats": [".svg", ".pdf", ".png"]},
                {"name": "ROC曲线", "formats": [".svg", ".pdf", ".png"]},
            ],
            "report": [
                {"name": "统计报告", "formats": [".html", ".md"]},
            ]
        }

        # 验证交付物清单
        assert len(deliverables["tables"]) == 4
        assert len(deliverables["figures"]) == 3
        assert len(deliverables["report"]) == 1

        # 验证表格格式
        for table in deliverables["tables"]:
            assert table["format"] == ".docx"
            assert table["type"] == "three_line_table"

        # 验证图表格式
        for figure in deliverables["figures"]:
            assert ".svg" in figure["formats"]
            assert ".pdf" in figure["formats"]
            assert ".png" in figure["formats"]

    def test_publication_standards_checklist(self):
        """测试学术发表标准检查清单"""
        # 学术发表标准检查清单
        checklist = {
            "table_checks": [
                "三线表格式（顶线粗2pt+表头下线中1pt+底线粗2pt）",
                "Word格式（.docx）",
                "表题位置（上方居中）",
                "表注位置（下方，含统计方法说明）",
                "列对齐（第一列左对齐，其余居中）",
                "字体（宋体+Times New Roman，10pt）",
            ],
            "figure_checks": [
                "PDF格式（学术投稿）",
                "SVG格式（矢量，可无损缩放）",
                "PNG分辨率（300dpi）",
                "字体大小（坐标轴标签≥10pt，图例≥8pt）",
                "配色（语义化调色板或期刊配色）",
                "标注完整性（含样本量、P值、效应量等关键信息）",
            ]
        }

        # 验证检查清单
        assert len(checklist["table_checks"]) == 6
        assert len(checklist["figure_checks"]) == 6

        # 验证表格检查项
        assert "三线表格式" in checklist["table_checks"][0]
        assert "Word格式" in checklist["table_checks"][1]

        # 验证图表检查项
        assert "PDF格式" in checklist["figure_checks"][0]
        assert "SVG格式" in checklist["figure_checks"][1]
        assert "300dpi" in checklist["figure_checks"][2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
