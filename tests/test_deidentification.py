"""
test_deidentification.py — deidentification.py 单元测试
"""
import pandas as pd
import pytest

from shared.data_sharing.deidentification import DataDeidentifier


@pytest.fixture
def deidentifier():
    return DataDeidentifier()


@pytest.fixture
def phi_df():
    """包含 PHI 的测试数据"""
    return pd.DataFrame({
        "姓名": ["张三", "李四", "王五"],
        "身份证号": ["110101199001011234", "110101199001021234", "110101199001031234"],
        "电话": ["13800138000", "13900139000", "13700137000"],
        "年龄": [25, 30, 35],
        "诊断": ["糖尿病", "高血压", "冠心病"],
        "邮编": ["100001", "100002", "100003"],
        "邮箱": ["test1@example.com", "test2@example.com", "test3@example.com"],
    })


class TestIdentifierDetection:
    """标识符检测测试"""

    def test_detect_name(self, deidentifier, phi_df):
        result = deidentifier.identify_identifiers(phi_df)
        direct_cols = [d["column"] for d in result["direct_identifiers"]]
        assert "姓名" in direct_cols

    def test_detect_id_card(self, deidentifier, phi_df):
        result = deidentifier.identify_identifiers(phi_df)
        direct_types = [d["type"] for d in result["direct_identifiers"]]
        assert "id_card" in direct_types

    def test_detect_phone(self, deidentifier, phi_df):
        result = deidentifier.identify_identifiers(phi_df)
        direct_types = [d["type"] for d in result["direct_identifiers"]]
        assert "phone" in direct_types

    def test_detect_email(self, deidentifier, phi_df):
        result = deidentifier.identify_identifiers(phi_df)
        direct_types = [d["type"] for d in result["direct_identifiers"]]
        assert "email" in direct_types

    def test_detect_zip_code(self, deidentifier, phi_df):
        result = deidentifier.identify_identifiers(phi_df)
        indirect_types = [d["type"] for d in result["indirect_identifiers"]]
        assert "zip_code" in indirect_types

    def test_no_phi_data(self, deidentifier):
        df = pd.DataFrame({"age": [25, 30], "score": [80, 90]})
        result = deidentifier.identify_identifiers(df)
        assert len(result["direct_identifiers"]) == 0


class TestDeidentification:
    """去标识化功能测试"""

    def test_suppress(self, deidentifier, phi_df):
        df_deid, report = deidentifier.deidentify_data(
            phi_df, strategy="suppress",
            columns_to_process=["姓名", "身份证号"]
        )
        assert "姓名" not in df_deid.columns
        assert "身份证号" not in df_deid.columns
        assert "诊断" in df_deid.columns  # 非标识符保留

    def test_hash(self, deidentifier, phi_df):
        df_deid, report = deidentifier.deidentify_data(
            phi_df, strategy="hash",
            columns_to_process=["姓名"],
            salt="test_salt"
        )
        assert "姓名" in df_deid.columns
        # 哈希后不应有原始值
        assert df_deid["姓名"].iloc[0] != "张三"
        # 哈希值长度一致
        assert all(len(str(v)) == 16 for v in df_deid["姓名"])

    def test_hash_deterministic_with_salt(self, deidentifier, phi_df):
        df1, _ = deidentifier.deidentify_data(
            phi_df.copy(), strategy="hash",
            columns_to_process=["姓名"], salt="fixed_salt"
        )
        df2, _ = deidentifier.deidentify_data(
            phi_df.copy(), strategy="hash",
            columns_to_process=["姓名"], salt="fixed_salt"
        )
        assert (df1["姓名"] == df2["姓名"]).all()

    def test_generalize(self, deidentifier, phi_df):
        df_deid, report = deidentifier.deidentify_data(
            phi_df, strategy="generalize",
            columns_to_process=["年龄"]
        )
        # 年龄应被分组
        assert df_deid["年龄"].dtype.name == "category" or df_deid["年龄"].iloc[0] != 25


class TestReport:
    """报告生成测试"""

    def test_report_content(self, deidentifier, phi_df):
        df_deid, report = deidentifier.deidentify_data(
            phi_df, strategy="suppress",
            columns_to_process=["姓名"]
        )
        report_text = deidentifier.generate_deidentification_report(
            phi_df, df_deid, report
        )
        assert "去标识化" in report_text
        assert "姓名" in report_text


class TestSave:
    """保存功能测试"""

    def test_save_csv(self, deidentifier, phi_df, tmp_dir):
        import os
        path = deidentifier.save_deidentified_data(
            phi_df, os.path.join(tmp_dir, "test"), format="csv"
        )
        assert os.path.exists(path)
        loaded = pd.read_csv(path)
        assert len(loaded) == len(phi_df)
