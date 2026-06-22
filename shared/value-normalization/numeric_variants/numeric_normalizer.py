"""
数值格式变体检测与规范化器 (Numeric Variant Normalizer)

检测临床数据中常见的非标准数值表示方式，包括:
1. 检测下限标记 (<1.5, 小于1.5, ≤0.05)
2. 检测上限标记 (>200, 大于200)
3. 逗号分隔多值 (1,2,3)
4. 范围表示 (5-10, 3.5~7.2)
5. 中文数字（仅检测，需用户确认）

用法:
  from numeric_normalizer import NumericVariantDetector

  detector = NumericVariantDetector()
  results = detector.detect_variants(df)
  detector.show_summary(results)    # 展示供用户确认
  df, log = detector.apply(df, results, strategies={
      "PSA": {"type": "lower_limit", "strategy": "threshold"},
      "lab_1": {"type": "multi_value", "strategy": "mean"}
  })
"""

import re
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable

# ── 正则模式库 ──────────────────────────────────────────────

# 检测下限（符号）
PATTERN_LOWER_SYMBOL = r"^[<＜]\s*(\d+\.?\d*)\s*$"
PATTERN_LOWER_EQ_SYMBOL = r"^[≤≦]\s*(\d+\.?\d*)\s*$"

# 检测下限（中文）
PATTERN_LOWER_CN = r"^小[于於]\s*(\d+\.?\d*)\s*$"
PATTERN_LOWER_CN_BUDAN = r"^不足\s*(\d+\.?\d*)\s*$"
PATTERN_LOWER_CN_WEIDA = r"^未达\s*(\d+\.?\d*)\s*$"
PATTERN_LOWER_CN_BUGUO = r"^不[超[过]?]\s*(\d+\.?\d*)\s*$"
PATTERN_LOWER_CN_DIYU = r"^[低[于]?]\s*(\d+\.?\d*)\s*$"

# 检测上限（符号）
PATTERN_UPPER_SYMBOL = r"^[>＞]\s*(\d+\.?\d*)\s*$"
PATTERN_UPPER_EQ_SYMBOL = r"^[≥≧]\s*(\d+\.?\d*)\s*$"

# 检测上限（中文）
PATTERN_UPPER_CN = r"^大[于於]\s*(\d+\.?\d*)\s*$"
PATTERN_UPPER_CN_CHAOGUO = r"^超[过]?\s*(\d+\.?\d*)\s*$"
PATTERN_UPPER_CN_BUXIAOYU = r"^不[低[于]?]\s*(\d+\.?\d*)\s*$"

# 逗号多值
PATTERN_COMMA_MULTI = r"^(\d+\.?\d*)\s*[，,]\s*(\d+\.?\d*)(?:\s*[，,]\s*(\d+\.?\d*))*\s*$"
PATTERN_SPACE_MULTI = r"^(\d+\.?\d*)\s+(\d+\.?\d*)\s*$"
PATTERN_SEMICOLON_MULTI = r"^(\d+\.?\d*)\s*[；;]\s*(\d+\.?\d*)\s*$"

# 范围表示
PATTERN_RANGE_HYPHEN = r"^(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)\s*$"
PATTERN_RANGE_TILDE = r"^(\d+\.?\d*)\s*[~～]\s*(\d+\.?\d*)\s*$"
PATTERN_RANGE_CN = r"^(\d+\.?\d*)\s*[至到]\s*(\d+\.?\d*)\s*$"


def _parse_lower_limit(match: re.Match) -> dict:
    """解析检测下限"""
    return {"type": "lower_limit", "threshold": float(match.group(1))}


def _parse_upper_limit(match: re.Match) -> dict:
    """解析检测上限"""
    return {"type": "upper_limit", "threshold": float(match.group(1))}


def _parse_multi_value(match: re.Match) -> dict:
    """解析逗号多值"""
    values = [float(g) for g in match.groups() if g is not None]
    return {"type": "multi_value", "values": values, "n": len(values)}


def _parse_range(match: re.Match) -> dict:
    """解析范围表示"""
    return {"type": "range", "low": float(match.group(1)), "high": float(match.group(2))}


