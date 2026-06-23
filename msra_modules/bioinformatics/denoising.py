"""
CellBender Denoising - CellBender去噪

BIO-008: CellBender去噪流程
"""

import subprocess
import numpy as np
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class CellBenderDenoiser:
    """CellBender单细胞去噪"""

    def __init__(self,
                 expected_cells: int = 3000,
                 total_droplets: int = 30000,
                 epochs: int = 200):
        """初始化去噪参数

        Args:
            expected_cells: 预期细胞数
            total_droplets: 总液滴数
            epochs: 训练轮数
        """
        self.expected_cells = expected_cells
        self.total_droplets = total_droplets
        self.epochs = epochs

    def check_installation(self) -> bool:
        """检查CellBender是否安装

        Returns:
            是否已安装
        """
        try:
            result = subprocess.run(
                ["cellbender", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_remove_background(self,
                              input_h5: str,
                              output_h5: str,
                              expected_cells: Optional[int] = None,
                              total_droplets: Optional[int] = None) -> Dict:
        """运行背景去除

        Args:
            input_h5: 输入H5文件路径
            output_h5: 输出H5文件路径
            expected_cells: 预期细胞数 (覆盖默认值)
            total_droplets: 总液滴数 (覆盖默认值)

        Returns:
            运行结果字典
        """
        if not self.check_installation():
            raise RuntimeError(
                "CellBender is not installed. "
                "Install with: pip install cellbender"
            )

        input_path = Path(input_h5)
        output_path = Path(output_h5)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_h5}")

        # 构建命令
        cmd = [
            "cellbender", "remove-background",
            "--input", str(input_path),
            "--output", str(output_path),
            "--expected-cells", str(expected_cells or self.expected_cells),
            "--total-droplets", str(total_droplets or self.total_droplets),
            "--epochs", str(self.epochs),
        ]

        logger.info(f"Running CellBender: {' '.join(cmd)}")

        # 运行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1小时超时
        )

        if result.returncode != 0:
            logger.error(f"CellBender failed: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr,
                "stdout": result.stdout
            }

        logger.info(f"CellBender complete, output: {output_path}")
        return {
            "success": True,
            "output_file": str(output_path),
            "stdout": result.stdout
        }

    def load_denoised(self, h5_path: str):
        """加载去噪后的数据

        Args:
            h5_path: H5文件路径

        Returns:
            AnnData对象
        """
        try:
            import scanpy as sc
        except ImportError as e:
            raise ImportError(f"Scanpy is required: {e}")

        adata = sc.read_10x_h5(h5_path)
        logger.info(f"Loaded denoised data: {adata.shape}")
        return adata

    def compare_before_after(self,
                             raw_adata,
                             denoised_adata) -> Dict:
        """比较去噪前后数据

        Args:
            raw_adata: 原始AnnData
            denoised_adata: 去噪后AnnData

        Returns:
            比较结果字典
        """
        import numpy as np

        raw_X = raw_adata.X
        denoised_X = denoised_adata.X

        # 转换为密集矩阵
        if hasattr(raw_X, "toarray"):
            raw_X = raw_X.toarray()
        if hasattr(denoised_X, "toarray"):
            denoised_X = denoised_X.toarray()

        # 计算差异
        diff = denoised_X - raw_X

        return {
            "raw_mean": float(np.mean(raw_X)),
            "denoised_mean": float(np.mean(denoised_X)),
            "raw_std": float(np.std(raw_X)),
            "denoised_std": float(np.std(denoised_X)),
            "mean_difference": float(np.mean(diff)),
            "std_difference": float(np.std(diff)),
            "n_cells_raw": raw_adata.shape[0],
            "n_cells_denoised": denoised_adata.shape[0],
            "n_genes_raw": raw_adata.shape[1],
            "n_genes_denoised": denoised_adata.shape[1],
        }
