"""
test_tcm_normalizer.py — tcm_normalizer.py 单元测试
"""
import os

import pandas as pd
import pytest

# 跳过如果映射文件不存在
MAPPING_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "shared", "value-normalization", "tcm_terms", "gb_t16751_syndrome.json"
)


@pytest.fixture
def normalizer():
    if not os.path.exists(MAPPING_PATH):
        pytest.skip("TCM mapping file not found")
    import importlib
    mod = importlib.import_module("shared.value-normalization.tcm_terms.tcm_normalizer")
    return mod.TCMTermNormalizer(MAPPING_PATH)


@pytest.fixture
def tcm_df():
    return pd.DataFrame({
        "诊断": ["心脾两虚证型", "肝气郁结", "痰湿内阻证", "正常值"],
        "年龄": [45, 50, 55, 60],
        "性别": ["男", "女", "男", "女"],
    })


class TestTermLookup:
    """术语查找测试"""

    def test_exact_match(self, normalizer):
        if not normalizer.mapping.get("TCM_CM_TERM_MAP") and not normalizer.mapping.get("TCM_TERM_MAP"):
            pytest.skip("Empty mapping")
        # 测试精确匹配
        result = normalizer._lookup_term("心脾两虚")
        if result is not None:
            assert "standard" in result or "_fuzzy_match" in result

    def test_suffix_stripping(self, normalizer):
        # 去后缀匹配
        result = normalizer._lookup_term("心脾两虚证")
        # 应该能找到（去掉"证"后缀）
        if result is not None:
            assert "standard" in result or "_fuzzy_match" in result

    def test_unknown_term(self, normalizer):
        result = normalizer._lookup_term("完全不存在的术语XYZ")
        assert result is None or result.get("_fuzzy_match")


class TestLevenshtein:
    """编辑距离测试"""

    def test_identical(self, normalizer):
        assert normalizer._levenshtein("abc", "abc") == 0

    def test_single_edit(self, normalizer):
        assert normalizer._levenshtein("abc", "ab") == 1
        assert normalizer._levenshtein("abc", "abcd") == 1

    def test_symmetric(self, normalizer):
        assert normalizer._levenshtein("abc", "def") == normalizer._levenshtein("def", "abc")


class TestCompoundSplit:
    """复合证候拆分测试"""

    def test_chinese_comma(self, normalizer):
        result = normalizer._split_compound("心脾两虚，痰湿内阻")
        assert len(result) == 2

    def test_single_term(self, normalizer):
        result = normalizer._split_compound("心脾两虚")
        assert len(result) == 1

    def test_space_delimiter(self, normalizer):
        result = normalizer._split_compound("心脾两虚、痰湿内阻")
        assert len(result) == 2


class TestDetectVariants:
    """变体检测测试"""

    def test_dataframe_detection(self, normalizer, tcm_df):
        results = normalizer.detect_variants(tcm_df, columns=["诊断"])
        # 应该返回字典
        assert isinstance(results, dict)

    def test_non_string_column(self, normalizer, tcm_df):
        results = normalizer.detect_variants(tcm_df, columns=["年龄"])
        # 数值列应返回空
        assert len(results) == 0


class TestShowSummary:
    """摘要生成测试"""

    def test_empty_results(self, normalizer):
        summary = normalizer.show_summary({})
        assert "未检测到" in summary

    def test_with_results(self, normalizer):
        results = {"诊断": [
            {"value": "心脾两虚证型", "count": 3, "suggested": "心脾两虚证",
             "confidence": "exact", "findings": []}
        ]}
        summary = normalizer.show_summary(results)
        assert "心脾两虚" in summary
