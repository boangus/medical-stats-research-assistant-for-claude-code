"""SDTM (Study Data Tabulation Model) reader.

读取 SAS XPT 文件，提供 SDTM domain 访问和校验。
依赖: pyreadstat (XPT 解析), pandas
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

from .exceptions import SDTMParseError, SDTMValidationError


# SDTM 各 domain 的必需变量（简化版，仅含最关键的标识变量）
# 完整列表见 SDTMIG (Study Data Tabulation Model Implementation Guide)
_REQUIRED_VARS: Dict[str, List[str]] = {
    "DM": ["STUDYID", "DOMAIN", "USUBJID"],
    "AE": ["STUDYID", "DOMAIN", "USUBJID", "AESEQ"],
    "LB": ["STUDYID", "DOMAIN", "USUBJID", "LBSEQ"],
    "EX": ["STUDYID", "DOMAIN", "USUBJID", "EXTRT"],
    "VS": ["STUDYID", "DOMAIN", "USUBJID", "VSSEQ"],
}


class SDTMReader:
    """SDTM XPT 文件读取器。

    Usage:
        reader = SDTMReader()
        domains = reader.read_xpt("sdtm.xpt")
        df_dm = reader.get_domain("DM")
        reader.validate("DM")
    """

    def __init__(self) -> None:
        self._domains: Dict[str, pd.DataFrame] = {}

    def read_xpt(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """读取 XPT 文件，返回 {domain_name: DataFrame} 映射。

        单个 XPT 文件可包含多个 domain（多个 table/member）。

        Args:
            file_path: XPT 文件路径

        Returns:
            domain -> DataFrame 字典

        Raises:
            SDTMParseError: 文件解析失败（不存在/格式错误）
        """
        try:
            import pyreadstat
        except ImportError as e:
            raise SDTMParseError(
                "pyreadstat 未安装。请运行: pip install pyreadstat",
                file_path=str(file_path),
            ) from e

        path = Path(file_path)
        if not path.exists():
            raise SDTMParseError(
                f"文件不存在: {path}", file_path=str(path)
            )

        try:
            # pyreadstat.read_xport 返回 (df, metadata)
            # 默认即返回 metadata，无需额外参数
            df, meta = pyreadstat.read_xport(str(path))
        except Exception as e:
            raise SDTMParseError(
                f"XPT 文件解析失败: {e}", file_path=str(path)
            ) from e

        domains: Dict[str, pd.DataFrame] = {}
        # 单个 domain 情况
        if isinstance(df, pd.DataFrame):
            domain_name = self._infer_domain_name(df, meta)
            domains[domain_name] = df

        self._domains.update(domains)
        return domains

    def list_domains(self) -> List[str]:
        """列出当前加载的所有 domain 名称。"""
        return list(self._domains.keys())

    def get_domain(self, name: str) -> pd.DataFrame:
        """获取指定 domain 的 DataFrame。

        Raises:
            KeyError: domain 未加载
        """
        if name not in self._domains:
            raise KeyError(
                f"Domain '{name}' 未加载。可用: {self.list_domains()}"
            )
        return self._domains[name]

    def validate(self, domain: str) -> None:
        """校验 domain 是否符合 SDTM 标准（必需变量存在）。

        Args:
            domain: domain 名称（如 "DM"）

        Raises:
            KeyError: domain 未加载
            SDTMValidationError: 缺少必需变量
        """
        df = self.get_domain(domain)
        required = _REQUIRED_VARS.get(domain, [])
        if not required:
            # 未知 domain — 跳过校验
            return

        missing = [v for v in required if v not in df.columns]
        if missing:
            raise SDTMValidationError(
                f"缺少必需变量: {missing}",
                domain=domain,
            )

    def _infer_domain_name(
        self, df: pd.DataFrame, meta: object
    ) -> str:
        """从 DataFrame 或 metadata 推断 domain 名称。"""
        # 优先使用 metadata 中的 table_name / member_name
        for attr in ("table_name", "member_name", "dataset_name"):
            val = getattr(meta, attr, None) if meta else None
            if val:
                return str(val).upper()

        # 其次从 DOMAIN 列取值
        if "DOMAIN" in df.columns and len(df) > 0:
            return str(df["DOMAIN"].iloc[0]).upper()

        # 最后用文件第一列名作 fallback
        return "UNKNOWN"
