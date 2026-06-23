"""
test_sensitivity_detector.py — 敏感信息检测引擎单元测试
"""
import os

import pandas as pd
import pytest

from shared.privacy.sensitivity_detector import (
    SensitivityDetector,
    PIIFinding,
    ScanResult,
    PIIDecision,
    DecisionLog,
)
from shared.privacy.masking_strategies import MaskingStrategies


# ── Fixtures ──


@pytest.fixture
def detector():
    return SensitivityDetector()


@pytest.fixture
def pii_df():
    """包含多种 PII 的测试数据"""
    return pd.DataFrame({
        "姓名": ["张三", "李四", "王五"],
        "身份证号": ["110101199001011234", "110101199001021234", "110101199001031234"],
        "手机号": ["13800138000", "13900139000", "13700137000"],
        "邮箱": ["zhangsan@example.com", "lisi@test.org", "wangwu@mail.cn"],
        "银行卡号": ["6222021234567890123", "6222021234567890124", "6222021234567890125"],
        "年龄": [25, 30, 35],
        "诊断": ["糖尿病", "高血压", "冠心病"],
    })


@pytest.fixture
def freetext_df():
    """包含自由文本中嵌入 PII 的数据"""
    return pd.DataFrame({
        "主诉": [
            "患者张三，电话13800138000，主诉头痛3天",
            "李四，邮箱lisi@test.org，发热1天",
            "王五身份证号110101199001011234，胸闷2天",
        ],
        "诊断": ["高血压", "糖尿病", "冠心病"],
    })


@pytest.fixture
def clean_df():
    """无 PII 的干净数据"""
    return pd.DataFrame({
        "年龄": [25, 30, 35],
        "收缩压": [120, 130, 140],
        "诊断": ["高血压", "糖尿病", "冠心病"],
    })


# ── 值层面 PII 检测 ──


