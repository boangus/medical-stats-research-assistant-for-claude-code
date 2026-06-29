"""CDISC module exceptions.

异常层级:
    CDISCError (base)
    ├── SDTMParseError         # SDTM XPT 文件解析失败
    ├── SDTMValidationError   # SDTM 数据集不符合标准
    └── ADaMNotFoundError      # ADaM 数据集不存在
"""


class CDISCError(Exception):
    """CDISC 模块基础异常。"""


class SDTMParseError(CDISCError):
    """SDTM XPT 文件解析失败。"""

    def __init__(self, reason: str, file_path: str = "") -> None:
        self.file_path = file_path
        self.reason = reason
        msg = f"SDTM 解析失败: {reason}"
        if file_path:
            msg = f"{msg} (file: {file_path})"
        super().__init__(msg)


class SDTMValidationError(CDISCError):
    """SDTM 数据集不符合标准（如缺少必需变量）。"""

    def __init__(self, reason: str, domain: str = "") -> None:
        self.domain = domain
        self.reason = reason
        msg = f"SDTM 校验失败: {reason}"
        if domain:
            msg = f"{msg} (domain: {domain})"
        super().__init__(msg)


class ADaMNotFoundError(CDISCError):
    """ADaM 数据集不存在。"""

    def __init__(self, adam_name: str) -> None:
        self.adam_name = adam_name
        super().__init__(f"ADaM 数据集 '{adam_name}' 不存在。")
