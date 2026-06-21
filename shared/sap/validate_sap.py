#!/usr/bin/env python3
"""
MSRA SAP 验证脚本

验证统计分析计划(SAP)的格式完整性和内容一致性。
用于 Stage 2.5 质量门闸和 Stage 3 执行前检查。
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SAPValidator:
    """SAP 验证器"""
    
    def __init__(self):
        """初始化验证器"""
        self.required_sections = [
            "1. 研究概述",
            "2. 分析人群",
            "3. 终点定义",
            "4. 统计方法",
            "5. 多重比较控制",
            "7. 变量构造定义",
            "8. 分析规范表"
        ]
        
        self.required_frontmatter = [
            "study_id",
            "version",
            "status",
            "study_type"
        ]
        
        self.valid_study_types = ["RCT", "observational", "diagnostic"]
        self.valid_statuses = ["draft", "under_review", "approved", "locked"]
    
    def validate_sap(self, sap_path: str) -> Dict[str, Any]:
        """
        验证SAP文件
        
        Args:
            sap_path: SAP文件路径
            
        Returns:
            验证结果字典
        """
        sap_path = Path(sap_path)
        
        if not sap_path.exists():
            return {"valid": False, "error": f"SAP文件不存在: {sap_path}"}
        
        # 读取SAP内容
        with open(sap_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析frontmatter
        frontmatter = self._parse_frontmatter(content)
        
        # 验证frontmatter
        frontmatter_issues = self._validate_frontmatter(frontmatter)
        
        # 验证章节完整性
        section_issues = self._validate_sections(content)
        
        # 验证变量构造定义
        variable_issues = self._validate_variable_definitions(content)
        
        # 验证分析规范表
        analysis_issues = self._validate_analysis_spec(content)
        
        # 汇总结果
        all_issues = frontmatter_issues + section_issues + variable_issues + analysis_issues
        
        return {
            "valid": len([i for i in all_issues if i["severity"] == "P0"]) == 0,
            "frontmatter": frontmatter,
            "issues": all_issues,
            "summary": {
                "total_issues": len(all_issues),
                "p0_issues": len([i for i in all_issues if i["severity"] == "P0"]),
                "p1_issues": len([i for i in all_issues if i["severity"] == "P1"]),
                "p2_issues": len([i for i in all_issues if i["severity"] == "P2"])
            }
        }
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """解析frontmatter"""
        frontmatter = {}
        
        # 匹配YAML frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
            except yaml.YAMLError:
                frontmatter = {}
        
        return frontmatter or {}
    
    def _validate_frontmatter(self, frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """验证frontmatter"""
        issues = []
        
        # 检查必需字段
        for field in self.required_frontmatter:
            if field not in frontmatter:
                issues.append({
                    "type": "frontmatter",
                    "severity": "P0",
                    "message": f"frontmatter缺少必需字段: {field}"
                })
        
        # 验证study_type
        if "study_type" in frontmatter:
            if frontmatter["study_type"] not in self.valid_study_types:
                issues.append({
                    "type": "frontmatter",
                    "severity": "P1",
                    "message": f"无效的study_type: {frontmatter['study_type']}。有效值: {self.valid_study_types}"
                })
        
        # 验证status
        if "status" in frontmatter:
            if frontmatter["status"] not in self.valid_statuses:
                issues.append({
                    "type": "frontmatter",
                    "severity": "P1",
                    "message": f"无效的status: {frontmatter['status']}。有效值: {self.valid_statuses}"
                })
        
        return issues
    
    def _validate_sections(self, content: str) -> List[Dict[str, Any]]:
        """验证章节完整性"""
        issues = []
        
        # 检查必需章节
        for section in self.required_sections:
            if section not in content:
                issues.append({
                    "type": "section",
                    "severity": "P0",
                    "message": f"缺少必需章节: {section}"
                })
        
        return issues
    
    def _validate_variable_definitions(self, content: str) -> List[Dict[str, Any]]:
        """验证变量构造定义"""
        issues = []
        
        # 检查Section 7是否存在表格
        section7_match = re.search(r'## 7\. 变量构造定义.*?(?=## 8\.|$)', content, re.DOTALL)
        if section7_match:
            section7 = section7_match.group(0)
            
            # 检查是否有表格
            if '|' not in section7:
                issues.append({
                    "type": "variable_definitions",
                    "severity": "P0",
                    "message": "Section 7 缺少变量构造定义表格"
                })
            else:
                # 检查表格列数
                rows = [line for line in section7.split('\n') if line.strip().startswith('|')]
                if len(rows) < 3:  # 表头 + 分隔线 + 至少1行数据
                    issues.append({
                        "type": "variable_definitions",
                        "severity": "P1",
                        "message": "Section 7 表格数据不足"
                    })
        else:
            issues.append({
                "type": "variable_definitions",
                "severity": "P0",
                "message": "未找到 Section 7 变量构造定义"
            })
        
        return issues
    
    def _validate_analysis_spec(self, content: str) -> List[Dict[str, Any]]:
        """验证分析规范表"""
        issues = []
        
        # 检查Section 8是否存在表格
        section8_match = re.search(r'## 8\. 分析规范表.*?(?=##|$)', content, re.DOTALL)
        if section8_match:
            section8 = section8_match.group(0)
            
            # 检查是否有表格
            if '|' not in section8:
                issues.append({
                    "type": "analysis_spec",
                    "severity": "P0",
                    "message": "Section 8 缺少分析规范表"
                })
            else:
                # 检查表格列数
                rows = [line for line in section8.split('\n') if line.strip().startswith('|')]
                if len(rows) < 3:  # 表头 + 分隔线 + 至少1行数据
                    issues.append({
                        "type": "analysis_spec",
                        "severity": "P1",
                        "message": "Section 8 表格数据不足"
                    })
        else:
            issues.append({
                "type": "analysis_spec",
                "severity": "P0",
                "message": "未找到 Section 8 分析规范表"
            })
        
        return issues
    
    def generate_validation_report(self, validation_result: Dict[str, Any]) -> str:
        """
        生成验证报告
        
        Args:
            validation_result: 验证结果
            
        Returns:
            报告字符串
        """
        report = f"""# SAP 验证报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 验证结果: {'✅ 通过' if validation_result['valid'] else '❌ 未通过'}

