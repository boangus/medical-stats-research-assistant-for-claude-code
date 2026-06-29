"""Tests for CDISC module exceptions."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.cdisc.exceptions import (
    CDISCError,
    SDTMParseError,
    SDTMValidationError,
    ADaMNotFoundError,
)


def test_cdisc_error_is_exception():
    err = CDISCError("msg")
    assert isinstance(err, Exception)
    assert str(err) == "msg"


def test_exception_hierarchy():
    assert issubclass(SDTMParseError, CDISCError)
    assert issubclass(SDTMValidationError, CDISCError)
    assert issubclass(ADaMNotFoundError, CDISCError)


def test_sdtm_parse_error_with_path():
    err = SDTMParseError("missing domain", file_path="/tmp/dm.xpt")
    assert isinstance(err, CDISCError)
    assert "/tmp/dm.xpt" in str(err)
    assert err.file_path == "/tmp/dm.xpt"


def test_sdtm_validation_error_with_domain():
    err = SDTMValidationError("missing USUBJID", domain="DM")
    assert isinstance(err, CDISCError)
    assert "DM" in str(err)
    assert err.domain == "DM"


def test_adam_not_found_error_with_name():
    err = ADaMNotFoundError("ADSL")
    assert isinstance(err, CDISCError)
    assert "ADSL" in str(err)
    assert err.adam_name == "ADSL"
