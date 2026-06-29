"""
MSRA Quality Gates — 检查项定义

各门闸的检查项结构化定义，支持自动化验证和LLM引导。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CheckItem:
    """单个检查项定义"""
    item_number: int
    item_id: str
    name: str
    name_en: str
    description: str
    is_key: bool
    check_method: str  # 检查方法描述
    pass_criteria: str  # 通过标准
    evidence_type: str  # 证据类型：file / metric / log / manual


@dataclass
class CheckItemCollection:
    """检查项集合"""
    gate_name: str
    gate_stage: str
    items: List[CheckItem] = field(default_factory=list)

    def get_key_items(self) -> List[CheckItem]:
        """获取关键项"""
        return [item for item in self.items if item.is_key]

    def get_item_by_number(self, number: int) -> Optional[CheckItem]:
        """按编号获取检查项"""
        for item in self.items:
            if item.item_number == number:
                return item
        return None


# ============================================================
# Gate 1.5 — 数据质量门闸 (9项)
# ============================================================

DataQualityCheckItems = CheckItemCollection(
    gate_name="数据质量门闸 / Data Quality Gate",
    gate_stage="1.5",
    items=[
        CheckItem(
            item_number=1,
            item_id="DG-01",
            name="清洗日志完整性",
            name_en="Cleaning Log Completeness",
            description="所有数据变更是否记录在案？清洗日志是否包含变更原因、变更前后值、影响范围？",
            is_key=False,
            check_method="审查 cleaning_log 文件，验证每条变更记录包含：变量名、行号、原值、新值、变更原因",
            pass_criteria="所有变更均有记录，无遗漏",
            evidence_type="log",
        ),
        CheckItem(
            item_number=2,
            item_id="DG-02",
            name="变量定义明确性",
            name_en="Variable Definition Clarity",
            description="所有变量的定义、类型、取值范围、编码规则是否在数据字典中明确记录？",
            is_key=False,
            check_method="对比数据字典与实际数据集，验证变量名、类型、取值范围一致",
            pass_criteria="数据字典覆盖所有变量，类型和范围与实际数据一致",
            evidence_type="file",
        ),
        CheckItem(
            item_number=3,
            item_id="DG-03",
            name="缺失机制评估",
            name_en="Missing Mechanism Assessment",
            description="是否已评估主要变量的缺失机制（MCAR/MAR/MNAR）？缺失率是否在可接受范围内？",
            is_key=False,
            check_method="审查缺失数据分析报告，验证主要变量缺失率<20%，缺失机制已评估",
            pass_criteria="主要变量缺失率<20%，缺失机制有评估结论",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=4,
            item_id="DG-04",
            name="异常值处理记录",
            name_en="Outlier Handling Documentation",
            description="统计异常值和领域异常值是否已识别？处理策略是否记录？",
            is_key=False,
            check_method="审查异常值检测报告，验证处理策略（保留/修正/删除）有记录",
            pass_criteria="异常值已识别，处理策略有记录",
            evidence_type="log",
        ),
        CheckItem(
            item_number=5,
            item_id="DG-05",
            name="🔑 数据完整性",
            name_en="Data Completeness (KEY)",
            description="记录数是否与预期一致？是否有重复记录？唯一标识符是否有效？",
            is_key=True,
            check_method="验证：(1) 行数与预期一致 (2) 无完全重复行 (3) ID列无重复",
            pass_criteria="行数正确，无重复记录，ID唯一",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=6,
            item_id="DG-06",
            name="🔑 变量类型一致性",
            name_en="Variable Type Consistency (KEY)",
            description="变量实际类型是否与数据字典定义一致？是否有意外的类型转换？",
            is_key=True,
            check_method="对比数据字典定义与实际数据类型，验证数值/分类/日期类型一致",
            pass_criteria="所有变量类型与数据字典一致",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=7,
            item_id="DG-07",
            name="🔑 值范围合理性",
            name_en="Value Range Plausibility (KEY)",
            description="所有数值是否在合理范围内？是否有不可能的值（如负年龄、未来出生日期）？",
            is_key=True,
            check_method="按数据字典定义的范围检查所有变量，标记超范围值",
            pass_criteria="无超范围值，或超范围值已标记并处理",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=8,
            item_id="DG-08",
            name="盲态审核完成",
            name_en="Blinding Review Completion",
            description="数据清理后的盲态审核是否已完成？审核意见是否已处理？",
            is_key=False,
            check_method="审查盲态审核记录，验证审核人、审核时间、审核意见、处理结果",
            pass_criteria="盲态审核已完成并签字",
            evidence_type="log",
        ),
        CheckItem(
            item_number=9,
            item_id="DG-09",
            name="🔑 隐私合规",
            name_en="Privacy Compliance (KEY)",
            description="PHI字段是否已脱敏或标记？HIPAA Safe Harbor 18类标识符是否已处理？",
            is_key=True,
            check_method="运行PHI检测，验证18类标识符已处理：姓名、日期、电话、地址、邮箱、SSN、MRN等",
            pass_criteria="所有PHI字段已处理，无明文敏感信息",
            evidence_type="metric",
        ),
    ],
)


# ============================================================
# Gate 2.5 — SAP质量门闸 (8项)
# ============================================================

SapQualityCheckItems = CheckItemCollection(
    gate_name="SAP质量门闸 / SAP Quality Gate",
    gate_stage="2.5",
    items=[
        CheckItem(
            item_number=1,
            item_id="SQ-01",
            name="Estimands五要素完整性",
            name_en="Estimands 5-Element Completeness",
            description="ICH E9(R1) 五要素是否全部定义：人群、干预、终点、伴发事件、汇总统计量？",
            is_key=False,
            check_method="审查SAP中Estimands定义，验证5个要素均有明确描述",
            pass_criteria="5个要素全部定义，无遗漏",
            evidence_type="file",
        ),
        CheckItem(
            item_number=2,
            item_id="SQ-02",
            name="主要终点定义明确",
            name_en="Primary Endpoint Definition",
            description="主要终点是否有操作性定义、测量方法、评估时间窗口？",
            is_key=False,
            check_method="审查SAP终点定义，验证包含：定义、测量工具、时间窗口、缺失处理",
            pass_criteria="主要终点定义完整、可操作",
            evidence_type="file",
        ),
        CheckItem(
            item_number=3,
            item_id="SQ-03",
            name="分析方法适当性",
            name_en="Statistical Method Appropriateness",
            description="统计方法是否与数据类型、分布假设、研究设计匹配？",
            is_key=False,
            check_method="对照决策树验证方法选择：数据类型→分布→设计→方法",
            pass_criteria="方法选择有依据，与数据特征匹配",
            evidence_type="file",
        ),
        CheckItem(
            item_number=4,
            item_id="SQ-04",
            name="🔑 样本量论证充分性",
            name_en="Sample Size Justification (KEY)",
            description="样本量计算的假设是否合理？效应量是否有临床/文献依据？",
            is_key=True,
            check_method="审查样本量计算：效应量来源、检验效能、α水平、脱落率假设",
            pass_criteria="效应量有依据，效能≥80%，脱落率假设合理",
            evidence_type="file",
        ),
        CheckItem(
            item_number=5,
            item_id="SQ-05",
            name="多重比较策略",
            name_en="Multiplicity Control Strategy",
            description="次要终点的多重比较控制策略是否已指定？",
            is_key=False,
            check_method="审查SAP多重比较部分，验证策略类型和适用范围",
            pass_criteria="有明确的多重比较控制策略",
            evidence_type="file",
        ),
        CheckItem(
            item_number=6,
            item_id="SQ-06",
            name="🔑 敏感性分析完整性",
            name_en="Sensitivity Analysis Completeness (KEY)",
            description="预设的敏感性分析是否覆盖关键假设和潜在偏差？",
            is_key=True,
            check_method="审查敏感性分析列表，验证覆盖：缺失数据、偏离方案、亚组分析",
            pass_criteria="至少3项敏感性分析，覆盖关键假设",
            evidence_type="file",
        ),
        CheckItem(
            item_number=7,
            item_id="SQ-07",
            name="变量构造逻辑",
            name_en="Variable Construction Logic",
            description="所有分析变量的构造逻辑是否已定义（公式、条件、缺失处理）？",
            is_key=False,
            check_method="审查变量构造定义，验证每个派生变量有明确的构造规则",
            pass_criteria="所有派生变量有构造逻辑",
            evidence_type="file",
        ),
        CheckItem(
            item_number=8,
            item_id="SQ-08",
            name="🔑 用户确认SAP",
            name_en="User SAP Confirmation (KEY)",
            description="用户是否已审查并确认SAP？确认记录是否在Passport中？",
            is_key=True,
            check_method="验证Passport中sap_user_confirmed标记为true",
            pass_criteria="用户明确确认SAP",
            evidence_type="log",
        ),
    ],
)


# ============================================================
# Gate 3.5 — 结果质量门闸 (9项)
# ============================================================

ResultsQualityCheckItems = CheckItemCollection(
    gate_name="结果质量门闸 / Results Quality Gate",
    gate_stage="3.5",
    items=[
        CheckItem(
            item_number=1,
            item_id="RQ-01",
            name="🔑 SAP合规性",
            name_en="SAP Compliance (KEY)",
            description="SAP中指定的所有分析是否已执行？偏差是否已记录？",
            is_key=True,
            check_method="逐项对照SAP分析计划与实际执行记录",
            pass_criteria="所有SAP分析已执行，偏差有记录",
            evidence_type="file",
        ),
        CheckItem(
            item_number=2,
            item_id="RQ-02",
            name="🔑 P值合理性",
            name_en="P-value Plausibility (KEY)",
            description="所有P值是否在[0,1]范围内？是否有p=0.000（应为<0.001）？P值与检验统计量是否一致？",
            is_key=True,
            check_method="自动检查所有P值范围和格式",
            pass_criteria="所有P值在[0,1]，格式正确，与统计量一致",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=3,
            item_id="RQ-03",
            name="置信区间一致性",
            name_en="CI Consistency",
            description="置信区间是否与点估计和P值一致？宽度是否与样本量匹配？",
            is_key=False,
            check_method="验证CI = estimate ± z * SE，宽度与样本量反比",
            pass_criteria="CI与点估计和P值一致",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=4,
            item_id="RQ-04",
            name="样本量一致性",
            name_en="Sample Size Consistency",
            description="分析中的N是否与数据一致？亚组N是否正确求和？",
            is_key=False,
            check_method="验证各表中N的加总关系",
            pass_criteria="所有N一致，加总正确",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=5,
            item_id="RQ-05",
            name="图表数据一致性",
            name_en="Table-Figure Consistency",
            description="表格中的数字是否与图表中的数字一致？",
            is_key=False,
            check_method="交叉验证表格和图表中的关键数值",
            pass_criteria="表格和图表数值一致",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=6,
            item_id="RQ-06",
            name="效应量合理性",
            name_en="Effect Size Plausibility",
            description="效应量是否在该临床领域的合理范围内？",
            is_key=False,
            check_method="对比效应量与文献参考范围",
            pass_criteria="效应量在合理范围内",
            evidence_type="metric",
        ),
        CheckItem(
            item_number=7,
            item_id="RQ-07",
            name="🔑 语言一致性",
            name_en="Language Consistency (KEY)",
            description="所有代码是否使用SAP中锁定的分析语言（R或Python）？",
            is_key=True,
            check_method="扫描所有生成的代码文件，验证语言一致性",
            pass_criteria="全部代码使用同一语言",
            evidence_type="file",
        ),
        CheckItem(
            item_number=8,
            item_id="RQ-08",
            name="🔑 代码可复现性",
            name_en="Code Reproducibility (KEY)",
            description="分析代码是否能从干净状态无错误运行？随机种子是否设置？",
            is_key=True,
            check_method="从干净状态运行代码，验证输出一致",
            pass_criteria="代码无错误运行，结果可复现",
            evidence_type="file",
        ),
        CheckItem(
            item_number=9,
            item_id="RQ-09",
            name="🔑 偏差日志完整性",
            name_en="Deviation Log Completeness (KEY)",
            description="所有SAP偏差是否已记录？偏差影响评估是否完成？",
            is_key=True,
            check_method="审查偏差日志，验证每个偏差有：描述、原因、影响评估",
            pass_criteria="所有偏差有记录和影响评估",
            evidence_type="log",
        ),
    ],
)
