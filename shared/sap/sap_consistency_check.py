#!/usr/bin/env python3
"""
MSRA SAP一致性检查器

比较SAP预设方法与数据特征，检测不匹配情况，提供替代方法建议。
用于 Exec Runner 的 Phase 7 假设检验流程。
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Any, Optional
import warnings
import logging

logger = logging.getLogger(__name__)


class SAPConsistencyCheck:
    """SAP一致性检查器"""
    
    def __init__(self, sap_config: Dict[str, Any]):
        """
        初始化SAP一致性检查器
        
        Args:
            sap_config: SAP配置字典，包含预设方法和参数
        """
        self.sap_config = sap_config
        self.consistency_results = []
        
    def check_normality(self, data: pd.DataFrame, variable: str, group_col: Optional[str] = None) -> Dict[str, Any]:
        """
        检查正态性假设与SAP方法的一致性
        
        Args:
            data: 数据框
            variable: 变量名
            group_col: 分组变量名（可选）
            
        Returns:
            一致性检查结果
        """
        result = {
            "check_type": "normality",
            "variable": variable,
            "sap_method": self.sap_config.get("normality_test", "shapiro-wilk"),
            "data_characteristics": {},
            "consistency": True,
            "mismatch_details": "",
            "alternative_method": "",
            "code_suggestion": ""
        }
        
        # 获取数据
        if group_col:
            groups = data[group_col].unique()
            for group in groups:
                group_data = data[data[group_col] == group][variable].dropna()
                if len(group_data) >= 3 and len(group_data) <= 5000:
                    # Shapiro-Wilk检验
                    stat, p_value = stats.shapiro(group_data)
                    result["data_characteristics"][f"group_{group}"] = {
                        "shapiro_stat": stat,
                        "p_value": p_value,
                        "normal": p_value > 0.05
                    }
        else:
            group_data = data[variable].dropna()
            if len(group_data) >= 3 and len(group_data) <= 5000:
                stat, p_value = stats.shapiro(group_data)
                result["data_characteristics"]["overall"] = {
                    "shapiro_stat": stat,
                    "p_value": p_value,
                    "normal": p_value > 0.05
                }
        
        # 检查一致性
        is_normal = all(
            chars.get("normal", True) 
            for chars in result["data_characteristics"].values()
        )
        
        sap_method = self.sap_config.get("normality_test", "shapiro-wilk")
        
        if is_normal:
            if "parametric" in self.sap_config.get("main_analysis", "").lower():
                result["consistency"] = True
                result["mismatch_details"] = "数据满足正态性，SAP预设参数方法合适"
            else:
                result["consistency"] = False
                result["mismatch_details"] = "数据满足正态性，但SAP预设非参数方法"
                result["alternative_method"] = "建议使用参数检验"
        else:
            if "non-parametric" in self.sap_config.get("main_analysis", "").lower() or "nonparametric" in self.sap_config.get("main_analysis", "").lower():
                result["consistency"] = True
                result["mismatch_details"] = "数据不满足正态性，SAP预设非参数方法合适"
            else:
                result["consistency"] = False
                result["mismatch_details"] = "数据不满足正态性，但SAP预设参数方法"
                result["alternative_method"] = "建议使用非参数检验"
                result["code_suggestion"] = self._generate_nonparametric_code(variable, group_col)
        
        return result
    
    def check_homogeneity(self, data: pd.DataFrame, variable: str, group_col: str) -> Dict[str, Any]:
        """
        检查方差齐性假设与SAP方法的一致性
        
        Args:
            data: 数据框
            variable: 变量名
            group_col: 分组变量名
            
        Returns:
            一致性检查结果
        """
        result = {
            "check_type": "homogeneity",
            "variable": variable,
            "group_variable": group_col,
            "sap_method": self.sap_config.get("homogeneity_test", "levene"),
            "data_characteristics": {},
            "consistency": True,
            "mismatch_details": "",
            "alternative_method": "",
            "code_suggestion": ""
        }
        
        # 按组获取数据
        groups = data[group_col].unique()
        group_data_list = []
        
        for group in groups:
            group_data = data[data[group_col] == group][variable].dropna()
            if len(group_data) > 0:
                group_data_list.append(group_data)
        
        # Levene检验
        if len(group_data_list) >= 2:
            stat, p_value = stats.levene(*group_data_list)
            result["data_characteristics"] = {
                "levene_stat": stat,
                "p_value": p_value,
                "homogeneous": p_value > 0.05
            }
        
        # 检查一致性
        is_homogeneous = result["data_characteristics"].get("homogeneous", True)
        
        if is_homogeneous:
            if "equal_var" in self.sap_config and self.sap_config["equal_var"]:
                result["consistency"] = True
                result["mismatch_details"] = "数据满足方差齐性，SAP预设等方差方法合适"
            else:
                result["consistency"] = False
                result["mismatch_details"] = "数据满足方差齐性，但SAP预设不等方差方法"
                result["alternative_method"] = "建议使用标准t检验/ANOVA"
        else:
            if "equal_var" in self.sap_config and not self.sap_config["equal_var"]:
                result["consistency"] = True
                result["mismatch_details"] = "数据不满足方差齐性，SAP预设Welch校正合适"
            else:
                result["consistency"] = False
                result["mismatch_details"] = "数据不满足方差齐性，但SAP预设等方差方法"
                result["alternative_method"] = "建议使用Welch校正"
                result["code_suggestion"] = self._generate_welch_code(variable, group_col)
        
        return result
    
    def check_multicollinearity(self, data: pd.DataFrame, outcome: str, predictors: List[str]) -> Dict[str, Any]:
        """
        检查多重共线性与SAP模型的一致性
        
        Args:
            data: 数据框
            outcome: 结局变量
            predictors: 预测变量列表
            
        Returns:
            一致性检查结果
        """
        result = {
            "check_type": "multicollinearity",
            "outcome": outcome,
            "predictors": predictors,
            "data_characteristics": {},
            "consistency": True,
            "mismatch_details": "",
            "alternative_method": "",
            "code_suggestion": ""
        }
        
        # 准备数据
        X = data[predictors].dropna()
        if len(X) < len(predictors) + 1:
            result["data_characteristics"] = {"error": "样本量不足"}
            return result
        
        # 计算VIF
        vif_values = {}
        for i, predictor in enumerate(predictors):
            # 简化的VIF计算
            y = X[predictor]
            X_other = X.drop(columns=[predictor])
            
            if len(X_other.columns) > 0:
                # 添加常数项
                X_other_with_const = np.column_stack([np.ones(len(X_other)), X_other.values])
                
                # 计算R²
                corr_matrix = np.corrcoef(X_other.values.T)
                r_squared = 1 - 1 / np.diag(np.linalg.inv(corr_matrix)) if len(X_other.columns) > 1 else 0
                
                # VIF = 1 / (1 - R²)
                vif = 1 / (1 - r_squared) if r_squared < 1 else float('inf')
                vif_values[predictor] = vif
        
        result["data_characteristics"]["vif_values"] = vif_values
        result["data_characteristics"]["max_vif"] = max(vif_values.values()) if vif_values else 0
        
        # 检查一致性
        max_vif = result["data_characteristics"]["max_vif"]
        
        if max_vif < 5:
            result["consistency"] = True
            result["mismatch_details"] = "无严重共线性，SAP模型合适"
        elif max_vif < 10:
            result["consistency"] = True
            result["mismatch_details"] = "中度共线性，SAP模型基本合适"
        else:
            result["consistency"] = False
            result["mismatch_details"] = f"严重共线性 (VIF={max_vif:.2f})，SAP模型可能不稳定"
            result["alternative_method"] = "建议删除高共线变量或使用正则化方法"
            result["code_suggestion"] = self._generate_collinearity_fix_code(vif_values, predictors)
        
        return result
    
    def check_sample_size(self, actual_n: int, planned_n: int) -> Dict[str, Any]:
        """
        检查样本量与SAP计划的一致性
        
        Args:
            actual_n: 实际样本量
            planned_n: SAP计划样本量
            
        Returns:
            一致性检查结果
        """
        result = {
            "check_type": "sample_size",
            "actual_n": actual_n,
            "planned_n": planned_n,
            "ratio": actual_n / planned_n if planned_n > 0 else 0,
            "consistency": True,
            "mismatch_details": "",
            "alternative_method": "",
            "power_impact": ""
        }
        
        ratio = result["ratio"]
        
        if ratio >= 0.9:
            result["consistency"] = True
            result["mismatch_details"] = "样本量充足，满足SAP计划"
            result["power_impact"] = "检验效能充足"
        elif ratio >= 0.7:
            result["consistency"] = True
            result["mismatch_details"] = f"样本量略低 ({ratio:.1%})，检验效能可能降低"
            result["power_impact"] = "建议报告效应量和置信区间"
        else:
            result["consistency"] = False
            result["mismatch_details"] = f"样本量不足 ({ratio:.1%})，无法满足SAP计划"
            result["alternative_method"] = "建议转为探索性分析"
            result["power_impact"] = "检验效能不足，可能无法检测到真实效应"
        
        return result
    
    def generate_consistency_report(self) -> Dict[str, Any]:
        """
        生成一致性检查报告
        
        Returns:
            一致性检查报告
        """
        report = {
            "summary": {
                "total_checks": len(self.consistency_results),
                "consistent": sum(1 for r in self.consistency_results if r.get("consistency", True)),
                "inconsistent": sum(1 for r in self.consistency_results if not r.get("consistency", True)),
                "overall_consistent": all(r.get("consistency", True) for r in self.consistency_results)
            },
            "details": self.consistency_results,
            "recommendations": []
        }
        
        # 生成建议 + SAP修正触发条件（Optimization #7）
        amendment_triggers = []
        for result in self.consistency_results:
            if not result.get("consistency", True):
                report["recommendations"].append({
                    "check_type": result["check_type"],
                    "variable": result.get("variable", ""),
                    "issue": result.get("mismatch_details", ""),
                    "recommendation": result.get("alternative_method", ""),
                    "code": result.get("code_suggestion", "")
                })
                # 生成 SAP 修正触发条件
                trigger = self._classify_amendment_trigger(result)
                if trigger:
                    amendment_triggers.append(trigger)

        report["amendment_triggers"] = amendment_triggers
        return report

    def _classify_amendment_trigger(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        将一致性检查结果分类为 SAP 修正触发条件

        Returns:
            修正触发条件字典，或 None（无需修正）
        """
        check_type = result.get("check_type", "")
        if result.get("consistency", True):
            return None

        # 根据检查类型确定修正类别
        amendment_class_map = {
            "normality": "A-Method Swap",
            "homogeneity": "A-Method Swap",
            "multicollinearity": "B-Covariate Adjust",
            "sample_size": "D-Sample Restriction",
        }

        return {
            "trigger_type": check_type,
            "amendment_class": amendment_class_map.get(check_type, "unknown"),
            "original_spec": result.get("sap_method", ""),
            "suggested_amendment": result.get("alternative_method", ""),
            "trigger_detail": result.get("mismatch_details", ""),
        }

    def check_amendment_limit(self, passport_manager) -> Dict[str, Any]:
        """检查 SAP Amendment 是否接近或达到硬性上限

        集成 passport_manager 的计数器，在执行新修正前提供预警/阻断信号。
        上限定义于 passport.py 的 SAP_AMENDMENT_MAX（=3）。

        Args:
            passport_manager: PassportManager 实例，需实现 get_sap_amendment_count()

        Returns:
            dict with keys:
                - status: "ok" / "warning" / "blocked"
                - current_count: 当前已记录的修正次数
                - max_limit: 硬性上限（SAP_AMENDMENT_MAX）
                - message: 人类可读的状态说明
        """
        # 动态导入以避免循环依赖
        from shared.passport.passport import SAP_AMENDMENT_MAX

        current_count = passport_manager.get_sap_amendment_count()

        if current_count >= SAP_AMENDMENT_MAX:
            return {
                "status": "blocked",
                "current_count": current_count,
                "max_limit": SAP_AMENDMENT_MAX,
                "message": (
                    f"SAP Amendment 已达硬性上限 ({SAP_AMENDMENT_MAX} 次)，"
                    f"不可再执行修正。请退回 Stage 2 重新制定 SAP。"
                ),
            }

        if current_count >= SAP_AMENDMENT_MAX - 1:
            return {
                "status": "warning",
                "current_count": current_count,
                "max_limit": SAP_AMENDMENT_MAX,
                "message": (
                    f"SAP Amendment 接近上限 ({current_count}/{SAP_AMENDMENT_MAX})，"
                    f"仅剩 {SAP_AMENDMENT_MAX - current_count} 次修正额度，请审慎使用。"
                ),
            }

        return {
            "status": "ok",
            "current_count": current_count,
            "max_limit": SAP_AMENDMENT_MAX,
            "message": (
                f"SAP Amendment 计数正常 ({current_count}/{SAP_AMENDMENT_MAX})。"
            ),
        }

    def _generate_nonparametric_code(self, variable: str, group_col: Optional[str]) -> str:
        """生成非参数检验代码"""
        if group_col:
            return f"""
# 非参数检验 (Mann-Whitney U / Kruskal-Wallis)
wilcox.test({variable} ~ {group_col}, data = df)
"""
        else:
            return f"""
# 单样本非参数检验
wilcox.test(df${variable}, mu = 0)
"""
    
    def _generate_welch_code(self, variable: str, group_col: str) -> str:
        """生成Welch校正代码"""
        return f"""
# Welch t检验 (不等方差)
t.test({variable} ~ {group_col}, data = df, var.equal = FALSE)

# 或 Welch ANOVA
library(onewaytests)
bf.test({variable} ~ {group_col}, data = df)
"""
    
    def _generate_collinearity_fix_code(self, vif_values: Dict[str, float], predictors: List[str]) -> str:
        """生成共线性修复代码"""
        high_vif_vars = [var for var, vif in vif_values.items() if vif > 10]
        
        if high_vif_vars:
            return f"""
# 删除高共线变量
high_vif_vars <- c({', '.join(['"' + var + '"' for var in high_vif_vars])})
model_reduced <- update(model, paste("~ . -", paste(high_vif_vars, collapse = " - ")))

# 或使用主成分分析
library(FactoMineR)
pca_result <- PCA(df[, c({', '.join(['"' + var + '"' for var in predictors])})], graph = FALSE)
"""
        else:
            return """
# 中度共线性，可考虑使用岭回归
library(glmnet)
cv_fit <- cv.glmnet(x, y, alpha = 0)  # alpha = 0 为岭回归
"""


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # SAP配置示例
    sap_config = {
        "normality_test": "shapiro-wilk",
        "homogeneity_test": "levene",
        "main_analysis": "t-test",
        "equal_var": True,
        "sample_size": 100
    }
    
    # 创建一致性检查器
    checker = SAPConsistencyCheck(sap_config)
    
    # 示例数据
    np.random.seed(42)
    data = pd.DataFrame({
        "outcome": np.random.normal(0, 1, 100),
        "group": np.random.choice(["A", "B"], 100),
        "age": np.random.normal(50, 10, 100)
    })
    
    # 执行检查
    normality_result = checker.check_normality(data, "outcome", "group")
    homogeneity_result = checker.check_homogeneity(data, "outcome", "group")
    sample_size_result = checker.check_sample_size(100, 100)
    
    # 打印结果
    logger.info("正态性检查:")
    logger.info(f"  一致性: {normality_result['consistency']}")
    logger.info(f"  详情: {normality_result['mismatch_details']}")
    
    logger.info("\n方差齐性检查:")
    logger.info(f"  一致性: {homogeneity_result['consistency']}")
    logger.info(f"  详情: {homogeneity_result['mismatch_details']}")
    
    logger.info("\n样本量检查:")
    logger.info(f"  一致性: {sample_size_result['consistency']}")
    logger.info(f"  详情: {sample_size_result['mismatch_details']}")
    
    # 生成报告
    checker.consistency_results = [normality_result, homogeneity_result, sample_size_result]
    report = checker.generate_consistency_report()
    
    logger.info(f"\n总体一致性: {report['summary']['overall_consistent']}")
    logger.info(f"不一致检查项: {report['summary']['inconsistent']}")