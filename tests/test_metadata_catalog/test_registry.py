"""Tests for MetadataRegistry — register/lookup/list_all/lineage/export_json."""

import json
import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.metadata_catalog import MetadataRegistry
from shared.metadata_catalog.exceptions import (
    InvalidLineageError,
    VariableAlreadyExistsError,
    VariableNotFoundError,
)
from shared.metadata_catalog.registry import MetadataEntry, VariableType


@pytest.fixture
def registry():
    return MetadataRegistry()


@pytest.fixture
def populated_registry(registry):
    """填充 bmi 血缘: weight + height -> bmi"""
    registry.register(MetadataEntry(
        variable="weight",
        description="体重 kg",
        variable_type=VariableType.CLINICAL,
        unit="kg",
        stage="stage1",
    ))
    registry.register(MetadataEntry(
        variable="height",
        description="身高 cm",
        variable_type=VariableType.CLINICAL,
        unit="cm",
        stage="stage1",
    ))
    registry.register(MetadataEntry(
        variable="bmi",
        description="Body Mass Index",
        variable_type=VariableType.DERIVED,
        source_variables=["weight", "height"],
        unit="kg/m^2",
        stage="stage2",
    ))
    registry.register(MetadataEntry(
        variable="obesity_class",
        description="肥胖分级",
        variable_type=VariableType.DERIVED,
        source_variables=["bmi"],
        stage="stage3",
    ))
    return registry


class TestRegister:
    def test_register_new_variable(self, registry):
        entry = MetadataEntry(
            variable="age",
            description="Patient age",
            variable_type=VariableType.DEMOGRAPHIC,
        )
        registry.register(entry)
        assert registry.lookup("age").variable == "age"

    def test_register_duplicate_raises(self, registry):
        entry = MetadataEntry(
            variable="age",
            description="x",
            variable_type=VariableType.DEMOGRAPHIC,
        )
        registry.register(entry)
        with pytest.raises(VariableAlreadyExistsError):
            registry.register(entry)

    def test_register_overwrite(self, registry):
        entry1 = MetadataEntry(
            variable="age",
            description="first",
            variable_type=VariableType.DEMOGRAPHIC,
        )
        entry2 = MetadataEntry(
            variable="age",
            description="updated",
            variable_type=VariableType.DEMOGRAPHIC,
        )
        registry.register(entry1)
        registry.register(entry2, overwrite=True)
        assert registry.lookup("age").description == "updated"


class TestLookup:
    def test_lookup_existing(self, populated_registry):
        entry = populated_registry.lookup("bmi")
        assert entry is not None
        assert entry.variable == "bmi"

    def test_lookup_nonexistent_raises(self, registry):
        with pytest.raises(VariableNotFoundError):
            registry.lookup("nonexistent_var")


class TestListAll:
    def test_list_all_returns_list(self, populated_registry):
        entries = populated_registry.list_all()
        assert isinstance(entries, list)
        assert len(entries) >= 4

    def test_list_all_returns_copies(self, populated_registry):
        entries = populated_registry.list_all()
        entries.clear()
        # 修改返回的列表不应影响内部状态
        assert populated_registry.lookup("bmi") is not None


class TestLineage:
    def test_lineage_upstream(self, populated_registry):
        graph = populated_registry.lineage("bmi")
        assert graph.variable == "bmi"
        upstream_vars = [e.variable for e in graph.upstream]
        assert "weight" in upstream_vars
        assert "height" in upstream_vars

    def test_lineage_multi_level(self, populated_registry):
        """obesity_class 源自 bmi，bmi 又源自 weight/height — 全部应出现在上游。"""
        graph = populated_registry.lineage("obesity_class")
        all_upstream = [e.variable for e in graph.upstream]
        assert "bmi" in all_upstream
        assert "weight" in all_upstream
        assert "height" in all_upstream

    def test_lineage_no_upstream(self, populated_registry):
        graph = populated_registry.lineage("weight")
        assert graph.variable == "weight"
        assert graph.upstream == []

    def test_lineage_nonexistent_raises(self, registry):
        with pytest.raises(VariableNotFoundError):
            registry.lineage("nonexistent")


class TestCycleDetection:
    def test_cycle_detection(self, registry):
        """构造循环: a -> b -> a"""
        from shared.metadata_catalog.registry import MetadataEntry, VariableType
        registry.register(MetadataEntry(
            variable="a", description="a",
            variable_type=VariableType.DERIVED,
            source_variables=["b"],
        ))
        # b 源自 a → 形成循环
        with pytest.raises(InvalidLineageError):
            registry.register(MetadataEntry(
                variable="b", description="b",
                variable_type=VariableType.DERIVED,
                source_variables=["a"],
            ))


class TestExportJson:
    def test_export_json(self, populated_registry, tmp_path):
        out = tmp_path / "metadata.json"
        populated_registry.export_json(out)
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "variables" in data
        assert any(v["variable"] == "bmi" for v in data["variables"])