class TestValueDetection:
    """值层面 PII 正则检测"""

    def test_detect_id_card_values(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        id_findings = result.get_findings_by_type("id_card")
        assert len(id_findings) > 0
        assert any(f.detection_method == "value_scan" for f in id_findings)

    def test_detect_phone_values(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        phone_findings = result.get_findings_by_type("phone")
        assert len(phone_findings) > 0

    def test_detect_email_values(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        email_findings = result.get_findings_by_type("email")
        assert len(email_findings) > 0

    def test_detect_bank_card_values(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        bank_findings = result.get_findings_by_type("bank_card")
        assert len(bank_findings) > 0

    def test_detect_ip_values(self, detector):
        df = pd.DataFrame({"日志": ["连接到 192.168.1.1 失败", "访问 10.0.0.1 成功"]})
        result = detector.scan_dataframe(df)
        ip_findings = result.get_findings_by_type("ip")
        assert len(ip_findings) > 0

    def test_detect_passport_values(self, detector):
        df = pd.DataFrame({"备注": ["护照号 E12345678 已登记", "护照 G87654321 有效"]})
        result = detector.scan_dataframe(df)
        passport_findings = result.get_findings_by_type("passport")
        assert len(passport_findings) > 0


# ── 列名检测 ──


class TestColumnNameDetection:
    """列名匹配检测"""

    def test_detect_name_column(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        name_findings = [f for f in result.findings if f.pii_type == "name"]
        assert len(name_findings) > 0
        assert name_findings[0].detection_method == "column_name"

    def test_detect_phone_column(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        # 去重后可能为 value_scan，只验证 phone 在"手机号"列被检测到
        phone_findings = result.get_findings_by_column("手机号")
        assert len(phone_findings) > 0
        assert phone_findings[0].pii_type == "phone"

    def test_detect_email_column(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        email_findings = result.get_findings_by_column("邮箱")
        assert len(email_findings) > 0
        assert email_findings[0].pii_type == "email"


# ── 自由文本扫描 ──


class TestFreetextDetection:
    """自由文本列 PII 检测"""

    def test_detect_phone_in_freetext(self, detector, freetext_df):
        result = detector.scan_dataframe(freetext_df)
        # 去重后可能为 value_scan 或 freetext_scan，只验证检测到
        phone_findings = result.get_findings_by_type("phone")
        assert len(phone_findings) > 0
        assert phone_findings[0].column == "主诉"

    def test_detect_id_card_in_freetext(self, detector, freetext_df):
        result = detector.scan_dataframe(freetext_df)
        id_findings = result.get_findings_by_type("id_card")
        assert len(id_findings) > 0
        assert id_findings[0].column == "主诉"

    def test_detect_email_in_freetext(self, detector, freetext_df):
        result = detector.scan_dataframe(freetext_df)
        email_findings = result.get_findings_by_type("email")
        assert len(email_findings) > 0
        assert email_findings[0].column == "主诉"


# ── 无 PII 场景 ──


class TestCleanData:
    """无 PII 数据检测"""

    def test_no_pii_detected(self, detector, clean_df):
        result = detector.scan_dataframe(clean_df)
        assert not result.has_pii
        assert len(result.findings) == 0
        assert result.summary == {}

    def test_empty_dataframe(self, detector):
        df = pd.DataFrame()
        result = detector.scan_dataframe(df)
        assert not result.has_pii
        assert result.total_rows == 0


# ── ScanResult 结构 ──


class TestScanResult:
    """扫描结果结构测试"""

    def test_result_has_metadata(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        assert result.total_rows == 3
        assert result.total_columns == 7
        assert result.scan_time != ""

    def test_result_summary(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        assert "id_card" in result.summary
        assert "phone" in result.summary
        assert result.summary["phone"] > 0

    def test_critical_count(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        assert result.critical_count > 0

    def test_to_dict(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        d = result.to_dict()
        assert "has_pii" in d
        assert "findings" in d
        assert isinstance(d["findings"], list)

    def test_findings_by_type(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        phones = result.get_findings_by_type("phone")
        assert all(f.pii_type == "phone" for f in phones)

    def test_findings_by_column(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        col_findings = result.get_findings_by_column("手机号")
        assert all(f.column == "手机号" for f in col_findings)


# ── 脱敏策略 ──


class TestMaskingStrategies:
    """脱敏策略测试"""

    def test_mask_id_card(self):
        assert MaskingStrategies.mask_id_card("110101199001011234") == "110***********1234"

    def test_mask_phone(self):
        assert MaskingStrategies.mask_phone("13800138000") == "138****8000"

    def test_mask_email(self):
        assert MaskingStrategies.mask_email("zhangsan@example.com") == "z***@example.com"

    def test_mask_bank_card(self):
        result = MaskingStrategies.mask_bank_card("6222021234567890123")
        assert result.endswith("0123")
        assert result.startswith("*")

    def test_mask_ip(self):
        assert MaskingStrategies.mask_ip("192.168.1.100") == "192.168.*.*"

    def test_mask_passport(self):
        result = MaskingStrategies.mask_passport("E12345678")
        assert result.startswith("E")
        assert result.endswith("8")
        assert "*" in result

    def test_mask_full(self):
        assert MaskingStrategies.mask_full("anything") == "[REDACTED]"

    def test_mask_full_custom_replacement(self):
        assert MaskingStrategies.mask_full("x", "***") == "***"

    def test_hash_value_deterministic(self):
        h1 = MaskingStrategies.hash_value("test", salt="fixed")
        h2 = MaskingStrategies.hash_value("test", salt="fixed")
        assert h1 == h2

    def test_hash_value_different_salt(self):
        h1 = MaskingStrategies.hash_value("test", salt="a")
        h2 = MaskingStrategies.hash_value("test", salt="b")
        assert h1 != h2

    def test_keep(self):
        assert MaskingStrategies.keep("original") == "original"

    def test_apply_dispatches_correctly(self):
        assert MaskingStrategies.apply("13800138000", "phone", "mask_partial") == "138****8000"
        assert MaskingStrategies.apply("test", "phone", "mask_full") == "[REDACTED]"

    def test_apply_unknown_type_mask_full(self):
        # 未知类型 mask_partial 应降级为 mask_full
        assert MaskingStrategies.apply("value", "unknown_type", "mask_partial") == "[REDACTED]"

    def test_mask_id_card_short_value(self):
        # 短值不脱敏
        assert MaskingStrategies.mask_id_card("123") == "123"

    def test_mask_phone_wrong_length(self):
        assert MaskingStrategies.mask_phone("12345") == "12345"

    def test_mask_email_no_at(self):
        assert MaskingStrategies.mask_email("noemail") == "noemail"


# ── 决策日志 ──


class TestDecisionLog:
    """决策审计日志测试"""

    def test_record_decision(self):
        log = DecisionLog()
        log.record(PIIDecision(
            pii_type="phone", column="手机号", action="mask_partial"
        ))
        assert len(log) == 1

    def test_auto_timestamp(self):
        log = DecisionLog()
        log.record(PIIDecision(
            pii_type="phone", column="手机号", action="mask_partial"
        ))
        assert log.decisions[0].timestamp != ""

    def test_generate_report(self):
        log = DecisionLog()
        log.record(PIIDecision(
            pii_type="phone", column="手机号", action="mask_partial",
            timestamp="2026-06-22T12:00:00+00:00"
        ))
        log.record(PIIDecision(
            pii_type="id_card", column="身份证号", action="hash",
            timestamp="2026-06-22T12:01:00+00:00"
        ))
        report = log.generate_report()
        assert "敏感信息处理审计报告" in report
        assert "phone" in report
        assert "id_card" in report
        # 报告使用中文动作标签
        assert "部分隐藏" in report
        assert "哈希替换" in report

    def test_save_report(self, tmp_dir):
        log = DecisionLog()
        log.record(PIIDecision(
            pii_type="email", column="邮箱", action="mask_full"
        ))
        path = os.path.join(tmp_dir, "audit.md")
        log.save(path)
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "敏感信息" in content


# ── apply_decision 集成 ──


class TestApplyDecision:
    """脱敏决策应用测试"""

    def test_mask_partial_phone(self, detector, pii_df):
        decision = PIIDecision(
            pii_type="phone", column="手机号", action="mask_partial"
        )
        df_out = detector.apply_decision(pii_df, decision)
        assert df_out["手机号"].iloc[0] == "138****8000"

    def test_mask_full_email(self, detector, pii_df):
        decision = PIIDecision(
            pii_type="email", column="邮箱", action="mask_full"
        )
        df_out = detector.apply_decision(pii_df, decision)
        assert all(v == "[REDACTED]" for v in df_out["邮箱"])

    def test_hash_id_card(self, detector, pii_df):
        decision = PIIDecision(
            pii_type="id_card", column="身份证号", action="hash",
            params={"salt": "test_salt"}
        )
        df_out = detector.apply_decision(pii_df, decision)
        # 哈希后不应有原始值
        assert df_out["身份证号"].iloc[0] != "110101199001011234"
        # 哈希值长度一致
        assert all(len(str(v)) == 16 for v in df_out["身份证号"])

    def test_suppress_column(self, detector, pii_df):
        decision = PIIDecision(
            pii_type="name", column="姓名", action="suppress"
        )
        df_out = detector.apply_decision(pii_df, decision)
        assert "姓名" not in df_out.columns

    def test_keep_column(self, detector, pii_df):
        decision = PIIDecision(
            pii_type="phone", column="手机号", action="keep"
        )
        df_out = detector.apply_decision(pii_df, decision)
        assert df_out["手机号"].iloc[0] == "13800138000"

    def test_decision_recorded_in_log(self, detector, pii_df):
        decision = PIIDecision(
            pii_type="phone", column="手机号", action="mask_partial"
        )
        detector.apply_decision(pii_df, decision)
        assert len(detector.decisions) == 1
        assert detector.decisions.decisions[0].pii_type == "phone"

    def test_apply_on_missing_column(self, detector, pii_df):
        decision = PIIDecision(
            pii_type="phone", column="不存在的列", action="mask_partial"
        )
        df_out = detector.apply_decision(pii_df, decision)
        # 不应报错，返回原 DataFrame
        assert len(df_out) == len(pii_df)

    def test_original_df_unchanged(self, detector, pii_df):
        original_phone = pii_df["手机号"].iloc[0]
        decision = PIIDecision(
            pii_type="phone", column="手机号", action="mask_partial"
        )
        detector.apply_decision(pii_df, decision)
        # 原始 DataFrame 不应被修改
        assert pii_df["手机号"].iloc[0] == original_phone


# ── 格式化报告 ──


class TestFormatReport:
    """交互报告格式化"""

    def test_report_with_pii(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        report = detector.format_scan_report(result)
        assert "敏感信息检测报告" in report
        assert "检测到" in report
        assert "处理选项" in report

    def test_report_no_pii(self, detector, clean_df):
        result = detector.scan_dataframe(clean_df)
        report = detector.format_scan_report(result)
        assert "未检测到" in report

    def test_report_contains_findings(self, detector, pii_df):
        result = detector.scan_dataframe(pii_df)
        report = detector.format_scan_report(result)
        assert "身份证号" in report or "id_card" in report
