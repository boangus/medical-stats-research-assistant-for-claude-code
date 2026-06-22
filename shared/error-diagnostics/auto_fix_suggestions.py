#!/usr/bin/env python3
"""
MSRA 自动修复建议生成器

根据错误类型和诊断结果，生成自动修复建议。
用于 Exec Runner 的自愈 Debug 流程。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class AutoFixSuggestions:
    """自动修复建议生成器"""
    
    def __init__(self):
        """初始化修复建议生成器"""
        self.suggestions = self._load_suggestions()
    
    def _load_suggestions(self) -> Dict[str, Any]:
        """加载修复建议库"""
        return {
            "multicollinearity": {
                "diagnosis": "VIF > 10",
                "suggestions": [
                    "删除高共线变量（保留临床意义更重要的）",
                    "合并相关变量（如创建复合评分）",
                    "使用主成分分析 (PCA) 降维",
                    "使用岭回归 (Ridge Regression)"
                ],
                "code_example": """
# R: 计算VIF
library(car)
vif(model)  # VIF > 10 提示严重共线性

# 删除高共线变量
high_vif <- names(which(vif(model) > 10))
model_reduced <- update(model, paste("~ . -", paste(high_vif, collapse = " - ")))
""",
                "risk": "删除变量可能丢失重要信息"
            },
            "perfect_separation": {
                "diagnosis": "系数估计趋向无穷大",
                "suggestions": [
                    "使用精确Logit回归 (Firth校正)",
                    "删除导致分离的变量",
                    "合并分类变量的类别",
                    "使用贝叶斯Logistic回归"
                ],
                "code_example": """
# R: Firth校正Logistic回归
library(logistf)
logistf(outcome ~ predictor, data = df)
""",
                "risk": "Firth校正可能引入轻微偏倚"
            },
            "insufficient_sample_size": {
                "diagnosis": "样本量 < 计划的70%",
                "suggestions": [
                    "转为探索性分析 (exploratory)",
                    "简化模型（减少变量）",
                    "使用精确检验而非渐近检验",
                    "报告效应量和置信区间，强调不确定性"
                ],
                "code_example": """
# R: 样本量验证
power.t.test(n = n_actual, delta = delta, sig.level = 0.05, power = NULL)
""",
                "risk": "检验效能降低，可能无法检测到真实效应"
            },
            "ph_assumption_violation": {
                "diagnosis": "Schoenfeld残差检验 p < 0.05",
                "suggestions": [
                    "使用分层Cox回归",
                    "添加时依协变量",
                    "使用参数生存模型",
                    "报告中明确说明PH假设违反"
                ],
                "code_example": """
# R: Schoenfeld残差检验
cox.zph(cox_model)  # p < 0.05 提示PH假设违反

# 分层Cox回归
cox_model_strat <- coxph(Surv(time, status) ~ treatment + strata(site), data = df)
""",
                "risk": "分层分析可能降低检验效能"
            },
            "missing_data_mar": {
                "diagnosis": "缺失模式为MAR",
                "suggestions": [
                    "使用多重插补 (MI)",
                    "使用全信息最大似然 (FIML)",
                    "进行敏感性分析比较不同方法"
                ],
                "code_example": """
# R: 多重插补
library(mice)
imp <- mice(df, m = 5, method = "pmm")
fit <- with(imp, lm(y ~ x))
pool(fit)
""",
                "risk": "多重插补假设MAR，如果MNAR则可能有偏"
            },
            "extreme_outliers": {
                "diagnosis": "IQR方法检测到异常值",
                "suggestions": [
                    "检查数据录入错误",
                    "使用稳健统计方法",
                    "对数变换或Winsorize",
                    "敏感性分析（包含/排除异常值）"
                ],
                "code_example": """
# R: Winsorize
library(DescTools)
df$variable_winsor <- Winsorize(df$variable, probs = c(0.05, 0.95))
""",
                "risk": "Winsorize可能改变数据分布"
            },
            "out_of_memory": {
                "diagnosis": "内存不足",
                "suggestions": [
                    "数据子采样",
                    "使用流式处理",
                    "优化数据类型（如将double转为float）",
                    "增加系统内存"
                ],
                "code_example": """
# R: 内存优化
gc()  # 强制垃圾回收
df$integer_var <- as.integer(df$double_var)  # 优化数据类型
""",
                "risk": "数据子采样可能丢失信息"
            }
        }
    
    def diagnose_and_suggest(self, error_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据错误类型和诊断结果生成修复建议
        
        Args:
            error_type: 错误类型
            details: 诊断详情
            
        Returns:
            修复建议字典
        """
        if error_type not in self.suggestions:
            return {
                "error_type": error_type,
                "diagnosis": "未知错误类型",
                "suggestions": ["请手动检查错误原因"],
                "code_example": "",
                "risk": "未知风险"
            }
        
        suggestion = self.suggestions[error_type].copy()
        
        # 根据details添加特定建议
        if "vif_value" in details and details["vif_value"] > 10:
            suggestion["diagnosis"] = f"VIF = {details['vif_value']:.2f} > 10"
        
        if "missing_rate" in details and details["missing_rate"] > 0.3:
            suggestion["suggestions"].append(f"主要变量缺失率 {details['missing_rate']:.1%}，建议多重插补")
        
        return suggestion
    
    def generate_fix_code(self, error_type: str, context: Dict[str, Any]) -> str:
        """
        生成修复代码
        
        Args:
            error_type: 错误类型
            context: 上下文信息（数据集名、变量名等）
            
        Returns:
            修复代码字符串
        """
        if error_type not in self.suggestions:
            return "# 无法生成修复代码，请手动检查"
        
        suggestion = self.suggestions[error_type]
        code_example = suggestion.get("code_example", "")
        
        # 根据context替换变量名
        if "dataframe_name" in context:
            code_example = code_example.replace("df", context["dataframe_name"])
        
        if "outcome_var" in context:
            code_example = code_example.replace("outcome", context["outcome_var"])
        
        if "predictor_var" in context:
            code_example = code_example.replace("predictor", context["predictor_var"])
        
        return code_example
    
    def assess_risk(self, error_type: str, fix_applied: bool) -> Dict[str, Any]:
        """
        评估修复风险
        
        Args:
            error_type: 错误类型
            fix_applied: 是否应用了修复
            
        Returns:
            风险评估字典
        """
        if error_type not in self.suggestions:
            return {"risk_level": "unknown", "message": "未知错误类型"}
        
        suggestion = self.suggestions[error_type]
        risk = suggestion.get("risk", "无特定风险")
        
        return {
            "risk_level": "medium" if fix_applied else "low",
            "message": risk,
            "recommendation": "建议进行敏感性分析验证修复效果" if fix_applied else "无需额外操作"
        }


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 创建修复建议生成器
    fix_generator = AutoFixSuggestions()
    
    # 示例：多重共线性诊断
    diagnosis = fix_generator.diagnose_and_suggest(
        "multicollinearity",
        {"vif_value": 12.5}
    )
    
    logger.info("诊断结果:")
    logger.info(f"  错误类型: {diagnosis['diagnosis']}")
    logger.info(f"  修复建议: {diagnosis['suggestions']}")
    logger.info(f"  风险提示: {diagnosis['risk']}")
    
    # 生成修复代码
    fix_code = fix_generator.generate_fix_code(
        "multicollinearity",
        {"dataframe_name": "cleaned_data"}
    )
    
    logger.info("\n修复代码:")
    logger.info("fix_code")