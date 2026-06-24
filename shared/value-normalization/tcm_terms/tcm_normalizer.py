"""
TCM 术语规范化检测器 (TCM Term Normalizer)

基于 GB/T 16751.2-2023 国家标准，检测中医临床数据中的证候术语变体，
向用户提供标准化建议。

功能:
  1. 检测中医证候术语的后缀变体（心脾两虚 ↔ 心脾两虚证 ↔ 心脾两虚证型）
  2. 检测同义/别称变体（肝气郁结 ↔ 肝郁气滞）
  3. 检测复合证候并拆分建议（"心脾两虚，痰湿内阻"）
  4. 输出规范化日志，供质量门闸消费

用法:
  from tcm_normalizer import TCMTermNormalizer

  normalizer = TCMTermNormalizer()
  results = normalizer.detect_variants(data, column="诊断")
  normalizer.show_summary(results)   # 展示检测结果（供用户确认）
  normalized_data = normalizer.apply(data, results, strategy="merge")
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple

import pandas as pd


class TCMTermNormalizer:
    """中医证候术语规范化器"""

    def __init__(self, mapping_file: Optional[str] = None):
        """
        初始化TCM术语规范化器

        Args:
            mapping_file: GB/T 16751 映射表JSON路径。为None则自动查找默认路径。
        """
        self.mapping = self._load_mapping(mapping_file)
        self.suffix_patterns = self.mapping.get("SUFFIX_PATTERNS", [])
        self.compound_delimiters = self.mapping.get("COMPOUND_DELIMITERS", ["，", ",", "、"])
        self._suffix_regexes = [re.compile(p) for p in self.suffix_patterns]

    def _load_mapping(self, mapping_file: Optional[str]) -> dict:
        """加载GB/T 16751映射表"""
        if mapping_file and os.path.exists(mapping_file):
            with open(mapping_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # 默认路径
        default_path = os.path.join(
            os.path.dirname(__file__), "gb_t16751_syndrome.json"
        )
        if os.path.exists(default_path):
            with open(default_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # 兜底：返回空映射
        return {"TCM_TERM_MAP": {}, "SUFFIX_PATTERNS": [], "COMPOUND_DELIMITERS": []}

    def _strip_tcm_suffix(self, term: str) -> str:
        """去除中医术语的常见后缀"""
        term = term.strip()
        for regex in self._suffix_regexes:
            term = regex.sub("", term)
        return term.strip()

    def _lookup_term(self, term: str) -> Optional[dict]:
        """在标准术语库中查找"""
        term_map = self.mapping.get("TCM_CM_TERM_MAP") or self.mapping.get("TCM_TERM_MAP", {})

        # 1. 精确匹配
        if term in term_map:
            return term_map[term]

        # 2. 去后缀后精确匹配
        stripped = self._strip_tcm_suffix(term)
        if stripped != term and stripped in term_map:
            return term_map[stripped]

        # 3. 模糊匹配：返回所有Levenshtein距离≤2的候选项
        #    预过滤：长度差 > max_distance 的候选项直接跳过，避免无效计算
        candidates = []
        max_dist = 2
        term_len = len(term)
        for key, value in term_map.items():
            if abs(len(key) - term_len) > max_dist:
                continue
            dist = self._levenshtein(term, key)
            if dist <= max_dist:
                candidates.append((key, value, dist))

        if candidates:
            candidates.sort(key=lambda x: x[2])  # 按距离升序
            return {
                "_fuzzy_match": True,
                "_original_term": term,
                "_candidates": [{"standard": c[1]["standard"], "code": c[1].get("code", ""),
                                 "matched_term": c[0], "distance": c[2]} for c in candidates]
            }

        return None

    def _levenshtein(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

    def _split_compound(self, value: str) -> List[str]:
        """拆分复合证候"""
        for delim in self.compound_delimiters:
            if delim in value:
                parts = [p.strip() for p in re.split(re.escape(delim), value)]
                return [p for p in parts if p]
        return [value]

    def _detect_column_variants(self, column: pd.Series, col_name: str) -> List[dict]:
        """
        检测单个列的术语变体

        Returns:
            [{"value": "心脾两虚证型", "count": 3, "suggested": "心脾两虚证",
              "code": "BZW.300", "confidence": "exact"}, ...]
        """
        # 只处理object/string/category类型
        if not pd.api.types.is_object_dtype(column) and \
           not pd.api.types.is_string_dtype(column) and \
           column.dtype.name != 'category':
            return []

        value_counts = column.value_counts()
        variants = []

        for value, count in value_counts.items():
            if pd.isna(value) or not isinstance(value, str):
                continue

            # 拆分复合证候
            terms = self._split_compound(value)

            all_matched = True
            term_findings = []

            for term in terms:
                result = self._lookup_term(term)
                if result is None:
                    all_matched = False
                    term_findings.append({"term": term, "matched": False})
                elif result.get("_fuzzy_match"):
                    term_findings.append({
                        "term": term,
                        "matched": True,
                        "fuzzy": True,
                        "candidates": result["_candidates"]
                    })
                else:
                    term_findings.append({
                        "term": term,
                        "matched": True,
                        "fuzzy": False,
                        "standard": result["standard"],
                        "code": result.get("code", "")
                    })

            # 只要不是全部精确匹配，就记录为变体
            if not all_matched or len(terms) > 1:
                variants.append({
                    "value": value,
                    "count": int(count),
                    "compound": len(terms) > 1,
                    "findings": term_findings,
                    "suggested": term_findings[0].get("standard", value)
                    if term_findings[0].get("matched") else value,
                    "confidence": "exact"
                    if all(m.get("matched") and not m.get("fuzzy") for m in term_findings)
                    else "fuzzy" if any(m.get("matched") for m in term_findings)
                    else "unknown"
                })

        return variants

    def detect_variants(self, data: pd.DataFrame,
                        columns: Optional[List[str]] = None) -> Dict[str, List[dict]]:
        """
        检测DataFrame中所有（或指定）列的TCM术语变体

        Args:
            data: 输入DataFrame
            columns: 要检测的列名列表。为None则检测所有字符列。

        Returns:
            {col_name: [variant_records]}
        """
        if columns is None:
            # 自动选择可能包含TCM术语的列：object/string/category列
            columns = [
                col for col in data.columns
                if pd.api.types.is_object_dtype(data[col])
                or pd.api.types.is_string_dtype(data[col])
                or data[col].dtype.name == 'category'
            ]

        results = {}
        for col in columns:
            variants = self._detect_column_variants(data[col], col)
            if variants:
                results[col] = variants

        return results

    def show_summary(self, results: Dict[str, List[dict]]) -> str:
        """生成检测结果的Markdown摘要（供用户确认）"""
        if not results:
            return "✅ 未检测到TCM术语变体。"

        lines = ["## TCM术语变体检测结果\n"]
        total_variants = 0

        for col, variants in results.items():
            lines.append(f"### 列：{col}\n")
            lines.append("| 原始值 | 出现次数 | 建议标准化值 | 匹配类型 |")
            lines.append("|--------|---------|-------------|---------|")

            for v in variants:
                confidence_mark = {
                    "exact": "✅ 精确",
                    "fuzzy": "⚠️ 模糊",
                    "unknown": "❌ 未匹配"
                }.get(v["confidence"], "❓")
                lines.append(
                    f"| {v['value']} | {v['count']} | {v['suggested']} | {confidence_mark} |"
                )
                total_variants += 1

            lines.append("")

        lines.append(f"\n> 共发现 {total_variants} 个术语变体。请选择处理策略：")
        lines.append("> [1] 按建议值自动合并\n> [2] 逐项确认\n> [3] 保留原值（仅记录，不修改）")

        return "\n".join(lines)

    def apply(self, data: pd.DataFrame, results: Dict[str, List[dict]],
              strategy: str = "merge") -> Tuple[pd.DataFrame, List[dict]]:
        """
        执行术语规范化

        Args:
            data: 原始DataFrame
            results: detect_variants()的输出
            strategy: "merge" | "confirm" | "record"

        Returns:
            (规范化后DataFrame, 规范化日志)
        """
        normalized = data.copy()
        log = []

        for col, variants in results.items():
            if col not in normalized.columns:
                continue

            for v in variants:
                original = v["value"]
                original_count = v["count"]

                if strategy == "merge" and v["confidence"] in ("exact", "fuzzy"):
                    suggested = v["suggested"]
                    # 标准化映射
                    term_map = self.mapping.get("TCM_TERM_MAP", {})
                    stripped = self._strip_tcm_suffix(suggested)
                    standard_entry = term_map.get(stripped) or term_map.get(suggested)
                    standard_name = standard_entry["standard"] if standard_entry else suggested
                    standard_code = standard_entry.get("code", "") if standard_entry else ""

                    mask = normalized[col] == original
                    normalized.loc[mask, col] = standard_name

                    log.append({
                        "column": col,
                        "original_value": original,
                        "normalized_value": standard_name,
                        "code": standard_code,
                        "strategy": "merge",
                        "records_affected": original_count,
                        "confidence": v["confidence"],
                        "reason": "GB/T 16751.2 术语规范化"
                    })

                elif strategy == "record":
                    log.append({
                        "column": col,
                        "original_value": original,
                        "normalized_value": original,
                        "code": "",
                        "strategy": "record_only",
                        "records_affected": original_count,
                        "confidence": v["confidence"],
                        "reason": "用户选择仅记录，不修改"
                    })

        return normalized, log
