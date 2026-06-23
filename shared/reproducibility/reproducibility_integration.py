#!/usr/bin/env python3
"""
MSRA 可重复性验证集成工具

将reproducibility模块集成到MSRA流水线中，提供自动化验证功能。
用于 Stage 3.5 质量门闸和 Stage 4 报告生成。
"""

import os
import json
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class ReproducibilityIntegrator:
    """可重复性验证集成器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化集成器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            project_root = os.getcwd()
        
        self.project_root = Path(project_root)
        self.reproducibility_dir = self.project_root / "shared" / "reproducibility"
        self.output_dir = self.project_root / "reproducibility_report"
        
        # 确保输出目录存在
        self.output_dir.mkdir(exist_ok=True)
    
    def run_reproducibility_check(self, script_path: str, n_runs: int = 3) -> Dict[str, Any]:
        """
        运行可重复性检查
        
        Args:
            script_path: 分析脚本路径
            n_runs: 运行次数
            
        Returns:
            检查结果字典
        """
        script_path = Path(script_path)
        
        if not script_path.exists():
            return {"error": f"脚本不存在: {script_path}"}
        
        # 根据脚本类型选择检查器
        if script_path.suffix == ".py":
            return self._run_python_check(script_path, n_runs)
        elif script_path.suffix == ".R":
            return self._run_r_check(script_path, n_runs)
        else:
            return {"error": f"不支持的脚本类型: {script_path.suffix}"}
    
    def _run_python_check(self, script_path: Path, n_runs: int) -> Dict[str, Any]:
        """运行Python脚本可重复性检查"""
        try:
            # 导入reproducibility_check模块
            import sys
            sys.path.insert(0, str(self.reproducibility_dir))
            
            from reproducibility_check import ReproducibilityChecker
            
            # 创建检查器
            checker = ReproducibilityChecker(
                script_path=str(script_path),
                n_runs=n_runs,
                output_dir=str(self.output_dir / "python_runs")
            )
            
            # 运行检查
            results = checker.run()
            
            return {
                "script": str(script_path),
                "n_runs": n_runs,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Python检查失败: {str(e)}"}
    
    def _run_r_check(self, script_path: Path, n_runs: int) -> Dict[str, Any]:
        """运行R脚本可重复性检查"""
        try:
            # 创建R脚本进行检查
            r_check_script = f"""
source("{self.reproducibility_dir / 'reproducibility_check.R'}")

# 检查你的分析脚本
check_reproducibility(
  script_path = "{script_path}",
  output_dir = "{self.output_dir / 'r_runs'}",
  n_runs = {n_runs}
)
"""
            
            # 保存并执行R脚本
            r_script_path = self.output_dir / "r_check.R"
            with open(r_script_path, 'w', encoding='utf-8') as f:
                f.write(r_check_script)
            
            # 执行R脚本
            result = subprocess.run(
                ["Rscript", str(r_script_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "script": str(script_path),
                "n_runs": n_runs,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"R检查失败: {str(e)}"}
    
    def generate_environment_report(self) -> Dict[str, Any]:
        """
        生成环境信息报告
        
        Returns:
            环境信息字典
        """
        import platform
        import sys
        
        env_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "python_path": sys.executable,
            "timestamp": datetime.now().isoformat(),
            "working_directory": os.getcwd()
        }
        
        # 尝试获取R版本
        try:
            r_version = subprocess.run(
                ["Rscript", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            env_info["r_version"] = r_version.stderr.strip()
        except Exception:
            env_info["r_version"] = "未检测到R"
        
        # 尝试获取关键包版本
        try:
            import numpy as np
            env_info["numpy_version"] = np.__version__
        except Exception:
            env_info["numpy_version"] = "未安装"
        
        try:
            import pandas as pd
            env_info["pandas_version"] = pd.__version__
        except Exception:
            env_info["pandas_version"] = "未安装"
        
        try:
            import scipy
            env_info["scipy_version"] = scipy.__version__
        except Exception:
            env_info["scipy_version"] = "未安装"
        
        try:
            import sklearn
            env_info["sklearn_version"] = sklearn.__version__
        except Exception:
            env_info["sklearn_version"] = "未安装"
        
        return env_info
    
    def compute_data_fingerprint(self, data_path: str) -> Dict[str, Any]:
        """
        计算数据指纹
        
        Args:
            data_path: 数据文件路径
            
        Returns:
            数据指纹字典
        """
        data_path = Path(data_path)
        
        if not data_path.exists():
            return {"error": f"数据文件不存在: {data_path}"}
        
        # 计算文件哈希
        file_hash = self._compute_file_hash(data_path)
        
        # 读取数据并计算统计指纹
        try:
            if data_path.suffix == ".csv":
                df = pd.read_csv(data_path)
            elif data_path.suffix in [".xlsx", ".xls"]:
                df = pd.read_excel(data_path)
            elif data_path.suffix == ".parquet":
                df = pd.read_parquet(data_path)
            else:
                return {"error": f"不支持的数据格式: {data_path.suffix}"}
            
            # 计算数据指纹
            fingerprint = {
                "file_path": str(data_path),
                "file_hash": file_hash,
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing_counts": df.isnull().sum().to_dict(),
                "numeric_stats": {}
            }
            
            # 计算数值列的统计指纹
            for col in df.select_dtypes(include=['number']).columns:
                fingerprint["numeric_stats"][col] = {
                    "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                    "std": float(df[col].std()) if not df[col].isnull().all() else None,
                    "min": float(df[col].min()) if not df[col].isnull().all() else None,
                    "max": float(df[col].max()) if not df[col].isnull().all() else None,
                    "median": float(df[col].median()) if not df[col].isnull().all() else None
                }
            
            return fingerprint
            
        except Exception as e:
            return {"error": f"数据指纹计算失败: {str(e)}"}
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def generate_verification_report(self, analysis_results: Dict[str, Any]) -> str:
        """
        生成可重复性验证报告
        
        Args:
            analysis_results: 分析结果字典
            
        Returns:
            报告文件路径
        """
        report_content = f"""# 可重复性验证报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 项目路径: {self.project_root}

