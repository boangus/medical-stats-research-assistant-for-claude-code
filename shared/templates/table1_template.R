# Table 1: Baseline Characteristics Template
# 适用于医学研究中的基线特征表

# 加载必要的包
if (!require("gtsummary")) install.packages("gtsummary")
if (!require("dplyr")) install.packages("dplyr")
library(gtsummary)
library(dplyr)

# 假设你的数据框名为 'data'，分组变量为 'group'
# 请根据实际情况修改变量名

create_table1 <- function(data, group_var, 
                          continuous_vars = NULL,
                          categorical_vars = NULL,
                          include_pvalue = TRUE) {
  
  # 选择变量
  select_vars <- c(group_var, continuous_vars, categorical_vars)
  
  # 创建表格
  tbl <- data %>%
    select(all_of(select_vars)) %>%
    tbl_summary(
      by = all_of(group_var),
      type = list(
        # 指定连续变量 (根据实际变量名修改)
        all_continuous() ~ "continuous2",
        # 指定分类变量 (根据实际变量名修改)
        all_categorical() ~ "categorical"
      ),
      statistic = list(
        # 连续变量: 均值±标准差 和 中位数(四分位距)
        all_continuous() ~ c("{mean} ({sd})", 
                             "{median} ({p25}, {p75})",
                             "{min}, {max}"),
        # 分类变量: 频数(百分比)
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits = list(
        all_continuous() ~ 1,
        all_categorical() ~ c(0, 1)
      ),
      missing = "ifany",  # 显示缺失值
      missing_text = "Missing"
    ) %>%
    # 添加统计检验
    add_p(
      test = list(
        # 连续变量使用 Wilcoxon rank-sum 或 t-test
        all_continuous() ~ "wilcox.test",
        # 分类变量使用卡方或 Fisher 精确检验
        all_categorical() ~ "chisq.test"
      ),
      pvalue_fun = function(x) style_pvalue(x, digits = 3)
    ) %>%
    # 添加总列
    add_overall() %>%
    # 修改列标题
    modify_header(
      label = "**Characteristic**",
      stat_0 = "**Overall**\nN = {N}",
      p.value = "**p-value**"
    ) %>%
    # 修改脚注
    modify_footnote(
      all_stat_cols() ~ "Mean (SD); Median (IQR); n (%)"
    ) %>%
    # 添加 bold 标签
    bold_labels()
  
  return(tbl)
}

# ==================== 使用示例 ====================

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
