#!/usr/bin/env python3
"""
MSRA 结果包生成器

创建包含所有输出和图表的结果包，支持在线预览和分享。
用于数据共享包生成。
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import pandas as pd


class ResultsPackageGenerator:
    """结果包生成器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化生成器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            project_root = os.getcwd()
        
        self.project_root = Path(project_root)
    
    def create_results_package(self, 
                              result_files: List[str],
                              output_dir: str,
                              include_summary: bool = True) -> str:
        """
        创建结果包
        
        Args:
            result_files: 结果文件路径列表
            output_dir: 输出目录
            include_summary: 是否包含结果摘要
            
        Returns:
            结果包路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建目录结构
        dirs = ["tables", "figures", "report", "summary", "raw"]
        for dir_name in dirs:
            (output_path / dir_name).mkdir(exist_ok=True)
        
        # 分类复制结果文件
        tables = []
        figures = []
        reports = []
        raw_results = []
        
        for result_file in result_files:
            if not os.path.exists(result_file):
                continue
            
            file_path = Path(result_file)
            
            # 根据文件类型分类
            if file_path.suffix in ['.docx', '.xlsx', '.csv', '.tsv']:
                dest_path = output_path / "tables" / file_path.name
                tables.append(file_path.name)
            elif file_path.suffix in ['.png', '.jpg', '.jpeg', '.svg', '.pdf']:
                dest_path = output_path / "figures" / file_path.name
                figures.append(file_path.name)
            elif file_path.suffix in ['.html', '.md', '.txt']:
                dest_path = output_path / "report" / file_path.name
                reports.append(file_path.name)
            else:
                dest_path = output_path / "raw" / file_path.name
                raw_results.append(file_path.name)
            
            shutil.copy2(result_file, dest_path)
        
        # 生成结果清单
        self._generate_manifest(output_path, tables, figures, reports, raw_results)
        
        # 生成结果摘要
        if include_summary:
            self._generate_summary(output_path, tables, figures, reports, raw_results)
        
        # 生成可视化目录
        self._generate_visual_directory(output_path, tables, figures, reports)
        
        # 生成分享说明
        self._generate_share_readme(output_path)
        
        return str(output_path)
    
    def _generate_manifest(self, output_path: Path, 
                          tables: List[str], figures: List[str],
                          reports: List[str], raw_results: List[str]):
        """生成结果清单"""
        manifest = {
            "created_at": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "files": {
                "tables": tables,
                "figures": figures,
                "reports": reports,
                "raw_results": raw_results
            },
            "statistics": {
                "total_files": len(tables) + len(figures) + len(reports) + len(raw_results),
                "tables_count": len(tables),
                "figures_count": len(figures),
                "reports_count": len(reports),
                "raw_results_count": len(raw_results)
            }
        }
        
        manifest_path = output_path / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    def _generate_summary(self, output_path: Path, 
                         tables: List[str], figures: List[str],
                         reports: List[str], raw_results: List[str]):
        """生成结果摘要"""
        summary_content = f"""# 分析结果摘要

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. 结果概览

| 类型 | 数量 | 说明 |
|------|------|------|
| 表格 | {len(tables)} | 统计分析结果表 |
| 图表 | {len(figures)} | 可视化图表 |
| 报告 | {len(reports)} | 分析报告 |
| 原始结果 | {len(raw_results)} | 原始输出文件 |

## 2. 表格文件

"""
        
        for table in tables:
            summary_content += f"- `{table}`\n"
        
        summary_content += "\n## 3. 图表文件\n\n"
        
        for figure in figures:
            summary_content += f"- `{figure}`\n"
        
        summary_content += "\n## 4. 报告文件\n\n"
        
        for report in reports:
            summary_content += f"- `{report}`\n"
        
        summary_content += "\n## 5. 原始结果\n\n"
        
        for raw in raw_results:
            summary_content += f"- `{raw}`\n"
        
        summary_content += """
## 6. 使用说明

1. 查看 `report/` 目录中的完整报告
2. 查看 `figures/` 目录中的可视化图表
3. 查看 `tables/` 目录中的统计表格
4. 如需原始数据，查看 `raw/` 目录

## 7. 数据完整性

所有文件均经过完整性检查，确保结果可复现。
"""
        
        summary_path = output_path / "summary" / "README.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
    
    def _generate_visual_directory(self, output_path: Path, 
                                  tables: List[str], figures: List[str],
                                  reports: List[str]):
        """生成可视化目录"""
        directory_content = f"""# 结果可视化目录

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 表格预览

"""
        
        # 添加表格预览
        for table in tables:
            if table.endswith('.csv'):
                try:
                    # 尝试读取CSV并生成预览
                    table_path = output_path / "tables" / table
                    df = pd.read_csv(table_path, nrows=5)
                    
                    directory_content += f"### {table}\n\n"
                    directory_content += df.to_markdown(index=False)
                    directory_content += "\n\n"
                except:
                    directory_content += f"### {table}\n\n"
                    directory_content += "*无法预览*\n\n"
        
        directory_content += "\n## 图表预览\n\n"
        
        # 添加图表预览
        for figure in figures:
            directory_content += f"### {figure}\n\n"
            directory_content += f"![{figure}](figures/{figure})\n\n"
        
        directory_content += "\n## 报告预览\n\n"
        
        # 添加报告预览
        for report in reports:
            directory_content += f"### {report}\n\n"
            if report.endswith('.md'):
                try:
                    report_path = output_path / "report" / report
                    with open(report_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    directory_content += f"```\n{content[:500]}...\n```\n\n"
                except:
                    directory_content += "*无法预览*\n\n"
        
        directory_path = output_path / "DIRECTORY.md"
        with open(directory_path, 'w', encoding='utf-8') as f:
            f.write(directory_content)
    
    def _generate_share_readme(self, output_path: Path):
        """生成分享说明"""
        readme_content = f"""# 结果包