# 模式注册表
PATTERNS: List[Dict[str, Any]] = [
    # 检测下限（符号）
    {"name": "lower_symbol", "regex": PATTERN_LOWER_SYMBOL, "parser": _parse_lower_limit, "category": "detection_limit"},
    {"name": "lower_eq_symbol", "regex": PATTERN_LOWER_EQ_SYMBOL, "parser": _parse_lower_limit, "category": "detection_limit"},
    # 检测下限（中文）
    {"name": "lower_cn", "regex": PATTERN_LOWER_CN, "parser": _parse_lower_limit, "category": "detection_limit"},
    {"name": "lower_cn_budan", "regex": PATTERN_LOWER_CN_BUDAN, "parser": _parse_lower_limit, "category": "detection_limit"},
    {"name": "lower_cn_weida", "regex": PATTERN_LOWER_CN_WEIDA, "parser": _parse_lower_limit, "category": "detection_limit"},
    {"name": "lower_cn_buguo", "regex": PATTERN_LOWER_CN_BUGUO, "parser": _parse_lower_limit, "category": "detection_limit"},
    {"name": "lower_cn_diyu", "regex": PATTERN_LOWER_CN_DIYU, "parser": _parse_lower_limit, "category": "detection_limit"},
    # 检测上限（符号）
    {"name": "upper_symbol", "regex": PATTERN_UPPER_SYMBOL, "parser": _parse_upper_limit, "category": "detection_limit"},
    {"name": "upper_eq_symbol", "regex": PATTERN_UPPER_EQ_SYMBOL, "parser": _parse_upper_limit, "category": "detection_limit"},
    # 检测上限（中文）
    {"name": "upper_cn", "regex": PATTERN_UPPER_CN, "parser": _parse_upper_limit, "category": "detection_limit"},
    {"name": "upper_cn_chaoguo", "regex": PATTERN_UPPER_CN_CHAOGUO, "parser": _parse_upper_limit, "category": "detection_limit"},
    {"name": "upper_cn_buxiaoyu", "regex": PATTERN_UPPER_CN_BUXIAOYU, "parser": _parse_upper_limit, "category": "detection_limit"},
    # 逗号多值
    {"name": "comma_multi", "regex": PATTERN_COMMA_MULTI, "parser": _parse_multi_value, "category": "multi_value"},
    {"name": "space_multi", "regex": PATTERN_SPACE_MULTI, "parser": _parse_multi_value, "category": "multi_value"},
    {"name": "semicolon_multi", "regex": PATTERN_SEMICOLON_MULTI, "parser": _parse_multi_value, "category": "multi_value"},
    # 范围
    {"name": "range_hyphen", "regex": PATTERN_RANGE_HYPHEN, "parser": _parse_range, "category": "range"},
    {"name": "range_tilde", "regex": PATTERN_RANGE_TILDE, "parser": _parse_range, "category": "range"},
    {"name": "range_cn", "regex": PATTERN_RANGE_CN, "parser": _parse_range, "category": "range"},
]


# ── 处理策略 ────────────────────────────────────────────────

STRATEGY_OPTIONS = {
    "lower_limit": {
        "label": "检测下限",
        "options": [
            {"id": "threshold", "label": "设为检测下限值替代",
             "description": "例如 <1.5 → 1.5"},
            {"id": "half", "label": "半限替代",
             "description": "例如 <1.5 → 0.75"},
            {"id": "missing_with_indicator", "label": "设为缺失 + 生成截断指示变量",
             "description": "保留截断信息"},
            {"id": "ordered_cat", "label": "转为有序分类变量",
             "description": "低/正常/高"},
        ]
    },
    "upper_limit": {
        "label": "检测上限",
        "options": [
            {"id": "threshold", "label": "设为检测上限值替代",
             "description": "例如 >200 → 200"},
            {"id": "missing_with_indicator", "label": "设为缺失 + 生成截断指示变量",
             "description": "保留截断信息"},
        ]
    },
    "multi_value": {
        "label": "逗号多值",
        "options": [
            {"id": "mean", "label": "取均值",
             "description": "例如 1,2,3 → 2.0"},
            {"id": "first", "label": "取第一个值",
             "description": "例如 1,2,3 → 1.0"},
            {"id": "mark_anomaly", "label": "标记为异常，建议回查原始记录",
             "description": "最严谨"},
        ]
    },
    "range": {
        "label": "范围表示",
        "options": [
            {"id": "midpoint", "label": "取中点值",
             "description": "例如 5-10 → 7.5"},
            {"id": "mark_anomaly", "label": "标记为异常，建议回查原始记录",
             "description": "范围值不适合直接纳入连续变量分析"},
        ]
    },
}


