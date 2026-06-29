"""变量名称标准化器

将原始数据中的缩写、非标准命名转换为学术标准名称。
支持中英文双语标签、单位提取和分类管理。

Usage:
    >>> standardizer = VariableStandardizer()
    >>> standardizer.get_label("crpc_月", lang="zh")
    'CRPC 时间（月）'
    >>> standardizer.get_label("BMI", lang="en")
    'Body mass index (BMI)'
    >>> standardizer.get_unit("PSA")
    'ng/mL'

    >>> import pandas as pd
    >>> df = pd.DataFrame({"crpc_月": [1, 2], "BMI": [23.5, 25.1]})
    >>> df_std = standardizer.standardize_dataframe(df)
    >>> list(df_std.columns)
    ['CRPC 时间（月）', '体质指数（BMI）']
"""

from __future__ import annotations

import copy
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


class VariableStandardizer:
    """变量名称标准化器

    将原始数据中的缩写、非标准命名转换为学术标准名称。

    Attributes:
        default_mapping: 内置的变量映射表，格式为
            ``{"原始名": {"zh": ..., "en": ..., "unit": ..., "category": ...}}``
        custom_mapping: 用户自定义的追加映射
    """

    # ── 内置映射 ──────────────────────────────────────────────

    DEFAULT_MAPPING: Dict[str, Dict[str, str]] = {
        # 人口学
        "age": {
            "zh": "年龄（岁）",
            "en": "Age (years)",
            "unit": "岁",
            "category": "人口学",
        },
        "性别": {
            "zh": "性别",
            "en": "Sex",
            "unit": "",
            "category": "人口学",
        },
        "male": {
            "zh": "男性",
            "en": "Male",
            "unit": "",
            "category": "人口学",
        },
        # 体格检查
        "身高_cm": {
            "zh": "身高（cm）",
            "en": "Height (cm)",
            "unit": "cm",
            "category": "体格检查",
        },
        "体重_kg": {
            "zh": "体重（kg）",
            "en": "Weight (kg)",
            "unit": "kg",
            "category": "体格检查",
        },
        "BMI": {
            "zh": "体质指数（BMI）",
            "en": "Body mass index (BMI)",
            "unit": "kg/m²",
            "category": "体格检查",
        },
        "腰围_cm": {
            "zh": "腰围（cm）",
            "en": "Waist circumference (cm)",
            "unit": "cm",
            "category": "体格检查",
        },
        "收缩压": {
            "zh": "收缩压（mmHg）",
            "en": "Systolic blood pressure (mmHg)",
            "unit": "mmHg",
            "category": "体格检查",
        },
        "舒张压": {
            "zh": "舒张压（mmHg）",
            "en": "Diastolic blood pressure (mmHg)",
            "unit": "mmHg",
            "category": "体格检查",
        },
        # 前列腺相关
        "PSA": {
            "zh": "前列腺特异性抗原（PSA）",
            "en": "Prostate-specific antigen (PSA)",
            "unit": "ng/mL",
            "category": "实验室检查",
        },
        "fPSA": {
            "zh": "游离前列腺特异性抗原（fPSA）",
            "en": "Free prostate-specific antigen (fPSA)",
            "unit": "ng/mL",
            "category": "实验室检查",
        },
        "GS": {
            "zh": "Gleason 评分（GS）",
            "en": "Gleason score (GS)",
            "unit": "分",
            "category": "病理",
        },
        "crpc_月": {
            "zh": "CRPC 时间（月）",
            "en": "CRPC duration (months)",
            "unit": "月",
            "category": "时间变量",
        },
        "T_stage": {
            "zh": "T 分期",
            "en": "T stage",
            "unit": "",
            "category": "肿瘤分期",
        },
        "N_stage": {
            "zh": "N 分期",
            "en": "N stage",
            "unit": "",
            "category": "肿瘤分期",
        },
        "M_stage": {
            "zh": "M 分期",
            "en": "M stage",
            "unit": "",
            "category": "肿瘤分期",
        },
        "isup_grade": {
            "zh": "ISUP 分级",
            "en": "ISUP grade group",
            "unit": "",
            "category": "病理",
        },
        # 实验室检查
        "HbA1c": {
            "zh": "糖化血红蛋白（HbA1c）",
            "en": "Glycated hemoglobin (HbA1c)",
            "unit": "%",
            "category": "实验室检查",
        },
        "eGFR": {
            "zh": "估算肾小球滤过率（eGFR）",
            "en": "Estimated GFR (eGFR)",
            "unit": "mL/min/1.73m²",
            "category": "实验室检查",
        },
        "WBC": {
            "zh": "白细胞计数（WBC）",
            "en": "White blood cell count (WBC)",
            "unit": "×10⁹/L",
            "category": "实验室检查",
        },
        "Hb": {
            "zh": "血红蛋白（Hb）",
            "en": "Hemoglobin (Hb)",
            "unit": "g/L",
            "category": "实验室检查",
        },
        "PLT": {
            "zh": "血小板计数（PLT）",
            "en": "Platelet count (PLT)",
            "unit": "×10⁹/L",
            "category": "实验室检查",
        },
        "ALT": {
            "zh": "丙氨酸氨基转移酶（ALT）",
            "en": "Alanine aminotransferase (ALT)",
            "unit": "U/L",
            "category": "实验室检查",
        },
        "AST": {
            "zh": "天冬氨酸氨基转移酶（AST）",
            "en": "Aspartate aminotransferase (AST)",
            "unit": "U/L",
            "category": "实验室检查",
        },
        "Cr": {
            "zh": "血肌酐（Cr）",
            "en": "Serum creatinine (Cr)",
            "unit": "μmol/L",
            "category": "实验室检查",
        },
        "BUN": {
            "zh": "血尿素氮（BUN）",
            "en": "Blood urea nitrogen (BUN)",
            "unit": "mmol/L",
            "category": "实验室检查",
        },
        "ALB": {
            "zh": "白蛋白（ALB）",
            "en": "Serum albumin (ALB)",
            "unit": "g/L",
            "category": "实验室检查",
        },
        "TC": {
            "zh": "总胆固醇（TC）",
            "en": "Total cholesterol (TC)",
            "unit": "mmol/L",
            "category": "实验室检查",
        },
        "TG": {
            "zh": "甘油三酯（TG）",
            "en": "Triglycerides (TG)",
            "unit": "mmol/L",
            "category": "实验室检查",
        },
        "LDL": {
            "zh": "低密度脂蛋白胆固醇（LDL-C）",
            "en": "Low-density lipoprotein cholesterol (LDL-C)",
            "unit": "mmol/L",
            "category": "实验室检查",
        },
        "HDL": {
            "zh": "高密度脂蛋白胆固醇（HDL-C）",
            "en": "High-density lipoprotein cholesterol (HDL-C)",
            "unit": "mmol/L",
            "category": "实验室检查",
        },
        # 合并症
        "charlson_index": {
            "zh": "Charlson 合并症指数",
            "en": "Charlson Comorbidity Index",
            "unit": "分",
            "category": "合并症",
        },
        "diabetes": {
            "zh": "糖尿病",
            "en": "Diabetes mellitus",
            "unit": "",
            "category": "合并症",
        },
        "hypertension": {
            "zh": "高血压",
            "en": "Hypertension",
            "unit": "",
            "category": "合并症",
        },
        # 治疗相关
        "ADT_type": {
            "zh": "雄激素剥夺治疗类型",
            "en": "ADT type",
            "unit": "",
            "category": "治疗",
        },
        "RT_dose": {
            "zh": "放疗剂量（Gy）",
            "en": "Radiation therapy dose (Gy)",
            "unit": "Gy",
            "category": "治疗",
        },
        "surgery_type": {
            "zh": "手术类型",
            "en": "Surgery type",
            "unit": "",
            "category": "治疗",
        },
        # 结局变量
        "OS": {
            "zh": "总生存期（OS）",
            "en": "Overall survival (OS)",
            "unit": "月",
            "category": "结局",
        },
        "PFS": {
            "zh": "无进展生存期（PFS）",
            "en": "Progression-free survival (PFS)",
            "unit": "月",
            "category": "结局",
        },
        "CSS": {
            "zh": "肿瘤特异性生存期（CSS）",
            "en": "Cancer-specific survival (CSS)",
            "unit": "月",
            "category": "结局",
        },
        "BCR": {
            "zh": "生化复发（BCR）",
            "en": "Biochemical recurrence (BCR)",
            "unit": "",
            "category": "结局",
        },
        "death": {
            "zh": "死亡",
            "en": "Death",
            "unit": "",
            "category": "结局",
        },
        # 时间变量
        "follow_up_months": {
            "zh": "随访时间（月）",
            "en": "Follow-up time (months)",
            "unit": "月",
            "category": "时间变量",
        },
        "time_to_event": {
            "zh": "事件发生时间（月）",
            "en": "Time to event (months)",
            "unit": "月",
            "category": "时间变量",
        },
    }

    # ── 初始化 ──────────────────────────────────────────────

    def __init__(self, mapping_file: Optional[Union[str, Path]] = None) -> None:
        """初始化，加载变量映射表

        Args:
            mapping_file: 可选的 YAML 映射文件路径，用于扩展或覆盖内置映射。

        Examples:
            >>> s = VariableStandardizer()
            >>> "BMI" in s.default_mapping
            True
        """
        self.default_mapping: Dict[str, Dict[str, str]] = copy.deepcopy(
            self.DEFAULT_MAPPING
        )
        self.custom_mapping: Dict[str, Dict[str, str]] = {}

        if mapping_file is not None:
            self._load_custom_mapping(mapping_file)

    # ── 映射加载 ────────────────────────────────────────────

    def _load_custom_mapping(self, mapping_file: Union[str, Path]) -> None:
        """从 YAML 文件加载自定义映射

        Args:
            mapping_file: YAML 文件路径。

        Raises:
            FileNotFoundError: 文件不存在。
            ValueError: 文件内容格式不正确。
        """
        path = Path(mapping_file)
        if not path.exists():
            raise FileNotFoundError(f"映射文件不存在: {path}")

        if yaml is None:
            raise ImportError(
                "需要安装 PyYAML 才能加载 YAML 映射文件: pip install pyyaml"
            )

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(
                f"映射文件格式不正确，期望字典结构，实际类型: {type(data).__name__}"
            )

        for key, value in data.items():
            if not isinstance(value, dict):
                warnings.warn(
                    f"跳过非字典条目: '{key}' (类型: {type(value).__name__})",
                    UserWarning,
                    stacklevel=2,
                )
                continue
            # 确保必要字段存在
            normalized: Dict[str, str] = {}
            for field in ("zh", "en", "unit", "category"):
                normalized[field] = str(value.get(field, ""))
            self.custom_mapping[str(key)] = normalized

    # ── 核心方法 ────────────────────────────────────────────

    def _get_all_mapping(self) -> Dict[str, Dict[str, str]]:
        """返回合并后的映射表（custom 优先于 default）"""
        merged = copy.deepcopy(self.default_mapping)
        merged.update(self.custom_mapping)
        return merged

    def get_label(self, raw_name: str, lang: str = "zh") -> str:
        """获取变量的标准化标签

        Args:
            raw_name: 原始变量名。
            lang: 语言，``"zh"`` 中文或 ``"en"`` 英文。

        Returns:
            标准化标签；若未找到映射则原样返回。

        Examples:
            >>> s = VariableStandardizer()
            >>> s.get_label("BMI", "zh")
            '体质指数（BMI）'
            >>> s.get_label("BMI", "en")
            'Body mass index (BMI)'
            >>> s.get_label("unknown_var", "zh")
            'unknown_var'
        """
        mapping = self._get_all_mapping()
        entry = mapping.get(raw_name)
        if entry is None:
            return raw_name
        return entry.get(lang, entry.get("zh", raw_name))

    def get_unit(self, raw_name: str) -> str:
        """获取变量的单位

        Args:
            raw_name: 原始变量名。

        Returns:
            单位字符串；若未找到则返回空字符串。

        Examples:
            >>> s = VariableStandardizer()
            >>> s.get_unit("PSA")
            'ng/mL'
            >>> s.get_unit("BMI")
            'kg/m²'
            >>> s.get_unit("unknown")
            ''
        """
        mapping = self._get_all_mapping()
        entry = mapping.get(raw_name, {})
        return entry.get("unit", "")

    def get_category(self, raw_name: str) -> str:
        """获取变量的分类

        Args:
            raw_name: 原始变量名。

        Returns:
            分类字符串；若未找到则返回空字符串。

        Examples:
            >>> s = VariableStandardizer()
            >>> s.get_category("PSA")
            '实验室检查'
            >>> s.get_category("OS")
            '结局'
        """
        mapping = self._get_all_mapping()
        entry = mapping.get(raw_name, {})
        return entry.get("category", "")

    def add_mapping(
        self,
        raw_name: str,
        zh: str,
        en: str,
        unit: str = "",
        category: str = "",
    ) -> None:
        """添加自定义映射

        Args:
            raw_name: 原始变量名。
            zh: 中文标准名称。
            en: 英文标准名称。
            unit: 单位（默认空）。
            category: 分类（默认空）。

        Examples:
            >>> s = VariableStandardizer()
            >>> s.add_mapping("LDH", zh="乳酸脱氢酶（LDH）", en="Lactate dehydrogenase (LDH)", unit="U/L", category="实验室检查")
            >>> s.get_label("LDH", "zh")
            '乳酸脱氢酶（LDH）'
            >>> s.get_unit("LDH")
            'U/L'
        """
        self.custom_mapping[raw_name] = {
            "zh": zh,
            "en": en,
            "unit": unit,
            "category": category,
        }

    def standardize_dataframe(
        self,
        df: pd.DataFrame,
        lang: str = "zh",
        unmapped_policy: str = "keep",
    ) -> pd.DataFrame:
        """标准化 DataFrame 的列名

        Args:
            df: 输入 DataFrame。
            lang: 标签语言，``"zh"`` 或 ``"en"``。
            unmapped_policy: 未映射列的处理策略：
                - ``"keep"``: 保留原始列名（默认）
                - ``"drop"``: 删除该列
                - ``"warn"``: 保留并发出警告

        Returns:
            列名已标准化的新 DataFrame（原始 df 不被修改）。

        Examples:
            >>> import pandas as pd
            >>> df = pd.DataFrame({"BMI": [23.5], "PSA": [5.1]})
            >>> s = VariableStandardizer()
            >>> df_std = s.standardize_dataframe(df)
            >>> list(df_std.columns)
            ['体质指数（BMI）', '前列腺特异性抗原（PSA）']
        """
        if unmapped_policy not in ("keep", "drop", "warn"):
            raise ValueError(
                f"unmapped_policy 必须是 'keep'/'drop'/'warn'，收到: '{unmapped_policy}'"
            )

        mapping = self._get_all_mapping()
        new_columns: Dict[str, str] = {}
        unmapped: List[str] = []

        for col in df.columns:
            col_str = str(col)
            entry = mapping.get(col_str)
            if entry is not None:
                new_columns[col_str] = entry.get(lang, entry.get("zh", col_str))
            else:
                unmapped.append(col_str)
                new_columns[col_str] = col_str

        if unmapped and unmapped_policy == "warn":
            warnings.warn(
                f"以下列未找到映射，保留原始名称: {unmapped}",
                UserWarning,
                stacklevel=2,
            )

        df_new = df.copy()
        df_new.columns = [new_columns[str(c)] for c in df.columns]

        if unmapped_policy == "drop":
            drop_cols = [
                new_columns[u]
                for u in unmapped
                if new_columns[u] in df_new.columns
            ]
            df_new = df_new.drop(columns=drop_cols, errors="ignore")

        return df_new

    def generate_mapping_table(
        self,
        df: pd.DataFrame,
        lang: str = "zh",
    ) -> List[Dict[str, str]]:
        """为 DataFrame 的列生成映射表建议

        已有映射的列返回标准名称，未映射的列返回空建议供用户填写。

        Args:
            df: 输入 DataFrame。
            lang: 语言。

        Returns:
            字典列表，每项包含 ``original``、``suggested``、``status``。

        Examples:
            >>> import pandas as pd
            >>> df = pd.DataFrame({"BMI": [1], "custom_col": [2]})
            >>> s = VariableStandardizer()
            >>> table = s.generate_mapping_table(df)
            >>> table[0]["status"]
            'mapped'
            >>> table[1]["status"]
            'unmapped'
        """
        mapping = self._get_all_mapping()
        results: List[Dict[str, str]] = []

        for col in df.columns:
            col_str = str(col)
            entry = mapping.get(col_str)
            if entry is not None:
                results.append(
                    {
                        "original": col_str,
                        "suggested": entry.get(lang, entry.get("zh", col_str)),
                        "status": "mapped",
                    }
                )
            else:
                results.append(
                    {
                        "original": col_str,
                        "suggested": "",
                        "status": "unmapped",
                    }
                )

        return results

    def validate_consistency(self, labels: Sequence[str]) -> Dict[str, Any]:
        """检查标签列表中同一变量是否使用一致的名称

        用于发现同一变量在不同表格/图表中使用了不同名称的情况。

        Args:
            labels: 标签字符串列表。

        Returns:
            字典，包含：
            - ``consistent``: bool，是否完全一致
            - ``groups``: 分组信息，按标准化后的名称分组

        Examples:
            >>> s = VariableStandardizer()
            >>> result = s.validate_consistency(["BMI", "体质指数（BMI）", "BMI"])
            >>> result["consistent"]
            False
            >>> len(result["groups"])
            2
        """
        mapping = self._get_all_mapping()

        # 反向映射：标准名 -> 原始名集合
        canonical_map: Dict[str, List[str]] = {}
        for raw_name, entry in mapping.items():
            for lang_key in ("zh", "en"):
                std_name = entry.get(lang_key, "")
                if std_name:
                    canonical_map.setdefault(std_name, []).append(raw_name)

        # 归一化每个标签
        normalized: Dict[str, List[str]] = {}
        for label in labels:
            label_str = str(label).strip()
            # 尝试匹配为某个标准名
            found_canonical: Optional[str] = None
            for std_name, raw_names in canonical_map.items():
                if label_str == std_name or label_str in raw_names:
                    found_canonical = std_name
                    break

            key = found_canonical if found_canonical else label_str
            normalized.setdefault(key, []).append(label_str)

        groups = {
            canonical: list(set(originals))
            for canonical, originals in normalized.items()
        }

        return {
            "consistent": all(len(v) == 1 for v in groups.values()),
            "groups": groups,
        }

    def get_mapping_for_export(
        self,
        lang: str = "zh",
        include_unit: bool = True,
        include_category: bool = True,
    ) -> Dict[str, str]:
        """导出为简化的单层映射字典

        Args:
            lang: 语言。
            include_unit: 是否在值中包含单位。
            include_category: 是否在值中包含分类。

        Returns:
            ``{原始名: 标准化名称}`` 的字典。

        Examples:
            >>> s = VariableStandardizer()
            >>> export = s.get_mapping_for_export(lang="zh", include_unit=False, include_category=False)
            >>> export["BMI"]
            '体质指数（BMI）'
        """
        mapping = self._get_all_mapping()
        result: Dict[str, str] = {}
        for raw_name, entry in mapping.items():
            label = entry.get(lang, entry.get("zh", raw_name))
            parts = [label]
            if include_unit and entry.get("unit"):
                parts.append(f"单位: {entry['unit']}")
            if include_category and entry.get("category"):
                parts.append(f"分类: {entry['category']}")
            result[raw_name] = " | ".join(parts)
        return result

    def reverse_lookup(self, standardized_name: str) -> Optional[str]:
        """根据标准名称反查原始变量名

        Args:
            standardized_name: 标准化后的名称。

        Returns:
            原始变量名；若未找到则返回 None。

        Examples:
            >>> s = VariableStandardizer()
            >>> s.reverse_lookup("体质指数（BMI）")
            'BMI'
            >>> s.reverse_lookup("不存在的名称") is None
            True
        """
        mapping = self._get_all_mapping()
        for raw_name, entry in mapping.items():
            if standardized_name in (entry.get("zh"), entry.get("en")):
                return raw_name
        return None

    def merge_mappings(
        self,
        other_mapping: Dict[str, Dict[str, str]],
        overwrite: bool = False,
    ) -> None:
        """合并外部映射表到 custom_mapping

        Args:
            other_mapping: 外部映射字典。
            overwrite: 若为 True 则覆盖已有映射，否则跳过重复键。

        Examples:
            >>> s = VariableStandardizer()
            >>> s.merge_mappings({"LDH": {"zh": "乳酸脱氢酶", "en": "LDH", "unit": "U/L", "category": "实验室"}})
            >>> s.get_label("LDH")
            '乳酸脱氢酶'
        """
        for key, value in other_mapping.items():
            if not isinstance(value, dict):
                continue
            if overwrite or key not in self.custom_mapping:
                normalized: Dict[str, str] = {}
                for field in ("zh", "en", "unit", "category"):
                    normalized[field] = str(value.get(field, ""))
                self.custom_mapping[key] = normalized

    def list_categories(self) -> Dict[str, List[str]]:
        """列出所有变量按分类分组

        Returns:
            ``{分类名: [原始变量名列表]}``

        Examples:
            >>> s = VariableStandardizer()
            >>> cats = s.list_categories()
            >>> "实验室检查" in cats
            True
            >>> "BMI" in cats.get("体格检查", [])
            True
        """
        mapping = self._get_all_mapping()
        result: Dict[str, List[str]] = {}
        for raw_name, entry in mapping.items():
            cat = entry.get("category", "未分类")
            result.setdefault(cat, []).append(raw_name)
        return result