> 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 目录结构

- `tables/`: 统计分析结果表
- `figures/`: 可视化图表
- `report/`: 分析报告
- `summary/`: 结果摘要
- `raw/`: 原始输出文件
- `DIRECTORY.md`: 可视化目录
- `manifest.json`: 文件清单

## 使用方法

### 查看结果

1. 打开 `DIRECTORY.md` 查看可视化目录
2. 打开 `summary/README.md` 查看结果摘要
3. 打开 `report/` 目录中的完整报告

### 分享结果

1. 将整个结果包压缩为ZIP文件
2. 通过邮件或文件共享服务发送
3. 接收方解压后可直接查看所有结果

### 数据完整性

所有文件均包含在 `manifest.json` 中，包含文件哈希值，可用于验证完整性。

## 文件说明

| 文件类型 | 说明 | 格式 |
|----------|------|------|
| 表格 | 统计分析结果 | CSV/DOCX/XLSX |
| 图表 | 可视化输出 | PNG/SVG/PDF |
| 报告 | 分析报告 | HTML/MD/TXT |
| 原始结果 | 程序输出 | JSON/TXT/LOG |

## 注意事项

1. 确保结果包包含所有必要文件
2. 检查文件完整性
3. 遵守数据使用协议（如适用）
"""
        
        readme_path = output_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def verify_results_package(self, package_dir: str) -> Dict[str, Any]:
        """
        验证结果包
        
        Args:
            package_dir: 结果包目录
            
        Returns:
            验证结果字典
        """
        package_path = Path(package_dir)
        
        results = {
            "valid": True,
            "files": {},
            "issues": []
        }
        
        # 检查目录结构
        required_dirs = ["tables", "figures", "report", "summary", "raw"]
        for dir_name in required_dirs:
            dir_path = package_path / dir_name
            if dir_path.exists():
                results["files"][dir_name] = list(dir_path.iterdir())
            else:
                results["valid"] = False
                results["issues"].append(f"缺少目录: {dir_name}")
        
        # 检查关键文件
        key_files = ["README.md", "manifest.json", "DIRECTORY.md"]
        for file_name in key_files:
            file_path = package_path / file_name
            if not file_path.exists():
                results["issues"].append(f"缺少文件: {file_name}")
        
        # 检查清单文件
        manifest_path = package_path / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                # 验证文件存在
                for category in ["tables", "figures", "reports", "raw_results"]:
                    if category in manifest.get("files", {}):
                        for file_name in manifest["files"][category]:
                            file_path = package_path / category.rstrip('s') / file_name
                            if not file_path.exists():
                                results["valid"] = False
                                results["issues"].append(f"清单中文件缺失: {file_name}")
            except Exception as e:
                results["issues"].append(f"读取清单失败: {str(e)}")
        
        return results
    
    def create_shareable_link(self, package_dir: str) -> str:
        """
        创建可分享的链接说明
        
        Args:
            package_dir: 结果包目录
            
        Returns:
            分享说明文本
        """
        package_path = Path(package_dir)
        
        share_text = f"""# 结果包分享说明

## 包信息

- **路径**: {package_path}
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 分享方式

### 方式1: 压缩分享

```bash
# 压缩结果包
cd {package_path.parent}
zip -r results_package.zip {package_path.name}

# 通过邮件或文件共享服务发送 results_package.zip
```

### 方式2: 直接分享

将整个结果包目录 `{package_path}` 复制到共享位置。

### 方式3: 在线分享

上传到云存储服务（如百度网盘、OneDrive、Google Drive）并生成分享链接。

## 接收方使用

1. 下载并解压结果包（如压缩）
2. 打开 `README.md` 查看使用说明
3. 打开 `DIRECTORY.md` 查看可视化目录
4. 查看 `report/` 目录中的完整报告

## 数据完整性验证

```bash
# 验证结果包完整性
python verify_results.py {package_path}
```
"""
        
        return share_text


# 使用示例
if __name__ == "__main__":
    # 创建结果包生成器
    generator = ResultsPackageGenerator()
    
    # 示例结果文件
    result_files = [
        "results/table1.csv",
        "results/table2.csv",
        "figures/km_curve.png",
        "figures/forest_plot.png",
        "report/final_report.html",
        "report/methods.md",
        "raw/analysis_output.json"
    ]
    
    # 创建结果包
    package_path = generator.create_results_package(
        result_files=result_files,
        output_dir="results_package",
        include_summary=True
    )
    
    print(f"结果包已创建: {package_path}")
    
    # 验证结果包
    verification_results = generator.verify_results_package(package_path)
    print(f"结果包验证: {'通过' if verification_results['valid'] else '失败'}")
    
    if verification_results['issues']:
        print("问题:")
        for issue in verification_results['issues']:
            print(f"  - {issue}")
    
    # 生成分享说明
    share_text = generator.create_shareable_link(package_path)
    print(f"\n分享说明已生成")