#!/usr/bin/env python3
"""
MSRA SAP到方法学描述转换器

解析SAP中的方法选择，生成符合报告规范的方法学描述。
用于 Report Generation 的 Phase 5 方法学描述生成。
"""

import json
import re
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SAPToMethods:
    """SAP到方法学描述转换器"""
    
    def __init__(self, sap_path: str = None, template_path: str = None):
        """
        初始化转换器
        
        Args:
            sap_path: SAP文件路径
            template_path: 模板文件路径
        """
        self.sap_data = {}
        self.templates = self._load_templates(template_path)
        
        if sap_path:
            self.load_sap(sap_path)
    
    def load_sap(self, sap_path: str) -> Dict[str, Any]:
        """
        加载SAP文件
        
        Args:
            sap_path: SAP文件路径
            
        Returns:
            SAP数据字典
        """
        try:
            with open(sap_path, 'r', encoding='utf-8') as f:
                if sap_path.endswith('.json'):
                    self.sap_data = json.load(f)
                else:
                    # 假设是Markdown格式
                    content = f.read()
                    self.sap_data = self._parse_markdown_sap(content)
            
            return self.sap_data
        except Exception as e:
            logger.info(f"加载SAP文件失败: {e}")
            return {}
    
    def _parse_markdown_sap(self, content: str) -> Dict[str, Any]:
        """解析Markdown格式的SAP"""
        sap_data = {
            "study_design": "",
            "population": "",
            "sample_size": "",
            "primary_analysis": "",
            "secondary_analyses": [],
            "sensitivity_analyses": [],
            "subgroup_analyses": [],
            "software": ""
        }
        
        # 简单解析逻辑（实际应用中需要更复杂的解析）
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测章节标题
            if line.startswith('#'):
                current_section = line.replace('#', '').strip().lower()
            elif current_section and line:
                if 'study design' in current_section:
                    sap_data["study_design"] += line + " "
                elif 'population' in current_section:
                    sap_data["population"] += line + " "
                elif 'sample size' in current_section:
                    sap_data["sample_size"] += line + " "
                elif 'primary' in current_section:
                    sap_data["primary_analysis"] += line + " "
                elif 'secondary' in current_section:
                    sap_data["secondary_analyses"].append(line)
                elif 'sensitivity' in current_section:
                    sap_data["sensitivity_analyses"].append(line)
                elif 'subgroup' in current_section:
                    sap_data["subgroup_analyses"].append(line)
                elif 'software' in current_section:
                    sap_data["software"] += line + " "
        
        return sap_data
    
    def _load_templates(self, template_path: str = None) -> Dict[str, str]:
        """加载方法学描述模板"""
        default_templates = {
            "study_design": "本研究采用{design}设计。",
            "population": "研究人群包括{population_description}。",
            "sample_size": "样本量计算基于{sample_size_justification}。",
            "primary_analysis": "主要分析采用{method}，效应量以{effect_measure}及其95%置信区间表示。",
            "secondary_analyses": "次要分析包括{analyses}。",
            "sensitivity_analyses": "敏感性分析包括{analyses}。",
            "subgroup_analyses": "亚组分析包括{analyses}。",
            "software": "统计分析使用{software}（版本{version}）进行。"
        }
        
        if template_path and Path(template_path).exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    default_templates.update(templates)
            except Exception as e:
                logger.info(f"加载模板文件失败: {e}")
        
        return default_templates
    
    def generate_methods_description(self, output_format: str = "markdown") -> str:
        """
        生成方法学描述
        
        Args:
            output_format: 输出格式（"markdown" 或 "text"）
            
        Returns:
            方法学描述字符串
        """
        if not self.sap_data:
            return "未加载SAP数据，无法生成方法学描述。"
        
        sections = []
        
        # 研究设计
        if self.sap_data.get("study_design"):
            sections.append(self._generate_study_design_section())
        
        # 研究人群
        if self.sap_data.get("population"):
            sections.append(self._generate_population_section())
        
        # 样本量
        if self.sap_data.get("sample_size"):
            sections.append(self._generate_sample_size_section())
        
        # 主要分析
        if self.sap_data.get("primary_analysis"):
            sections.append(self._generate_primary_analysis_section())
        
        # 次要分析
        if self.sap_data.get("secondary_analyses"):
            sections.append(self._generate_secondary_analyses_section())
        
        # 敏感性分析
        if self.sap_data.get("sensitivity_analyses"):
            sections.append(self._generate_sensitivity_analyses_section())
        
        # 亚组分析
        if self.sap_data.get("subgroup_analyses"):
            sections.append(self._generate_subgroup_analyses_section())
        
        # 软件
        if self.sap_data.get("software"):
            sections.append(self._generate_software_section())
        
        # 组装完整描述
        full_description = "\n\n".join(sections)
        
        if output_format == "markdown":
            return f"## 统计分析方法\n\n{full_description}"
        else:
            return full_description
    
    def _generate_study_design_section(self) -> str:
        """生成研究设计部分"""
        design = self.sap_data.get("study_design", "")
        template = self.templates.get("study_design", "")
        
        return template.format(design=design)
    
    def _generate_population_section(self) -> str:
        """生成研究人群部分"""
        population = self.sap_data.get("population", "")
        template = self.templates.get("population", "")
        
        return template.format(population_description=population)
    
    def _generate_sample_size_section(self) -> str:
        """生成样本量部分"""
        sample_size = self.sap_data.get("sample_size", "")
        template = self.templates.get("sample_size", "")
        
        return template.format(sample_size_justification=sample_size)
    
    def _generate_primary_analysis_section(self) -> str:
        """生成主要分析部分"""
        primary_analysis = self.sap_data.get("primary_analysis", "")
        template = self.templates.get("primary_analysis", "")
        
        # 解析主要分析方法
        method = self._extract_method(primary_analysis)
        effect_measure = self._extract_effect_measure(primary_analysis)
        
        return template.format(
            method=method,
            effect_measure=effect_measure
        )
    
    def _generate_secondary_analyses_section(self) -> str:
        """生成次要分析部分"""
        secondary_analyses = self.sap_data.get("secondary_analyses", [])
        template = self.templates.get("secondary_analyses", "")
        
        if secondary_analyses:
            analyses_text = "、".join(secondary_analyses[:3])  # 最多列出3个
            if len(secondary_analyses) > 3:
                analyses_text += f"等{len(secondary_analyses)}项分析"
        else:
            analyses_text = "无"
        
        return template.format(analyses=analyses_text)
    
    def _generate_sensitivity_analyses_section(self) -> str:
        """生成敏感性分析部分"""
        sensitivity_analyses = self.sap_data.get("sensitivity_analyses", [])
        template = self.templates.get("sensitivity_analyses", "")
        
        if sensitivity_analyses:
            analyses_text = "、".join(sensitivity_analyses[:3])  # 最多列出3个
            if len(sensitivity_analyses) > 3:
                analyses_text += f"等{len(sensitivity_analyses)}项分析"
        else:
            analyses_text = "无"
        
        return template.format(analyses=analyses_text)
    
    def _generate_subgroup_analyses_section(self) -> str:
        """生成亚组分析部分"""
        subgroup_analyses = self.sap_data.get("subgroup_analyses", [])
        template = self.templates.get("subgroup_analyses", "")
        
        if subgroup_analyses:
            analyses_text = "、".join(subgroup_analyses[:3])  # 最多列出3个
            if len(subgroup_analyses) > 3:
                analyses_text += f"等{len(subgroup_analyses)}项分析"
        else:
            analyses_text = "无"
        
        return template.format(analyses=analyses_text)
    
    def _generate_software_section(self) -> str:
        """生成软件部分"""
        software = self.sap_data.get("software", "")
        template = self.templates.get("software", "")
        
        # 尝试提取软件名称和版本
        software_name = software
        version = ""
        
        version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', software)
        if version_match:
            version = version_match.group(1)
            software_name = software.replace(version, "").strip()
        
        return template.format(
            software=software_name,
            version=version
        )
    
    def _extract_method(self, analysis_text: str) -> str:
        """从分析文本中提取方法"""
        method_keywords = {
            "t检验": "独立样本t检验",
            "t-test": "独立样本t检验",
            "ANOVA": "单因素方差分析",
            "anova": "单因素方差分析",
            "卡方": "χ²检验",
            "chi-square": "χ²检验",
            "Fisher": "Fisher精确检验",
            "Mann-Whitney": "Mann-Whitney U检验",
            "Kruskal-Wallis": "Kruskal-Wallis检验",
            "线性回归": "线性回归",
            "linear regression": "线性回归",
            "Logistic回归": "Logistic回归",
            "logistic regression": "Logistic回归",
            "Cox": "Cox比例风险回归",
            "cox": "Cox比例风险回归"
        }
        
        for keyword, method in method_keywords.items():
            if keyword.lower() in analysis_text.lower():
                return method
        
        return "适当的统计方法"
    
    def _extract_effect_measure(self, analysis_text: str) -> str:
        """从分析文本中提取效应量"""
        effect_keywords = {
            "均数差": "均数差",
            "mean difference": "均数差",
            "MD": "均数差",
            "标准化均数差": "标准化均数差",
            "SMD": "标准化均数差",
            "Cohen's d": "Cohen's d",
            "优势比": "优势比",
            "OR": "优势比",
            "odds ratio": "优势比",
            "风险比": "风险比",
            "HR": "风险比",
            "hazard ratio": "风险比",
            "相对风险": "相对风险",
            "RR": "相对风险",
            "relative risk": "相对风险"
        }
        
        for keyword, effect in effect_keywords.items():
            if keyword.lower() in analysis_text.lower():
                return effect
        
        return "效应量"
    
    def generate_methods_for_report(self, report_type: str = "CONSORT") -> Dict[str, str]:
        """
        为特定报告规范生成方法学描述
        
        Args:
            report_type: 报告类型（CONSORT/STROBE/STARD等）
            
        Returns:
            各部分的方法学描述字典
        """
        sections = {}
        
        # 根据报告类型调整描述
        if report_type == "CONSORT":
            sections["randomization"] = "采用随机数字表法进行随机分组。"
            sections["blinding"] = "采用双盲设计，患者和研究者均不知分组情况。"
            sections["allocation_concealment"] = "采用中央随机化系统进行分配隐藏。"
        elif report_type == "STROBE":
            sections["design"] = "本研究采用队列/病例对照设计。"
            sections["setting"] = "研究在[研究机构]进行，招募时间为[时间范围]。"
            sections["participants"] = "纳入标准：[标准1]、[标准2]；排除标准：[标准1]、[标准2]。"
        elif report_type == "STARD":
            sections["study_design"] = "本研究采用诊断准确性研究设计。"
            sections["index_test"] = "索引试验：[试验名称]。"
            sections["reference_standard"] = "金标准：[金标准名称]。"
        
        # 生成通用方法学描述
        sections["statistical_analysis"] = self.generate_methods_description()
        
        return sections


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 创建转换器
    converter = SAPToMethods()
    
    # 示例SAP数据
    converter.sap_data = {
        "study_design": "随机对照试验",
        "population": "年龄18-65岁、确诊为[疾病]的患者",
        "sample_size": "基于主要结局指标的效应量0.5，检验效能80%，双侧α=0.05，计算需要每组至少80例患者",
        "primary_analysis": "主要分析采用独立样本t检验比较两组主要结局指标的差异，效应量以均数差及其95%置信区间表示",
        "secondary_analyses": ["次要结局指标的组间比较", "亚组分析", "相关性分析"],
        "sensitivity_analyses": ["缺失数据敏感性分析", "不同统计方法敏感性分析"],
        "subgroup_analyses": ["年龄亚组分析", "性别亚组分析", "疾病严重程度亚组分析"],
        "software": "R 4.3.1"
    }
    
    # 生成方法学描述
    methods_description = converter.generate_methods_description()
    
    logger.info("生成的方法学描述：")
    logger.info("methods_description")
    
    # 为CONSORT报告生成方法学描述
    consort_methods = converter.generate_methods_for_report("CONSORT")
    
    logger.info("\nCONSORT报告方法学描述：")
    for section, content in consort_methods.items():
        logger.info(f"\n{section}:")
        logger.info("content")