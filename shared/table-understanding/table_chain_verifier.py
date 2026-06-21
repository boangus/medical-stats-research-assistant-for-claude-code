"""
Chain-of-Table 核查器

基于 Chain-of-Table 方法逐步构建和验证表格，提升复杂表格的理解能力。

参考文献：
Wang et al. "Chain-of-Table: Evolving Tables in the Reasoning Chain for Table Understanding"

主要功能：
1. 解析表格结构
2. 逐步验证数据一致性
3. 检查逻辑关系
4. 生成核查报告
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class VerificationStep(Enum):
    """验证步骤枚举"""
    STRUCTURE = "structure"           # 结构验证
    DATA_TYPE = "data_type"          # 数据类型验证
    CONSISTENCY = "consistency"       # 一致性验证
    LOGIC = "logic"                  # 逻辑关系验证
    COMPLETENESS = "completeness"     # 完整性验证


@dataclass
class VerificationResult:
    """验证结果数据类"""
    step: VerificationStep
    passed: bool
    score: float
    details: Dict[str, Any]
    issues: List[str]
    suggestions: List[str]


class TableChainVerifier:
    """
    Chain-of-Table 核查器
    
    通过逐步验证表格的各个方面，提供全面的表格质量评估。
    
    使用方法：
    ```python
    verifier = TableChainVerifier(table_data)
    results = verifier.verify()
    ```
    """
    
    def __init__(self, table_data: Dict[str, Any]):
        """
        初始化核查器
        
        Parameters
        ----------
        table_data : Dict
            表格数据，包含以下字段：
            - headers: List[str] - 表头列表
            - rows: List[List[str]] - 数据行列表
            - metadata: Dict (可选) - 表格元数据
        """
        self.table_data = table_data
        self.headers = table_data.get('headers', [])
        self.rows = table_data.get('rows', [])
        self.metadata = table_data.get('metadata', {})
        
        # 验证结果
        self.results: List[VerificationResult] = []
        self.overall_score = 0.0
        self.issues: List[str] = []
        self.suggestions: List[str] = []
    
    def verify(self) -> Dict[str, Any]:
        """
        执行完整的表格验证
        
        Returns
        -------
        Dict
            验证结果，包含：
            - score: 总体分数 (0-1)
            - steps: 各步骤验证结果
            - issues: 发现的问题
            - suggestions: 改进建议
        """
        # 重置结果
        self.results = []
        self.issues = []
        self.suggestions = []
        
        # 执行验证步骤
        self._verify_structure()
        self._verify_data_types()
        self._verify_consistency()
        self._verify_logic()
        self._verify_completeness()
        
        # 计算总体分数
        self._calculate_overall_score()
        
        return {
            'score': self.overall_score,
            'steps': [
                {
                    'step': result.step.value,
                    'passed': result.passed,
                    'score': result.score,
                    'details': result.details,
                    'issues': result.issues,
                    'suggestions': result.suggestions
                }
                for result in self.results
            ],
            'issues': self.issues,
            'suggestions': self.suggestions,
            'summary': self._generate_summary()
        }
    
    def _verify_structure(self):
        """验证表格结构"""
        issues = []
        suggestions = []
        score = 1.0
        
        # 检查表头是否存在
        if not self.headers:
            issues.append("表格缺少表头")
            suggestions.append("添加表头行以标识各列内容")
            score -= 0.3
        
        # 检查数据行是否存在
        if not self.rows:
            issues.append("表格没有数据行")
            suggestions.append("添加数据行以填充表格内容")
            score -= 0.5
        
        # 检查列数一致性
        if self.headers and self.rows:
            header_count = len(self.headers)
            for i, row in enumerate(self.rows):
                if len(row) != header_count:
                    issues.append(f"第{i+1}行列数({len(row)})与表头列数({header_count})不匹配")
                    suggestions.append(f"调整第{i+1}行的列数以匹配表头")
                    score -= 0.1
        
        # 检查空行
        empty_rows = [i for i, row in enumerate(self.rows) if all(cell.strip() == '' for cell in row)]
        if empty_rows:
            issues.append(f"发现{len(empty_rows)}个空行")
            suggestions.append("删除空行或填充数据")
            score -= 0.05 * len(empty_rows)
        
        # 检查重复表头
        if self.headers:
            duplicate_headers = [h for h in self.headers if self.headers.count(h) > 1]
            if duplicate_headers:
                issues.append(f"发现重复的表头: {set(duplicate_headers)}")
                suggestions.append("确保每个表头名称唯一")
                score -= 0.2
        
        score = max(0.0, score)
        
        self.results.append(VerificationResult(
            step=VerificationStep.STRUCTURE,
            passed=score >= 0.7,
            score=score,
            details={
                'header_count': len(self.headers),
                'row_count': len(self.rows),
                'empty_rows': len(empty_rows) if 'empty_rows' in locals() else 0,
                'duplicate_headers': list(set(duplicate_headers)) if 'duplicate_headers' in locals() else []
            },
            issues=issues,
            suggestions=suggestions
        ))
        
        self.issues.extend(issues)
        self.suggestions.extend(suggestions)
    
    def _verify_data_types(self):
        """验证数据类型一致性"""
        issues = []
        suggestions = []
        score = 1.0
        
        if not self.headers or not self.rows:
            self.results.append(VerificationResult(
                step=VerificationStep.DATA_TYPE,
                passed=False,
                score=0.0,
                details={'error': '缺少表头或数据行'},
                issues=['无法进行数据类型验证'],
                suggestions=['确保表格有表头和数据行']
            ))
            return
        
        # 分析每列的数据类型
        column_types = {}
        for col_idx, header in enumerate(self.headers):
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            column_types[header] = self._detect_column_type(column_values)
        
        # 检查类型一致性
        for col_idx, header in enumerate(self.headers):
            expected_type = column_types[header]
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            
            type_violations = 0
            for value in column_values:
                if value.strip() and not self._check_type(value, expected_type):
                    type_violations += 1
            
            if type_violations > 0:
                violation_rate = type_violations / len(column_values)
                if violation_rate > 0.1:  # 超过10%的类型不一致
                    issues.append(f"列'{header}'有{type_violations}个值类型不一致")
                    suggestions.append(f"检查列'{header}'的数据类型，确保所有值类型一致")
                    score -= 0.1
        
        score = max(0.0, score)
        
        self.results.append(VerificationResult(
            step=VerificationStep.DATA_TYPE,
            passed=score >= 0.8,
            score=score,
            details={
                'column_types': column_types,
                'total_violations': sum(1 for issue in issues if '类型不一致' in issue)
            },
            issues=issues,
            suggestions=suggestions
        ))
        
        self.issues.extend(issues)
        self.suggestions.extend(suggestions)
    
    def _verify_consistency(self):
        """验证数据一致性"""
        issues = []
        suggestions = []
        score = 1.0
        
        if not self.headers or not self.rows:
            self.results.append(VerificationResult(
                step=VerificationStep.CONSISTENCY,
                passed=False,
                score=0.0,
                details={'error': '缺少表头或数据行'},
                issues=['无法进行一致性验证'],
                suggestions=['确保表格有表头和数据行']
            ))
            return
        
        # 检查数值范围一致性
        for col_idx, header in enumerate(self.headers):
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            numeric_values = []
            
            for value in column_values:
                try:
                    if value.strip():
                        numeric_values.append(float(value))
                except ValueError:
                    continue
            
            if numeric_values:
                min_val = min(numeric_values)
                max_val = max(numeric_values)
                mean_val = sum(numeric_values) / len(numeric_values)
                
                # 检查异常值 (超过3个标准差)
                if len(numeric_values) > 1:
                    variance = sum((x - mean_val) ** 2 for x in numeric_values) / len(numeric_values)
                    std_val = variance ** 0.5
                    
                    outliers = [x for x in numeric_values if abs(x - mean_val) > 3 * std_val]
                    if outliers:
                        issues.append(f"列'{header}'发现{len(outliers)}个异常值")
                        suggestions.append(f"检查列'{header}'的异常值: {outliers[:3]}")
                        score -= 0.05
        
        # 检查分类变量一致性
        for col_idx, header in enumerate(self.headers):
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            unique_values = list(set(v.strip() for v in column_values if v.strip()))
            
            # 检查是否有多余的空格或大小写不一致
            normalized_values = [v.lower().strip() for v in unique_values]
            if len(set(normalized_values)) < len(unique_values):
                issues.append(f"列'{header}'存在大小写或空格不一致")
                suggestions.append(f"统一列'{header}'的值格式")
                score -= 0.1
        
        score = max(0.0, score)
        
        self.results.append(VerificationResult(
            step=VerificationStep.CONSISTENCY,
            passed=score >= 0.8,
            score=score,
            details={
                'columns_checked': len(self.headers),
                'issues_found': len(issues)
            },
            issues=issues,
            suggestions=suggestions
        ))
        
        self.issues.extend(issues)
        self.suggestions.extend(suggestions)
    
    def _verify_logic(self):
        """验证逻辑关系"""
        issues = []
        suggestions = []
        score = 1.0
        
        if not self.headers or not self.rows:
            self.results.append(VerificationResult(
                step=VerificationStep.LOGIC,
                passed=False,
                score=0.0,
                details={'error': '缺少表头或数据行'},
                issues=['无法进行逻辑关系验证'],
                suggestions=['确保表格有表头和数据行']
            ))
            return
        
        # 检查百分比列是否总和接近100%
        for col_idx, header in enumerate(self.headers):
            if '百分比' in header.lower() or '%' in header or 'percent' in header.lower():
                column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
                numeric_values = []
                
                for value in column_values:
                    try:
                        if value.strip():
                            # 移除百分号
                            clean_value = value.replace('%', '').strip()
                            numeric_values.append(float(clean_value))
                    except ValueError:
                        continue
                
                if numeric_values:
                    total = sum(numeric_values)
                    if abs(total - 100) > 5:  # 允许5%的误差
                        issues.append(f"百分比列'{header}'总和为{total:.1f}%，不等于100%")
                        suggestions.append(f"检查列'{header}'的百分比计算是否正确")
                        score -= 0.2
        
        # 检查ID列的唯一性
        for col_idx, header in enumerate(self.headers):
            if 'id' in header.lower() or '编号' in header or '序号' in header:
                column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
                unique_values = [v.strip() for v in column_values if v.strip()]
                
                if len(unique_values) != len(set(unique_values)):
                    duplicate_count = len(unique_values) - len(set(unique_values))
                    issues.append(f"ID列'{header}'有{duplicate_count}个重复值")
                    suggestions.append(f"确保列'{header}'的值唯一")
                    score -= 0.3
        
        # 检查日期列的顺序
        date_columns = []
        for col_idx, header in enumerate(self.headers):
            if '日期' in header.lower() or 'date' in header.lower() or '时间' in header.lower():
                date_columns.append((col_idx, header))
        
        for col_idx, header in date_columns:
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            # 简单检查日期格式一致性
            date_formats = set()
            for value in column_values:
                if value.strip():
                    if '-' in value:
                        date_formats.add('YYYY-MM-DD')
                    elif '/' in value:
                        date_formats.add('YYYY/MM/DD')
                    elif '.' in value:
                        date_formats.add('YYYY.MM.DD')
            
            if len(date_formats) > 1:
                issues.append(f"日期列'{header}'使用了多种日期格式")
                suggestions.append(f"统一列'{header}'的日期格式")
                score -= 0.1
        
        score = max(0.0, score)
        
        self.results.append(VerificationResult(
            step=VerificationStep.LOGIC,
            passed=score >= 0.7,
            score=score,
            details={
                'logic_checks_performed': ['percentage_sum', 'id_uniqueness', 'date_format'],
                'issues_found': len(issues)
            },
            issues=issues,
            suggestions=suggestions
        ))
        
        self.issues.extend(issues)
        self.suggestions.extend(suggestions)
    
    def _verify_completeness(self):
        """验证数据完整性"""
        issues = []
        suggestions = []
        score = 1.0
        
        if not self.headers or not self.rows:
            self.results.append(VerificationResult(
                step=VerificationStep.COMPLETENESS,
                passed=False,
                score=0.0,
                details={'error': '缺少表头或数据行'},
                issues=['无法进行完整性验证'],
                suggestions=['确保表格有表头和数据行']
            ))
            return
        
        # 检查缺失值
        total_cells = len(self.headers) * len(self.rows)
        missing_cells = 0
        missing_columns = {}
        
        for col_idx, header in enumerate(self.headers):
            column_missing = 0
            for row in self.rows:
                if col_idx < len(row):
                    if row[col_idx].strip() == '' or row[col_idx].strip().lower() in ['na', 'n/a', 'null', 'none', '-']:
                        column_missing += 1
                        missing_cells += 1
            
            if column_missing > 0:
                missing_rate = column_missing / len(self.rows)
                missing_columns[header] = {
                    'count': column_missing,
                    'rate': missing_rate
                }
                
                if missing_rate > 0.1:  # 超过10%缺失
                    issues.append(f"列'{header}'有{column_missing}个缺失值({missing_rate:.1%})")
                    suggestions.append(f"处理列'{header}'的缺失值")
                    score -= 0.1
        
        # 计算总体缺失率
        missing_rate = missing_cells / total_cells if total_cells > 0 else 0
        if missing_rate > 0.05:  # 超过5%总体缺失
            issues.append(f"表格总体缺失率为{missing_rate:.1%}")
            suggestions.append("考虑使用数据填充或删除高缺失率的列")
            score -= 0.2
        
        score = max(0.0, score)
        
        self.results.append(VerificationResult(
            step=VerificationStep.COMPLETENESS,
            passed=score >= 0.8,
            score=score,
            details={
                'total_cells': total_cells,
                'missing_cells': missing_cells,
                'missing_rate': missing_rate,
                'missing_columns': missing_columns
            },
            issues=issues,
            suggestions=suggestions
        ))
        
        self.issues.extend(issues)
        self.suggestions.extend(suggestions)
    
    def _detect_column_type(self, values: List[str]) -> str:
        """检测列的数据类型"""
        numeric_count = 0
        date_count = 0
        text_count = 0
        
        for value in values:
            if not value.strip():
                continue
            
            # 尝试解析为数字
            try:
                float(value.replace(',', '').replace('%', ''))
                numeric_count += 1
                continue
            except ValueError:
                pass
            
            # 尝试解析为日期
            if any(sep in value for sep in ['-', '/', '.']):
                parts = value.replace('.', '-').replace('/', '-').split('-')
                if len(parts) == 3:
                    try:
                        int(parts[0])
                        int(parts[1])
                        int(parts[2])
                        date_count += 1
                        continue
                    except ValueError:
                        pass
            
            text_count += 1
        
        total = numeric_count + date_count + text_count
        if total == 0:
            return 'empty'
        
        if numeric_count / total > 0.7:
            return 'numeric'
        elif date_count / total > 0.7:
            return 'date'
        else:
            return 'text'
    
    def _check_type(self, value: str, expected_type: str) -> bool:
        """检查值是否符合预期类型"""
        if not value.strip():
            return True  # 空值被认为是有效的
        
        if expected_type == 'numeric':
            try:
                float(value.replace(',', '').replace('%', ''))
                return True
            except ValueError:
                return False
        
        elif expected_type == 'date':
            if any(sep in value for sep in ['-', '/', '.']):
                parts = value.replace('.', '-').replace('/', '-').split('-')
                if len(parts) == 3:
                    try:
                        int(parts[0])
                        int(parts[1])
                        int(parts[2])
                        return True
                    except ValueError:
                        return False
            return False
        
        else:  # text
            return True
    
    def _calculate_overall_score(self):
        """计算总体分数"""
        if not self.results:
            self.overall_score = 0.0
            return
        
        # 加权平均
        weights = {
            VerificationStep.STRUCTURE: 0.25,
            VerificationStep.DATA_TYPE: 0.20,
            VerificationStep.CONSISTENCY: 0.25,
            VerificationStep.LOGIC: 0.20,
            VerificationStep.COMPLETENESS: 0.10
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for result in self.results:
            weight = weights.get(result.step, 0.2)
            weighted_sum += result.score * weight
            total_weight += weight
        
        self.overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_summary(self) -> str:
        """生成验证摘要"""
        if not self.results:
            return "未执行验证"
        
        passed_count = sum(1 for result in self.results if result.passed)
        total_count = len(self.results)
        
        if self.overall_score >= 0.9:
            quality = "优秀"
        elif self.overall_score >= 0.8:
            quality = "良好"
        elif self.overall_score >= 0.7:
            quality = "一般"
        else:
            quality = "需要改进"
        
        summary = f"表格质量评估: {quality} (得分: {self.overall_score:.2f})\n"
        summary += f"验证步骤: {passed_count}/{total_count} 通过\n"
        
        if self.issues:
            summary += f"发现 {len(self.issues)} 个问题\n"
        
        if self.suggestions:
            summary += f"提供 {len(self.suggestions)} 条改进建议"
        
        return summary


# 示例用法
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 示例表格数据
    sample_table = {
        'headers': ['姓名', '年龄', '性别', '血压(mmHg)', '血糖(mmol/L)'],
        'rows': [
            ['张三', '25', '男', '120/80', '5.6'],
            ['李四', '30', '女', '115/75', '4.8'],
            ['王五', '28', '男', '130/85', '6.2'],
            ['赵六', '35', '女', '125/80', '5.1'],
        ]
    }
    
    verifier = TableChainVerifier(sample_table)
    results = verifier.verify()
    
    logger.info("验证结果:")
    logger.info("%s %s %s", json.dumps(results, ensure_ascii=False, indent=2))