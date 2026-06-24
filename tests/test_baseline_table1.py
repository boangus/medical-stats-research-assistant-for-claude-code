"""
test_baseline_table1.py — Table 1 基线特征表引擎单元测试
"""
import numpy as np
import pandas as pd
import pytest

from shared.templates.baseline_table1_engine import (
    BaselineTable1Engine,
    Table1Result,
    VariableConfig,
)

# ── Fixtures ──


@pytest.fixture
def engine():
    return BaselineTable1Engine()


@pytest.fixture
def rct_df():
    """RCT 模拟数据"""
    np.random.seed(42)
    n = 300
    return pd.DataFrame({
        "treatment": np.random.choice(["Drug", "Placebo"], n),
        "age": np.random.normal(55, 10, n),
        "bmi": np.random.lognormal(3, 0.3, n),  # 非正态
        "sex": np.random.choice(["Male", "Female"], n),
        "smoking": np.random.choice(["Never", "Former", "Current"], n),
        "diabetes": np.random.choice([0, 1], n, p=[0.7, 0.3]),
    })


@pytest.fixture
def small_df():
    """小样本数据"""
    np.random.seed(42)
    return pd.DataFrame({
        "group": ["A"] * 10 + ["B"] * 10,
        "value": np.random.normal(50, 10, 20),
        "category": np.random.choice(["X", "Y"], 20),
    })


@pytest.fixture
def vars_config():
    """标准变量配置"""
    return [
        VariableConfig("age", "Age (years)", "continuous"),
        VariableConfig("bmi", "BMI (kg/m²)", "continuous"),
        VariableConfig("sex", "Sex", "categorical"),
        VariableConfig("smoking", "Smoking Status", "categorical"),
        VariableConfig("diabetes", "Diabetes", "categorical"),
    ]


# ── 数据验证 ──


class TestDataValidation:
    """数据验证测试"""

    def test_empty_dataframe(self, engine):
        df = pd.DataFrame()
        result = engine.generate(df)
        assert len(result.warnings) > 0
        assert "空" in result.warnings[0]

    def test_small_sample_warning(self, engine):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        result = engine.generate(df)
        assert any("样本量" in w for w in result.warnings)

    def test_missing_group_var(self, engine, rct_df):
        result = engine.generate(rct_df, group_var="nonexistent")
        assert len(result.warnings) > 0
        assert any("nonexistent" in w for w in result.warnings)

    def test_missing_variable_warning(self, engine, rct_df):
        vars_bad = [VariableConfig("nonexistent", "Missing", "continuous")]
        result = engine.generate(rct_df, group_var="treatment", variables=vars_bad)
        assert len(result.warnings) > 0
        assert any("nonexistent" in w for w in result.warnings)

    def test_high_missing_rate_warning(self, engine):
        df = pd.DataFrame({
            "group": ["A"] * 50 + ["B"] * 50,
            "sparse": [np.nan] * 80 + list(range(20)),  # 80% 缺失
        })
        result = engine.generate(
            df, group_var="group",
            variables=[VariableConfig("sparse", "Sparse", "continuous")]
        )
        assert any("缺失率" in w for w in result.warnings)


# ── 正态性检验 ──


class TestNormalityTest:
    """正态性检验"""

    def test_normal_detected(self, engine):
        np.random.seed(42)
        normal_data = pd.Series(np.random.normal(50, 10, 200))
        assert engine._test_normality(normal_data) == True

    def test_nonnormal_detected(self, engine):
        np.random.seed(42)
        skewed_data = pd.Series(np.random.exponential(10, 200))
        assert engine._test_normality(skewed_data) == False

    def test_small_sample_defaults_normal(self, engine):
        tiny = pd.Series([1.0, 2.0])
        assert engine._test_normality(tiny) == True

    def test_large_sample_ks(self, engine):
        np.random.seed(42)
        large_normal = pd.Series(np.random.normal(0, 1, 6000))
        assert engine._test_normality(large_normal) == True


# ── 连续变量检验 ──


class TestContinuousTests:
    """连续变量检验选择"""

    def test_parametric_two_groups(self, engine, rct_df):
        # age 近似正态，应选参数检验
        groups = ["Drug", "Placebo"]
        test_name, stat, p = engine._test_continuous_parametric(
            rct_df, "age", "treatment", groups
        )
        assert "t-test" in test_name
        assert stat is not None
        assert 0 <= p <= 1

    def test_nonparametric_two_groups(self, engine, rct_df):
        # bmi 非正态，应选非参数检验
        groups = ["Drug", "Placebo"]
        test_name, stat, p = engine._test_continuous_nonparametric(
            rct_df, "bmi", "treatment", groups
        )
        assert "Wilcoxon" in test_name
        assert stat is not None
        assert 0 <= p <= 1

    def test_no_group_returns_empty(self, engine, rct_df):
        test_name, stat, p = engine._test_continuous_parametric(
            rct_df, "age", None, []
        )
        assert test_name == ""


# ── 分类变量检验 ──


