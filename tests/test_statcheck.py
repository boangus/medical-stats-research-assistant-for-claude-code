"""
test_statcheck.py — statcheck_patterns.py 单元测试
"""
import importlib

# 目录名含连字符，需用 importlib 导入
_mod = importlib.import_module("shared.reporting-guidelines.statcheck_patterns")
check_text = _mod.check_text
format_report = _mod.format_report
RE_T_TEST = _mod.RE_T_TEST
RE_F_TEST = _mod.RE_F_TEST
RE_R_CORR = _mod.RE_R_CORR
RE_CHI2 = _mod.RE_CHI2
RE_Z_TEST = _mod.RE_Z_TEST


class TestRegexPatterns:
    """正则表达式模式测试"""

    def test_t_test_match(self):
        text = "t(48) = 2.34, p = .023"
        m = RE_T_TEST.search(text)
        assert m is not None
        assert m.group(1) == "48"
        assert m.group(2) == "2.34"
        assert m.group(3) == ".023"

    def test_f_test_match(self):
        text = "F(2, 97) = 4.56, p = .013"
        m = RE_F_TEST.search(text)
        assert m is not None
        assert m.group(1) == "2"
        assert m.group(2) == "97"
        assert m.group(3) == "4.56"

    def test_r_correlation_match(self):
        text = "r(48) = .45, p = .001"
        m = RE_R_CORR.search(text)
        assert m is not None
        assert m.group(1) == "48"
        assert m.group(2) == ".45"

    def test_chi2_match(self):
        text = "χ²(1, N = 100) = 4.56, p = .033"
        m = RE_CHI2.search(text)
        assert m is not None
        assert m.group(1) == "1"
        assert m.group(3) == "4.56"

    def test_z_test_match(self):
        text = "z = 2.34, p = .019"
        m = RE_Z_TEST.search(text)
        assert m is not None
        assert m.group(1) == "2.34"

    def test_no_match_for_invalid(self):
        assert RE_T_TEST.search("no stats here") is None
        assert RE_F_TEST.search("t(48) = 2.34") is None


class TestCheckText:
    """文本检查功能测试"""

    def test_consistent_stats(self):
        # t(48) = 2.34, p ≈ .023 是一致的
        text = "两组差异有统计学意义 (t(48) = 2.34, p = .023)。"
        report = check_text(text)
        assert report.total_stats_found >= 1
        # 不应该有 error 级别的不一致
        assert report.error_count == 0

    def test_inconsistent_stats(self):
        # 故意写一个不一致的: t=2.34, df=48 对应 p≈.023, 但写 p=.230
        text = "差异显著 (t(48) = 2.34, p = .230)。"
        report = check_text(text)
        assert report.total_stats_found >= 1
        assert len(report.inconsistencies) >= 1

    def test_multiple_stats(self):
        text = """
        t 检验结果 (t(48) = 2.34, p = .023)。
        F 检验结果 (F(2, 97) = 4.56, p = .013)。
        相关分析 (r(98) = .45, p = .001)。
        """
        report = check_text(text)
        assert report.total_stats_found >= 3

    def test_empty_text(self):
        report = check_text("")
        assert report.total_stats_found == 0
        assert len(report.inconsistencies) == 0

    def test_no_stats_text(self):
        report = check_text("这是一段没有统计量的普通文本。")
        assert report.total_stats_found == 0


class TestFormatReport:
    """报告格式化测试"""

    def test_report_structure(self):
        text = "t(48) = 2.34, p = .023"
        report = check_text(text)
        formatted = format_report(report)
        assert "statcheck" in formatted
        assert "检查统计量数" in formatted

    def test_report_with_inconsistencies(self):
        text = "t(48) = 2.34, p = .500"  # 不一致
        report = check_text(text)
        formatted = format_report(report)
        assert "不一致" in formatted or "⚠️" in formatted or "❌" in formatted


class TestSeverityClassification:
    """严重程度分类测试"""

    def test_consistent_is_ok(self):
        # p ≈ .023 与 t(48)=2.34 一致
        text = "t(48) = 2.34, p = .023"
        report = check_text(text)
        if report.details:
            assert report.details[0]["severity"] == "ok"

    def test_conclusion_flip_is_error(self):
        # p=.500 与 t(48)=2.34 不一致 → 结论翻转
        text = "t(48) = 2.34, p = .500"
        report = check_text(text)
        if report.inconsistencies:
            assert report.inconsistencies[0].severity == "error"
