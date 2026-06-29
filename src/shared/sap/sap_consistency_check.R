# MSRA SAP一致性检查器 (R版本)
#
# 比较SAP预设方法与数据特征，检测不匹配情况，提供替代方法建议。
# 用于 Exec Runner 的 Phase 7 假设检验流程。

#' SAP一致性检查器
#'
#' @description 比较SAP预设方法与数据特征，检测不匹配情况
#' @param sap_config SAP配置列表
#' @return 一致性检查器对象
SAPConsistencyCheck <- function(sap_config) {
  # 初始化检查结果列表
  consistency_results <- list()
  
  #' 检查正态性假设
  #'
  #' @param data 数据框
  #' @param variable 变量名
  #' @param group_col 分组变量名（可选）
  #' @return 一致性检查结果
  check_normality <- function(data, variable, group_col = NULL) {
    result <- list(
      check_type = "normality",
      variable = variable,
      sap_method = sap_config$normality_test %||% "shapiro-wilk",
      data_characteristics = list(),
      consistency = TRUE,
      mismatch_details = "",
      alternative_method = "",
      code_suggestion = ""
    )
    
    # 获取数据
    if (!is.null(group_col)) {
      groups <- unique(data[[group_col]])
      for (group in groups) {
        group_data <- data[data[[group_col]] == group, variable]
        group_data <- group_data[!is.na(group_data)]
        
        if (length(group_data) >= 3 && length(group_data) <= 5000) {
          # Shapiro-Wilk检验
          test_result <- shapiro.test(group_data)
          result$data_characteristics[[paste0("group_", group)]] <- list(
            shapiro_stat = test_result$statistic,
            p_value = test_result$p.value,
            normal = test_result$p.value > 0.05
          )
        }
      }
    } else {
      group_data <- data[[variable]]
      group_data <- group_data[!is.na(group_data)]
      
      if (length(group_data) >= 3 && length(group_data) <= 5000) {
        test_result <- shapiro.test(group_data)
        result$data_characteristics$overall <- list(
          shapiro_stat = test_result$statistic,
          p_value = test_result$p.value,
          normal = test_result$p.value > 0.05
        )
      }
    }
    
    # 检查一致性
    is_normal <- all(sapply(result$data_characteristics, function(x) x$normal %||% TRUE))
    
    if (is_normal) {
      if (grepl("parametric", sap_config$main_analysis, ignore.case = TRUE)) {
        result$consistency <- TRUE
        result$mismatch_details <- "数据满足正态性，SAP预设参数方法合适"
      } else {
        result$consistency <- FALSE
        result$mismatch_details <- "数据满足正态性，但SAP预设非参数方法"
        result$alternative_method <- "建议使用参数检验"
      }
    } else {
      if (grepl("non-parametric|nonparametric", sap_config$main_analysis, ignore.case = TRUE)) {
        result$consistency <- TRUE
        result$mismatch_details <- "数据不满足正态性，SAP预设非参数方法合适"
      } else {
        result$consistency <- FALSE
        result$mismatch_details <- "数据不满足正态性，但SAP预设参数方法"
        result$alternative_method <- "建议使用非参数检验"
        result$code_suggestion <- generate_nonparametric_code(variable, group_col)
      }
    }
    
    return(result)
  }
  
  #' 检查方差齐性假设
  #'
  #' @param data 数据框
  #' @param variable 变量名
  #' @param group_col 分组变量名
  #' @return 一致性检查结果
  check_homogeneity <- function(data, variable, group_col) {
    result <- list(
      check_type = "homogeneity",
      variable = variable,
      group_variable = group_col,
      sap_method = sap_config$homogeneity_test %||% "levene",
      data_characteristics = list(),
      consistency = TRUE,
      mismatch_details = "",
      alternative_method = "",
      code_suggestion = ""
    )
    
    # 按组获取数据
    groups <- unique(data[[group_col]])
    group_data_list <- list()
    
    for (group in groups) {
      group_data <- data[data[[group_col]] == group, variable]
      group_data <- group_data[!is.na(group_data)]
      if (length(group_data) > 0) {
        group_data_list[[group]] <- group_data
      }
    }
    
    # Levene检验
    if (length(group_data_list) >= 2) {
      # 使用car包的Levene检验
      if (requireNamespace("car", quietly = TRUE)) {
        levene_result <- car::leveneTest(as.formula(paste(variable, "~", group_col)), data = data)
        result$data_characteristics <- list(
          levene_stat = levene_result$`F value`[1],
          p_value = levene_result$`Pr(>F)`[1],
          homogeneous = levene_result$`Pr(>F)`[1] > 0.05
        )
      }
    }
    
    # 检查一致性
    is_homogeneous <- result$data_characteristics$homogeneous %||% TRUE
    
    if (is_homogeneous) {
      if (isTRUE(sap_config$equal_var)) {
        result$consistency <- TRUE
        result$mismatch_details <- "数据满足方差齐性，SAP预设等方差方法合适"
      } else {
        result$consistency <- FALSE
        result$mismatch_details <- "数据满足方差齐性，但SAP预设不等方差方法"
        result$alternative_method <- "建议使用标准t检验/ANOVA"
      }
    } else {
      if (isFALSE(sap_config$equal_var)) {
        result$consistency <- TRUE
        result$mismatch_details <- "数据不满足方差齐性，SAP预设Welch校正合适"
      } else {
        result$consistency <- FALSE
        result$mismatch_details <- "数据不满足方差齐性，但SAP预设等方差方法"
        result$alternative_method <- "建议使用Welch校正"
        result$code_suggestion <- generate_welch_code(variable, group_col)
      }
    }
    
    return(result)
  }
  
  #' 检查样本量
  #'
  #' @param actual_n 实际样本量
  #' @param planned_n SAP计划样本量
  #' @return 一致性检查结果
  check_sample_size <- function(actual_n, planned_n) {
    result <- list(
      check_type = "sample_size",
      actual_n = actual_n,
      planned_n = planned_n,
      ratio = actual_n / planned_n,
      consistency = TRUE,
      mismatch_details = "",
      alternative_method = "",
      power_impact = ""
    )
    
    ratio <- result$ratio
    
    if (ratio >= 0.9) {
      result$consistency <- TRUE
      result$mismatch_details <- "样本量充足，满足SAP计划"
      result$power_impact <- "检验效能充足"
    } else if (ratio >= 0.7) {
      result$consistency <- TRUE
      result$mismatch_details <- paste0("样本量略低 (", round(ratio * 100, 1), "%)，检验效能可能降低")
      result$power_impact <- "建议报告效应量和置信区间"
    } else {
      result$consistency <- FALSE
      result$mismatch_details <- paste0("样本量不足 (", round(ratio * 100, 1), "%)，无法满足SAP计划")
      result$alternative_method <- "建议转为探索性分析"
      result$power_impact <- "检验效能不足，可能无法检测到真实效应"
    }
    
    return(result)
  }
  
  #' 生成非参数检验代码
  #'
  #' @param variable 变量名
  #' @param group_col 分组变量名（可选）
  #' @return 代码字符串
  generate_nonparametric_code <- function(variable, group_col = NULL) {
    if (!is.null(group_col)) {
      return(paste0("
# 非参数检验 (Mann-Whitney U / Kruskal-Wallis)
wilcox.test(", variable, " ~ ", group_col, ", data = df)
"))
    } else {
      return(paste0("
# 单样本非参数检验
wilcox.test(df$", variable, ", mu = 0)
"))
    }
  }
  
  #' 生成Welch校正代码
  #'
  #' @param variable 变量名
  #' @param group_col 分组变量名
  #' @return 代码字符串
  generate_welch_code <- function(variable, group_col) {
    return(paste0("
# Welch t检验 (不等方差)
t.test(", variable, " ~ ", group_col, ", data = df, var.equal = FALSE)

# 或 Welch ANOVA
library(onewaytests)
bf.test(", variable, " ~ ", group_col, ", data = df)
"))
  }
  
  #' 生成一致性检查报告
  #'
  #' @return 一致性检查报告列表
  generate_consistency_report <- function() {
    report <- list(
      summary = list(
        total_checks = length(consistency_results),
        consistent = sum(sapply(consistency_results, function(x) x$consistency %||% TRUE)),
        inconsistent = sum(sapply(consistency_results, function(x) !x$consistency %||% TRUE)),
        overall_consistent = all(sapply(consistency_results, function(x) x$consistency %||% TRUE))
      ),
      details = consistency_results,
      recommendations = list()
    )
    
    # 生成建议
    for (result in consistency_results) {
      if (!result$consistency %||% TRUE) {
        report$recommendations <- c(report$recommendations, list(list(
          check_type = result$check_type,
          variable = result$variable %||% "",
          issue = result$mismatch_details,
          recommendation = result$alternative_method,
          code = result$code_suggestion
        )))
      }
    }
    
    return(report)
  }
  
  # 返回检查器对象
  list(
    check_normality = check_normality,
    check_homogeneity = check_homogeneity,
    check_sample_size = check_sample_size,
    generate_consistency_report = generate_consistency_report,
    consistency_results = consistency_results
  )
}

# 使用示例
if (FALSE) {
  # SAP配置示例
  sap_config <- list(
    normality_test = "shapiro-wilk",
    homogeneity_test = "levene",
    main_analysis = "t-test",
    equal_var = TRUE,
    sample_size = 100
  )
  
  # 创建一致性检查器
  checker <- SAPConsistencyCheck(sap_config)
  
  # 示例数据
  set.seed(42)
  data <- data.frame(
    outcome = rnorm(100),
    group = sample(c("A", "B"), 100, replace = TRUE),
    age = rnorm(100, 50, 10)
  )
  
  # 执行检查
  normality_result <- checker$check_normality(data, "outcome", "group")
  homogeneity_result <- checker$check_homogeneity(data, "outcome", "group")
  sample_size_result <- checker$check_sample_size(100, 100)
  
  # 打印结果
  cat("正态性检查:\n")
  cat("  一致性:", normality_result$consistency, "\n")
  cat("  详情:", normality_result$mismatch_details, "\n")
  
  cat("\n方差齐性检查:\n")
  cat("  一致性:", homogeneity_result$consistency, "\n")
  cat("  详情:", homogeneity_result$mismatch_details, "\n")
  
  cat("\n样本量检查:\n")
  cat("  一致性:", sample_size_result$consistency, "\n")
  cat("  详情:", sample_size_result$mismatch_details, "\n")
  
  # 生成报告
  checker$consistency_results <- list(normality_result, homogeneity_result, sample_size_result)
  report <- checker$generate_consistency_report()
  
  cat("\n总体一致性:", report$summary$overall_consistent, "\n")
  cat("不一致检查项:", report$summary$inconsistent, "\n")
}