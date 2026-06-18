"""
表格理解模块

提供先进的表格理解方法，包括：
- Chain-of-Table：逐步构建和验证表格
- Tree-of-Table：将大表格层次化分解为树状结构
- TableMaster：提取和语义化表格内容

这些方法基于最新的学术研究，旨在提升医学统计研究中表格的理解和核查能力。

参考文献：
[1] Wang et al. "Chain-of-Table: Evolving Tables in the Reasoning Chain for Table Understanding"
[2] Ji et al. "Tree-of-Table: Unleashing the Power of LLMs for Enhanced Table Reasoning"
[3] Cao and Liu "TableMaster: A Recipe for LLM Mastery of Table Understanding"
"""

from .table_chain_verifier import TableChainVerifier
from .table_tree_analyzer import TableTreeAnalyzer
from .table_master_extractor import TableMasterExtractor

__version__ = "1.0.0"
__author__ = "MSRA Team"

__all__ = [
    'TableChainVerifier',
    'TableTreeAnalyzer', 
    'TableMasterExtractor'
]

# 模块信息
MODULE_INFO = {
    'name': 'table-understanding',
    'description': '表格理解模块，提供Chain-of-Table、Tree-of-Table、TableMaster等先进方法',
    'version': __version__,
    'methods': {
        'chain_of_table': {
            'description': '逐步构建和验证表格，提升复杂表格的理解能力',
            'reference': 'Wang et al. (2024)',
            'use_cases': ['表格核查', '数据一致性验证', '逻辑关系检查']
        },
        'tree_of_table': {
            'description': '将大表格层次化分解为树状结构，便于LLM推理',
            'reference': 'Ji et al. (2024)',
            'use_cases': ['复杂表格分析', '层次化理解', '多层级表格处理']
        },
        'table_master': {
            'description': '提取和语义化表格内容，在文本和符号推理间自适应切换',
            'reference': 'Cao and Liu (2024)',
            'use_cases': ['表格语义提取', '内容理解', '推理优化']
        }
    }
}