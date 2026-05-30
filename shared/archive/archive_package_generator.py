#!/usr/bin/env python3
"""
MSRA 存档包生成器

创建完整的存档包，支持长期保存和共享。
用于 Stage 4 报告生成后的存档。
"""

import os
import json
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import pandas as pd


class ArchivePackageGenerator:
    """存档包生成器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化生成器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            project_root = os.getcwd()
        
        self.project_root = Path(project_root)
        self.archive_base_dir = self.project_root / "archive_packages"
        
        # 确保基础目录存在
        self.archive_base_dir.mkdir(exist_ok=True)
    
    def create_archive_package(self, 
                              analysis_results: Dict[str, Any],
                              include_data: bool = True,
                              include_code: bool = True,
                              include_results: bool = True) -> str:
        """
        创建存档包
        
        Args:
            analysis_results: 分析结果字典
            include_data: 是否包含数据
            include_code: 是否包含代码
            include_results: 是否包含结果
            
        Returns:
            存档包路径
        """
        # 创建存档包目录
        archive_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        archive_dir = self.archive_base_dir / archive_name
        archive_dir.mkdir(exist_ok=True)
        
        # 创建存档包结构
        dirs = ["data", "code", "results", "figures", "tables", "docs", "metadata"]
        for dir_name in dirs:
            (archive_dir / dir_name).mkdir(exist_ok=True)
        
        # 生成存档清单
        manifest = self._generate_manifest(analysis_results)
        
        # 复制文件到存档包
        if include_data and "data_paths" in analysis_results:
            self._copy_data_files(analysis_results["data_paths"], archive_dir / "data")
        
        if include_code and "code_paths" in analysis_results:
            self._copy_code_files(analysis_results["code_paths"], archive_dir / "code")
        
        if include_results and "result_paths" in analysis_results:
            self._copy_result_files(analysis_results["result_paths"], archive_dir / "results")
        
        # 复制图表和表格
        if "figure_paths" in analysis_results:
            self._copy_files(analysis_results["figure_paths"], archive_dir / "figures")
        
        if "table_paths" in analysis_results:
            self._copy_files(analysis_results["table_paths"], archive_dir / "tables")
        
        # 复制文档
        if "doc_paths" in analysis_results:
            self._copy_files(analysis_results["doc_paths"], archive_dir / "docs")
        
        # 保存存档清单
        manifest_path = archive_dir / "metadata" / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # 生成README
        self._generate_readme(archive_dir, manifest)
        
        # 生成验证脚本
        self._generate_verification_script(archive_dir, manifest)
        
        return str(archive_dir)
    
    def _generate_manifest(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成存档清单"""
        manifest = {
            "created_at": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "archive_version": "1.0.0",
            "msra_version": "0.6.0",
            "files": {},
            "metadata": {}
        }
        
        # 添加文件信息
        if "data_paths" in analysis_results:
            manifest["files"]["data"] = []
            for data_path in analysis_results["data_paths"]:
                if os.path.exists(data_path):
                    file_info = self._get_file_info(data_path)
                    manifest["files"]["data"].append(file_info)
        
        if "code_paths" in analysis_results:
            manifest["files"]["code"] = []
            for code_path in analysis_results["code_paths"]:
                if os.path.exists(code_path):
                    file_info = self._get_file_info(code_path)
                    manifest["files"]["code"].append(file_info)
        
        if "result_paths" in analysis_results:
            manifest["files"]["results"] = []
            for result_path in analysis_results["result_paths"]:
                if os.path.exists(result_path):
                    file_info = self._get_file_info(result_path)
                    manifest["files"]["results"].append(file_info)
        
        # 添加元数据
        if "sap_path" in analysis_results:
            manifest["metadata"]["sap"] = analysis_results["sap_path"]
        
        if "research_type" in analysis_results:
            manifest["metadata"]["research_type"] = analysis_results["research_type"]
        
        if "report_type" in analysis_results:
            manifest["metadata"]["report_type"] = analysis_results["report_type"]
        
        return manifest
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """获取文件信息"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": f"文件不存在: {file_path}"}
        
        # 计算文件哈希
        file_hash = self._compute_file_hash(file_path)
        
        return {
            "path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "hash": file_hash,
            "hash_algorithm": "sha256"
        }
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """计算文件哈希"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _copy_data_files(self, data_paths: List[str], target_dir: Path):
        """复制数据文件"""
        for data_path in data_paths:
            if os.path.exists(data_path):
                dest_path = target_dir / Path(data_path).name
                shutil.copy2(data_path, dest_path)
    
    def _copy_code_files(self, code_paths: List[str], target_dir: Path):
        """复制代码文件"""
        for code_path in code_paths:
            if os.path.exists(code_path):
                dest_path = target_dir / Path(code_path).name
                shutil.copy2(code_path, dest_path)
    
    def _copy_result_files(self, result_paths: List[str], target_dir: Path):
        """复制结果文件"""
        for result_path in result_paths:
            if os.path.exists(result_path):
                dest_path = target_dir / Path(result_path).name
                shutil.copy2(result_path, dest_path)
    
    def _copy_files(self, file_paths: List[str], target_dir: Path):
        """复制文件列表"""
        for file_path in file_paths:
            if os.path.exists(file_path):
                dest_path = target_dir / Path(file_path).name
                shutil.copy2(file_path, dest_path)
    
    def _generate_readme(self, archive_dir: Path, manifest: Dict[str, Any]):
        """生成README文件"""
        readme_content = f"""# MSRA 存档包

> 创建时间: {manifest['created_at']}
> 项目路径: {manifest['project_root']}
> 存档版本: {manifest['archive_version']}
> MSRA版本: {manifest['msra_version']}

## 目录结构

- `data/`: 原始数据文件
- `code/`: 分析代码
- `results/`: 分析结果
- `figures/`: 图表文件
- `tables/`: 表格文件
- `docs/`: 文档文件
- `metadata/`: 元数据文件

## 文件清单

### 数据文件
"""
        
        if "data" in manifest.get("files", {}):
            for file_info in manifest["files"]["data"]:
                if "error" not in file_info:
                    readme_content += f"- `{file_info['name']}` ({file_info['size']} bytes)\n"
        
        readme_content += "\n### 代码文件\n"
        
        if "code" in manifest.get("files", {}):
            for file_info in manifest["files"]["code"]:
                if "error" not in file_info:
                    readme_content += f"- `{file_info['name']}` ({file_info['size']} bytes)\n"
        
        readme_content += "\n### 结果文件\n"
        
        if "results" in manifest.get("files", {}):
            for file_info in manifest["files"]["results"]:
                if "error" not in file_info:
                    readme_content += f"- `{file_info['name']}` ({file_info['size']} bytes)\n"
        
        readme_content += """
## 使用方法

1. 确保已安装所有依赖
2. 运行分析代码
3. 使用验证脚本检查结果一致性

## 验证

运行 `verify_archive.py` 或 `verify_archive.R` 验证存档包完整性。
"""
        
        readme_path = archive_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _generate_verification_script(self, archive_dir: Path, manifest: Dict[str, Any]):
        """生成验证脚本"""
        # Python验证脚本
        python_script = f"""#!/usr/bin/env python3
\"\"\"
存档包验证脚本

验证存档包的完整性和一致性。
\"\"\"

import json
import hashlib
from pathlib import Path


def compute_file_hash(file_path):
    \"\"\"计算文件哈希\"\"\"
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def verify_archive(archive_dir):
    \"\"\"验证存档包\"\"\"
    archive_dir = Path(archive_dir)
    
    # 读取存档清单
    manifest_path = archive_dir / "metadata" / "manifest.json"
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    print("存档包验证")
    print("=" * 50)
    print(f"创建时间: {{manifest['created_at']}}")
    print(f"项目路径: {{manifest['project_root']}}")
    print()
    
    # 验证文件
    all_valid = True
    
    for category in ["data", "code", "results"]:
        if category in manifest.get("files", {}):
            print(f"{{category.capitalize()}} 文件:")
            for file_info in manifest["files"][category]:
                if "error" in file_info:
                    print(f"  ❌ {{file_info['error']}}")
                    all_valid = False
                else:
                    file_path = archive_dir / category / file_info["name"]
                    if file_path.exists():
                        current_hash = compute_file_hash(file_path)
                        if current_hash == file_info["hash"]:
                            print(f"  ✅ {{file_info['name']}} - 完整")
                        else:
                            print(f"  ❌ {{file_info['name']}} - 哈希不匹配")
                            all_valid = False
                    else:
                        print(f"  ❌ {{file_info['name']}} - 文件缺失")
                        all_valid = False
    
    print()
    if all_valid:
        print("✅ 存档包验证通过")
    else:
        print("❌ 存档包验证失败")
    
    return all_valid


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        archive_dir = sys.argv[1]
    else:
        archive_dir = "."
    
    verify_archive(archive_dir)
"""
        
        python_script_path = archive_dir / "verify_archive.py"
        with open(python_script_path, 'w', encoding='utf-8') as f:
            f.write(python_script)
        
        # R验证脚本
        r_script = f"""# 存档包验证脚本
#
# 验证存档包的完整性和一致性。

#' 验证存档包
#'
#' @param archive_dir 存档包目录
#' @return 是否验证通过
verify_archive <- function(archive_dir) {{
  # 读取存档清单
  manifest_path <- file.path(archive_dir, "metadata", "manifest.json")
  manifest <- jsonlite::fromJSON(manifest_path)
  
  cat("存档包验证\\n")
  cat(rep("=", 50), "\\n", sep = "")
  cat("创建时间:", manifest$created_at, "\\n")
  cat("项目路径:", manifest$project_root, "\\n\\n")
  
  # 验证文件
  all_valid <- TRUE
  
  for (category in c("data", "code", "results")) {{
    if (category %in% names(manifest$files)) {{
      cat(paste0(toupper(category), " 文件:\\n"))
      for (i in 1:nrow(manifest$files[[category]])) {{
        file_info <- manifest$files[[category]][i, ]
        
        if ("error" %in% names(file_info)) {{
          cat(paste0("  ❌ ", file_info$error, "\\n"))
          all_valid <- FALSE
        }} else {{
          file_path <- file.path(archive_dir, category, file_info$name)
          if (file.exists(file_path)) {{
            # 计算文件哈希
            current_hash <- digest::digest(file_path, file = TRUE)
            if (current_hash == file_info$hash) {{
              cat(paste0("  ✅ ", file_info$name, " - 完整\\n"))
            }} else {{
              cat(paste0("  ❌ ", file_info$name, " - 哈希不匹配\\n"))
              all_valid <- FALSE
            }}
          }} else {{
            cat(paste0("  ❌ ", file_info$name, " - 文件缺失\\n"))
            all_valid <- FALSE
          }}
        }}
      }}
    }}
  }}
  
  cat("\\n")
  if (all_valid) {{
    cat("✅ 存档包验证通过\\n")
  }} else {{
    cat("❌ 存档包验证失败\\n")
  }}
  
  return(all_valid)
}}

# 运行验证
if (!interactive()) {{
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) > 0) {{
    archive_dir <- args[1]
  }} else {{
    archive_dir <- "."
  }}
  
  verify_archive(archive_dir)
}}
"""
        
        r_script_path = archive_dir / "verify_archive.R"
        with open(r_script_path, 'w', encoding='utf-8') as f:
            f.write(r_script)
    
    def verify_archive_package(self, archive_dir: str) -> Dict[str, Any]:
        """
        验证存档包
        
        Args:
            archive_dir: 存档包目录
            
        Returns:
            验证结果字典
        """
        archive_dir = Path(archive_dir)
        
        # 检查存档清单
        manifest_path = archive_dir / "metadata" / "manifest.json"
        if not manifest_path.exists():
            return {"valid": False, "error": "存档清单不存在"}
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception as e:
            return {"valid": False, "error": f"读取存档清单失败: {str(e)}"}
        
        # 验证文件
        verification_results = {
            "valid": True,
            "manifest": manifest,
            "file_checks": [],
            "errors": []
        }
        
        for category in ["data", "code", "results"]:
            if category in manifest.get("files", {}):
                for file_info in manifest["files"][category]:
                    if "error" in file_info:
                        verification_results["valid"] = False
                        verification_results["errors"].append(file_info["error"])
                    else:
                        file_path = archive_dir / category / file_info["name"]
                        if file_path.exists():
                            # 计算当前哈希
                            current_hash = self._compute_file_hash(file_path)
                            if current_hash == file_info["hash"]:
                                verification_results["file_checks"].append({
                                    "file": file_info["name"],
                                    "status": "valid"
                                })
                            else:
                                verification_results["valid"] = False
                                verification_results["file_checks"].append({
                                    "file": file_info["name"],
                                    "status": "hash_mismatch",
                                    "expected": file_info["hash"],
                                    "actual": current_hash
                                })
                                verification_results["errors"].append(f"文件哈希不匹配: {file_info['name']}")
                        else:
                            verification_results["valid"] = False
                            verification_results["file_checks"].append({
                                "file": file_info["name"],
                                "status": "missing"
                            })
                            verification_results["errors"].append(f"文件缺失: {file_info['name']}")
        
        return verification_results


# 使用示例
if __name__ == "__main__":
    # 创建生成器
    generator = ArchivePackageGenerator()
    
    # 示例分析结果
    analysis_results = {
        "data_paths": ["data/raw_data.csv", "data/cleaned_data.csv"],
        "code_paths": ["analysis/main_analysis.py", "analysis/sensitivity_analysis.py"],
        "result_paths": ["results/main_results.json", "results/sensitivity_results.json"],
        "figure_paths": ["figures/km_curve.png", "figures/forest_plot.png"],
        "table_paths": ["tables/table1.docx", "tables/table2.docx"],
        "doc_paths": ["docs/methods.md", "docs/results.md"],
        "sap_path": "sap/statistical_analysis_plan.md",
        "research_type": "RCT",
        "report_type": "CONSORT"
    }
    
    # 创建存档包
    archive_path = generator.create_archive_package(analysis_results)
    print(f"存档包已创建: {archive_path}")
    
    # 验证存档包
    verification_result = generator.verify_archive_package(archive_path)
    print(f"存档包验证: {'通过' if verification_result['valid'] else '失败'}")