"""
Tree-of-Table 分析器

基于 Tree-of-Table 方法将大表格层次化分解为树状结构，便于LLM推理。

参考文献：
Ji et al. "Tree-of-Table: Unleashing the Power of LLMs for Enhanced Table Reasoning"

主要功能：
1. 构建表格的树状结构
2. 分析表格层次关系
3. 支持复杂表格的层次化理解
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """节点类型枚举"""
    ROOT = "root"              # 根节点
    HEADER = "header"          # 表头节点
    CATEGORY = "category"      # 分类节点
    DATA = "data"              # 数据节点
    AGGREGATE = "aggregate"    # 聚合节点


@dataclass
class TreeNode:
    """树节点数据类"""
    id: str
    name: str
    node_type: NodeType
    level: int
    parent_id: Optional[str]
    children: List[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class TableTreeAnalyzer:
    """
    Tree-of-Table 分析器
    
    将表格分解为树状结构，支持层次化理解和分析。
    
    使用方法：
    ```python
    analyzer = TableTreeAnalyzer(table_data)
    tree = analyzer.build_tree()
    analysis = analyzer.analyze()
    ```
    """
    
    def __init__(self, table_data: Dict[str, Any]):
        """
        初始化分析器
        
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
        
        # 树结构
        self.nodes: Dict[str, TreeNode] = {}
        self.root_id: Optional[str] = None
        
        # 分析结果
        self.analysis_results: Dict[str, Any] = {}
    
    def build_tree(self) -> Dict[str, Any]:
        """
        构建表格的树状结构
        
        Returns
        -------
        Dict
            树结构，包含节点和层次关系
        """
        # 重置树结构
        self.nodes = {}
        self.root_id = None
        
        # 创建根节点
        self._create_root_node()
        
        # 创建表头节点
        self._create_header_nodes()
        
        # 创建数据节点
        self._create_data_nodes()
        
        # 创建聚合节点
        self._create_aggregate_nodes()
        
        # 构建层次关系
        self._build_hierarchy()
        
        return {
            'root_id': self.root_id,
            'nodes': {
                node_id: {
                    'id': node.id,
                    'name': node.name,
                    'type': node.node_type.value,
                    'level': node.level,
                    'parent_id': node.parent_id,
                    'children': node.children,
                    'data': node.data,
                    'metadata': node.metadata
                }
                for node_id, node in self.nodes.items()
            },
            'statistics': self._get_tree_statistics()
        }
    
    def analyze(self) -> Dict[str, Any]:
        """
        分析表格的层次结构
        
        Returns
        -------
        Dict
            分析结果，包含层次结构、数据分布、模式识别等
        """
        # 如果还没有构建树，先构建
        if not self.nodes:
            self.build_tree()
        
        # 执行分析
        self.analysis_results = {
            'hierarchy_analysis': self._analyze_hierarchy(),
            'data_distribution': self._analyze_data_distribution(),
            'pattern_recognition': self._analyze_patterns(),
            'complexity_metrics': self._calculate_complexity_metrics(),
            'recommendations': self._generate_recommendations()
        }
        
        # 计算总体分数
        self.analysis_results['score'] = self._calculate_overall_score()
        
        return self.analysis_results
    
    def _create_root_node(self):
        """创建根节点"""
        root_id = "root"
        self.root_id = root_id
        
        # 计算表格基本信息
        row_count = len(self.rows)
        col_count = len(self.headers)
        
        self.nodes[root_id] = TreeNode(
            id=root_id,
            name="表格根节点",
            node_type=NodeType.ROOT,
            level=0,
            parent_id=None,
            children=[],
            data={
                'row_count': row_count,
                'col_count': col_count,
                'total_cells': row_count * col_count
            },
            metadata=self.metadata
        )
    
    def _create_header_nodes(self):
        """创建表头节点"""
        for col_idx, header in enumerate(self.headers):
            header_id = f"header_{col_idx}"
            
            # 分析列数据类型
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            column_type = self._detect_column_type(column_values)
            
            # 计算列统计信息
            stats = self._calculate_column_stats(column_values, column_type)
            
            self.nodes[header_id] = TreeNode(
                id=header_id,
                name=header,
                node_type=NodeType.HEADER,
                level=1,
                parent_id=self.root_id,
                children=[],
                data={
                    'column_index': col_idx,
                    'column_type': column_type,
                    'statistics': stats
                },
                metadata={
                    'header_name': header
                }
            )
            
            # 添加到根节点的子节点
            self.nodes[self.root_id].children.append(header_id)
    
    def _create_data_nodes(self):
        """创建数据节点"""
        for row_idx, row in enumerate(self.rows):
            for col_idx, cell_value in enumerate(row):
                if col_idx < len(self.headers):
                    data_id = f"data_{row_idx}_{col_idx}"
                    header_id = f"header_{col_idx}"
                    
                    self.nodes[data_id] = TreeNode(
                        id=data_id,
                        name=f"R{row_idx}C{col_idx}",
                        node_type=NodeType.DATA,
                        level=2,
                        parent_id=header_id,
                        children=[],
                        data={
                            'row_index': row_idx,
                            'column_index': col_idx,
                            'value': cell_value,
                            'is_empty': cell_value.strip() == ''
                        },
                        metadata={}
                    )
                    
                    # 添加到表头节点的子节点
                    if header_id in self.nodes:
                        self.nodes[header_id].children.append(data_id)
    
    def _create_aggregate_nodes(self):
        """创建聚合节点（用于数值列）"""
        for col_idx, header in enumerate(self.headers):
            header_id = f"header_{col_idx}"
            
            if header_id not in self.nodes:
                continue
            
            header_node = self.nodes[header_id]
            
            # 只对数值列创建聚合节点
            if header_node.data.get('column_type') == 'numeric':
                # 获取列数据
                column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
                numeric_values = []
                
                for value in column_values:
                    try:
                        if value.strip():
                            numeric_values.append(float(value.replace(',', '')))
                    except ValueError:
                        continue
                
                if numeric_values:
                    # 创建聚合节点
                    aggregate_id = f"aggregate_{col_idx}"
                    
                    self.nodes[aggregate_id] = TreeNode(
                        id=aggregate_id,
                        name=f"{header}统计",
                        node_type=NodeType.AGGREGATE,
                        level=2,
                        parent_id=header_id,
                        children=[],
                        data={
                            'min': min(numeric_values),
                            'max': max(numeric_values),
                            'mean': sum(numeric_values) / len(numeric_values),
                            'count': len(numeric_values),
                            'sum': sum(numeric_values)
                        },
                        metadata={
                            'aggregation_type': 'numeric_stats'
                        }
                    )
                    
                    # 添加到表头节点的子节点
                    self.nodes[header_id].children.append(aggregate_id)
    
    def _build_hierarchy(self):
        """构建层次关系"""
        # 这里可以添加更复杂的层次关系构建逻辑
        # 目前已经通过parent_id和children建立了基本层次关系
        pass
    
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
    
    def _calculate_column_stats(self, values: List[str], column_type: str) -> Dict[str, Any]:
        """计算列统计信息"""
        stats = {
            'total_count': len(values),
            'empty_count': 0,
            'unique_count': 0
        }
        
        # 统计空值
        empty_count = sum(1 for v in values if not v.strip())
        stats['empty_count'] = empty_count
        stats['missing_rate'] = empty_count / len(values) if values else 0
        
        # 统计唯一值
        unique_values = list(set(v.strip() for v in values if v.strip()))
        stats['unique_count'] = len(unique_values)
        
        # 根据类型计算特定统计信息
        if column_type == 'numeric':
            numeric_values = []
            for value in values:
                try:
                    if value.strip():
                        numeric_values.append(float(value.replace(',', '')))
                except ValueError:
                    continue
            
            if numeric_values:
                stats['min'] = min(numeric_values)
                stats['max'] = max(numeric_values)
                stats['mean'] = sum(numeric_values) / len(numeric_values)
                stats['median'] = sorted(numeric_values)[len(numeric_values) // 2]
        
        elif column_type == 'text':
            # 文本长度统计
            text_lengths = [len(v) for v in values if v.strip()]
            if text_lengths:
                stats['avg_length'] = sum(text_lengths) / len(text_lengths)
                stats['max_length'] = max(text_lengths)
                stats['min_length'] = min(text_lengths)
        
        return stats
    
    def _get_tree_statistics(self) -> Dict[str, Any]:
        """获取树统计信息"""
        if not self.nodes:
            return {}
        
        # 统计各类型节点数量
        type_counts = {}
        for node in self.nodes.values():
            node_type = node.node_type.value
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        # 计算树深度
        max_level = max(node.level for node in self.nodes.values())
        
        # 计算叶子节点数量
        leaf_count = sum(1 for node in self.nodes.values() if not node.children)
        
        return {
            'total_nodes': len(self.nodes),
            'node_types': type_counts,
            'max_depth': max_level,
            'leaf_count': leaf_count,
            'branching_factor': len(self.nodes[self.root_id].children) if self.root_id else 0
        }
    
    def _analyze_hierarchy(self) -> Dict[str, Any]:
        """分析层次结构"""
        if not self.nodes:
            return {}
        
        # 分析层次分布
        level_distribution = {}
        for node in self.nodes.values():
            level = node.level
            level_distribution[level] = level_distribution.get(level, 0) + 1
        
        # 分析分支模式
        branch_patterns = {}
        for node in self.nodes.values():
            child_count = len(node.children)
            branch_patterns[child_count] = branch_patterns.get(child_count, 0) + 1
        
        # 识别关键路径
        key_paths = self._identify_key_paths()
        
        return {
            'level_distribution': level_distribution,
            'branch_patterns': branch_patterns,
            'key_paths': key_paths,
            'hierarchy_balance': self._calculate_hierarchy_balance()
        }
    
    def _analyze_data_distribution(self) -> Dict[str, Any]:
        """分析数据分布"""
        if not self.nodes:
            return {}
        
        # 分析各列的数据分布
        column_distributions = {}
        
        for col_idx, header in enumerate(self.headers):
            header_id = f"header_{col_idx}"
            if header_id not in self.nodes:
                continue
            
            header_node = self.nodes[header_id]
            column_type = header_node.data.get('column_type', 'text')
            
            # 获取列数据
            column_values = [row[col_idx] for row in self.rows if col_idx < len(row)]
            
            if column_type == 'numeric':
                # 数值分布
                numeric_values = []
                for value in column_values:
                    try:
                        if value.strip():
                            numeric_values.append(float(value.replace(',', '')))
                    except ValueError:
                        continue
                
                if numeric_values:
                    # 计算分位数
                    sorted_values = sorted(numeric_values)
                    n = len(sorted_values)
                    
                    column_distributions[header] = {
                        'type': 'numeric',
                        'count': n,
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'mean': sum(numeric_values) / n,
                        'q25': sorted_values[n // 4],
                        'median': sorted_values[n // 2],
                        'q75': sorted_values[3 * n // 4],
                        'std': (sum((x - sum(numeric_values) / n) ** 2 for x in numeric_values) / n) ** 0.5
                    }
            
            elif column_type == 'text':
                # 文本分布
                value_counts = {}
                for value in column_values:
                    if value.strip():
                        value_counts[value.strip()] = value_counts.get(value.strip(), 0) + 1
                
                # 排序取前10个
                sorted_counts = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                column_distributions[header] = {
                    'type': 'text',
                    'unique_count': len(value_counts),
                    'top_values': sorted_counts,
                    'distribution': 'categorical' if len(value_counts) < 10 else 'high_cardinality'
                }
        
        return {
            'column_distributions': column_distributions,
            'data_quality': self._assess_data_quality()
        }
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """分析数据模式"""
        patterns = {
            'correlations': [],
            'trends': [],
            'outliers': [],
            'missing_patterns': []
        }
        
        # 分析数值列之间的相关性
        numeric_columns = []
        for col_idx, header in enumerate(self.headers):
            header_id = f"header_{col_idx}"
            if header_id in self.nodes:
                if self.nodes[header_id].data.get('column_type') == 'numeric':
                    numeric_columns.append((col_idx, header))
        
        # 计算相关性（简化版本）
        if len(numeric_columns) >= 2:
            for i in range(len(numeric_columns)):
                for j in range(i + 1, len(numeric_columns)):
                    col1_idx, col1_name = numeric_columns[i]
                    col2_idx, col2_name = numeric_columns[j]
                    
                    # 获取数值
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
                        # 计算相关系数（简化版本）
                        mean1 = sum(values1) / len(values1)
                        mean2 = sum(values2) / len(values2)
                        
                        numerator = sum((v1 - mean1) * (v2 - mean2) for v1, v2 in zip(values1, values2))
                        denominator1 = sum((v1 - mean1) ** 2 for v1 in values1) ** 0.5
                        denominator2 = sum((v2 - mean2) ** 2 for v2 in values2) ** 0.5
                        
                        if denominator1 > 0 and denominator2 > 0:
                            correlation = numerator / (denominator1 * denominator2)
                            
                            if abs(correlation) > 0.7:
                                patterns['correlations'].append({
                                    'column1': col1_name,
                                    'column2': col2_name,
                                    'correlation': correlation,
                                    'strength': 'strong' if abs(correlation) > 0.8 else 'moderate'
                                })
        
        # 分析缺失模式
        missing_patterns = self._analyze_missing_patterns()
        patterns['missing_patterns'] = missing_patterns
        
        return patterns
    
    def _calculate_complexity_metrics(self) -> Dict[str, Any]:
        """计算复杂度指标"""
        if not self.nodes:
            return {}
        
        # 计算树复杂度
        total_nodes = len(self.nodes)
        max_depth = max(node.level for node in self.nodes.values())
        leaf_count = sum(1 for node in self.nodes.values() if not node.children)
        
        # 计算分支因子
        branch_factors = []
        for node in self.nodes.values():
            if node.children:
                branch_factors.append(len(node.children))
        
        avg_branch_factor = sum(branch_factors) / len(branch_factors) if branch_factors else 0
        
        # 计算数据密度
        total_cells = len(self.headers) * len(self.rows)
        non_empty_cells = sum(
            1 for row in self.rows
            for cell in row
            if cell.strip()
        )
        data_density = non_empty_cells / total_cells if total_cells > 0 else 0
        
        return {
            'total_nodes': total_nodes,
            'max_depth': max_depth,
            'leaf_count': leaf_count,
            'avg_branch_factor': avg_branch_factor,
            'data_density': data_density,
            'complexity_score': self._calculate_complexity_score(total_nodes, max_depth, leaf_count)
        }
    
    def _calculate_complexity_score(self, total_nodes: int, max_depth: int, leaf_count: int) -> float:
        """计算复杂度分数"""
        # 归一化各项指标
        nodes_score = min(total_nodes / 100, 1.0)  # 假设100个节点为满分
        depth_score = min(max_depth / 5, 1.0)  # 假设5层深度为满分
        leaf_score = min(leaf_count / 50, 1.0)  # 假设50个叶子节点为满分
        
        # 加权平均
        return (nodes_score * 0.4 + depth_score * 0.3 + leaf_score * 0.3)
    
    def _calculate_hierarchy_balance(self) -> Dict[str, Any]:
        """计算层次平衡性"""
        if not self.nodes:
            return {}
        
        # 计算各层的节点数
        level_counts = {}
        for node in self.nodes.values():
            level = node.level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # 计算平衡性指标
        if len(level_counts) > 1:
            values = list(level_counts.values())
            mean_val = sum(values) / len(values)
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_val = variance ** 0.5
            
            # 变异系数
            cv = std_val / mean_val if mean_val > 0 else 0
            
            balance_score = max(0, 1 - cv)  # 变异系数越小，平衡性越好
        else:
            balance_score = 1.0
        
        return {
            'level_counts': level_counts,
            'balance_score': balance_score,
            'is_balanced': balance_score > 0.7
        }
    
    def _identify_key_paths(self) -> List[List[str]]:
        """识别关键路径"""
        key_paths = []
        
        # 找到从根节点到叶子节点的路径
        if self.root_id and self.root_id in self.nodes:
            root_node = self.nodes[self.root_id]
            
            # 递归查找路径
            def find_paths(node_id: str, current_path: List[str]):
                node = self.nodes.get(node_id)
                if not node:
                    return
                
                current_path.append(node_id)
                
                if not node.children:
                    # 叶子节点，保存路径
                    key_paths.append(current_path.copy())
                else:
                    # 继续遍历子节点
                    for child_id in node.children:
                        find_paths(child_id, current_path)
                
                current_path.pop()
            
            find_paths(self.root_id, [])
        
        # 只返回前10条路径
        return key_paths[:10]
    
    def _analyze_missing_patterns(self) -> List[Dict[str, Any]]:
        """分析缺失模式"""
        patterns = []
        
        # 检查每列的缺失情况
        for col_idx, header in enumerate(self.headers):
            missing_rows = []
            
            for row_idx, row in enumerate(self.rows):
                if col_idx < len(row):
                    if not row[col_idx].strip():
                        missing_rows.append(row_idx)
            
            if missing_rows:
                patterns.append({
                    'column': header,
                    'missing_count': len(missing_rows),
                    'missing_rows': missing_rows[:10],  # 只显示前10个
                    'missing_rate': len(missing_rows) / len(self.rows) if self.rows else 0
                })
        
        return patterns
    
    def _assess_data_quality(self) -> Dict[str, Any]:
        """评估数据质量"""
        if not self.rows:
            return {}
        
        total_cells = len(self.headers) * len(self.rows)
        empty_cells = 0
        inconsistent_cells = 0
        
        for row in self.rows:
            for col_idx, cell in enumerate(row):
                if col_idx < len(self.headers):
                    if not cell.strip():
                        empty_cells += 1
                    
                    # 检查类型一致性
                    header_id = f"header_{col_idx}"
                    if header_id in self.nodes:
                        expected_type = self.nodes[header_id].data.get('column_type', 'text')
                        if expected_type == 'numeric':
                            try:
                                if cell.strip():
                                    float(cell.replace(',', ''))
                            except ValueError:
                                inconsistent_cells += 1
        
        return {
            'total_cells': total_cells,
            'empty_cells': empty_cells,
            'inconsistent_cells': inconsistent_cells,
            'completeness': 1 - (empty_cells / total_cells) if total_cells > 0 else 0,
            'consistency': 1 - (inconsistent_cells / total_cells) if total_cells > 0 else 0,
            'overall_quality': 1 - ((empty_cells + inconsistent_cells) / total_cells) if total_cells > 0 else 0
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于分析结果生成建议
        if self.analysis_results:
            hierarchy = self.analysis_results.get('hierarchy_analysis', {})
            data_dist = self.analysis_results.get('data_distribution', {})
            patterns = self.analysis_results.get('pattern_recognition', {})
            
            # 基于层次结构的建议
            balance = hierarchy.get('hierarchy_balance', {})
            if not balance.get('is_balanced', True):
                recommendations.append("表格层次结构不平衡，建议重新组织数据结构")
            
            # 基于数据质量的建议
            quality = data_dist.get('data_quality', {})
            completeness = quality.get('completeness', 1.0)
            if completeness < 0.9:
                recommendations.append(f"数据完整性为{completeness:.1%}，建议处理缺失值")
            
            consistency = quality.get('consistency', 1.0)
            if consistency < 0.95:
                recommendations.append(f"数据一致性为{consistency:.1%}，建议检查数据类型")
            
            # 基于模式识别的建议
            correlations = patterns.get('correlations', [])
            if correlations:
                recommendations.append(f"发现{len(correlations)}个强相关性，建议进一步分析")
            
            missing_patterns = patterns.get('missing_patterns', [])
            if missing_patterns:
                recommendations.append(f"发现{len(missing_patterns)}列有缺失模式，建议检查数据收集过程")
        
        return recommendations
    
    def _calculate_overall_score(self) -> float:
        """计算总体分数"""
        if not self.analysis_results:
            return 0.0
        
        scores = []
        
        # 层次结构分数
        hierarchy = self.analysis_results.get('hierarchy_analysis', {})
        balance = hierarchy.get('hierarchy_balance', {})
        if 'balance_score' in balance:
            scores.append(balance['balance_score'])
        
        # 数据质量分数
        data_dist = self.analysis_results.get('data_distribution', {})
        quality = data_dist.get('data_quality', {})
        if 'overall_quality' in quality:
            scores.append(quality['overall_quality'])
        
        # 复杂度分数
        complexity = self.analysis_results.get('complexity_metrics', {})
        if 'complexity_score' in complexity:
            scores.append(complexity['complexity_score'])
        
        return sum(scores) / len(scores) if scores else 0.0


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
    
    analyzer = TableTreeAnalyzer(sample_table)
    tree = analyzer.build_tree()
    analysis = analyzer.analyze()
    
    logger.info("树结构:")
    logger.info("%s %s %s", json.dumps(tree, ensure_ascii=False, indent=2))
    
    logger.info("\n分析结果:")
    logger.info("%s %s %s", json.dumps(analysis, ensure_ascii=False, indent=2))