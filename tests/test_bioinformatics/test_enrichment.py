"""
Tests for PathwayEnrichment - 通路富集分析测试

使用 mock 数据和 mock gseapy 调用，不需要真实 API。
"""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


# 导入被测模块
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from msra_modules.bioinformatics.enrichment import PathwayEnrichment


class TestPathwayEnrichmentInit:
    """测试 PathwayEnrichment 初始化"""

    def test_default_init(self):
        """测试默认初始化"""
        enricher = PathwayEnrichment()
        assert enricher.organism == "human"
        assert enricher.gene_sets is None
        assert enricher.outdir is None

    def test_custom_init(self):
        """测试自定义参数初始化"""
        enricher = PathwayEnrichment(
            organism="mouse",
            gene_sets="custom.gmt",
            outdir="/tmp/enrichment",
        )
        assert enricher.organism == "mouse"
        assert enricher.gene_sets == "custom.gmt"
        assert enricher.outdir == "/tmp/enrichment"


class TestPathwayEnrichmentGo:
    """测试 GO 富集分析"""

    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment._check_gseapy")
    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment.run_enrichr")
    def test_run_go_bp(self, mock_enrichr, mock_check):
        """测试 GO Biological Process 分析"""
        mock_check.return_value = None
        mock_enrichr.return_value = pd.DataFrame({
            "Term": ["apoptotic process", "cell cycle"],
            "P-value": [0.001, 0.005],
            "Adjusted P-value": [0.01, 0.05],
            "Overlap": ["10/200", "8/150"],
        })

        enricher = PathwayEnrichment(organism="human")
        gene_list = ["TP53", "BRCA1", "EGFR", "MYC", "KRAS"]

        result = enricher.run_go(gene_list, ontology="BP")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "Term" in result.columns
        mock_enrichr.assert_called_once()

    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment._check_gseapy")
    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment.run_enrichr")
    def test_run_go_mf(self, mock_enrichr, mock_check):
        """测试 GO Molecular Function 分析"""
        mock_check.return_value = None
        mock_enrichr.return_value = pd.DataFrame({
            "Term": ["protein binding"],
            "P-value": [0.01],
            "Adjusted P-value": [0.05],
        })

        enricher = PathwayEnrichment(organism="human")
        result = enricher.run_go(["TP53", "BRCA1"], ontology="MF")

        assert isinstance(result, pd.DataFrame)
        # 验证传入了正确的基因集库名称
        call_args = mock_enrichr.call_args
        assert "GO_Molecular_Function" in call_args[1]["gene_sets_library"]

    def test_run_go_invalid_ontology(self):
        """测试无效 GO 本体类型"""
        enricher = PathwayEnrichment(organism="human")
        with pytest.raises(ValueError, match="Invalid ontology"):
            enricher._resolve_go_library("INVALID")


class TestPathwayEnrichmentKegg:
    """测试 KEGG 通路富集分析"""

    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment._check_gseapy")
    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment.run_enrichr")
    def test_run_kegg(self, mock_enrichr, mock_check):
        """测试 KEGG 通路分析"""
        mock_check.return_value = None
        mock_enrichr.return_value = pd.DataFrame({
            "Term": ["Pathway in cancer", "PI3K-Akt signaling"],
            "P-value": [0.001, 0.003],
            "Adjusted P-value": [0.01, 0.03],
        })

        enricher = PathwayEnrichment(organism="human")
        result = enricher.run_kegg(["TP53", "BRCA1", "EGFR"])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2


