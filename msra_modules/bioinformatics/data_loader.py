"""
Single-cell RNA-seq Data Loader - 单细胞数据加载器

BIO-003: 10x Genomics数据导入器
BIO-004: Biopython SeqIO集成
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Union
import logging

logger = logging.getLogger(__name__)


class ScRNASeqLoader:
    """单细胞RNA-seq数据加载器"""

    def __init__(self):
        """初始化加载器"""
        self._adata = None

    def read_10x_mtx(self, mtx_dir: str,
                     var_names: str = "gene_symbols",
                     cache: bool = True):
        """读取10x Genomics MTX格式数据

        Args:
            mtx_dir: 10x输出目录 (包含matrix.mtx, features.tsv, barcodes.tsv)
            var_names: 基因名类型 ("gene_symbols" 或 "gene_ids")
            cache: 是否缓存

        Returns:
            AnnData对象
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(
                f"Scanpy is required: {e}. Install with: pip install scanpy"
            )

        mtx_path = Path(mtx_dir)
        if not mtx_path.exists():
            raise FileNotFoundError(f"Directory not found: {mtx_dir}")

        adata = sc.read_10x_mtx(
            str(mtx_path),
            var_names=var_names,
            cache=cache
        )

        logger.info(f"Loaded 10x data: {adata.shape[0]} cells, {adata.shape[1]} genes")
        self._adata = adata
        return adata

    def read_10x_h5(self, h5_path: str,
                    genome: Optional[str] = None):
        """读取10x Genomics H5格式数据

        Args:
            h5_path: H5文件路径
            genome: 基因组名称 (可选)

        Returns:
            AnnData对象
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        path = Path(h5_path)
        if not path.exists():
            raise FileNotFoundError(f"H5 file not found: {h5_path}")

        adata = sc.read_10x_h5(str(path), genome=genome)
        logger.info(f"Loaded H5 data: {adata.shape[0]} cells, {adata.shape[1]} genes")
        self._adata = adata
        return adata

    def read_csv(self, csv_path: str, **kwargs):
        """读取CSV格式表达矩阵

        Args:
            csv_path: CSV文件路径
            **kwargs: 传递给pandas.read_csv的参数

        Returns:
            AnnData对象
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        df = pd.read_csv(csv_path, **kwargs)
        adata = sc.AnnData(df)
        logger.info(f"Loaded CSV data: {adata.shape[0]} cells, {adata.shape[1]} genes")
        self._adata = adata
        return adata

    def read_fasta(self, fasta_path: str):
        """读取FASTA序列文件 (使用Biopython)

        Args:
            fasta_path: FASTA文件路径

        Returns:
            序列列表
        """
        try:
            from Bio import SeqIO
        except ImportError as e:
            raise ImportError(
                f"Biopython is required: {e}. Install with: pip install biopython"
            )

        path = Path(fasta_path)
        if not path.exists():
            raise FileNotFoundError(f"FASTA file not found: {fasta_path}")

        sequences = list(SeqIO.parse(str(path), "fasta"))
        logger.info(f"Loaded {len(sequences)} sequences from {fasta_path}")
        return sequences

    def get_metadata(self) -> Dict:
        """获取当前数据的元数据

        Returns:
            元数据字典
        """
        if self._adata is None:
            return {"error": "No data loaded"}

        return {
            "n_cells": self._adata.shape[0],
            "n_genes": self._adata.shape[1],
            "obs_columns": list(self._adata.obs.columns),
            "var_columns": list(self._adata.var.columns),
            "is_sparse": hasattr(self._adata.X, "toarray"),
        }


def read_10x_mtx(mtx_dir: str, **kwargs):
    """便捷函数：读取10x MTX数据"""
    loader = ScRNASeqLoader()
    return loader.read_10x_mtx(mtx_dir, **kwargs)
