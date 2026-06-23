#!/usr/bin/env python3
"""
MSRA 敏感信息检测引擎

对 DataFrame 进行列名 + 值层面双重扫描，自动识别各类 PII（个人身份信息）。
检测结果以结构化形式返回，支持用户交互式决策和审计日志记录。

用法:
    from shared.privacy import SensitivityDetector

    detector = SensitivityDetector()
    result = detector.scan_dataframe(df)
    for f in result.findings:
        print(f.pii_type, f.column, f.match_count)

    # 用户决策后记录
    detector.decisions.record(PIIDecision(...))
    report = detector.decisions.generate_report()
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .masking_strategies import MaskingStrategies


# ── 数据结构 ──


@dataclass
class PIIFinding:
    """单条 PII 检测结果"""
    pii_type: str          # id_card / phone / email / bank_card / ip / passport / name / address
    severity: str          # critical / warning / info
    column: str            # 所在列名
    match_count: int       # 匹配行数
    sample_values: list    # 前 5 个匹配样本（原始值，由调用方决定是否脱敏展示）
    detection_method: str  # column_name / value_scan / freetext_scan
    description: str = ""  # 人类可读描述


@dataclass
class ScanResult:
    """DataFrame 扫描结果"""
    findings: List[PIIFinding] = field(default_factory=list)
    total_rows: int = 0
    total_columns: int = 0
    scan_time: str = ""
    summary: Dict[str, int] = field(default_factory=dict)

    @property
    def has_pii(self) -> bool:
        return len(self.findings) > 0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")

    def get_findings_by_type(self, pii_type: str) -> List[PIIFinding]:
        return [f for f in self.findings if f.pii_type == pii_type]

    def get_findings_by_column(self, column: str) -> List[PIIFinding]:
        return [f for f in self.findings if f.column == column]

    def to_dict(self) -> dict:
        return {
            "has_pii": self.has_pii,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "scan_time": self.scan_time,
            "summary": self.summary,
            "findings": [
                {
                    "pii_type": f.pii_type,
                    "severity": f.severity,
                    "column": f.column,
                    "match_count": f.match_count,
                    "sample_values": f.sample_values,
                    "detection_method": f.detection_method,
                    "description": f.description,
                }
                for f in self.findings
            ],
        }


@dataclass
class PIIDecision:
    """用户对单条 PII 的处理决策"""
    pii_type: str          # PII 类型
    column: str            # 所在列
    action: str            # mask_partial / mask_full / hash / suppress / keep / redact
    params: dict = field(default_factory=dict)  # 策略参数
    timestamp: str = ""    # 决策时间
    user_confirmed: bool = True  # 是否用户确认


@dataclass
class DecisionLog:
    """决策审计日志"""
    _decisions: List[PIIDecision] = field(default_factory=list)

    def record(self, decision: PIIDecision):
        """记录一条决策"""
        if not decision.timestamp:
            decision.timestamp = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S+00:00"
            )
        self._decisions.append(decision)

    @property
    def decisions(self) -> List[PIIDecision]:
        return list(self._decisions)

    def __len__(self) -> int:
        return len(self._decisions)

    def generate_report(self) -> str:
        """生成 Markdown 格式的审计报告"""
        lines = [
            "# 敏感信息处理审计报告",
            "",
            f"> 生成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"> 决策总数: {len(self._decisions)}",
            "",
            "---",
            "",
            "## 决策记录",
            "",
            "| # | PII 类型 | 所在列 | 处理动作 | 参数 | 决策时间 | 用户确认 |",
            "|---|---------|--------|---------|------|---------|---------|",
        ]

        action_labels = {
            "mask_partial": "部分隐藏",
            "mask_full": "完全隐藏",
            "hash": "哈希替换",
            "suppress": "删除列",
            "keep": "保留原样",
            "redact": "[REDACTED]",
        }

        for i, d in enumerate(self._decisions, 1):
            label = action_labels.get(d.action, d.action)
            params_str = str(d.params) if d.params else "-"
            confirmed = "✅" if d.user_confirmed else "❌"
            lines.append(
                f"| {i} | {d.pii_type} | {d.column} | {label} | "
                f"{params_str} | {d.timestamp} | {confirmed} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "*本报告记录了所有敏感信息的处理决策，确保数据处理过程的可追溯性和合规性。*",
        ])

        return "\n".join(lines)

    def save(self, path: str):
        """保存审计报告到文件"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.generate_report())


