# Troubleshooting 故障排除指南

> **版本**: v1.0.0 | **更新日期**: 2026-06-26

---

## 常见问题

### 1. 安装问题

#### 1.1 Python 版本不兼容

**症状**:
```
ERROR: Package 'xxx' requires Python '>=3.10' but the running Python is 3.9.x
```

**解决方案**:
```bash
# 检查当前 Python 版本
python --version

# 推荐使用 Python 3.11 或 3.12
# 使用 pyenv (Mac/Linux)
pyenv install 3.12.0
pyenv local 3.12.0

# Windows: 从 python.org 下载安装 Python 3.12
```

#### 1.2 pip 安装失败

**症状**:
```
ERROR: Could not install packages due to an EnvironmentError
```

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用用户目录安装
pip install --user -r requirements.txt

# 或使用虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### 1.3 依赖冲突

**症状**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**解决方案**:
```bash
# 查看冲突的包
pip check

# 升级冲突的包
pip install --upgrade xxx

# 如果仍然冲突，使用虚拟环境隔离
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 2. 可选依赖问题

#### 2.1 harmonypy 安装失败 (Windows)

**症状**:
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**原因**: harmonypy 需要 CMake 编译，Windows 上缺少编译工具。

**解决方案**:
- **方案 A**: 安装 Visual Studio Build Tools
  - 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - 安装 "C++ build tools" 工作负载

- **方案 B**: 跳过 harmonypy（不影响核心功能）
  - harmonypy 仅用于单细胞数据批次校正
  - 其他功能（差异表达、通路富集）正常工作

- **方案 C**: 使用 conda 安装
  ```bash
  conda install -c bioconda harmonypy
  ```

详见: `docs/dev/harmonypy-windows-installation.md`

#### 2.2 pyradiomics 安装失败 (Python 3.13)

**症状**:
```
ERROR: No matching distribution found for pyradiomics
```

**原因**: pyradiomics 尚未发布 Python 3.13 的 wheel。

**解决方案**:
- **方案 A**: 使用 Python 3.12
  ```bash
  pyenv install 3.12.0
  pyenv local 3.12.0
  pip install pyradiomics
  ```

- **方案 B**: 从源码编译
  ```bash
  pip install pyradiomics --no-binary :all:
  ```

- **方案 C**: 跳过 pyradiomics（不影响核心功能）
  - 源码自带的特征提取功能正常工作
  - 仅高级放射组学特征受影响

#### 2.3 dask 未安装

**症状**:
```
ModuleNotFoundError: No module named 'dask'
```

**解决方案**:
```bash
# 安装 dask
pip install "dask[dataframe]>=2024.5.0"

# 或使用完整安装
pip install -r requirements.txt
```

**注意**: dask 仅用于 >100GB 的大规模数据处理。如果您的数据集较小（<10GB），可以使用 Polars 或 DuckDB 引擎。

---

### 3. R 包问题

#### 3.1 R 未安装或版本过低

**症状**:
```
Rscript: command not found
```

**解决方案**:
```bash
# 检查 R 是否安装
R --version

# 推荐 R 4.3+
# 下载: https://cran.r-project.org/
```

#### 3.2 R 包安装失败

**症状**:
```
installation of package 'xxx' had non-zero exit status
```

**解决方案**:
```r
# 设置 CRAN 镜像（中国用户）
options(repos = c(CRAN = "https://mirrors.tuna.tsinghua.edu.cn/CRAN/"))

# 安装系统依赖（Ubuntu/Debian）
# sudo apt-get install r-base-dev libcurl4-openssl-dev libssl-dev

