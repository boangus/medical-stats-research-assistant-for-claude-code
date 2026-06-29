"""Terminology module exceptions.

异常层级:
    TerminologyError (base)
    ├── ICD10LookupError          # 编码查询失败
    └── ICD10DataNotFoundError    # 字典数据文件缺失
"""


class TerminologyError(Exception):
    """术语模块基础异常。"""


class ICD10LookupError(TerminologyError):
    """ICD-10 编码查询失败。"""


class ICD10DataNotFoundError(TerminologyError):
    """ICD-10 字典数据文件缺失。"""

    def __init__(self, data_path: str) -> None:
        self.data_path = data_path
        super().__init__(
            f"ICD-10-CM 数据文件未找到: {data_path}. "
            f"请运行 python scripts/download_icd10_cm.py 下载字典。"
        )