# ── PII 正则模式 ──

# 严重程度定义
_SEVERITY_MAP = {
    "id_card": "critical",
    "phone": "critical",
    "email": "warning",
    "bank_card": "critical",
    "ip": "warning",
    "passport": "critical",
    "name": "critical",
    "address": "warning",
}

# 值层面正则（匹配单元格内容）
_VALUE_PATTERNS: Dict[str, re.Pattern] = {
    "id_card": re.compile(
        r"[1-9]\d{5}"           # 6 位地区码
        r"(?:19|20)\d{2}"       # 年份
        r"(?:0[1-9]|1[0-2])"    # 月份
        r"(?:0[1-9]|[12]\d|3[01])"  # 日
        r"\d{3}[\dXx]"          # 顺序码 + 校验码
    ),
    "phone": re.compile(
        r"(?<!\d)"              # 前方非数字
        r"1[3-9]\d{9}"          # 11 位手机号
        r"(?!\d)"               # 后方非数字
    ),
    "email": re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    ),
    "bank_card": re.compile(
        r"(?<!\d)"
        r"[1-9]\d{15,18}"      # 16-19 位银行卡号
        r"(?!\d)"
    ),
    "ip": re.compile(
        r"(?<!\d)"
        r"(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|[01]?\d\d?)"
        r"(?!\d)"
    ),
    "passport": re.compile(
        r"(?<![A-Za-z])"
        r"[A-Z]\d{8}"
        r"(?![A-Za-z])"
    ),
}

# 列名匹配模式（复用 deidentification.py 的模式 + 扩展）
_COLUMN_PATTERNS: Dict[str, List[str]] = {
    "name": [
        r"姓名", r"name", r"patient.*name", r"患者.*姓名", r"受试者.*姓名",
    ],
    "id_card": [
        r"身份证", r"id.*card", r"身份证号", r"证件号", r"公民身份号码",
    ],
    "phone": [
        r"电话", r"手机", r"phone", r"mobile", r"tel", r"联系电话", r"手机号码",
    ],
    "email": [
        r"邮箱", r"email", r"电子邮件", r"邮件地址",
    ],
    "address": [
        r"地址", r"address", r"住址", r"居住地", r"家庭住址", r"通讯地址",
    ],
    "bank_card": [
        r"银行卡", r"bank.*card", r"卡号", r"account.*num", r"账号",
    ],
    "ip": [
        r"IP.*地址", r"ip.*addr",
    ],
}

# 描述模板
_DESCRIPTION_MAP = {
    "id_card": "检测到疑似身份证号码（18 位）",
    "phone": "检测到疑似手机号码（11 位）",
    "email": "检测到疑似电子邮箱地址",
    "bank_card": "检测到疑似银行卡号（16-19 位）",
    "ip": "检测到疑似 IP 地址",
    "passport": "检测到疑似护照号码",
    "name": "列名匹配：可能包含姓名信息",
    "address": "列名匹配：可能包含地址信息",
}


# ── 核心检测器 ──