class NumericVariantDetector:
    """数值格式变体检测与规范化器"""

    def __init__(self):
        self._compiled = [
            {**p, "_regex": re.compile(p["regex"])}
            for p in PATTERNS
        ]

    def _detect_value(self, value: Any) -> Optional[dict]:
        """检测单个值的格式变体"""
        if pd.isna(value) or not isinstance(value, (str, int, float)):
            return None

        value_str = str(value).strip()

        # 已经是纯数值 → 跳过
        try:
            float(value_str)
            return None
        except ValueError:
            pass

        # 遍历所有模式
        for pattern in self._compiled:
            match = pattern["_regex"].match(value_str)
            if match:
                parsed = pattern["parser"](match)
                parsed["pattern_name"] = pattern["name"]
                parsed["category"] = pattern["category"]
                return parsed

        return None

    def detect_variants(self, data: pd.DataFrame,
                        columns: Optional[List[str]] = None) -> Dict[str, List[dict]]:
        """
        检测DataFrame中数值列的格式变体

        Args:
            data: 输入DataFrame
            columns: 要检测的列名。为None则检测所有数值/对象列。

        Returns:
            {col_name: [{"value": "<1.5", "count": 3, "parsed": {...}}, ...]}
        """
        if columns is None:
            # 自动选择可能包含数值的列
            columns = [
                col for col in data.columns
                if pd.api.types.is_numeric_dtype(data[col])
                or pd.api.types.is_object_dtype(data[col])
            ]

        results = {}
        for col in columns:
            col_data = data[col]
            variant_counts: Dict[str, dict] = {}

            for val in col_data:
                if pd.isna(val):
                    continue
                result = self._detect_value(val)
                if result:
                    key = str(val)
                    if key not in variant_counts:
                        variant_counts[key] = {
                            "value": str(val),
                            "count": 0,
                            "parsed": result
                        }
                    variant_counts[key]["count"] += 1

            if variant_counts:
                results[col] = list(variant_counts.values())

        return results

    def show_summary(self, results: Dict[str, List[dict]]) -> str:
        """生成检测结果的Markdown摘要"""
        if not results:
            return "✅ 未检测到数值格式变体。"

        lines = ["## 数值格式变体检测结果\n"]
        total_variants = 0

        for col, variants in results.items():
            # 按类别分组
            by_category: Dict[str, list] = {}
            for v in variants:
                cat = v["parsed"]["category"]
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(v)

            lines.append(f"### 列：{col}\n")

            category_labels = {
                "detection_limit": "🔻 检测下限/上限",
                "multi_value": "🔢 逗号多值",
                "range": "📏 范围表示",
            }

            for cat_key, cat_variants in by_category.items():
                cat_label = category_labels.get(cat_key, cat_key)
                lines.append(f"**{cat_label}**\n")

                lines.append("| 原始值 | 出现次数 | 解析结果 |")
                lines.append("|--------|---------|---------|")
                for v in cat_variants:
                    parsed = v["parsed"]
                    if parsed["type"] in ("lower_limit", "upper_limit"):
                        detail = f"{'≤' if parsed['type']=='lower_limit' else '≥'} {parsed['threshold']}"
                    elif parsed["type"] == "multi_value":
                        detail = f"{parsed['n']} 个值: {parsed['values']}"
                    elif parsed["type"] == "range":
                        detail = f"{parsed['low']} ~ {parsed['high']}"
                    else:
                        detail = str(parsed)
                    lines.append(f"| {v['value']} | {v['count']} | {detail} |")
                lines.append("")
                total_variants += len(cat_variants)

        lines.append(f"\n> 共发现 {total_variants} 个数值格式变体。请逐类选择处理策略。")

        return "\n".join(lines)

    def _apply_strategy(self, value: str, parsed: dict,
                        strategy: str, col_name: str) -> Tuple[Any, dict]:
        """
        按用户选择的策略处理单个值

        Returns:
            (规范化后的值, 日志记录)
        """
        ptype = parsed["type"]
        log_entry = {
            "column": col_name,
            "original_value": str(value),
            "parsed_type": ptype,
            "strategy": strategy,
        }

        if ptype == "lower_limit":
            threshold = parsed["threshold"]
            if strategy == "threshold":
                result = threshold
                log_entry["normalized_value"] = threshold
            elif strategy == "half":
                result = threshold / 2
                log_entry["normalized_value"] = result
            elif strategy == "missing_with_indicator":
                result = pd.NA
                log_entry["normalized_value"] = "NA"
                log_entry["indicator_flag"] = f"{col_name}_below_LLOQ"
            elif strategy == "ordered_cat":
                result = str(value)
                log_entry["normalized_value"] = str(value)
                log_entry["note"] = "保留原值，作为有序分类变量"
            else:
                result = pd.NA
                log_entry["normalized_value"] = "NA"

        elif ptype == "upper_limit":
            threshold = parsed["threshold"]
            if strategy == "threshold":
                result = threshold
                log_entry["normalized_value"] = threshold
            elif strategy == "missing_with_indicator":
                result = pd.NA
                log_entry["normalized_value"] = "NA"
                log_entry["indicator_flag"] = f"{col_name}_above_ULOQ"
            else:
                result = pd.NA
                log_entry["normalized_value"] = "NA"

        elif ptype == "multi_value":
            values = parsed["values"]
            if strategy == "mean":
                result = sum(values) / len(values)
                log_entry["normalized_value"] = result
            elif strategy == "first":
                result = values[0]
                log_entry["normalized_value"] = result
            elif strategy == "mark_anomaly":
                result = str(value)
                log_entry["normalized_value"] = str(value)
                log_entry["note"] = "标记为异常，建议回查原始记录"
            else:
                result = pd.NA
                log_entry["normalized_value"] = "NA"

        elif ptype == "range":
            mid = (parsed["low"] + parsed["high"]) / 2
            if strategy == "midpoint":
                result = mid
                log_entry["normalized_value"] = mid
            elif strategy == "mark_anomaly":
                result = str(value)
                log_entry["normalized_value"] = str(value)
                log_entry["note"] = "标记为异常，建议回查原始记录"
            else:
                result = pd.NA
                log_entry["normalized_value"] = "NA"

        else:
            result = pd.NA
            log_entry["normalized_value"] = "NA"

        return result, log_entry

    def apply(self, data: pd.DataFrame,
              results: Dict[str, List[dict]],
              strategies: Dict[str, Dict[str, str]],
              indicator_df: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, List[dict]]:
        """
        执行数值格式规范化

        Args:
            data: 原始DataFrame
            results: detect_variants()的输出
            strategies: {col_name: {"type": "<parsed_type>", "strategy": "<strategy_id>"}}
                        type用于确认，strategy指定处理方式
            indicator_df: 可选的外部指示变量DataFrame，用于追加截断标记列

        Returns:
            (规范化后DataFrame, 规范化日志)
        """
        normalized = data.copy()
        log = []

        for col, variants in results.items():
            if col not in normalized.columns:
                continue

            col_strategy = strategies.get(col, {})
            strategy_id = col_strategy.get("strategy", "threshold")

            for v in variants:
                original_value = v["value"]
                parsed = v["parsed"]

                new_val, entry = self._apply_strategy(
                    original_value, parsed, strategy_id, col
                )

                # 批量替换
                mask = normalized[col].astype(str).str.strip() == original_value
                normalized.loc[mask, col] = new_val
                entry["records_affected"] = int(mask.sum())
                log.append(entry)

                # 截断指示变量
                if strategy_id == "missing_with_indicator" and "indicator_flag" in entry:
                    indicator_name = entry["indicator_flag"]
                    if indicator_df is not None:
                        indicator_df.loc[mask, indicator_name] = 1

        return normalized, log


def get_strategy_options(category: str) -> List[dict]:
    """获取指定类别的处理策略选项"""
    info = STRATEGY_OPTIONS.get(category)
    if info is None:
        return [{"id": "mark_anomaly", "label": "标记异常",
                 "description": "建议回查原始记录"}]
    return info["options"]