class TestPathwayEnrichmentEnrichr:
    """测试 Enrichr 通用富集分析"""

    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment._check_gseapy")
    def test_run_enrichr_empty_gene_list(self, mock_check):
        """测试空基因列表"""
        mock_check.return_value = None

        enricher = PathwayEnrichment(organism="human")
        # Need to mock the import inside run_enrichr since _check_gseapy is mocked
        with patch.dict("sys.modules", {"gseapy": MagicMock()}):
            result = enricher.run_enrichr([])

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment._check_gseapy")
    def test_run_enrichr_no_install(self, mock_check):
        """测试 gseapy 未安装"""
        mock_check.side_effect = ImportError("gseapy not installed")

        enricher = PathwayEnrichment(organism="human")
        with pytest.raises(ImportError):
            enricher.run_enrichr(["TP53"])


class TestPathwayEnrichmentGSEA:
    """测试 GSEA 分析"""

    @patch("msra_modules.bioinformatics.enrichment.PathwayEnrichment._check_gseapy")
    def test_run_gsea_empty(self, mock_check):
        """测试空基因排名"""
        mock_check.return_value = None

        enricher = PathwayEnrichment(organism="human")
        with patch.dict("sys.modules", {"gseapy": MagicMock()}):
            result = enricher.run_gsea(pd.Series(dtype=float))

        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestPathwayEnrichmentUtils:
    """测试工具方法"""

    def test_get_top_pathways(self):
        """测试获取 Top N 通路"""
        enricher = PathwayEnrichment()

        results = pd.DataFrame({
            "Term": [f"Pathway_{i}" for i in range(30)],
            "Adjusted P-value": np.random.uniform(0.001, 0.1, 30),
        })

        top = enricher.get_top_pathways(results, n=10)
        assert len(top) == 10

    def test_get_top_pathways_empty(self):
        """测试空结果获取 Top N"""
        enricher = PathwayEnrichment()
        top = enricher.get_top_pathways(pd.DataFrame(), n=10)
        assert top.empty

    def test_export_csv(self, tmp_path):
        """测试导出 CSV"""
        enricher = PathwayEnrichment()

        results = pd.DataFrame({
            "Term": ["Pathway_A", "Pathway_B"],
            "P-value": [0.01, 0.05],
        })

        output_path = str(tmp_path / "enrichment.csv")
        returned_path = enricher.export_results(results, output_path, format="csv")

        assert returned_path == output_path
        # 验证文件内容
        loaded = pd.read_csv(output_path)
        assert len(loaded) == 2
        assert "Term" in loaded.columns

    def test_export_tsv(self, tmp_path):
        """测试导出 TSV"""
        enricher = PathwayEnrichment()

        results = pd.DataFrame({
            "Term": ["Pathway_A"],
            "P-value": [0.01],
        })

        output_path = str(tmp_path / "enrichment.tsv")
        enricher.export_results(results, output_path, format="tsv")

        loaded = pd.read_csv(output_path, sep="\t")
        assert len(loaded) == 1

    def test_export_json(self, tmp_path):
        """测试导出 JSON"""
        enricher = PathwayEnrichment()

        results = pd.DataFrame({
            "Term": ["Pathway_A"],
            "P-value": [0.01],
        })

        output_path = str(tmp_path / "enrichment.json")
        enricher.export_results(results, output_path, format="json")

        import json
        with open(output_path) as f:
            loaded = json.load(f)
        assert len(loaded) == 1

    def test_export_invalid_format(self, tmp_path):
        """测试无效导出格式"""
        enricher = PathwayEnrichment()
        results = pd.DataFrame({"Term": ["A"]})

        with pytest.raises(ValueError, match="Unsupported format"):
            enricher.export_results(results, str(tmp_path / "out.xyz"), format="xyz")

    def test_resolve_kegg_library(self):
        """测试 KEGG 库名解析"""
        enricher = PathwayEnrichment(organism="human")
        lib_name = enricher._resolve_kegg_library()
        assert lib_name == "KEGG_2021_Human"

    def test_resolve_kegg_library_mouse(self):
        """测试小鼠 KEGG 库名"""
        enricher = PathwayEnrichment(organism="mouse")
        lib_name = enricher._resolve_kegg_library()
        assert lib_name == "KEGG_2019_Mouse"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
