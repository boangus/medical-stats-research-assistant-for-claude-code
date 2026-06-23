"""
TableMaster 提取器

基于 TableMaster 框架提取和语义化表格内容，在文本和符号推理间自适应切换。

参考文献：
Cao and Liu "TableMaster: A Recipe for LLM Mastery of Table Understanding"

主要功能：
1. 提取表格关键信息
2. 语义化表格内容
3. 在文本和符号推理间自适应切换
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReasoningMode(Enum):
    """推理模式枚举"""
    TEXTUAL = "textual"      # 文本推理模式
    SYMBOLIC = "symbolic"    # 符号推理模式
    HYBRID = "hybrid"        # 混合推理模式


@dataclass
class ExtractedInfo:
    """提取信息数据类"""
    key_entities: List[str]
    relationships: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    patterns: List[str]
    summary: str


class TableMasterExtractor:
    """
    TableMaster 提取器
    
    提取表格关键信息并语义化，支持文本和符号推理的自适应切换。
    
    使用方法：
    ```python
    extractor = TableMasterExtractor(table_data)
    semantic_info = extractor.extract()
    reasoning_result = extractor.reason("What is the average age?")
    ```
    """
    
    def __init__(self, table_data: Dict[str, Any]):
        """
        初始化提取器
        
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
        
        # 分析结果缓存
        self._column_analysis: Dict[str, Any] = {}
        self._extracted_info: Optional[ExtractedInfo] = None
        self._reasoning_mode: ReasoningMode = ReasoningMode.HYBRID
        
        # 初始化分析
        self._analyze_columns()
    
    def extract(self) -> Dict[str, Any]:
        """
        提取表格关键信息
        
        Returns
        -------
        Dict
            提取的信息，包含实体、关系、统计、模式等
        """
        if self._extracted_info is None:
            self._extracted_info = self._perform_extraction()
        
        return {
            'key_entities': self._extracted_info.key_entities,
            'relationships': self._extracted_info.relationships,
            'statistics': self._extracted_info.statistics,
            'patterns': self._extracted_info.patterns,
            'summary': self._extracted_info.summary,
            'reasoning_mode': self._reasoning_mode.value,
            'column_analysis': self._column_analysis
        }
    
    def reason(self, query: str) -> Dict[str, Any]:
        """
        基于查询进行推理
        
        Parameters
        ----------
        query : str
            查询问题
            
        Returns
        -------
        Dict
            推理结果，包含答案、推理过程、置信度等
        """
        # 选择推理模式
        reasoning_mode = self._select_reasoning_mode(query)
        
        # 执行推理
        if reasoning_mode == ReasoningMode.TEXTUAL:
            result = self._textual_reasoning(query)
        elif reasoning_mode == ReasoningMode.SYMBOLIC:
            result = self._symbolic_reasoning(query)
        else:
            result = self._hybrid_reasoning(query)
        
        return {
            'query': query,
            'reasoning_mode': reasoning_mode.value,
            'result': result,
            'confidence': result.get('confidence', 0.0),
            'explanation': result.get('explanation', '')
        }
    
    def get_semantic_description(self) -> str:
        """
        获取表格的语义描述
        
        Returns
        -------
        str
            表格的自然语言描述
        """
        if self._extracted_info is None:
            self._extracted_info = self._perform_extraction()
        
        # 构建语义描述
        description_parts = []
        
        # 表格概述
        description_parts.append(f"该表格包含{len(self.headers)}列{len(self.rows)}行数据。")
        
        # 列描述
        column_descriptions = []
        for header in self.headers:
            analysis = self._column_analysis.get(header, {})
            col_type = analysis.get('type', 'text')
            
            if col_type == 'numeric':
                stats = analysis.get('statistics', {})
                if 'mean' in stats:
                    column_descriptions.append(
                        f"{header}为数值型，平均值为{stats['mean']:.2f}，"
                        f"范围从{stats.get('min', 'N/A')}到{stats.get('max', 'N/A')}"
                    )
                else:
                    column_descriptions.append(f"{header}为数值型")
            elif col_type == 'categorical':
                unique_count = analysis.get('unique_count', 0)
                column_descriptions.append(f"{header}为分类型，有{unique_count}个不同值")
            else:
                column_descriptions.append(f"{header}为文本型")
        
        if column_descriptions:
            description_parts.append("各列特征：" + "；".join(column_descriptions) + "。")
        
        # 关键发现
        if self._extracted_info.patterns:
            description_parts.append("关键发现：" + "；".join(self._extracted_info.patterns[:3]) + "。")
        
        return "".join(description_parts)
    
    def _analyze_columns(self):
        """分析各列特征"""
        for col_idx, header in enumerate(self.headers):
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            
            # 检测列类型
            col_type = self._detect_column_type(column_values)
            
            # 计算统计信息
            stats = self._calculate_column_statistics(column_values, col_type)
            
            # 分析唯一值
            unique_values = list(set(v.strip() for v in column_values if v.strip()))
            
            self._column_analysis[header] = {
                'index': col_idx,
                'type': col_type,
                'statistics': stats,
                'unique_count': len(unique_values),
                'unique_values': unique_values[:10],  # 只保留前10个
                'missing_count': sum(1 for v in column_values if not v.strip()),
                'missing_rate': sum(1 for v in column_values if not v.strip()) / len(column_values) if column_values else 0
            }
    
    def _perform_extraction(self) -> ExtractedInfo:
        """执行信息提取"""
        # 提取关键实体
        key_entities = self._extract_key_entities()
        
        # 提取关系
        relationships = self._extract_relationships()
        
        # 计算统计信息
        statistics = self._calculate_overall_statistics()
        
        # 识别模式
        patterns = self._identify_patterns()
        
        # 生成摘要
        summary = self._generate_summary()
        
        return ExtractedInfo(
            key_entities=key_entities,
            relationships=relationships,
            statistics=statistics,
            patterns=patterns,
            summary=summary
        )
    
    def _extract_key_entities(self) -> List[str]:
        """提取关键实体"""
        entities = []
        
        # 从表头提取实体
        entities.extend(self.headers)
        
        # 从分类列提取高频值
        for header, analysis in self._column_analysis.items():
            if analysis['type'] == 'categorical':
                unique_values = analysis.get('unique_values', [])
                entities.extend(unique_values[:5])  # 每列最多5个
        
        # 从数值列提取统计量
        for header, analysis in self._column_analysis.items():
            if analysis['type'] == 'numeric':
                stats = analysis.get('statistics', {})
                if 'mean' in stats:
                    entities.append(f"{header}_mean_{stats['mean']:.2f}")
                if 'max' in stats:
                    entities.append(f"{header}_max_{stats['max']}")
        
        return list(set(entities))  # 去重
    
    def _extract_relationships(self) -> List[Dict[str, Any]]:
        """提取关系"""
        relationships = []
        
        # 分析数值列之间的相关性
        numeric_columns = [
            header for header, analysis in self._column_analysis.items()
            if analysis['type'] == 'numeric'
        ]
        
        if len(numeric_columns) >= 2:
            for i in range(len(numeric_columns)):
                for j in range(i + 1, len(numeric_columns)):
                    col1 = numeric_columns[i]
                    col2 = numeric_columns[j]
                    
                    # 获取数值
                    col1_idx = self._column_analysis[col1]['index']
                    col2_idx = self._column_analysis[col2]['index']
                    
                    values1 = []
                    values2 = []
                    
                    for row in self.rows:
                        if col1_idx < len(row) and col2_idx < len(row):
                            try:
                                v1 = float(row[col1_idx].replace(',', ''))
                                v2 = float(row[col2_idx].replace(',', ''))
                                values1.append(v1)
                                values2.append(v2)
                            except ValueError:
                                continue
                    
                    if len(values1) > 2:
                        # 计算相关系数
                        correlation = self._calculate_correlation(values1, values2)
                        
                        if abs(correlation) > 0.5:
                            relationships.append({
                                'type': 'correlation',
                                'entity1': col1,
                                'entity2': col2,
                                'strength': abs(correlation),
                                'direction': 'positive' if correlation > 0 else 'negative',
                                'description': f"{col1}与{col2}呈{'正' if correlation > 0 else '负'}相关"
                            })
        
        # 分析分类列与数值列的关系
        categorical_columns = [
            header for header, analysis in self._column_analysis.items()
            if analysis['type'] == 'categorical'
        ]
        
        for cat_col in categorical_columns:
            cat_idx = self._column_analysis[cat_col]['index']
            unique_values = self._column_analysis[cat_col].get('unique_values', [])
            
            for num_col in numeric_columns:
                num_idx = self._column_analysis[num_col]['index']
                
                # 按分类分组计算均值
                group_means = {}
                for value in unique_values:
                    group_values = []
                    for row in self.rows:
                        if cat_idx < len(row) and num_idx < len(row):
                            if row[cat_idx].strip() == value:
                                try:
                                    group_values.append(float(row[num_idx].replace(',', '')))
                                except ValueError:
                                    continue
                    
                    if group_values:
                        group_means[value] = sum(group_values) / len(group_values)
                
                if len(group_means) >= 2:
                    # 检查组间差异
                    values = list(group_means.values())
                    max_diff = max(values) - min(values)
                    mean_val = sum(values) / len(values)
                    
                    if mean_val > 0 and max_diff / mean_val > 0.2:  # 差异超过20%
                        relationships.append({
                            'type': 'group_difference',
                            'categorical_column': cat_col,
                            'numeric_column': num_col,
                            'group_means': group_means,
                            'max_difference': max_diff,
                            'description': f"不同{cat_col}的{num_col}存在显著差异"
                        })
        
        return relationships
    
    def _calculate_overall_statistics(self) -> Dict[str, Any]:
        """计算总体统计信息"""
        stats = {
            'total_rows': len(self.rows),
            'total_columns': len(self.headers),
            'total_cells': len(self.headers) * len(self.rows),
            'column_types': {},
            'missing_summary': {}
        }
        
        # 统计列类型
        for header, analysis in self._column_analysis.items():
            col_type = analysis['type']
            stats['column_types'][col_type] = stats['column_types'].get(col_type, 0) + 1
        
        # 统计缺失情况
        total_missing = 0
        for header, analysis in self._column_analysis.items():
            missing = analysis.get('missing_count', 0)
            total_missing += missing
            if missing > 0:
                stats['missing_summary'][header] = {
                    'count': missing,
                    'rate': analysis.get('missing_rate', 0)
                }
        
        stats['total_missing'] = total_missing
        stats['missing_rate'] = total_missing / stats['total_cells'] if stats['total_cells'] > 0 else 0
        
        return stats
    
    def _identify_patterns(self) -> List[str]:
        """识别数据模式"""
        patterns = []
        
        # 识别数值列的分布模式
        for header, analysis in self._column_analysis.items():
            if analysis['type'] == 'numeric':
                stats = analysis.get('statistics', {})
                if 'mean' in stats and 'std' in stats:
                    cv = stats['std'] / stats['mean'] if stats['mean'] != 0 else 0
                    if cv < 0.1:
                        patterns.append(f"{header}分布较为集中（变异系数{cv:.2f}）")
                    elif cv > 0.5:
                        patterns.append(f"{header}分布较为分散（变异系数{cv:.2f}）")
        
        # 识别分类列的分布模式
        for header, analysis in self._column_analysis.items():
            if analysis['type'] == 'categorical':
                unique_count = analysis.get('unique_count', 0)
                total_count = len(self.rows)
                
                if unique_count == total_count:
                    patterns.append(f"{header}为唯一标识符")
                elif unique_count / total_count < 0.1:
                    patterns.append(f"{header}为低基数分类变量")
        
        # 识别缺失模式
        missing_columns = [
            header for header, analysis in self._column_analysis.items()
            if analysis.get('missing_rate', 0) > 0.1
        ]
        
        if missing_columns:
            patterns.append(f"以下列缺失率较高：{', '.join(missing_columns)}")
        
        return patterns
    
    def _generate_summary(self) -> str:
        """生成摘要"""
        if not self._extracted_info:
            return ""
        
        summary_parts = []
        
        # 基本信息
        stats = self._extracted_info.statistics
        summary_parts.append(
            f"该表格包含{stats['total_rows']}行{stats['total_columns']}列数据，"
            f"共{stats['total_cells']}个单元格。"
        )
        
        # 列类型分布
        col_types = stats.get('column_types', {})
        type_descriptions = []
        for col_type, count in col_types.items():
            if col_type == 'numeric':
                type_descriptions.append(f"{count}个数值列")
            elif col_type == 'categorical':
                type_descriptions.append(f"{count}个分类列")
            elif col_type == 'text':
                type_descriptions.append(f"{count}个文本列")
        
        if type_descriptions:
            summary_parts.append("列类型分布：" + "、".join(type_descriptions) + "。")
        
        # 缺失情况
        missing_rate = stats.get('missing_rate', 0)
        if missing_rate > 0:
            summary_parts.append(f"总体缺失率为{missing_rate:.1%}。")
        
        # 关键发现
        if self._extracted_info.patterns:
            summary_parts.append("关键发现：" + "；".join(self._extracted_info.patterns[:2]) + "。")
        
        return "".join(summary_parts)
    
    def _select_reasoning_mode(self, query: str) -> ReasoningMode:
        """选择推理模式"""
        query_lower = query.lower()
        
        # 符号推理关键词
        symbolic_keywords = ['计算', '平均', '总和', '最大', '最小', '百分比', '比例', 
                           'calculate', 'average', 'sum', 'max', 'min', 'percentage', 'ratio']
        
        # 文本推理关键词
        textual_keywords = ['描述', '解释', '说明', '总结', '概述', 
                          'describe', 'explain', 'summarize', 'overview']
        
        # 检查是否包含符号推理关键词
        if any(keyword in query_lower for keyword in symbolic_keywords):
            return ReasoningMode.SYMBOLIC
        
        # 检查是否包含文本推理关键词
        if any(keyword in query_lower for keyword in textual_keywords):
            return ReasoningMode.TEXTUAL
        
        # 默认使用混合模式
        return ReasoningMode.HYBRID
    
    def _textual_reasoning(self, query: str) -> Dict[str, Any]:
        """文本推理"""
        # 基于语义描述进行推理
        semantic_desc = self.get_semantic_description()
        
        # 简单的关键词匹配
        query_lower = query.lower()
        
        # 检查是否询问特定列
        for header in self.headers:
            if header.lower() in query_lower:
                analysis = self._column_analysis.get(header, {})
                col_type = analysis.get('type', 'text')
                
                if col_type == 'numeric':
                    stats = analysis.get('statistics', {})
                    if 'mean' in stats:
                        return {
                            'answer': f"{header}的平均值为{stats['mean']:.2f}",
                            'confidence': 0.9,
                            'explanation': f"基于{len(self.rows)}行数据计算得出"
                        }
                elif col_type == 'categorical':
                    unique_count = analysis.get('unique_count', 0)
                    return {
                        'answer': f"{header}有{unique_count}个不同的值",
                        'confidence': 0.9,
                        'explanation': f"基于{len(self.rows)}行数据统计得出"
                    }
        
        # 默认回答
        return {
            'answer': f"根据表格分析，{semantic_desc}",
            'confidence': 0.7,
            'explanation': "基于表格整体语义描述"
        }
    
    def _symbolic_reasoning(self, query: str) -> Dict[str, Any]:
        """符号推理"""
        query_lower = query.lower()
        
        # 检查是否询问计算
        if any(keyword in query_lower for keyword in ['计算', 'calculate']):
            # 尝试找到要计算的列
            for header in self.headers:
                if header.lower() in query_lower:
                    analysis = self._column_analysis.get(header, {})
                    if analysis.get('type') == 'numeric':
                        stats = analysis.get('statistics', {})
                        if 'sum' in stats:
                            return {
                                'answer': f"{header}的总和为{stats['sum']:.2f}",
                                'confidence': 0.95,
                                'explanation': f"基于{len(self.rows)}行数据直接计算"
                            }
        
        # 检查是否询问平均值
        if any(keyword in query_lower for keyword in ['平均', 'average', '均值']):
            for header in self.headers:
                if header.lower() in query_lower:
                    analysis = self._column_analysis.get(header, {})
                    if analysis.get('type') == 'numeric':
                        stats = analysis.get('statistics', {})
                        if 'mean' in stats:
                            return {
                                'answer': f"{header}的平均值为{stats['mean']:.2f}",
                                'confidence': 0.95,
                                'explanation': f"基于{len(self.rows)}行数据计算得出"
                            }
        
        # 检查是否询问最大/最小值
        if any(keyword in query_lower for keyword in ['最大', 'max', '最高']):
            for header in self.headers:
                if header.lower() in query_lower:
                    analysis = self._column_analysis.get(header, {})
                    if analysis.get('type') == 'numeric':
                        stats = analysis.get('statistics', {})
                        if 'max' in stats:
                            return {
                                'answer': f"{header}的最大值为{stats['max']}",
                                'confidence': 0.95,
                                'explanation': f"基于{len(self.rows)}行数据直接计算"
                            }
        
        if any(keyword in query_lower for keyword in ['最小', 'min', '最低']):
            for header in self.headers:
                if header.lower() in query_lower:
                    analysis = self._column_analysis.get(header, {})
                    if analysis.get('type') == 'numeric':
                        stats = analysis.get('statistics', {})
                        if 'min' in stats:
                            return {
                                'answer': f"{header}的最小值为{stats['min']}",
                                'confidence': 0.95,
                                'explanation': f"基于{len(self.rows)}行数据直接计算"
                            }
        
        # 默认使用文本推理
        return self._textual_reasoning(query)
    
    def _hybrid_reasoning(self, query: str) -> Dict[str, Any]:
        """混合推理"""
        # 先尝试符号推理
        symbolic_result = self._symbolic_reasoning(query)
        
        # 如果置信度高，直接返回
        if symbolic_result.get('confidence', 0) > 0.8:
            return symbolic_result
        
        # 否则结合文本推理
        textual_result = self._textual_reasoning(query)
        
        # 选择置信度更高的结果
        if symbolic_result.get('confidence', 0) >= textual_result.get('confidence', 0):
            return symbolic_result
        else:
            return textual_result
    
    def _detect_column_type(self, values: List[str]) -> str:
        """检测列的数据类型"""
        numeric_count = 0
        categorical_count = 0
        text_count = 0
        
        unique_values = set()
        
        for value in values:
            if not value.strip():
                continue
            
            unique_values.add(value.strip())
            
            # 尝试解析为数字
            try:
                float(value.replace(',', '').replace('%', ''))
                numeric_count += 1
                continue
            except ValueError:
                pass
            
            # 检查是否为分类变量（唯一值较少）
            if len(unique_values) <= 20:  # 假设20个唯一值以内为分类变量
                categorical_count += 1
            else:
                text_count += 1
        
        total = numeric_count + categorical_count + text_count
        if total == 0:
            return 'empty'
        
        # 判断类型
        if numeric_count / total > 0.7:
            return 'numeric'
        elif len(unique_values) <= 20 and categorical_count / total > 0.7:
            return 'categorical'
        else:
            return 'text'
    
    def _calculate_column_statistics(self, values: List[str], col_type: str) -> Dict[str, Any]:
        """计算列统计信息"""
        stats = {}
        
        if col_type == 'numeric':
            numeric_values = []
            for value in values:
                try:
                    if value.strip():
                        numeric_values.append(float(value.replace(',', '')))
                except ValueError:
                    continue
            
            if numeric_values:
                stats['count'] = len(numeric_values)
                stats['sum'] = sum(numeric_values)
                stats['mean'] = stats['sum'] / stats['count']
                stats['min'] = min(numeric_values)
                stats['max'] = max(numeric_values)
                
                # 计算标准差
                variance = sum((x - stats['mean']) ** 2 for x in numeric_values) / len(numeric_values)
                stats['std'] = variance ** 0.5
                
                # 计算中位数
                sorted_values = sorted(numeric_values)
                n = len(sorted_values)
                if n % 2 == 0:
                    stats['median'] = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
                else:
                    stats['median'] = sorted_values[n//2]
        
        elif col_type == 'categorical':
            # 统计各类别频次
            value_counts = {}
            for value in values:
                if value.strip():
                    value_counts[value.strip()] = value_counts.get(value.strip(), 0) + 1
            
            stats['value_counts'] = value_counts
            stats['most_common'] = max(value_counts.items(), key=lambda x: x[1])[0] if value_counts else None
            stats['least_common'] = min(value_counts.items(), key=lambda x: x[1])[0] if value_counts else None
        
        return stats
    
    def _calculate_correlation(self, values1: List[float], values2: List[float]) -> float:
        """计算相关系数"""
        if len(values1) != len(values2) or len(values1) < 2:
            return 0.0
        
        n = len(values1)
        mean1 = sum(values1) / n
        mean2 = sum(values2) / n
        
        numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
        denominator1 = sum((v1 - mean1) ** 2 for v1 in values1) ** 0.5
        denominator2 = sum((v2 - mean2) ** 2 for v2 in values2) ** 0.5
        
        if denominator1 == 0 or denominator2 == 0:
            return 0.0
        
        return numerator / (denominator1 * denominator2)


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
    
    extractor = TableMasterExtractor(sample_table)
    
    logger.info("提取结果:")
    logger.info("%s %s %s", json.dumps(extractor.extract(), ensure_ascii=False, indent=2))
    
    logger.info("\n语义描述:")
    logger.info("extractor.get_semantic_description()")
    
    logger.info("\n推理测试:")
    queries = [
        "年龄的平均值是多少？",
        "计算血压的总和",
        "描述一下这个表格",
        "性别有哪些不同的值？"
    ]
    
    for query in queries:
        result = extractor.reason(query)
        logger.info(f"\n问题: {query}")
        logger.info(f"答案: {result['result']['answer']}")
        logger.info(f"置信度: {result['confidence']}")
        logger.info(f"推理模式: {result['reasoning_mode']}")