"""
Bioinformatics Module - 生物信息学模块

提供基于Scanpy和CellBender的单细胞分析功能。
"""

from .data_loader import ScRNASeqLoader, read_10x_mtx
from .qc import SingleCellQC
from .analysis import DifferentialExpression, TrajectoryAnalysis, DimensionalityReduction
from .denoising import CellBenderDenoiser
from .visualization import BioVisualizer

__version__ = "1.0.0"
__all__ = [
    "ScRNASeqLoader",
    "read_10x_mtx",
    "SingleCellQC",
    "DifferentialExpression",
    "TrajectoryAnalysis",
    "DimensionalityReduction",
    "CellBenderDenoiser",
    "BioVisualizer",
]
