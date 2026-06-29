"""变量名称标准化模块

提供变量名称标准化和统计结果格式化功能，
用于将原始数据中的非标准命名转换为学术规范名称。

Usage:
    from shared.variable_standardization import VariableStandardizer, StatFormatter

    standardizer = VariableStandardizer()
    df_std = standardizer.standardize_dataframe(df)

    formatter = StatFormatter()
    print(formatter.ci(1.23, 1.05, 1.45))  # "HR=1.23, 95%CI: 1.05-1.45"
"""

from .stat_formatter import StatFormatter
from .variable_standardizer import VariableStandardizer

__all__ = ["VariableStandardizer", "StatFormatter"]