# 安装包
install.packages(c("survival", "tableone", "MatchIt"))
```

#### 3.3 R 脚本执行失败

**症状**:
```
Error in source("script.R") : script.R not found
```

**解决方案**:
```bash
# 检查 R 脚本路径
ls -la src/shared/templates/*.R

# 确保 R 可执行
which Rscript

# 手动测试 R 脚本
Rscript src/shared/templates/cox_template.R
```

---

### 4. 测试问题

#### 4.1 测试失败

**症状**:
```
FAILED tests/test_xxx.py::TestClass::test_method - AssertionError
```

**解决方案**:
```bash
# 运行单个测试
python -m pytest tests/test_xxx.py::TestClass::test_method -v

# 查看详细错误
python -m pytest tests/test_xxx.py -v --tb=long

# 运行所有测试
python -m pytest tests/ -v
```

#### 4.2 跳过的测试

**症状**:
```
SKIPPED [1] tests/test_dask_engine.py: dask not installed
```

**原因**: 可选依赖未安装，测试被正确跳过。

**解决方案**:
- 安装对应的可选依赖（见第 2 节）
- 或忽略跳过的测试（不影响核心功能）

#### 4.3 测试覆盖率报告

**生成覆盖率报告**:
```bash
# 安装 pytest-cov
pip install pytest-cov

# 运行测试并生成报告
python -m pytest tests/ --cov=shared --cov-report=html

# 查看报告
open htmlcov/index.html  # Mac
start htmlcov/index.html  # Windows
```

---

### 5. Pipeline 问题

#### 5.1 Pipeline 卡住

**症状**: Pipeline 长时间无响应

**解决方案**:
```bash
# 检查 Pipeline 状态
/msra-status

# 查看日志
tail -f debug.log

# 强制停止 Pipeline
# 在 Claude Code 中按 Ctrl+C
```

#### 5.2 质量门闸失败

**症状**:
```
❌ Gate 1.5 (数据质量) BLOCKED: 3 项未通过
```

**解决方案**:
```bash
# 查看门闸详情
/msra-status --verbose

# 根据提示修复问题
# 常见问题：
# - 缺失值 > 20%
# - 异常值未处理
# - 数据类型不一致
```

#### 5.3 产物文件损坏

**症状**:
```
Error: passport.json is corrupted
```

**解决方案**:
```bash
# 备份当前产物
cp -r .msra .msra.backup

# 重新生成产物
/msra --from <stage>

# 或手动修复
# 编辑 .msra/passport.json
```

---

### 6. 性能问题

#### 6.1 内存不足

**症状**:
```
MemoryError: Unable to allocate array
```

**解决方案**:
```bash
# 使用大规模数据引擎
/msra-data --engine polars  # <10GB
/msra-data --engine duckdb  # 10-100GB
/msra-data --engine dask    # >100GB

# 或增加系统内存
# 或使用采样数据进行开发测试
```

#### 6.2 处理速度慢

**症状**: Pipeline 执行时间过长

**解决方案**:
```bash
# 使用更快的引擎
/msra-data --engine polars

# 启用并行处理
/msra-exec --parallel

# 减少数据量（开发阶段）
/msra-data --sample 1000
```

---

### 7. 文档问题

#### 7.1 找不到文档

**文档位置**:
- 用户指南: `docs/user_guide/`
- API 参考: `docs/api/`
- 开发文档: `docs/dev/`
- 故障排除: 本文档

#### 7.2 文档过时

如果发现文档与实际功能不符，请提交 Issue:
- GitHub: https://github.com/boangus/medical-stats-research-assistant-for-claude-code/issues

---

## 获取帮助

### 1. 查看日志

```bash
# 查看调试日志
tail -100 debug.log

# 查看测试日志
python -m pytest tests/ -v --tb=long 2>&1 | tee test_output.log
```

### 2. 运行诊断

```bash
# 检查环境
python -c "import pandas, numpy, scipy, statsmodels; print('Core imports OK')"

# 检查可选依赖
python -c "
try:
    import dask
    print(f'dask: {dask.__version__}')
except ImportError:
    print('dask: not installed')
"

# 检查 R
Rscript -e "R.version.string"
```

### 3. 提交 Issue

如果问题仍未解决，请提交 Issue 并包含:
- 操作系统和版本
- Python 版本
- R 版本（如适用）
- 完整的错误信息
- 复现步骤

**GitHub Issues**: https://github.com/boangus/medical-stats-research-assistant-for-claude-code/issues

---

## 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| `E001` | Python 版本不兼容 | 升级到 Python 3.9+ |
| `E002` | 依赖安装失败 | 检查网络连接，使用镜像源 |
| `E003` | R 包缺失 | 安装对应的 R 包 |
| `E004` | 质量门闸失败 | 查看门闸详情，修复数据问题 |
| `E005` | 内存不足 | 使用大规模数据引擎或增加内存 |
| `E006` | 文件路径错误 | 检查文件路径是否正确 |
| `E007` | 权限不足 | 使用 `--user` 或管理员权限 |
| `E008` | 网络连接失败 | 检查网络连接或使用代理 |

---

> **最后更新**: 2026-06-26
> **维护者**: MSRA Team
