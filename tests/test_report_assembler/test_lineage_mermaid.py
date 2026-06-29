"""Tests for lineage Mermaid diagram generator."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.metadata_catalog import MetadataEntry, MetadataRegistry, VariableType
from shared.report_assembler.lineage_mermaid import generate_lineage_mermaid


@pytest.fixture
def registry_with_lineage():
    """构造: weight + height -> bmi -> obesity_class"""
    reg = MetadataRegistry()
    reg.register(MetadataEntry(
        variable="weight", description="体重",
        variable_type=VariableType.CLINICAL, unit="kg", stage="stage1",
    ))
    reg.register(MetadataEntry(
        variable="height", description="身高",
        variable_type=VariableType.CLINICAL, unit="cm", stage="stage1",
    ))
    reg.register(MetadataEntry(
        variable="bmi", description="BMI",
        variable_type=VariableType.DERIVED,
        source_variables=["weight", "height"], unit="kg/m^2", stage="stage2",
    ))
    reg.register(MetadataEntry(
        variable="obesity_class", description="肥胖分级",
        variable_type=VariableType.DERIVED,
        source_variables=["bmi"], stage="stage3",
    ))
    return reg


def test_mermaid_basic_structure(registry_with_lineage):
    """生成的 Mermaid 文本包含 graph LR 和节点定义。"""
    mermaid = generate_lineage_mermaid(registry_with_lineage, "bmi")
    assert "graph" in mermaid
    assert "weight" in mermaid
    assert "height" in mermaid
    assert "bmi" in mermaid


def test_mermaid_contains_arrows(registry_with_lineage):
    """血缘箭头应从源变量指向派生变量。"""
    mermaid = generate_lineage_mermaid(registry_with_lineage, "bmi")
    # Mermaid 边语法: A --> B
    assert "-->" in mermaid
    assert "weight" in mermaid and "bmi" in mermaid


def test_mermaid_full_registry(registry_with_lineage):
    """不指定 variable 时，导出整个图。"""
    mermaid = generate_lineage_mermaid(registry_with_lineage)
    assert "obesity_class" in mermaid
    assert "bmi" in mermaid


def test_mermaid_single_variable_no_upstream(registry_with_lineage):
    """对原始变量生成图：只有自身节点，无入边。"""
    mermaid = generate_lineage_mermaid(registry_with_lineage, "weight")
    assert "weight" in mermaid
    # weight 没有源变量，所以不应有指向 weight 的箭头
    assert "--> weight" not in mermaid.replace("weight -->", "")


def test_mermaid_invalid_syntax(registry_with_lineage):
    """生成的文本不应包含明显语法错误（如空节点 ID）。"""
    mermaid = generate_lineage_mermaid(registry_with_lineage)
    # 节点定义不应有空 ID
    lines = mermaid.split("\n")
    for line in lines:
        if "-->" in line:
            # 边定义: A --> B
            parts = line.split("-->")
            assert len(parts) == 2
            assert parts[0].strip()
            assert parts[1].strip()