---

## 1. 环境信息

"""
        
        # 添加环境信息
        env_info = self.generate_environment_report()
        for key, value in env_info.items():
            report_content += f"- **{key}**: {value}\n"
        
        report_content += "\n---\n\n## 2. 数据指纹\n\n"
        
        # 添加数据指纹（如果提供）
        if "data_fingerprints" in analysis_results:
            for data_name, fingerprint in analysis_results["data_fingerprints"].items():
                report_content += f"### {data_name}\n"
                if "error" in fingerprint:
                    report_content += f"- **错误**: {fingerprint['error']}\n"
                else:
                    report_content += f"- **文件哈希**: {fingerprint['file_hash'][:16]}...\n"
                    report_content += f"- **数据形状**: {fingerprint['shape']}\n"
                    report_content += f"- **列数**: {len(fingerprint['columns'])}\n"
                report_content += "\n"
        
        report_content += "\n---\n\n## 3. 可重复性检查结果\n\n"
        
        # 添加检查结果
        if "reproducibility_checks" in analysis_results:
            for check_name, check_result in analysis_results["reproducibility_checks"].items():
                report_content += f"### {check_name}\n"
                if "error" in check_result:
                    report_content += f"- **错误**: {check_result['error']}\n"
                else:
                    report_content += f"- **脚本**: {check_result.get('script', 'N/A')}\n"
                    report_content += f"- **运行次数**: {check_result.get('n_runs', 'N/A')}\n"
                    report_content += f"- **时间戳**: {check_result.get('timestamp', 'N/A')}\n"
                report_content += "\n"
        
        report_content += "\n---\n\n## 4. 总结\n\n"
        
        # 添加总结
        report_content += f"- **验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_content += f"- **项目路径**: {self.project_root}\n"
        report_content += "- **状态**: 验证完成\n"
        
        # 保存报告
        report_path = self.output_dir / f"reproducibility_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)
    
    def create_archive_package(self, analysis_results: Dict[str, Any]) -> str:
        """
        创建存档包
        
        Args:
            analysis_results: 分析结果字典
            
        Returns:
            存档包路径
        """
        archive_dir = self.output_dir / f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        archive_dir.mkdir(exist_ok=True)
        
        # 创建存档包结构
        dirs = ["data", "code", "results", "figures", "tables", "docs"]
        for dir_name in dirs:
            (archive_dir / dir_name).mkdir(exist_ok=True)
        
        # 生成存档清单
        manifest = {
            "created_at": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "files": {}
        }
        
        # 复制关键文件到存档包
        if "analysis_script" in analysis_results:
            script_path = Path(analysis_results["analysis_script"])
            if script_path.exists():
                import shutil
                dest_path = archive_dir / "code" / script_path.name
                shutil.copy2(script_path, dest_path)
                manifest["files"]["analysis_script"] = str(dest_path)
        
        if "data_path" in analysis_results:
            data_path = Path(analysis_results["data_path"])
            if data_path.exists():
                import shutil
                dest_path = archive_dir / "data" / data_path.name
                shutil.copy2(data_path, dest_path)
                manifest["files"]["data"] = str(dest_path)
        
        # 保存存档清单
        manifest_path = archive_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # 生成README
        readme_content = f"""# 存档包

> 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 项目路径: {self.project_root}

## 目录结构

- `data/`: 原始数据文件
- `code/`: 分析代码
- `results/`: 分析结果
- `figures/`: 图表文件
- `tables/`: 表格文件
- `docs/`: 文档文件

## 使用方法

1. 确保已安装所有依赖（见 manifest.json）
2. 运行分析代码
3. 检查结果是否与原始结果一致

## 验证

使用 `reproducibility_check.py` 或 `reproducibility_check.R` 进行验证。
"""
        
        readme_path = archive_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return str(archive_dir)


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 创建集成器
    integrator = ReproducibilityIntegrator()
    
    # 生成环境报告
    env_report = integrator.generate_environment_report()
    logger.info("环境报告:")
    for key, value in env_report.items():
        logger.info(f"  {key}: {value}")
    
    # 创建存档包
    analysis_results = {
        "analysis_script": "analysis/main_analysis.py",
        "data_path": "data/cleaned_data.csv"
    }
    
    archive_path = integrator.create_archive_package(analysis_results)
    logger.info(f"\n存档包已创建: {archive_path}")