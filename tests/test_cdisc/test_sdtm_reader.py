"""Tests for SDTMReader — read_xpt/list_domains/validate/get_domain."""

import sys
from pathlib import Path

import pandas as pd
import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.cdisc import SDTMReader
from msra_modules.cdisc.exceptions import SDTMParseError, SDTMValidationError

ParseError = SDTMParseError  # alias for clarity


@pytest.fixture
def sample_xpt_path():
    """构造一个最小 DM domain XPT 文件用于测试。"""
    pyreadstat = pytest.importorskip("pyreadstat")
    import tempfile
    import os

    df = pd.DataFrame({
        "STUDYID": ["STUDY001"] * 3,
        "DOMAIN": ["DM"] * 3,
        "USUBJID": ["001", "002", "003"],
        "AGE": [45, 60, 32],
        "SEX": ["M", "F", "M"],
    })

    tmp = tempfile.NamedTemporaryFile(suffix=".xpt", delete=False)
    tmp.close()
    pyreadstat.write_xport(df, tmp.name, table_name="DM", file_format_version=5)
    yield Path(tmp.name)

    os.unlink(tmp.name)


class TestReadXpt:
    def test_read_returns_dict(self, sample_xpt_path):
        reader = SDTMReader()
        domains = reader.read_xpt(sample_xpt_path)
        assert isinstance(domains, dict)
        assert "DM" in domains

    def test_read_domain_dataframe(self, sample_xpt_path):
        reader = SDTMReader()
        domains = reader.read_xpt(sample_xpt_path)
        assert isinstance(domains["DM"], pd.DataFrame)
        assert len(domains["DM"]) == 3


class TestListDomains:
    def test_list_domains(self, sample_xpt_path):
        reader = SDTMReader()
        reader.read_xpt(sample_xpt_path)
        domains = reader.list_domains()
        assert "DM" in domains


class TestValidate:
    def test_validate_valid_dm(self, sample_xpt_path):
        reader = SDTMReader()
        reader.read_xpt(sample_xpt_path)
        # 不抛异常即视为通过
        reader.validate("DM")

    def test_validate_missing_required_var(self):
        """缺少 USUBJID 应抛 SDTMValidationError。"""
        pyreadstat = pytest.importorskip("pyreadstat")
        import tempfile
        import os

        df = pd.DataFrame({
            "STUDYID": ["S1"],
            "DOMAIN": ["DM"],
            # 缺少 USUBJID
            "AGE": [50],
        })
        tmp = tempfile.NamedTemporaryFile(suffix=".xpt", delete=False)
        tmp.close()
        pyreadstat.write_xport(df, tmp.name, table_name="DM", file_format_version=5)
        try:
            reader = SDTMReader()
            reader.read_xpt(tmp.name)
            with pytest.raises(SDTMValidationError):
                reader.validate("DM")
        finally:
            os.unlink(tmp.name)


class TestGetDomain:
    def test_get_existing_domain(self, sample_xpt_path):
        reader = SDTMReader()
        reader.read_xpt(sample_xpt_path)
        df = reader.get_domain("DM")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_get_nonexistent_domain(self, sample_xpt_path):
        reader = SDTMReader()
        reader.read_xpt(sample_xpt_path)
        with pytest.raises(KeyError):
            reader.get_domain("NONEXIST")


class TestParseError:
    def test_invalid_xpt_raises(self, tmp_path):
        fake = tmp_path / "fake.xpt"
        fake.write_bytes(b"not a real xpt file")
        reader = SDTMReader()
        with pytest.raises(ParseError):
            reader.read_xpt(fake)
