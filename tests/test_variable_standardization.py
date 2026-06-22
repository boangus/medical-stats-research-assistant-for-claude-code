"""VariableStandardizer 单元测试

覆盖 shared/variable_standardization/variable_standardizer.py 的核心方法：
- get_label / get_unit / get_category
- add_mapping
- standardize_dataframe
- generate_mapping_table
- validate_consistency
- get_mapping_for_export
- reverse_lookup
- custom mapping (YAML 加载)
"""

import warnings
from pathlib import Path

import pandas as pd
import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.variable_standardization.variable_standardizer import VariableStandardizer


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def standardizer():
    """返回默认的 VariableStandardizer 实例"""
    return VariableStandardizer()


@pytest.fixture
def sample_df():
    """返回包含常见医学变量的 DataFrame"""
    return pd.DataFrame({
        "BMI": [23.5, 25.1],
        "PSA": [5.1, 8.3],
        "age": [65, 72],
        "unknown_col": [1, 2],
    })


# ── get_label tests ───────────────────────────────────────────────


class TestGetLabel:
    def test_chinese_label(self, standardizer):
        assert standardizer.get_label("BMI", "zh") == "体质指数（BMI）"

    def test_english_label(self, standardizer):
        assert standardizer.get_label("BMI", "en") == "Body mass index (BMI)"

    def test_unknown_variable_returns_raw(self, standardizer):
        assert standardizer.get_label("unknown_var", "zh") == "unknown_var"

    def test_default_lang_is_zh(self, standardizer):
        assert standardizer.get_label("PSA") == "前列腺特异性抗原（PSA）"

    def test_unit_variable(self, standardizer):
        assert standardizer.get_label("身高_cm", "zh") == "身高（cm）"


# ── get_unit tests ────────────────────────────────────────────────


class TestGetUnit:
    def test_known_unit(self, standardizer):
        assert standardizer.get_unit("PSA") == "ng/mL"

    def test_bmi_unit(self, standardizer):
        assert standardizer.get_unit("BMI") == "kg/m²"

    def test_unknown_returns_empty(self, standardizer):
        assert standardizer.get_unit("unknown") == ""

    def test_no_unit_variable(self, standardizer):
        assert standardizer.get_unit("性别") == ""


# ── get_category tests ────────────────────────────────────────────


class TestGetCategory:
    def test_laboratory_category(self, standardizer):
        assert standardizer.get_category("PSA") == "实验室检查"

    def test_outcome_category(self, standardizer):
        assert standardizer.get_category("OS") == "结局"

    def test_unknown_returns_empty(self, standardizer):
        assert standardizer.get_category("nonexistent") == ""


# ── add_mapping tests ─────────────────────────────────────────────


class TestAddMapping:
    def test_add_and_retrieve(self, standardizer):
        standardizer.add_mapping(
            "LDH", zh="乳酸脱氢酶（LDH）", en="Lactate dehydrogenase (LDH)",
            unit="U/L", category="实验室检查"
        )
        assert standardizer.get_label("LDH", "zh") == "乳酸脱氢酶（LDH）"
        assert standardizer.get_unit("LDH") == "U/L"

    def test_custom_overrides_default(self, standardizer):
        original_label = standardizer.get_label("BMI", "zh")
        standardizer.add_mapping(
            "BMI", zh="自定义BMI", en="Custom BMI", unit="custom", category="自定义"
        )
        assert standardizer.get_label("BMI", "zh") == "自定义BMI"
        assert standardizer.get_unit("BMI") == "custom"
        # Restore
        standardizer.custom_mapping.pop("BMI", None)


# ── standardize_dataframe tests ───────────────────────────────────


class TestStandardizeDataframe:
    def test_basic_standardization(self, standardizer, sample_df):
        df_std = standardizer.standardize_dataframe(sample_df)
        assert "体质指数（BMI）" in df_std.columns
        assert "前列腺特异性抗原（PSA）" in df_std.columns
        assert "年龄（岁）" in df_std.columns

    def test_unmapped_kept(self, standardizer, sample_df):
        df_std = standardizer.standardize_dataframe(sample_df, unmapped_policy="keep")
        assert "unknown_col" in df_std.columns

    def test_unmapped_dropped(self, standardizer, sample_df):
        df_std = standardizer.standardize_dataframe(sample_df, unmapped_policy="drop")
        assert "unknown_col" not in df_std.columns

    def test_unmapped_warn(self, standardizer, sample_df):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            df_std = standardizer.standardize_dataframe(sample_df, unmapped_policy="warn")
            assert len(w) >= 1
            assert "未找到映射" in str(w[0].message)

    def test_invalid_policy_raises(self, standardizer, sample_df):
        with pytest.raises(ValueError, match="unmapped_policy"):
            standardizer.standardize_dataframe(sample_df, unmapped_policy="invalid")

    def test_english_standardization(self, standardizer, sample_df):
        df_std = standardizer.standardize_dataframe(sample_df, lang="en")
        assert "Body mass index (BMI)" in df_std.columns

    def test_original_df_not_modified(self, standardizer, sample_df):
        original_cols = list(sample_df.columns)
        _ = standardizer.standardize_dataframe(sample_df)
        assert list(sample_df.columns) == original_cols


