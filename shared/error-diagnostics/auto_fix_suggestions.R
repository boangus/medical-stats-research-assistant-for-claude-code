# MSRA 自动修复建议生成器 (R版本)
#
# 根据错误类型和诊断结果，生成自动修复建议。
# 用于 Exec Runner 的自愈 Debug 流程。

#' 自动修复建议生成器
#'
#' @description 根据错误类型生成修复建议和代码
#' @param error_type 错误类型
#' @param details 诊断详情列表
#' @return 修复建议列表
generate_fix_suggestions <- function(error_type, details = list()) {
  # 修复建议库
  suggestions <- list(
    multicollinearity = list(
      diagnosis = "VIF > 10",
      suggestions = c(
        "删除高共线变量（保留临床意义更重要的）",
        "合并相关变量（如创建复合评分）",
        "使用主成分分析 (PCA) 降维",
        "使用岭回归 (Ridge Regression)"
      ),
      code_example = "
# R: 计算VIF
library(car)
vif(model)  # VIF > 10 提示严重共线性

# 删除高共线变量
high_vif <- names(which(vif(model) > 10))
model_reduced <- update(model, paste('~ . -', paste(high_vif, collapse = ' - ')))
",
      risk = "删除变量可能丢失重要信息"
    ),
    
    perfect_separation = list(
      diagnosis = "系数估计趋向无穷大",
      suggestions = c(
        "使用精确Logit回归 (Firth校正)",
        "删除导致分离的变量",
        "合并分类变量的类别",
        "使用贝叶斯Logistic回归"
      ),
      code_example = "
# R: Firth校正Logistic回归
library(logistf)
logistf(outcome ~ predictor, data = df)
",
      risk = "Firth校正可能引入轻微偏倚"
    ),
    
    insufficient_sample_size = list(
      diagnosis = "样本量 < 计划的70%",
      suggestions = c(
        "转为探索性分析 (exploratory)",
        "简化模型（减少变量）",
        "使用精确检验而非渐近检验",
        "报告效应量和置信区间，强调不确定性"
      ),
      code_example = "
# R: 样本量验证
power.t.test(n = n_actual, delta = delta, sig.level = 0.05, power = NULL)
",
      risk = "检验效能降低，可能无法检测到真实效应"
    ),
    
    ph_assumption_violation = list(
      diagnosis = "Schoenfeld残差检验 p < 0.05",
      suggestions = c(
        "使用分层Cox回归",
        "添加时依协变量",
        "使用参数生存模型",
        "报告中明确说明PH假设违反"
      ),
      code_example = "
# R: Schoenfeld残差检验
cox.zph(cox_model)  # p < 0.05 提示PH假设违反

# 分层Cox回归
cox_model_strat <- coxph(Surv(time, status) ~ treatment + strata(site), data = df)
",
      risk = "分层分析可能降低检验效能"
    ),
    
    missing_data_mar = list(
      diagnosis = "缺失模式为MAR",
      suggestions = c(
        "使用多重插补 (MI)",
        "使用全信息最大似然 (FIML)",
        "进行敏感性分析比较不同方法"
      ),
      code_example = "
# R: 多重插补
library(mice)
imp <- mice(df, m = 5, method = 'pmm')
fit <- with(imp, lm(y ~ x))
pool(fit)
",
      risk = "多重插补假设MAR，如果MNAR则可能有偏"
    ),
    
    extreme_outliers = list(
      diagnosis = "IQR方法检测到异常值",
      suggestions = c(
        "检查数据录入错误",
        "使用稳健统计方法",
        "对数变换或Winsorize",
        "敏感性分析（包含/排除异常值）"
      ),
      code_example = "
# R: Winsorize
library(DescTools)
df$variable_winsor <- Winsorize(df$variable, probs = c(0.05, 0.95))
",
      risk = "Winsorize可能改变数据分布"
    ),
    
    out_of_memory = list(
      diagnosis = "内存不足",
      suggestions = c(
        "数据子采样",
        "使用流式处理",
        "优化数据类型（如将double转为float）",
        "增加系统内存"
      ),
      code_example = "
# R: 内存优化
gc()  # 强制垃圾回收
df$integer_var <- as.integer(df$double_var)  # 优化数据类型
",
      risk = "数据子采样可能丢失信息"
    )
  )
  
  # 检查错误类型是否存在
  if (!error_type %in% names(suggestions)) {
    return(list(
      error_type = error_type,
      diagnosis = "未知错误类型",
      suggestions = "请手动检查错误原因",
      code_example = "",
      risk = "未知风险"
    ))
  }
  
  # 获取建议
  result <- suggestions[[error_type]]
  
  # 根据details添加特定建议
  if (!is.null(details$vif_value) && details$vif_value > 10) {
    result$diagnosis <- paste0("VIF = ", sprintf("%.2f", details$vif_value), " > 10")
  }
  
  if (!is.null(details$missing_rate) && details$missing_rate > 0.3) {
    result$suggestions <- c(result$suggestions, 
                           paste0("主要变量缺失率 ", sprintf("%.1f%%", details$missing_rate * 100), "，建议多重插补"))
  }
  
  return(result)
}

#' 生成修复代码
#'
#' @param error_type 错误类型
#' @param context 上下文信息列表（数据集名、变量名等）
#' @return 修复代码字符串
generate_fix_code <- function(error_type, context = list()) {
  # 获取建议
  suggestion <- generate_fix_suggestions(error_type)
  
  if (is.null(suggestion$code_example) || suggestion$code_example == "") {
    return("# 无法生成修复代码，请手动检查")
  }
  
  code <- suggestion$code_example
  
  # 根据context替换变量名
  if (!is.null(context$dataframe_name)) {
    code <- gsub("df", context$dataframe_name, code)
  }
  
  if (!is.null(context$outcome_var)) {
    code <- gsub("outcome", context$outcome_var, code)
  }
  
  if (!is.null(context$predictor_var)) {
    code <- gsub("predictor", context$predictor_var, code)
  }
  
  return(code)
}

#' 评估修复风险
#'
#' @param error_type 错误类型
#' @param fix_applied 是否应用了修复
#' @return 风险评估列表
assess_fix_risk <- function(error_type, fix_applied = FALSE) {
  # 获取建议
  suggestion <- generate_fix_suggestions(error_type)
  
  risk <- suggestion$risk
  
  return(list(
    risk_level = ifelse(fix_applied, "medium", "low"),
    message = risk,
    recommendation = ifelse(fix_applied, "建议进行敏感性分析验证修复效果", "无需额外操作")
  ))
}

# 使用示例
if (FALSE) {
  # 示例：多重共线性诊断
  diagnosis <- generate_fix_suggestions("multicollinearity", list(vif_value = 12.5))
  
  cat("诊断结果:\n")
  cat("  错误类型:", diagnosis$diagnosis, "\n")
  cat("  修复建议:", paste(diagnosis$suggestions, collapse = ", "), "\n")
  cat("  风险提示:", diagnosis$risk, "\n")
  
  # 生成修复代码
  fix_code <- generate_fix_code("multicollinearity", list(dataframe_name = "cleaned_data"))
  
  cat("\n修复代码:\n")
  cat(fix_code, "\n")
}