# Table 1: Baseline Characteristics Template
# 适用于医学研究中的基线特征表
#
# 整合了三套方案：
#   1. gtsummary — 出版级（推荐，一行代码出表）
#   2. janitor tabyl + adorn — 快速交叉表（灵活可控）
#   3. base R — 手动计算（无额外依赖）

# 加载必要的包
if (!require("gtsummary")) install.packages("gtsummary")
if (!require("janitor")) install.packages("janitor")
if (!require("dplyr")) install.packages("dplyr")
if (!require("tidyr")) install.packages("tidyr")
library(gtsummary)
library(janitor)
library(dplyr)
library(tidyr)

# 假设你的数据框名为 'data'，分组变量为 'group'
# 请根据实际情况修改变量名

# ==================== 方案1: gtsummary 出版级 Table 1（推荐） ====================

create_table1 <- function(data, group_var, 
                          continuous_vars = NULL,
                          categorical_vars = NULL,
                          include_pvalue = TRUE,
                          normal_dist = FALSE) {
  
  # 选择变量
  select_vars <- c(group_var, continuous_vars, categorical_vars)
  
  # 根据分布类型选择统计量
  if (normal_dist) {
    cont_stat <- c("{mean} ({sd})", "{median} ({p25}, {p75})", "{min}, {max}")
    test_method <- "t.test"
  } else {
    cont_stat <- c("{median} ({p25}, {p75})", "{mean} ({sd})", "{min}, {max}")
    test_method <- "wilcox.test"
  }
  
  # 创建表格
  tbl <- data %>%
    select(all_of(select_vars)) %>%
    tbl_summary(
      by = all_of(group_var),
      type = list(
        all_continuous() ~ "continuous2",
        all_categorical() ~ "categorical"
      ),
      statistic = list(
        all_continuous() ~ cont_stat,
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits = list(
        all_continuous() ~ 1,
        all_categorical() ~ c(0, 1)
      ),
      missing = "ifany",
      missing_text = "Missing"
    )
  
  if (include_pvalue) {
    tbl <- tbl %>% add_p(
      test = list(
        all_continuous() ~ test_method,
        all_categorical() ~ "chisq.test"
      ),
      pvalue_fun = function(x) style_pvalue(x, digits = 3)
    )
  }
  
  tbl <- tbl %>%
    add_overall() %>%
    modify_header(
      label = "**Characteristic**",
      stat_0 = "**Overall**\nN = {N}",
      p.value = "**p-value**"
    ) %>%
    modify_footnote(
      all_stat_cols() ~ "Median (IQR); Mean (SD); n (%)"
    ) %>%
    bold_labels()
  
  return(tbl)
}

# ==================== 方案2: janitor tabyl 快速交叉表 ====================

#' 使用 janitor tabyl 生成基线比较表
#' 适合快速探索性分析
create_table1_tabyl <- function(data, group_var, cat_vars,
                                pct_type = "col", digits = 1,
                                include_test = TRUE) {
  
  results <- list()
  
  for (var in cat_vars) {
    cat("\n=== ", var, " × ", group_var, " ===\n", sep = "")
    
    tab <- data %>%
      tabyl(!!sym(var), !!sym(group_var))
    
    tab <- tab %>%
      adorn_totals("row") %>%
      adorn_percentages(pct_type) %>%
      adorn_pct_formatting(digits = digits) %>%
      adorn_ns() %>%
      adorn_title("combined")
    
    print(tab)
    
    if (include_test) {
      # 自动选择检验
      ct <- suppressWarnings(chisq.test(data[[var]], data[[group_var]]))
      if (any(ct$expected < 5)) {
        ft <- fisher.test(data[[var]], data[[group_var]], simulate.p.value = TRUE)
        cat("Fisher exact test: p =", format.pval(ft$p.value, digits = 3), "\n")
      } else {
        cat("χ² =", round(ct$statistic, 2), ", df =", ct$parameter,
            ", p =", format.pval(ct$p.value, digits = 3), "\n")
      }
    }
    
    results[[var]] <- tab
  }
  
  invisible(results)
}

#' 使用 janitor 生成连续变量汇总
create_table1_continuous_tabyl <- function(data, group_var, cont_vars,
                                           digits = 1) {
  
  results <- data.frame(variable = character(),
                        level = character(),
                        n = integer(),
                        median = numeric(),
                        q25 = numeric(),
                        q75 = numeric(),
                        stringsAsFactors = FALSE)
  
  groups <- unique(data[[group_var]])
  
  for (var in cont_vars) {
    row_start <- nrow(results) + 1
    
    for (grp in groups) {
      vals <- data[[var]][data[[group_var]] == grp]
      vals <- vals[!is.na(vals)]
      
      results <- rbind(results, data.frame(
        variable = var,
        level = as.character(grp),
        n = length(vals),
        median = round(median(vals), digits),
        q25 = round(quantile(vals, 0.25, na.rm = TRUE), digits),
        q75 = round(quantile(vals, 0.75, na.rm = TRUE), digits),
        stringsAsFactors = FALSE
      ))
    }
    
    # 整体
    vals_all <- data[[var]][!is.na(data[[var]])]
    results <- rbind(results, data.frame(
      variable = var,
      level = "Overall",
      n = length(vals_all),
      median = round(median(vals_all), digits),
      q25 = round(quantile(vals_all, 0.25, na.rm = TRUE), digits),
      q75 = round(quantile(vals_all, 0.75, na.rm = TRUE), digits),
      stringsAsFactors = FALSE
    ))
  }
  
  cat("\n=== 连续变量汇总 (Median [Q1, Q3]) ===\n")
  print(results, row.names = FALSE)
  
  invisible(results)
}

# ==================== 方案3: base R 手动计算（向后兼容） ====================

# 假设数据框名为 'mydata'，分组变量为 'treatment'
# 连续变量: age, bmi, sbp (收缩压), dbp (舒张压)
# 分类变量: sex, smoking, diabetes

# table1 <- create_table1(
#   data = mydata,
#   group_var = "treatment",
#   continuous_vars = c("age", "bmi", "sbp", "dbp"),
#   categorical_vars = c("sex", "smoking", "diabetes"),
#   include_pvalue = TRUE
# )

# 显示表格
# table1

# 导出为 Word 文档
# table1 %>% as_flex_table() %>% flextable::save_as_docx(path = "Table1.docx")

# 导出为 HTML
# table1 %>% as_gt() %>% gt::gtsave("Table1.html")

# ==================== 手动创建版本 ====================

# 如果不使用 gtsummary，可以手动计算

create_table1_manual <- function(data, group_var) {
  
  # 按分组计算统计量
  summary_stats <- data %>%
    group_by(across(all_of(group_var))) %>%
    summarise(
      # 连续变量示例
      age_mean = mean(age, na.rm = TRUE),
      age_sd = sd(age, na.rm = TRUE),
      age_median = median(age, na.rm = TRUE),
      age_q25 = quantile(age, 0.25, na.rm = TRUE),
      age_q75 = quantile(age, 0.75, na.rm = TRUE),
      
      # 分类变量示例
      female_n = sum(sex == "Female", na.rm = TRUE),
      female_pct = mean(sex == "Female", na.rm = TRUE) * 100,
      
      # 样本量
      n = n()
    )
  
  return(summary_stats)
}

# ==================== 统计检验函数 ====================

# 根据数据特征自动选择检验方法
auto_test <- function(data, var, group_var, var_type = "auto") {
  
  # 自动判断变量类型
  if (var_type == "auto") {
    var_type <- ifelse(is.numeric(data[[var]]), "continuous", "categorical")
  }
  
  # 提取数据
  group1 <- data[[var]][data[[group_var]] == unique(data[[group_var]])[1]]
  group2 <- data[[var]][data[[group_var]] == unique(data[[group_var]])[2]]
  
  if (var_type == "continuous") {
    # 检查正态性 (Shapiro-Wilk 检验)
    if (length(group1) < 5000 && length(group2) < 5000) {
      normal1 <- shapiro.test(group1)$p.value > 0.05
      normal2 <- shapiro.test(group2)$p.value > 0.05
      
      if (normal1 && normal2) {
        # t 检验
        test_result <- t.test(group1, group2)
        method <- "Independent t-test"
      } else {
        # Mann-Whitney U 检验
        test_result <- wilcox.test(group1, group2)
        method <- "Mann-Whitney U test"
      }
    } else {
      # 大样本使用 t 检验
      test_result <- t.test(group1, group2)
      method <- "Independent t-test"
    }
  } else {
    # 卡方检验
    contingency_table <- table(data[[var]], data[[group_var]])
    
    # 检查期望频数
    expected <- chisq.test(contingency_table)$expected
    if (any(expected < 5)) {
      test_result <- fisher.test(contingency_table)
      method <- "Fisher's exact test"
    } else {
      test_result <- chisq.test(contingency_table)
      method <- "Chi-square test"
    }
  }
  
  return(list(
    method = method,
    statistic = test_result$statistic,
    p_value = test_result$p.value
  ))
}
