#!/usr/bin/env python3
"""
MSRA 代码包生成器

创建包含所有分析代码的可执行包，支持依赖管理和运行说明。
用于数据共享包生成。
"""

import os
import json
import shutil
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # fallback for Python < 3.11
    except ImportError:
        tomllib = None


class CodePackageGenerator:
    """代码包生成器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化生成器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            project_root = os.getcwd()
        
        self.project_root = Path(project_root)
    
    def create_code_package(self, 
                           code_files: List[str],
                           output_dir: str,
                           include_data: bool = False,
                           data_files: List[str] = None) -> str:
        """
        创建代码包
        
        Args:
            code_files: 代码文件路径列表
            output_dir: 输出目录
            include_data: 是否包含数据
            data_files: 数据文件路径列表
            
        Returns:
            代码包路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建目录结构
        dirs = ["R", "python", "data", "docs", "results"]
        for dir_name in dirs:
            (output_path / dir_name).mkdir(exist_ok=True)
        
        # 复制代码文件
        r_files = []
        python_files = []
        
        for code_file in code_files:
            if not os.path.exists(code_file):
                continue
            
            file_path = Path(code_file)
            
            if file_path.suffix == ".R":
                dest_path = output_path / "R" / file_path.name
                r_files.append(file_path.name)
            elif file_path.suffix == ".py":
                dest_path = output_path / "python" / file_path.name
                python_files.append(file_path.name)
            else:
                dest_path = output_path / "docs" / file_path.name
            
            shutil.copy2(code_file, dest_path)
        
        # 复制数据文件（如果需要）
        if include_data and data_files:
            for data_file in data_files:
                if os.path.exists(data_file):
                    dest_path = output_path / "data" / Path(data_file).name
                    shutil.copy2(data_file, dest_path)
        
        # 生成依赖清单
        self._generate_requirements(output_path, r_files, python_files)
        
        # 生成运行说明
        self._generate_readme(output_path, r_files, python_files, include_data)
        
        # 生成环境配置
        self._generate_environment_config(output_path)
        
        return str(output_path)
    
    def _generate_requirements(self, output_path: Path, 
                             r_files: List[str], python_files: List[str]):
        """生成依赖清单"""
        # R依赖
        if r_files:
            r_requirements = self._detect_r_dependencies(r_files)
            r_req_path = output_path / "R" / "requirements.R"
            
            with open(r_req_path, 'w', encoding='utf-8') as f:
                f.write("# R 依赖包\n")
                f.write("# 运行此脚本安装所有依赖\n\n")
                f.write("required_packages <- c(\n")
                for i, pkg in enumerate(r_requirements):
                    f.write(f'  "{pkg}"')
                    if i < len(r_requirements) - 1:
                        f.write(",")
                    f.write("\n")
                f.write(")\n\n")
                f.write("# 安装缺失的包\n")
                f.write("for (pkg in required_packages) {\n")
                f.write("  if (!requireNamespace(pkg, quietly = TRUE)) {\n")
                f.write(f'    install.packages("{pkg}")\n')
                f.write("  }\n")
                f.write("}\n")
        
        # Python依赖
        if python_files:
            python_requirements = self._detect_python_dependencies(python_files)
            python_req_path = output_path / "python" / "requirements.txt"
            
            with open(python_req_path, 'w', encoding='utf-8') as f:
                f.write("# Python 依赖包\n")
                f.write("# 运行: pip install -r requirements.txt\n\n")
                for pkg in python_requirements:
                    f.write(f"{pkg}\n")
    
    def _detect_r_dependencies(self, r_files: List[str]) -> List[str]:
        """检测R依赖"""
        dependencies = set()
        
        # 常见R包
        common_packages = [
            "survival", "ggplot2", "dplyr", "tidyr", "readr", "jsonlite",
            "gtsummary", "table1", "forestplot", "survminer", "km.ci",
            "car", "lmtest", "sandwich", "multiwayvcov", "clubSandwich",
            "mice", "missForest", "VIM", "naniar", "visdat",
            "pROC", "ROCR", "rms", "dcurves"
        ]
        
        for r_file in r_files:
            try:
                with open(r_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 检测library()调用
                    import re
                    library_calls = re.findall(r'library\((\w+)\)', content)
                    dependencies.update(library_calls)
                    
                    # 检测require()调用
                    require_calls = re.findall(r'require\((\w+)\)', content)
                    dependencies.update(require_calls)
                    
                    # 检测::调用
                    namespace_calls = re.findall(r'(\w+)::', content)
                    dependencies.update(namespace_calls)
                    
            except Exception as e:
                print(f"检测R依赖失败 {r_file}: {e}")
        
        # 添加常见依赖
        dependencies.update(common_packages)
        
        return sorted(list(dependencies))
    
    def _detect_python_dependencies(self, python_files: List[str]) -> List[str]:
        """检测Python依赖"""
        dependencies = set()
        
        # 常见Python包
        common_packages = [
            "numpy", "pandas", "scipy", "scikit-learn", "matplotlib",
            "seaborn", "statsmodels", "lifelines", "shap", "xgboost",
            "lightgbm", "catboost", "imbalanced-learn", "feature-engine",
            "plotly", "altair", "streamlit", "dash"
        ]
        
        for python_file in python_files:
            try:
                with open(python_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 检测import语句
                    import re
                    import_statements = re.findall(r'import\s+(\w+)', content)
                    dependencies.update(import_statements)
                    
                    # 检测from...import语句
                    from_import_statements = re.findall(r'from\s+(\w+)', content)
                    dependencies.update(from_import_statements)
                    
            except Exception as e:
                print(f"检测Python依赖失败 {python_file}: {e}")
        
        # 添加常见依赖
        dependencies.update(common_packages)
        
        # 过滤掉标准库
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'datetime', 'pathlib', 'typing',
            'collections', 'itertools', 'functools', 'operator', 'math',
            'random', 'string', 'io', 'csv', 'xml', 'html', 'urllib',
            'http', 'email', 'sqlite3', 'dbm', 'gzip', 'zipfile',
            'tarfile', 'shutil', 'glob', 'fnmatch', 'tempfile', 'pickle',
            'copy', 'pprint', 'textwrap', 'difflib', 'enum', 'dataclasses',
            'abc', 'contextlib', 'decimal', 'fractions', 'statistics',
            'hashlib', 'hmac', 'secrets', 'uuid', 'socket', 'ssl',
            'select', 'selectors', 'signal', 'mmap', 'ctypes', 'sysconfig'
        }
        
        dependencies = dependencies - stdlib_modules
        
        return sorted(list(dependencies))
    
    def _generate_readme(self, output_path: Path, 
                        r_files: List[str], python_files: List[str],
                        include_data: bool):
        """生成运行说明"""
        readme_content = f"""# 代码包

> 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 目录结构

```
├── R/                  # R代码文件
├── python/             # Python代码文件
├── data/               # 数据文件（如包含）
├── docs/               # 文档文件
└── results/            # 结果文件（运行后生成）
```

## 运行说明

### R 代码

1. 安装依赖：
```r
source("R/requirements.R")
```

2. 运行分析：
```r
source("R/analysis.R")
```

### Python 代码

1. 安装依赖：
```bash
pip install -r python/requirements.txt
```

2. 运行分析：
```bash
python python/analysis.py
```

## 代码文件

### R 文件
"""
        
        for r_file in r_files:
            readme_content += f"- `{r_file}`\n"
        
        readme_content += "\n### Python 文件\n"
        
        for python_file in python_files:
            readme_content += f"- `{python_file}`\n"
        
        if include_data:
            readme_content += """
## 数据文件

数据文件包含在 `data/` 目录中。

## 注意事项

1. 确保已安装所有依赖
2. 根据需要修改数据路径
3. 检查输出目录权限
"""
        
        readme_content += """
## 环境要求

- R >= 4.0.0（如使用R代码）
- Python >= 3.8（如使用Python代码）
- 操作系统：Windows/Linux/macOS

## 联系方式

如有问题，请联系项目维护者。
"""
        
        readme_path = output_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _generate_environment_config(self, output_path: Path):
        """生成环境配置"""
        # 生成R环境配置
        r_env_path = output_path / "R" / ".Rprofile"
        with open(r_env_path, 'w', encoding='utf-8') as f:
            f.write("# R 环境配置\n")
            f.write("options(repos = c(CRAN = 'https://cloud.r-project.org'))\n")
            f.write("options(stringsAsFactors = FALSE)\n")
        
        # 生成Python环境配置
        python_env_path = output_path / "python" / ".env"
        with open(python_env_path, 'w', encoding='utf-8') as f:
            f.write("# Python 环境配置\n")
            f.write("PYTHONPATH=.\n")
            f.write("PYTHONDONTWRITEBYTECODE=1\n")
        
        # 生成pyproject.toml（手动写入，避免 toml 依赖）
        pyproject_path = output_path / "python" / "pyproject.toml"
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            f.write('[project]\n')
            f.write('name = "msra-analysis"\n')
            f.write('version = "0.1.0"\n')
            f.write('description = "MSRA 分析代码包"\n')
            f.write('requires-python = ">=3.8"\n')
            f.write('dependencies = []\n\n')
            f.write('[build-system]\n')
            f.write('requires = ["setuptools>=42", "wheel"]\n')
            f.write('build-backend = "setuptools.backends._legacy:_Backend"\n')
    
    def verify_code_package(self, package_dir: str) -> Dict[str, Any]:
        """
        验证代码包
        
        Args:
            package_dir: 代码包目录
            
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
        required_dirs = ["R", "python", "data", "docs", "results"]
        for dir_name in required_dirs:
            dir_path = package_path / dir_name
            if dir_path.exists():
                results["files"][dir_name] = list(dir_path.iterdir())
            else:
                results["valid"] = False
                results["issues"].append(f"缺少目录: {dir_name}")
        
        # 检查README
        readme_path = package_path / "README.md"
        if not readme_path.exists():
            results["valid"] = False
            results["issues"].append("缺少README.md")
        
        # 检查依赖文件
        r_req_path = package_path / "R" / "requirements.R"
        python_req_path = package_path / "python" / "requirements.txt"
        
        if not r_req_path.exists() and not python_req_path.exists():
            results["issues"].append("缺少依赖文件")
        
        return results


# 使用示例
if __name__ == "__main__":
    # 创建代码包生成器
    generator = CodePackageGenerator()
    
    # 示例代码文件
    code_files = [
        "analysis/main_analysis.R",
        "analysis/sensitivity_analysis.R",
        "analysis/visualization.py"
    ]
    
    # 创建代码包
    package_path = generator.create_code_package(
        code_files=code_files,
        output_dir="code_package",
        include_data=True,
        data_files=["data/cleaned_data.csv"]
    )
    
    print(f"代码包已创建: {package_path}")
    
    # 验证代码包
    verification_results = generator.verify_code_package(package_path)
    print(f"代码包验证: {'通过' if verification_results['valid'] else '失败'}")
    
    if verification_results['issues']:
        print("问题:")
        for issue in verification_results['issues']:
            print(f"  - {issue}")