# ── generate_mapping_table tests ──────────────────────────────────


class TestGenerateMappingTable:
    def test_mapped_and_unmapped(self, standardizer, sample_df):
        table = standardizer.generate_mapping_table(sample_df)
        assert len(table) == 4
        mapped = [t for t in table if t["status"] == "mapped"]
        unmapped = [t for t in table if t["status"] == "unmapped"]
        assert len(mapped) == 3
        assert len(unmapped) == 1

    def test_mapped_has_suggestion(self, standardizer, sample_df):
        table = standardizer.generate_mapping_table(sample_df)
        for entry in table:
            if entry["status"] == "mapped":
                assert entry["suggested"] != ""

    def test_unmapped_empty_suggestion(self, standardizer, sample_df):
        table = standardizer.generate_mapping_table(sample_df)
        for entry in table:
            if entry["status"] == "unmapped":
                assert entry["suggested"] == ""


# ── validate_consistency tests ────────────────────────────────────


class TestValidateConsistency:
    def test_consistent_labels(self, standardizer):
        result = standardizer.validate_consistency(["BMI", "BMI", "BMI"])
        assert result["consistent"] is True

    def test_inconsistent_labels(self, standardizer):
        result = standardizer.validate_consistency(["BMI", "体质指数（BMI）", "BMI"])
        # "BMI" and "体质指数（BMI）" map to the same variable
        assert result["consistent"] is False
        # 1 canonical group ("体质指数（BMI）") with 2 distinct original labels
        assert len(result["groups"]) == 1
        assert set(result["groups"]["体质指数（BMI）"]) == {"BMI", "体质指数（BMI）"}

    def test_completely_different_labels(self, standardizer):
        result = standardizer.validate_consistency(["PSA", "BMI", "Hb"])
        assert result["consistent"] is True  # Each is a unique variable


# ── get_mapping_for_export tests ──────────────────────────────────


class TestGetMappingForExport:
    def test_basic_export(self, standardizer):
        export = standardizer.get_mapping_for_export()
        assert "BMI" in export
        assert "体质指数（BMI）" in export["BMI"]

    def test_export_with_unit(self, standardizer):
        export = standardizer.get_mapping_for_export(include_unit=True, include_category=False)
        assert "单位: kg/m²" in export["BMI"]

    def test_export_without_unit(self, standardizer):
        export = standardizer.get_mapping_for_export(include_unit=False, include_category=False)
        assert export["BMI"] == "体质指数（BMI）"


# ── reverse_lookup tests ──────────────────────────────────────────


class TestReverseLookup:
    def test_reverse_lookup_chinese(self, standardizer):
        assert standardizer.reverse_lookup("体质指数（BMI）") == "BMI"

    def test_reverse_lookup_english(self, standardizer):
        assert standardizer.reverse_lookup("Body mass index (BMI)") == "BMI"

    def test_reverse_lookup_not_found(self, standardizer):
        assert standardizer.reverse_lookup("不存在的名称") is None


# ── Custom mapping (YAML) tests ──────────────────────────────────


class TestCustomMapping:
    def test_custom_mapping_file(self, tmp_path):
        yaml_content = """
custom_var:
  zh: 自定义变量
  en: Custom variable
  unit: mg
  category: 自定义
"""
        yaml_file = tmp_path / "custom_mapping.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        s = VariableStandardizer(mapping_file=yaml_file)
        assert s.get_label("custom_var", "zh") == "自定义变量"
        assert s.get_unit("custom_var") == "mg"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError, match="映射文件不存在"):
            VariableStandardizer(mapping_file="/nonexistent/path.yaml")

    def test_custom_overrides_default(self, tmp_path):
        yaml_content = """
BMI:
  zh: 自定义BMI
  en: Custom BMI
  unit: custom_unit
  category: 自定义
"""
        yaml_file = tmp_path / "override.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        s = VariableStandardizer(mapping_file=yaml_file)
        assert s.get_label("BMI", "zh") == "自定义BMI"