class SensitivityDetector:
    """敏感信息检测引擎"""

    def __init__(self):
        self.decisions = DecisionLog()

    # ── 列名检测 ──

    def _detect_by_column_name(self, df: pd.DataFrame) -> List[PIIFinding]:
        """通过列名匹配检测标识符列"""
        findings = []
        for col in df.columns:
            col_lower = col.lower()
            for pii_type, patterns in _COLUMN_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, col_lower):
                        findings.append(PIIFinding(
                            pii_type=pii_type,
                            severity=_SEVERITY_MAP.get(pii_type, "warning"),
                            column=col,
                            match_count=int(df[col].notna().sum()),
                            sample_values=self._safe_sample(df[col]),
                            detection_method="column_name",
                            description=_DESCRIPTION_MAP.get(pii_type, f"列名匹配: {pii_type}"),
                        ))
                        break  # 每列每类型只报一次
        return findings

    # ── 值层面扫描 ──

    def _detect_by_value_scan(self, df: pd.DataFrame) -> List[PIIFinding]:
        """扫描每列的值内容，检测 PII"""
        findings = []
        for col in df.columns:
            # 跳过数值型列（身份证号/银行卡可能被读为数值，但正则只匹配字符串）
            col_str = df[col].dropna().astype(str)

            for pii_type, pattern in _VALUE_PATTERNS.items():
                matches = col_str[col_str.str.contains(pattern, regex=True, na=False)]
                if len(matches) > 0:
                    findings.append(PIIFinding(
                        pii_type=pii_type,
                        severity=_SEVERITY_MAP.get(pii_type, "warning"),
                        column=col,
                        match_count=len(matches),
                        sample_values=matches.head(5).tolist(),
                        detection_method="value_scan",
                        description=_DESCRIPTION_MAP.get(pii_type, f"值匹配: {pii_type}"),
                    ))
        return findings

    # ── 自由文本扫描 ──

    def _detect_in_freetext(self, df: pd.DataFrame) -> List[PIIFinding]:
        """扫描文本列（object dtype + 唯一值比例低），检测嵌入的 PII"""
        findings = []
        freetext_cols = []

        for col in df.columns:
            if df[col].dtype != "object":
                continue
            # 文本列特征：平均字符串长度 > 10 或唯一值比例 < 0.8
            sample = df[col].dropna().astype(str)
            if len(sample) == 0:
                continue
            avg_len = sample.str.len().mean()
            unique_ratio = sample.nunique() / len(sample)
            if avg_len > 10 or unique_ratio < 0.8:
                freetext_cols.append(col)

        for col in freetext_cols:
            col_str = df[col].dropna().astype(str)
            for pii_type in ["phone", "id_card", "email"]:
                pattern = _VALUE_PATTERNS[pii_type]
                matches = col_str[col_str.str.contains(pattern, regex=True, na=False)]
                if len(matches) > 0:
                    findings.append(PIIFinding(
                        pii_type=pii_type,
                        severity=_SEVERITY_MAP.get(pii_type, "warning"),
                        column=col,
                        match_count=len(matches),
                        sample_values=matches.head(5).tolist(),
                        detection_method="freetext_scan",
                        description=f"自由文本列中检测到{_DESCRIPTION_MAP.get(pii_type, pii_type)}",
                    ))
        return findings

    # ── 主扫描方法 ──

    def scan_dataframe(self, df: pd.DataFrame) -> ScanResult:
        """扫描整个 DataFrame，返回结构化检测结果

        扫描策略（三层）：
        1. 列名匹配 — 快速识别已知字段名
        2. 值层面扫描 — 正则匹配每列单元格内容
        3. 自由文本扫描 — 对长文本列深度检测嵌入的 PII

        Args:
            df: 待扫描的 DataFrame

        Returns:
            ScanResult 结构化检测结果
        """
        findings = []

        # 三层扫描
        findings.extend(self._detect_by_column_name(df))
        findings.extend(self._detect_by_value_scan(df))
        findings.extend(self._detect_in_freetext(df))

        # 去重：同列同类型只保留 match_count 最大的
        findings = self._deduplicate(findings)

        # 汇总
        summary = {}
        for f in findings:
            summary[f.pii_type] = summary.get(f.pii_type, 0) + f.match_count

        return ScanResult(
            findings=findings,
            total_rows=len(df),
            total_columns=len(df.columns),
            scan_time=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            summary=summary,
        )

    # ── 应用脱敏 ──

    def apply_decision(
        self, df: pd.DataFrame, decision: PIIDecision
    ) -> pd.DataFrame:
        """对 DataFrame 应用一条脱敏决策

        Args:
            df: 原始 DataFrame
            decision: 用户决策

        Returns:
            处理后的 DataFrame
        """
        if decision.column not in df.columns:
            return df

        df = df.copy()

        if decision.action == "suppress":
            df = df.drop(columns=[decision.column])
        elif decision.action == "keep":
            pass  # 不做修改
        else:
            # mask_partial / mask_full / hash / redact
            df[decision.column] = df[decision.column].apply(
                lambda x: MaskingStrategies.apply(
                    str(x), decision.pii_type, decision.action, **decision.params
                )
                if pd.notna(x) else x
            )

        # 记录决策
        self.decisions.record(decision)

        return df

    # ── 交互式报告 ──

    def format_scan_report(self, result: ScanResult) -> str:
        """将扫描结果格式化为人类可读的交互报告

        Args:
            result: 扫描结果

        Returns:
            Markdown 格式报告
        """
        lines = [
            "# 敏感信息检测报告",
            "",
            f"> 扫描时间: {result.scan_time}",
            f"> 数据规模: {result.total_rows} 行 × {result.total_columns} 列",
            "",
        ]

        if not result.has_pii:
            lines.append("✅ **未检测到敏感个人信息**")
            lines.append("")
            return "\n".join(lines)

        lines.append(f"⚠️ **检测到 {len(result.findings)} 类敏感信息**")
        lines.append("")

        # 汇总表
        lines.extend([
            "## 检测汇总",
            "",
            "| PII 类型 | 匹配数量 | 严重程度 | 所在列 | 检测方式 |",
            "|---------|---------|---------|--------|---------|",
        ])

        severity_labels = {"critical": "🔴 严重", "warning": "🟡 警告", "info": "🔵 信息"}
        method_labels = {"column_name": "列名匹配", "value_scan": "值扫描", "freetext_scan": "文本扫描"}

        for f in result.findings:
            sev = severity_labels.get(f.severity, f.severity)
            method = method_labels.get(f.detection_method, f.detection_method)
            lines.append(
                f"| {f.pii_type} | {f.match_count} | {sev} | {f.column} | {method} |"
            )

        lines.append("")

        # 详细发现
        lines.extend([
            "## 详细发现",
            "",
        ])

        for f in result.findings:
            lines.extend([
                f"### {f.description}",
                f"- **类型**: {f.pii_type}",
                f"- **所在列**: `{f.column}`",
                f"- **匹配行数**: {f.match_count}",
                f"- **检测方式**: {method_labels.get(f.detection_method, f.detection_method)}",
                f"- **样本值**: {f.sample_values[:3]}",
                "",
            ])

        # 处理选项说明
        lines.extend([
            "## 处理选项",
            "",
            "请为每种检测到的敏感信息选择处理方式：",
            "",
            "| 选项 | 动作 | 说明 |",
            "|------|------|------|",
            "| 1 | `mask_partial` | 部分隐藏（如 138****8000） |",
            "| 2 | `mask_full` | 完全隐藏（替换为 [REDACTED]） |",
            "| 3 | `hash` | 哈希替换（不可逆） |",
            "| 4 | `suppress` | 删除整列 |",
            "| 5 | `keep` | 保留原样（记录决策） |",
            "",
        ])

        return "\n".join(lines)

    # ── 内部工具 ──

    @staticmethod
    def _safe_sample(series: pd.Series, n: int = 5) -> list:
        """安全获取样本值"""
        try:
            return series.dropna().head(n).tolist()
        except Exception:
            return []

    @staticmethod
    def _deduplicate(findings: List[PIIFinding]) -> List[PIIFinding]:
        """去重：同列同类型保留 match_count 最大的，相同时优先 value_scan"""
        method_priority = {"value_scan": 0, "freetext_scan": 1, "column_name": 2}
        seen = {}
        for f in findings:
            key = (f.column, f.pii_type)
            if key not in seen:
                seen[key] = f
            elif f.match_count > seen[key].match_count:
                seen[key] = f
            elif f.match_count == seen[key].match_count:
                # 相同 match_count 时优先 value_scan（更精确）
                if method_priority.get(f.detection_method, 99) < method_priority.get(seen[key].detection_method, 99):
                    seen[key] = f
        return list(seen.values())