## 问题摘要

- **P0 问题**: {validation_result['summary']['p0_issues']} 个（必须修复）
- **P1 问题**: {validation_result['summary']['p1_issues']} 个（建议修复）
- **P2 问题**: {validation_result['summary']['p2_issues']} 个（信息性）

## 问题详情

"""
        
        for issue in validation_result['issues']:
            severity_icon = {'P0': '🔴', 'P1': '🟡', 'P2': '🔵'}.get(issue['severity'], '⚪')
            report += f"### {severity_icon} {issue['type']}\n"
            report += f"- **严重程度**: {issue['severity']}\n"
            report += f"- **问题**: {issue['message']}\n\n"
        
        return report


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 创建验证器
    validator = SAPValidator()
    
    # 示例SAP内容
    sample_sap = """---
study_id: "RCT001"
version: "1.0"
created_date: "2026-05-30"
status: "approved"
study_type: "RCT"
---

# 统计分析计划 (Statistical Analysis Plan)

## 1. 研究概述

### 1.1 研究设计和目的
- 研究类型: RCT
- 研究目的: 评估药物A对HbA1c的影响

## 2. 分析人群

### 2.1 意向性治疗人群 (ITT)
- 定义: 所有随机化患者

## 3. 终点定义

### 3.1 主要终点
- 名称: HbA1c变化
- 定义: 基线到24周的HbA1c变化

## 4. 统计方法

### 4.1 主要分析
- 方法: ANCOVA
- 调整变量: baseline_hba1c, age

## 5. 多重比较控制
- 主要终点单独检验

## 7. 变量构造定义

| 变量名 | 类型 | 构造公式 | 切点/分类 | 依据 | 缺失处理 |
|--------|------|---------|----------|------|---------|
| age | 连续 | 入组日期 - 出生日期（年） | - | 标准人口学 | 删除 |
| hba1c_change | 连续 | 24周HbA1c - 基线HbA1c | - | 主要终点 | 多重插补 |

## 8. 分析规范表

| 分析ID | 分析名称 | 人群 | 方法 | 主要变量 | 调整变量 | 缺失处理 | 假设检验 |
|--------|---------|------|------|---------|---------|---------|---------|
| A1 | 主要终点分析 | ITT | ANCOVA | hba1c_change | baseline_hba1c, age | 多重插补 | F-test |
"""
    
    # 写入临时文件
    temp_sap = Path("temp_sap.md")
    with open(temp_sap, 'w', encoding='utf-8') as f:
        f.write(sample_sap)
    
    # 验证SAP
    result = validator.validate_sap(temp_sap)
    
    # 生成报告
    report = validator.generate_validation_report(result)
    
    logger.info("report")
    
    # 清理临时文件
    temp_sap.unlink()