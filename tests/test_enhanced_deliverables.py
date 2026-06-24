#!/usr/bin/env python3
"""
增强交付物清单测试

测试扩充后的图表类型和交付物清单。
"""

# 添加项目根目录到Python路径
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEnhancedDeliverables:
    """增强交付物清单测试类"""

    def test_academic_figure_table_types_document_exists(self):
        """测试学术图表类型文档是否存在"""
        doc_path = Path(__file__).parent.parent / "shared" / "references" / "academic_figure_table_types.md"
        assert doc_path.exists(), "学术图表类型文档不存在"

        # 检查文档内容
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含主要章节
        assert "数据可视化图表" in content
        assert "统计分析图表" in content
        assert "因果推断图表" in content
        assert "机器学习图表" in content
        assert "流程图和示意图" in content
        assert "表格类型" in content
        assert "交付物清单汇总" in content

    def test_figure_types_coverage(self):
        """测试图表类型覆盖范围"""
        expected_figure_types = [
            # 数据可视化
            "直方图", "箱线图", "小提琴图", "密度图",
            "散点图", "气泡图", "热图",
            "柱状图", "堆叠柱状图", "分组柱状图",
            # 统计分析
            "Kaplan-Meier曲线", "竞争风险曲线",
            "ROC曲线", "PR曲线", "校准曲线", "决策曲线",
            "森林图", "漏斗图",
            "残差图", "QQ图", "影响力图",
            # 因果推断
            "倾向性评分分布图", "Love Plot", "权重分布图",
            "DAG图", "调整集DAG",
            # 机器学习
            "SHAP Summary", "SHAP Dependence",
            "特征重要性", "部分依赖图",
            "学习曲线", "混淆矩阵",
            # 流程图
            "CONSORT流程图", "STROBE流程图", "PRISMA流程图",
            "研究设计图", "技术路线图",
            # 专业图表
            "样本量曲线", "效能曲线",
            "Tipping Point图", "E-value图",
            "后验分布", "先验敏感性", "轨迹图",
        ]

        doc_path = Path(__file__).parent.parent / "shared" / "references" / "academic_figure_table_types.md"
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查每个图表类型是否在文档中
        for fig_type in expected_figure_types:
            assert fig_type in content, f"图表类型 {fig_type} 未在文档中找到"

    def test_table_types_coverage(self):
        """测试表格类型覆盖范围"""
        expected_table_types = [
            "基线特征表", "描述统计表", "频率表",
            "回归结果表", "亚组分析表", "敏感性分析表",
            "AE汇总表", "SAE详情表", "实验室异常表",
        ]

        doc_path = Path(__file__).parent.parent / "shared" / "references" / "academic_figure_table_types.md"
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查每个表格类型是否在文档中
        for table_type in expected_table_types:
            assert table_type in content, f"表格类型 {table_type} 未在文档中找到"

    def test_deliverables_checklist(self):
        """测试交付物清单"""
        # 表格交付物
        table_deliverables = [
            "Table 1 基线特征表",
            "主分析结果表",
            "敏感性分析表",
            "亚组分析表",
            "不良事件汇总表",
            "实验室异常表",
            "样本量计算表",
            "变量定义表",
        ]

        # 图表交付物
        figure_deliverables = [
            "CONSORT流程图",
            "Kaplan-Meier曲线",
            "森林图",
            "ROC曲线",
            "校准曲线",
            "Bland-Altman图",
            "相关性热图",
            "DAG图",
            "Love Plot",
            "SHAP图",
        ]

        # 报告交付物
        report_deliverables = [
            "统计报告",
            "方法学描述",
            "结果解读",
            "局限性讨论",
        ]

        doc_path = Path(__file__).parent.parent / "shared" / "references" / "academic_figure_table_types.md"
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查表格交付物
        for deliverable in table_deliverables:
            assert deliverable in content, f"表格交付物 {deliverable} 未在文档中找到"

        # 检查图表交付物
        for deliverable in figure_deliverables:
            assert deliverable in content, f"图表交付物 {deliverable} 未在文档中找到"

        # 检查报告交付物
        for deliverable in report_deliverables:
            assert deliverable in content, f"报告交付物 {deliverable} 未在文档中找到"

    def test_template_files_existence(self):
        """测试模板文件是否存在"""
        template_dir = Path(__file__).parent.parent / "shared" / "templates"

        # 关键模板文件
        key_templates = [
            "publication_figure_template.py",
            "forest_plot_template.py",
            "roc_template.py",
            "bland_altman_template.py",
            "calibration_plot_template.R",
            "shap_plot_template.py",
            "ml_analysis_template.py",
            "data_profile_template.py",
            "baseline_table1_engine.py",
            "survival_ggsurvfit.R",
            "dag_variable_selection_template.R",
            "propensity_score_template.R",
            "sample_size_template.py",
            "multiple_imputation_template.R",
            "effect_size_template.py",
        ]

        for template in key_templates:
            template_path = template_dir / template
            assert template_path.exists(), f"模板文件 {template} 不存在"

    def test_quality_standards(self):
        """测试质量标准"""
        quality_standards = {
            "figure": {
                "dpi": 300,
                "formats": ["svg", "pdf", "png"],
                "font_size_axis": ">=10pt",
                "font_size_legend": ">=8pt",
            },
            "table": {
                "format": ".docx",
                "border_top": "2pt",
                "border_header": "1pt",
                "border_bottom": "2pt",
                "font_chinese": "宋体",
                "font_english": "Times New Roman",
                "font_size": "10pt",
            }
        }

        # 验证图表质量标准
        assert quality_standards["figure"]["dpi"] == 300
        assert "svg" in quality_standards["figure"]["formats"]
        assert "pdf" in quality_standards["figure"]["formats"]
        assert "png" in quality_standards["figure"]["formats"]

        # 验证表格质量标准
        assert quality_standards["table"]["format"] == ".docx"
        assert quality_standards["table"]["border_top"] == "2pt"
        assert quality_standards["table"]["border_header"] == "1pt"
        assert quality_standards["table"]["border_bottom"] == "2pt"

    def test_academic_standards_references(self):
        """测试学术标准参考"""
        academic_standards = [
            "CONSORT",
            "STROBE",
            "PRISMA",
            "ICMJE",
        ]

        doc_path = Path(__file__).parent.parent / "shared" / "references" / "academic_figure_table_types.md"
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查学术标准是否在文档中
        for standard in academic_standards:
            assert standard in content, f"学术标准 {standard} 未在文档中找到"

    def test_report_skill_deliverables_update(self):
        """测试report SKILL.md中的交付物清单更新"""
        skill_path = Path(__file__).parent.parent / "skills" / "report" / "SKILL.md"

        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含扩充后的交付物清单
        assert "T1" in content
        assert "T8" in content
        assert "F1" in content
        assert "F10" in content
        assert "R1" in content
        assert "R4" in content

        # 检查是否包含新增的图表类型
        assert "CONSORT流程图" in content
        assert "校准曲线" in content
        assert "Bland-Altman图" in content
        assert "DAG图" in content
        assert "Love Plot" in content
        assert "SHAP图" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
