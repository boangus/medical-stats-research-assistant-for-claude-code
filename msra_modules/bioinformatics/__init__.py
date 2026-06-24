"""
Bioinformatics Module - 生物信息学模块

提供基于Scanpy和CellBender的单细胞分析功能。
新增通路富集分析 (gseapy)、批次效应校正 (ComBat/Harmony)、质量门闸检查。
"""

from .data_loader import ScRNASeqLoader, read_10x_mtx
from .qc import SingleCellQC
from .analysis import DifferentialExpression, TrajectoryAnalysis, DimensionalityReduction
from .denoising import CellBenderDenoiser
from .visualization import BioVisualizer
from .enrichment import PathwayEnrichment
from .batch_correction import BatchCorrector
from .quality_gates import BioQualityGateChecker

__version__ = "1.1.0"
__all__ = [
    "ScRNASeqLoader",
    "read_10x_mtx",
    "SingleCellQC",
    "DifferentialExpression",
    "TrajectoryAnalysis",
    "DimensionalityReduction",
    "CellBenderDenoiser",
    "BioVisualizer",
    "PathwayEnrichment",
    "BatchCorrector",
    "BioQualityGateChecker",
]
