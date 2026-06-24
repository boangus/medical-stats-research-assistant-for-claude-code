"""
Pathway Enrichment Analysis - 通路富集分析

提供基于 gseapy 的 GO (BP/MF/CC)、KEGG、GSEA 和 Enrichr 富集分析功能。
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List, Union
import logging

logger = logging.getLogger(__name__)


class PathwayEnrichment:
    """通路富集分析引擎

    基于 gseapy 实现 GO (BP/MF/CC)、KEGG、GSEA 分析。
    支持人类和小鼠物种，可自定义基因集库。

    Usage:
        enricher = PathwayEnrichment(organism="human")

        # GO Biological Process
        go_results = enricher.run_go(gene_list, ontology="BP")

        # KEGG pathways
        kegg_results = enricher.run_kegg(gene_list)

        # GSEA with ranked genes
        gsea_results = enricher.run_gsea(ranked_genes)

        # Custom gene sets library
        enrichr_results = enricher.run_enrichr(gene_list, gene_sets_library="KEGG_2021_Human")
    """

    # 物种名称到 Enrichr 前缀的映射
    _ORGANISM_KEGG_MAP: Dict[str, str] = {
        "human": "hsa",
        "mouse": "mmu",
        "rat": "rno",
        "zebrafish": "dre",
        "fly": "dme",
        "worm": "cel",
        "yeast": "sce",
    }

    _ORGANISM_ENRICHR_SUFFIX: Dict[str, str] = {
        "human": "2023",
        "mouse": "2023",
    }

    # 默认 GO 基因集库名称模板
    _GO_LIBRARY_TEMPLATES: Dict[str, str] = {
        "BP": "GO_Biological_Process_{year}",
        "MF": "GO_Molecular_Function_{year}",
        "CC": "GO_Cellular_Component_{year}",
    }

    def __init__(
        self,
        organism: str = "human",
        gene_sets: Optional[str] = None,
        outdir: Optional[str] = None,
    ):
        """初始化通路富集分析器

        Args:
            organism: 物种名称 ("human", "mouse" 等)
            gene_sets: 自定义 .gmt 基因集文件路径 (可选)
            outdir: 输出目录 (可选)
        """
        self.organism = organism.lower()
        self.gene_sets = gene_sets
        self.outdir = outdir

    def _check_gseapy(self) -> None:
        """检查 gseapy 是否已安装"""
        try:
            import gseapy  # noqa: F401
        except ImportError:
            raise ImportError(
                "gseapy is required for pathway enrichment analysis. "
                "Install with: pip install gseapy"
            )

    def _resolve_go_library(self, ontology: str) -> str:
        """解析 GO 基因集库名称

        Args:
            ontology: GO 本体类型 ("BP", "MF", "CC")

        Returns:
            完整的 Enrichr 基因集库名称
        """
        ontology = ontology.upper()
        if ontology not in self._GO_LIBRARY_TEMPLATES:
            raise ValueError(
                f"Invalid ontology '{ontology}'. Must be one of: BP, MF, CC"
            )
        suffix = self._ORGANISM_ENRICHR_SUFFIX.get(self.organism, "2023")
        return self._GO_LIBRARY_TEMPLATES[ontology].format(year=suffix)

    def _resolve_kegg_library(self) -> str:
        """解析 KEGG 基因集库名称

        Returns:
            完整的 Enrichr KEGG 基因集库名称
        """
        suffix = self._ORGANISM_ENRICHR_SUFFIX.get(self.organism, "2023")
        return f"KEGG_{suffix}"

    def run_enrichr(
        self,
        gene_list: List[str],
        gene_sets_library: str = "GO_Biological_Process_2023",
        cutoff: float = 0.05,
    ) -> pd.DataFrame:
        """运行 Enrichr 富集分析 (Over-Representation Analysis)

        Args:
            gene_list: 基因列表 (gene symbols)
            gene_sets_library: 基因集库名称
            cutoff: FDR 阈值

        Returns:
            DataFrame: Term, Overlap, P-value, Adjusted P-value,
                       Old P-value, Odds Ratio, Combined Score, Genes
        """
        self._check_gseapy()
        import gseapy

        if not gene_list:
            logger.warning("Empty gene list provided, returning empty results")
            return pd.DataFrame()

        try:
            enr = gseapy.enrichr(
                gene_list=gene_list,
                gene_sets=gene_sets_library,
                organism=self.organism,
                outdir=self.outdir,
                cutoff=cutoff,
                no_plot=True,
                verbose=False,
            )

            results = enr.results.copy()

            if results.empty:
                logger.info(
                    f"No significant pathways found (cutoff={cutoff}) "
                    f"for library '{gene_sets_library}'"
                )
            else:
                logger.info(
                    f"Enrichr found {len(results)} significant pathways "
                    f"(cutoff={cutoff}, library='{gene_sets_library}')"
                )

            return results

        except Exception as e:
            logger.error(f"Enrichr analysis failed: {e}")
            raise RuntimeError(f"Enrichr analysis failed: {e}")

    def run_gsea(
        self,
        ranked_genes: pd.Series,
        gene_sets: str = "GO_Biological_Process_2023",
        min_size: int = 15,
        max_size: int = 500,
        permutation_num: int = 100,
    ) -> pd.DataFrame:
        """运行 GSEA 基因集富集分析

        Args:
            ranked_genes: 基因排名序列 (index=gene symbols, values=ranking metric)
            gene_sets: 基因集库名称或 .gmt 文件路径
            min_size: 基因集最小大小
            max_size: 基因集最大大小
            permutation_num: 置换次数

        Returns:
            DataFrame: Term, ES, NES, NOM p-val, FDR q-val, FWER p-val,
                       Tag %, Lead_genes
        """
        self._check_gseapy()
        import gseapy

        if ranked_genes.empty:
            logger.warning("Empty ranked genes provided, returning empty results")
            return pd.DataFrame()

        # 确保排名序列按值排序（降序）
        ranked_genes = ranked_genes.sort_values(ascending=False)

        try:
            pre_res = gseapy.prerank(
                rnk=ranked_genes,
                gene_sets=gene_sets,
                organism=self.organism,
                outdir=self.outdir,
                min_size=min_size,
                max_size=max_size,
                permutation_num=permutation_num,
                no_plot=True,
                seed=42,
                verbose=False,
            )

            results = pre_res.res2d.copy()

            if results.empty:
                logger.info("No significant GSEA results found")
            else:
                # 过滤 FDR < 0.05 的结果
                fdr_col = [c for c in results.columns if "fdr" in c.lower()]
                if fdr_col:
                    sig_mask = results[fdr_col[0]] < 0.05
                    n_sig = sig_mask.sum()
                    logger.info(
                        f"GSEA found {n_sig} significant gene sets (FDR < 0.05)"
                    )

            return results

        except Exception as e:
            logger.error(f"GSEA analysis failed: {e}")
            raise RuntimeError(f"GSEA analysis failed: {e}")

    def run_go(
        self,
        gene_list: List[str],
        ontology: str = "BP",
        cutoff: float = 0.05,
    ) -> pd.DataFrame:
        """运行 GO 富集分析 (便捷方法)

        Args:
            gene_list: 基因列表 (gene symbols)
            ontology: GO 本体类型 ("BP" / "MF" / "CC")
            cutoff: FDR 阈值

        Returns:
            DataFrame: GO 富集结果
        """
        library = self._resolve_go_library(ontology)
        logger.info(f"Running GO enrichment ({ontology}) for {len(gene_list)} genes")
        return self.run_enrichr(gene_list, gene_sets_library=library, cutoff=cutoff)

    def run_kegg(
        self,
        gene_list: List[str],
        cutoff: float = 0.05,
    ) -> pd.DataFrame:
        """运行 KEGG 通路富集分析 (便捷方法)

        Args:
            gene_list: 基因列表 (gene symbols)
            cutoff: FDR 阈值

        Returns:
            DataFrame: KEGG 通路富集结果
        """
        library = self._resolve_kegg_library()
        logger.info(f"Running KEGG enrichment for {len(gene_list)} genes")
        return self.run_enrichr(gene_list, gene_sets_library=library, cutoff=cutoff)

    def get_top_pathways(
        self,
        results: pd.DataFrame,
        n: int = 20,
        sort_by: str = "Adjusted P-value",
    ) -> pd.DataFrame:
        """获取 Top N 通路

        Args:
            results: 富集结果 DataFrame
            n: 返回的通路数
            sort_by: 排序字段

        Returns:
            按指定字段排序的 Top N 结果
        """
        if results.empty:
            return results

        if sort_by not in results.columns:
            # 尝试模糊匹配
            candidates = [
                c for c in results.columns
                if sort_by.lower() in c.lower()
            ]
            if candidates:
                sort_by = candidates[0]
            else:
                logger.warning(
                    f"Column '{sort_by}' not found. "
                    f"Available columns: {list(results.columns)}"
                )
                return results.head(n)

        ascending = "p" in sort_by.lower()
        sorted_results = results.sort_values(sort_by, ascending=ascending)
        return sorted_results.head(n)

    def export_results(
        self,
        results: pd.DataFrame,
        output_path: str,
        format: str = "csv",
    ) -> str:
        """导出富集结果

        Args:
            results: 富集结果 DataFrame
            output_path: 输出文件路径
            format: 输出格式 ("csv" / "json" / "tsv")

        Returns:
            输出文件路径
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if format == "csv":
            results.to_csv(output, index=False)
        elif format == "tsv":
            results.to_csv(output, sep="\t", index=False)
        elif format == "json":
            results.to_json(output, orient="records", indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}. Use csv/tsv/json")

        logger.info(f"Exported enrichment results to {output} (format={format})")
        return str(output)
