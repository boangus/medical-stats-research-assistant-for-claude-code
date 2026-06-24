# harmonypy Windows 安装指南

> **版本**: v1.0 | **日期**: 2026-06-25 | **状态**: Active
> **适用范围**: MSRA bioinformatics 模块 (BatchCorrector Harmony 校正)
> **平台**: Windows 10/11, Python 3.9+

---

## 1. 问题背景

`harmonypy` 是用于单细胞数据批次效应校正的 Python 包，MSRA 的 `bioinformatics` 模块通过 `BatchCorrector.run_harmony()` 调用。

在 Windows 上，`harmonypy` 依赖 CMake/nmake 进行 C 扩展编译。由于 Windows 默认缺少 CMake 构建环境，`pip install harmonypy` 通常失败，错误信息类似：

```
*** CMake configuration failed
ERROR: Failed building wheel for harmonypy
```

### 影响范围

| 影响项 | 说明 |
|--------|------|
| **受影响功能** | `BatchCorrector.run_harmony()` — Harmony 批次校正 |
| **不受影响功能** | `BatchCorrector.run_combat()` — ComBat 校正不依赖 harmonypy |
| **测试影响** | 单元测试中使用 `@patch` 模拟 harmonypy 调用，不依赖真实安装 |
| **CI 策略** | CI 在 Linux (Ubuntu) 上运行，`pip install harmonypy` 可直接成功 |

---

## 2. 三层降级方案

### 方案一（首选）：Conda 安装

**适用条件**: 已安装 Anaconda 或 Miniconda

```bash
# 方法 A: conda-forge 频道安装
conda install -c conda-forge harmonypy

# 方法 B: bioconda 频道安装
conda install -c bioconda harmonypy

# 验证安装
python -c "import harmonypy; print('harmonypy OK')"
```

**优点**: 预编译二进制，无需 CMake，安装快速可靠
**缺点**: 需要安装 conda 环境

### 方案二（次选）：预编译 Wheel 安装

**适用条件**: 未安装 conda，但有可用的预编译 wheel

```bash
# 尝试直接安装（某些 Python 版本有预编译 wheel）
pip install harmonypy

# 如果失败，尝试 --only-binary 标志
pip install harmonypy --only-binary :all:

# 从 GitHub Releases 下载对应 Python 版本的 wheel
# 访问: https://github.com/slowkow/harmonypy/releases
# 下载 .whl 文件后本地安装
pip install harmonypy-X.X.X-cpXX-cpXX-win_amd64.whl
```

**优点**: 无需 conda
**缺点**: 预编译 wheel 可能不覆盖所有 Python 版本

### 方案三（兜底）：WSL (Windows Subsystem for Linux) 安装

**适用条件**: 无 conda 且无预编译 wheel

```bash
# 1. 安装 WSL (以管理员身份运行 PowerShell)
wsl --install -d Ubuntu-22.04

# 2. 在 WSL 中安装 Python 和 harmonypy
wsl
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 -m pip install harmonypy

# 3. 在 WSL 中运行需要 harmonypy 的 MSRA 命令
cd /mnt/d/开发/medical-stats-research-assistant
python3 -m pip install -e ".[bioinformatics]"
python3 -c "import harmonypy; print('harmonypy OK')"
```

**优点**: Linux 环境下编译无障碍
**缺点**: 需要 WSL 环境，开发体验略有不便

---

## 3. 替代方案：使用 ComBat 校正

如果无法安装 harmonypy，可使用 MSRA 内置的 ComBat 批次校正方法作为替代：

```python
from msra_modules.bioinformatics import BatchCorrector

# 使用 ComBat 而非 Harmony
corrector = BatchCorrector(batch_key="batch", method="combat")
corrector.run_combat(adata)
```

ComBat 不依赖 harmonypy，使用 `scanpy` 内置的 ComBat 实现，在 Windows 上可直接运行。

---

## 4. 故障排查

### 4.1 CMake 未找到

```
CMake Error: CMAKE_C_COMPILER not set
```

**解决**: 安装 CMake 和 Visual Studio Build Tools

```bash
# 安装 CMake
pip install cmake

# 或通过 Chocolatey
choco install cmake

# 安装 Visual Studio Build Tools (C++ 桌面开发工作负载)
# 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

安装后重试 `pip install harmonypy`。

### 4.2 Python 版本不兼容

harmonypy 可能不支持最新的 Python 版本。检查兼容性：

```bash
python --version
pip install harmonypy==0.0.9  # 尝试特定版本
```

### 4.3 验证安装

```python
import harmonypy
print(f"harmonypy version: {harmonypy.__version__}")

# 快速功能测试
import numpy as np
import pandas as pd
# ... 创建测试数据并运行 harmony ...
```

---

## 5. CI/CD 策略

| 环境 | 安装方式 | 预期结果 |
|------|---------|---------|
| **CI (Linux)** | `pip install harmonypy` | ✅ 成功 |
| **CI (Windows)** | `pip install harmonypy` | ❌ 可能失败 |
| **本地开发 (Windows + conda)** | `conda install -c conda-forge harmonypy` | ✅ 成功 |
| **本地开发 (Windows + 纯 pip)** | 使用 ComBat 替代 或 WSL | ✅ 可用 |

**推荐 CI 配置**:
```yaml
# .github/workflows/test.yml
jobs:
  test-linux:
    runs-on: ubuntu-latest
    steps:
      - run: pip install -e ".[experimental,dev]"  # harmonypy 直接安装
  
  test-windows:
    runs-on: windows-latest
    steps:
      - run: pip install -e ".[experimental,dev]"  # harmonypy 可能失败，测试使用 mock
```

---

## 6. 当前环境状态

| 依赖 | 版本 | 状态 | 安装方式 |
|------|------|------|---------|
| nibabel | 5.4.2 | ✅ 已安装 | pip |
| SimpleITK | 2.5.5 | ✅ 已安装 | pip |
| gseapy | 1.3.0 | ✅ 已安装 | pip |
| anndata | 0.12.18 | ✅ 已安装 | pip |
| scanpy | 1.12.1 | ✅ 已安装 | pip |
| scikit-image | 0.26.0 | ✅ 已安装 | pip |
| harmonypy | — | ❌ 未安装 | CMake 编译失败，无 conda |
| pyradiomics | — | ❌ 未安装 | 无 Python 3.13 预编译 wheel |

**当前测试 skip 数**: 0（单元测试使用 `@patch` 模拟 harmonypy 调用，不依赖真实安装）

---

**文档结束**

> MSRA QA Team | 2026-06-25 | harmonypy Windows Installation Guide
