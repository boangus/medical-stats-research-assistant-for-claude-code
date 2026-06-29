"""Tests for ICD10Engine — lookup/validate/search/map_to_chapter/list_chapters."""

import sys
from pathlib import Path

import pytest

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.terminology import ICD10Engine
from shared.terminology.exceptions import ICD10DataNotFoundError


@pytest.fixture
def engine(sample_data_path):
    return ICD10Engine(data_path=sample_data_path)


class TestLookup:
    def test_lookup_existing_code(self, engine):
        concept = engine.lookup("E11.9")
        assert concept is not None
        assert concept.code == "E11.9"
        assert "diabetes" in concept.long_description.lower()

    def test_lookup_returns_none_for_nonexistent(self, engine):
        assert engine.lookup("ZZZ.99") is None

    def test_lookup_hypertension(self, engine):
        concept = engine.lookup("I10")
        assert concept is not None
        assert "hypertension" in concept.short_description.lower()


class TestValidate:
    def test_validate_existing_code(self, engine):
        assert engine.validate("E11.9") is True

    def test_validate_nonexistent_code(self, engine):
        assert engine.validate("ZZZ.99") is False

    def test_validate_empty_string(self, engine):
        assert engine.validate("") is False


class TestSearch:
    def test_search_diabetes(self, engine):
        results = engine.search("diabetes", limit=5)
        assert len(results) > 0
        assert any("diabetes" in r.long_description.lower() for r in results)

    def test_search_hypertension(self, engine):
        results = engine.search("hypertension")
        assert any("hypertension" in r.short_description.lower() for r in results)

    def test_search_limit(self, engine):
        results = engine.search("pain", limit=3)
        assert len(results) <= 3

    def test_search_no_match(self, engine):
        results = engine.search("zzznonexistentxyz")
        assert results == []


class TestMapToChapter:
    def test_map_endocrine(self, engine):
        assert "Endocrine" in engine.map_to_chapter("E11.9")

    def test_map_circulatory(self, engine):
        assert "Circulatory" in engine.map_to_chapter("I10")


class TestListChapters:
    def test_list_chapters_returns_list(self, engine):
        chapters = engine.list_chapters()
        assert isinstance(chapters, list)
        assert len(chapters) >= 10

    def test_list_chapters_contains_endocrine(self, engine):
        chapters = engine.list_chapters()
        assert any("Endocrine" in c for c in chapters)


class TestDataNotFound:
    def test_missing_data_file_raises(self, tmp_path):
        with pytest.raises(ICD10DataNotFoundError):
            ICD10Engine(data_path=tmp_path / "nonexistent.csv")
