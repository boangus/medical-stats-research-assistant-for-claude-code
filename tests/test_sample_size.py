"""
test_sample_size.py — sample_size_calculator.py 单元测试
"""
import importlib

_mod = importlib.import_module("shared.sample-size.sample_size_calculator")
calc_sample_size_t = _mod.calc_sample_size_t
calc_sample_size_prop = _mod.calc_sample_size_prop
calc_sample_size_survival = _mod.calc_sample_size_survival
calc_sample_size_logistic = _mod.calc_sample_size_logistic
calc_sample_size_noninferiority = _mod.calc_sample_size_noninf
calc_sample_size_diagnostic = _mod.calc_sample_size_diagnostic


class TestSampleSizeT:
    """t 检验样本量测试"""

    def test_basic_calculation(self):
        result = calc_sample_size_t(delta=5, sd=10)
        assert result["n_per_group"] > 0
        assert result["n_total"] == result["n_per_group"] * 2

    def test_larger_effect_smaller_sample(self):
        small = calc_sample_size_t(delta=5, sd=10)
        large = calc_sample_size_t(delta=10, sd=10)
        assert large["n_per_group"] < small["n_per_group"]

    def test_higher_power_larger_sample(self):
        p80 = calc_sample_size_t(delta=5, sd=10, power=0.80)
        p90 = calc_sample_size_t(delta=5, sd=10, power=0.90)
        assert p90["n_per_group"] > p80["n_per_group"]

    def test_unequal_ratio(self):
        result = calc_sample_size_t(delta=5, sd=10, ratio=2.0)
        assert result["n_per_group"] > 0

    def test_paired_test(self):
        result = _mod.calc_sample_size_paired_t(delta=3, sd_diff=5)
        assert result["n"] > 0


class TestSampleSizeProp:
    """率比较样本量测试"""

    def test_basic_calculation(self):
        result = calc_sample_size_prop(p1=0.3, p2=0.5)
        assert result["n_per_group"] > 0

    def test_equal_rates(self):
        # 相等率会导致效应量为 0，样本量趋向无穷
        # 这里只测试不崩溃
        try:
            result = calc_sample_size_prop(p1=0.5, p2=0.5)
            assert result["n_per_group"] > 1000
        except (OverflowError, ValueError):
            pass  # 预期的溢出


class TestSampleSizeSurvival:
    """生存分析样本量测试"""

    def test_basic_calculation(self):
        result = calc_sample_size_survival(hr=0.7)
        assert result["n_events"] > 0
        assert result["n_total"] > 0

    def test_hr_near_one(self):
        result = calc_sample_size_survival(hr=0.95)
        assert result["n_events"] > 100  # HR 接近 1 需要大样本


class TestSampleSizeLogistic:
    """Logistic 回归样本量测试"""

    def test_epv_rule(self):
        result = calc_sample_size_logistic(n_predictors=5, prop_events=0.3)
        assert result["n_total"] > 0

    def test_more_predictors_larger_sample(self):
        r5 = calc_sample_size_logistic(n_predictors=5, prop_events=0.3)
        r10 = calc_sample_size_logistic(n_predictors=10, prop_events=0.3)
        assert r10["n_total"] > r5["n_total"]


class TestNoninferiority:
    """非劣效性样本量测试"""

    def test_basic_calculation(self):
        result = calc_sample_size_noninferiority(
            delta=0.10, sd=1.0
        )
        assert result["n_per_group"] > 0


class TestDiagnostic:
    """诊断试验样本量测试"""

    def test_basic_calculation(self):
        result = calc_sample_size_diagnostic(
            sensitivity=0.90, specificity=0.85, prevalence=0.3
        )
        assert result["n_positive"] > 0
        assert result["n_negative"] > 0
        assert result["n_total"] > 0

    def test_narrower_ci_larger_sample(self):
        wide = calc_sample_size_diagnostic(
            sensitivity=0.90, specificity=0.85, prevalence=0.3, ci_width=0.20
        )
        narrow = calc_sample_size_diagnostic(
            sensitivity=0.90, specificity=0.85, prevalence=0.3, ci_width=0.05
        )
        assert narrow["n_total"] > wide["n_total"]

    def test_low_prevalence_inflates_sample(self):
        high_prev = calc_sample_size_diagnostic(
            sensitivity=0.90, specificity=0.85, prevalence=0.5
        )
        low_prev = calc_sample_size_diagnostic(
            sensitivity=0.90, specificity=0.85, prevalence=0.05
        )
        assert low_prev["n_total"] > high_prev["n_total"]