class TestCategoricalTests:
    """分类变量三路卡方检验"""

    def test_pearson_chi_square(self, engine, rct_df):
        # sex 期望频数通常 ≥ 5
        test_name, stat, p = engine._test_categorical(
            rct_df, "sex", "treatment", ["Drug", "Placebo"]
        )
        assert "χ²" in test_name or "Fisher" in test_name
        assert 0 <= p <= 1

    def test_fisher_for_small_expected(self, engine):
        # 构造 2×2 表且期望频数 < 1 的场景
        df = pd.DataFrame({
            "group": ["A"] * 50 + ["B"] * 50,
            "rare": ["X"] * 99 + ["Y"],
        })
        test_name, stat, p = engine._test_categorical(
            df, "rare", "group", ["A", "B"]
        )
        # 应选 Fisher 或 Yates
        assert "Fisher" in test_name or "Yates" in test_name


# ── 完整生成 ──


class TestGenerate:
    """完整 Table 1 生成"""

    def test_basic_generation(self, engine, rct_df, vars_config):
        result = engine.generate(
            rct_df, group_var="treatment", variables=vars_config
        )
        assert isinstance(result, Table1Result)
        assert len(result.rows) > 0
        assert result.metadata["n_total"] == 300

    def test_no_group(self, engine, rct_df, vars_config):
        result = engine.generate(rct_df, variables=vars_config)
        assert not result.has_pvalue
        assert result.metadata["n_per_group"] == {}

    def test_auto_infer_variables(self, engine, rct_df):
        result = engine.generate(rct_df, group_var="treatment")
        assert len(result.rows) > 0

    def test_include_smd(self, engine, rct_df, vars_config):
        result = engine.generate(
            rct_df, group_var="treatment", variables=vars_config,
            include_pvalue=True, include_smd=True
        )
        assert result.has_smd

    def test_single_variable(self, engine, rct_df):
        result = engine.generate(
            rct_df, group_var="treatment",
            variables=[VariableConfig("age", "Age", "continuous")]
        )
        assert len(result.rows) == 1

    def test_single_level_factor_skipped(self, engine):
        df = pd.DataFrame({
            "group": ["A"] * 50 + ["B"] * 50,
            "constant": ["X"] * 100,  # 单水平
        })
        result = engine.generate(
            df, group_var="group",
            variables=[VariableConfig("constant", "Const", "categorical")]
        )
        assert len(result.rows) == 0


# ── 输出格式 ──


class TestOutputFormats:
    """输出格式测试"""

    def test_to_dataframe(self, engine, rct_df, vars_config):
        result = engine.generate(
            rct_df, group_var="treatment", variables=vars_config
        )
        df = result.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "Overall" in df.columns
        assert "Drug" in df.columns
        assert "Placebo" in df.columns

    def test_to_markdown(self, engine, rct_df, vars_config):
        result = engine.generate(
            rct_df, group_var="treatment", variables=vars_config
        )
        md = result.to_markdown()
        assert "Table 1" in md
        assert "|" in md
        assert "---" in md

    def test_to_dict(self, engine, rct_df, vars_config):
        result = engine.generate(
            rct_df, group_var="treatment", variables=vars_config
        )
        d = result.to_dict()
        assert "metadata" in d
        assert "rows" in d
        assert isinstance(d["rows"], list)

    def test_markdown_with_warnings(self, engine):
        df = pd.DataFrame({"x": [1, 2, 3]})
        result = engine.generate(df)
        md = result.to_markdown()
        if result.warnings:
            assert "Warnings" in md


# ── 格式化 ──


class TestFormatting:
    """统计量格式化"""

    def test_mean_sd_format(self, engine):
        vals = pd.Series([10.0, 20.0, 30.0])
        result = engine._format_continuous(vals, "mean_sd", 1)
        assert "20.0" in result
        assert "(" in result

    def test_median_iqr_format(self, engine):
        vals = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
        result = engine._format_continuous(vals, "median_iqr", 1)
        assert "30.0" in result
        assert "[" in result

    def test_empty_series_format(self, engine):
        vals = pd.Series([], dtype=float)
        assert engine._format_continuous(vals, "mean_sd", 1) == ""


# ── 变量类型检测 ──


class TestVarTypeDetection:
    """变量类型自动检测"""

    def test_continuous_detected(self, engine):
        df = pd.DataFrame({"age": np.random.normal(50, 10, 100)})
        assert engine._detect_var_type(df, "age") == "continuous"

    def test_categorical_detected(self, engine):
        df = pd.DataFrame({"group": np.random.choice(["A", "B", "C"], 100)})
        assert engine._detect_var_type(df, "group") == "categorical"

    def test_numeric_low_cardinality_as_categorical(self, engine):
        df = pd.DataFrame({"stage": np.random.choice([0, 1, 2, 3], 100)})
        assert engine._detect_var_type(df, "stage") == "categorical"


# ── VariableConfig ──


class TestVariableConfig:
    """变量配置测试"""

    def test_default_label(self):
        vc = VariableConfig("age")
        assert vc.label == "age"

    def test_custom_label(self):
        vc = VariableConfig("age", "Age (years)")
        assert vc.label == "Age (years)"

    def test_auto_type(self):
        vc = VariableConfig("x")
        assert vc.var_type == "auto"
