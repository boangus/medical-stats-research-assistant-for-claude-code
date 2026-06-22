#!/usr/bin/env python3
"""
MSRA Multi-Center Analysis Template — 多中心分析模板

支持多中心研究的多数据集输入，提供跨中心一致性检查和汇总分析框架。

Usage:
    from multicenter_template import MultiCenterAnalyzer
    mca = MultiCenterAnalyzer(data_dir="data/multicenter/")
    report = mca.cross_site_consistency_check()
"""

import os
import json
from typing import Optional, Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MultiCenterAnalyzer:
    """多中心分析器"""

    def __init__(self, data_dir: str = None, dataframes: Dict[str, Any] = None):
        """
        初始化多中心分析器

        Args:
            data_dir: 包含多个 CSV 文件的目录路径
            dataframes: 或直接传入 {site_name: DataFrame} 字典
        """
        self.sites = {}
        self.site_names = []

        if dataframes:
            self.sites = dataframes
            self.site_names = list(dataframes.keys())
        elif data_dir:
            self._load_from_directory(data_dir)

    def _load_from_directory(self, data_dir: str):
        """从目录加载多中心数据"""
        import pandas as pd

        data_path = Path(data_dir)
        if not data_path.exists():
            raise FileNotFoundError(f"数据目录不存在: {data_dir}")

        csv_files = sorted(data_path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"目录中无 CSV 文件: {data_dir}")

        for f in csv_files:
            site_name = f.stem  # 文件名作为中心名
            self.sites[site_name] = pd.read_csv(f, encoding="utf-8")
            self.site_names.append(site_name)

    # ── 跨中心一致性检查 ──

    def cross_site_consistency_check(self) -> Dict[str, Any]:
        """
        执行跨中心一致性检查

        Returns:
            一致性检查报告
        """
        report = {
            "site_count": len(self.site_names),
            "site_names": self.site_names,
            "checks": {}
        }

        # 1. 变量名一致性
        report["checks"]["variable_consistency"] = self._check_variable_consistency()

        # 2. 变量类型一致性
        report["checks"]["type_consistency"] = self._check_type_consistency()

        # 3. 样本量汇总
        report["checks"]["sample_sizes"] = self._summarize_sample_sizes()

        # 4. 缺失率比较
        report["checks"]["missing_rate_comparison"] = self._compare_missing_rates()

        # 5. 基线特征分布差异
        report["checks"]["baseline_distribution"] = self._compare_baseline_distributions()

        # 总体一致性判定
        all_consistent = all(
            check.get("consistent", True)
            for check in report["checks"].values()
            if isinstance(check, dict)
        )
        report["overall_consistent"] = all_consistent

        return report

    def _check_variable_consistency(self) -> Dict[str, Any]:
        """检查各中心变量名是否一致"""
        if not self.sites:
            return {"consistent": True, "detail": "无数据"}

        # 取第一个中心的变量名作为基准
        reference_cols = set(self.sites[self.site_names[0]].columns)
        mismatches = {}

        for site in self.site_names[1:]:
            site_cols = set(self.sites[site].columns)
            missing = reference_cols - site_cols
            extra = site_cols - reference_cols
            if missing or extra:
                mismatches[site] = {
                    "missing_in_site": sorted(missing),
                    "extra_in_site": sorted(extra),
                }

        return {
            "consistent": len(mismatches) == 0,
            "reference_site": self.site_names[0],
            "mismatches": mismatches,
        }

    def _check_type_consistency(self) -> Dict[str, Any]:
        """检查同名变量在不同中心的类型是否一致"""
        import pandas as pd

        if len(self.sites) < 2:
            return {"consistent": True, "detail": "仅1个中心"}

        # 收集所有变量的类型
        type_map = {}  # {var_name: {site: dtype}}
        for site, df in self.sites.items():
            for col in df.columns:
                type_map.setdefault(col, {})[site] = str(df[col].dtype)

        # 检查类型不一致
        inconsistencies = {}
        for var, site_types in type_map.items():
            unique_types = set(site_types.values())
            if len(unique_types) > 1:
                inconsistencies[var] = site_types

        return {
            "consistent": len(inconsistencies) == 0,
            "inconsistencies": inconsistencies,
        }

    def _summarize_sample_sizes(self) -> Dict[str, Any]:
        """汇总各中心样本量"""
        sizes = {}
        for site, df in self.sites.items():
            sizes[site] = {
                "rows": len(df),
                "cols": len(df.columns),
            }

        total_rows = sum(s["rows"] for s in sizes.values())
        return {
            "sites": sizes,
            "total_rows": total_rows,
            "min_site_rows": min(s["rows"] for s in sizes.values()),
            "max_site_rows": max(s["rows"] for s in sizes.values()),
        }

    def _compare_missing_rates(self) -> Dict[str, Any]:
        """比较各中心缺失率"""
        import pandas as pd
        import numpy as np

        if len(self.sites) < 2:
            return {"consistent": True, "detail": "仅1个中心"}

        # 计算各中心缺失率
        missing_rates = {}
        for site, df in self.sites.items():
            rates = df.isnull().mean() * 100
            missing_rates[site] = rates.to_dict()

        # 检查缺失率差异 > 20% 的变量
        high_diff_vars = {}
        all_vars = set()
        for df in self.sites.values():
            all_vars.update(df.columns)

        for var in all_vars:
            var_rates = {}
            for site in self.site_names:
                if var in self.sites[site].columns:
                    var_rates[site] = self.sites[site][var].isnull().mean() * 100

            if var_rates:
                max_rate = max(var_rates.values())
                min_rate = min(var_rates.values())
                if max_rate - min_rate > 20:
                    high_diff_vars[var] = {
                        "rates": var_rates,
                        "diff": round(max_rate - min_rate, 2),
                    }

        return {
            "consistent": len(high_diff_vars) == 0,
            "high_diff_variables": high_diff_vars,
        }

    def _compare_baseline_distributions(self) -> Dict[str, Any]:
        """比较各中心基线特征分布差异"""
        import pandas as pd
        import numpy as np
        from scipy import stats

        if len(self.sites) < 2:
            return {"consistent": True, "detail": "仅1个中心"}

        # 取公共数值变量
        common_numeric = set()
        for site, df in self.sites.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not common_numeric:
                common_numeric = set(numeric_cols)
            else:
                common_numeric &= set(numeric_cols)

        distribution_diffs = {}
        for var in sorted(common_numeric):
            groups = []
            for site in self.site_names:
                vals = self.sites[site][var].dropna().values
                if len(vals) >= 5:
                    groups.append(vals)

            if len(groups) >= 2:
                try:
                    # Kruskal-Wallis 检验（非参数）
                    stat, p_value = stats.kruskal(*groups)
                    distribution_diffs[var] = {
                        "test": "Kruskal-Wallis",
                        "statistic": round(stat, 4),
                        "p_value": round(p_value, 4),
                        "significant": p_value < 0.05,
                    }
                except Exception:
                    pass

        significant_diffs = {
            k: v for k, v in distribution_diffs.items() if v.get("significant", False)
        }

        return {
            "consistent": len(significant_diffs) == 0,
            "significant_diffs": significant_diffs,
            "total_variables_tested": len(distribution_diffs),
        }

    # ── 汇总分析 ──

    def generate_summary_report(self, output_path: str = None) -> str:
        """
        生成多中心分析汇总报告

        Args:
            output_path: 输出文件路径（可选）

        Returns:
            Markdown 格式报告
        """
        report = self.cross_site_consistency_check()

        lines = []
        lines.append("# 多中心数据分析报告")
        lines.append("")

        # 1. 中心概况
        lines.append("## 1. 中心概况")
        lines.append("")
        lines.append(f"- 中心数量: {report['site_count']}")
        lines.append(f"- 中心名称: {', '.join(report['site_names'])}")
        lines.append("")

        # 2. 样本量
        sample_sizes = report["checks"]["sample_sizes"]
        lines.append("## 2. 样本量汇总")
        lines.append("")
        lines.append("| 中心 | 样本量 | 变量数 |")
        lines.append("|------|--------|--------|")
        for site, info in sample_sizes["sites"].items():
            lines.append(f"| {site} | {info['rows']:,} | {info['cols']} |")
        lines.append(f"| **总计** | **{sample_sizes['total_rows']:,}** | - |")
        lines.append("")

        # 3. 变量一致性
        var_check = report["checks"]["variable_consistency"]
        lines.append("## 3. 变量一致性检查")
        lines.append("")
        if var_check["consistent"]:
            lines.append("✅ 所有中心变量名一致。")
        else:
            lines.append("⚠️ 发现变量名不一致：")
            for site, mismatch in var_check["mismatches"].items():
                if mismatch["missing_in_site"]:
                    lines.append(f"  - {site} 缺失: {', '.join(mismatch['missing_in_site'])}")
                if mismatch["extra_in_site"]:
                    lines.append(f"  - {site} 多余: {', '.join(mismatch['extra_in_site'])}")
        lines.append("")

        # 4. 缺失率比较
        missing_check = report["checks"]["missing_rate_comparison"]
        lines.append("## 4. 缺失率比较")
        lines.append("")
        if missing_check["consistent"]:
            lines.append("✅ 各中心缺失率差异均 < 20%。")
        else:
            lines.append("⚠️ 以下变量缺失率差异 > 20%：")
            for var, info in missing_check["high_diff_variables"].items():
                lines.append(f"  - {var}: 差异 {info['diff']}%")
        lines.append("")

        # 5. 基线分布
        baseline_check = report["checks"]["baseline_distribution"]
        lines.append("## 5. 基线特征分布差异")
        lines.append("")
        if baseline_check["consistent"]:
            lines.append("✅ 各中心基线特征分布无显著差异。")
        else:
            lines.append(f"⚠️ {len(baseline_check['significant_diffs'])} 个变量存在显著差异：")
            for var, info in baseline_check["significant_diffs"].items():
                lines.append(f"  - {var}: {info['test']} p={info['p_value']}")
        lines.append("")

        # 6. 总结
        lines.append("## 6. 总结")
        lines.append("")
        if report["overall_consistent"]:
            lines.append("✅ **总体一致性良好**，可直接进行汇总分析。")
        else:
            lines.append("⚠️ **发现不一致项**，建议在汇总分析前处理差异。")

        md_text = "\n".join(lines)

        if output_path:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_text)

        return md_text


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    import sys

    if len(sys.argv) < 2:
        logger.info("Usage: python multicenter_template.py <data_dir> [output_path]")
        logger.info("  data_dir: 包含多个 CSV 文件的目录")
        sys.exit(1)

    data_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    mca = MultiCenterAnalyzer(data_dir=data_dir)
    report_md = mca.generate_summary_report(output_path)
    logger.info("report_md")
