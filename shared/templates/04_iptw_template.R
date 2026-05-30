# 04_iptw.R
# IPTW (逆概率处理加权) 分析脚本
# 输入: load/01_extracted.rda, load/02_var_defined.rda
# 输出: outcome/tables/Table1b_IPTW_Baseline.docx
#       outcome/figures/PSM_Balance_Plot.pdf
#       outcome/figures/IPTW_Weight_Distribution.pdf

rm(list = ls())

# 1. 加载配置和依赖 -------------------------------------------------
load("load/00_config.rda")
load("load/01_extracted.rda")
load("load/02_var_defined.rda")

cat("[04_iptw] 开始 IPTW 分析\n")

# 2. 输入输出声明 ---------------------------------------------------
input_file <- "load/01_extracted.rda"
output_dir <- file.path(outcome_dir)

# 3. 准备数据 -------------------------------------------------------
# 确保处理变量是因子
data_select[[treatment_var]] <- as.factor(data_select[[treatment_var]])

# 4. IPTW 权重计算 --------------------------------------------------
# 构建公式
fml <- as.formula(paste(treatment_var, "~", paste(covariates, collapse = " + ")))

# 使用 WeightIt 计算 IPTW 权重
set.seed(20250101)
ipw_fit <- weightit(
  fml,
  data = data_select,
  method = "ps",           # 倾向得分加权
  link = "logit",          # 逻辑回归
  stabilize = TRUE         # 稳定化权重
)

cat("[04_iptw] IPTW 权重计算完成\n")
cat("[04_iptw] 权重范围:", round(min(ipw_fit$weights), 3), "-", round(max(ipw_fit$weights), 3), "\n")

# 5. 权重截断（处理极端权重）---------------------------------------
# 使用 95% 分位数截断
truncation_quantile <- quantile(ipw_fit$weights, probs = 0.95, na.rm = TRUE)
extreme_count <- sum(ipw_fit$weights > truncation_quantile, na.rm = TRUE)

cat("[04_iptw] 95% 分位数截断阈值:", round(truncation_quantile, 3), "\n")
cat("[04_iptw] 极端值数量:", extreme_count, "\n")

# 应用截断
ipw_fit$weights_truncated <- pmin(ipw_fit$weights, truncation_quantile)

# 6. 创建加权调查设计对象 -------------------------------------------
data_select$weights_truncated <- ipw_fit$weights_truncated

data_iptw <- svydesign(
  ids = ~1,
  data = data_select,
  weights = ~weights_truncated,
  nest = TRUE
)

# 7. 保存 IPTW 数据 -------------------------------------------------
save(data_select, ipw_fit, data_iptw, 
     file = file.path(load_dir, "04_iptw.rda"))

cat("[04_iptw] IPTW 数据已保存\n")

# 8. 生成 IPTW 后的基线表 -------------------------------------------
# 正态分布检验
normal_vars <- character(0)
for (var in continuous_vars) {
  if (var %in% names(data_select)) {
    var_data <- data_select[[var]]
    var_data <- var_data[!is.na(var_data)]
    if (length(var_data) > 3 && length(var_data) <= 5000) {
      if (shapiro.test(var_data)$p.value > 0.05) {
        normal_vars <- c(normal_vars, var)
      }
    }
  }
}

# 统计表示方式
statistic_list <- list()
statistic_list["all_categorical()"] <- "{n} ({p}%)"
statistic_list["all_continuous()"] <- "{median} [{p25}, {p75}]"
for (var in normal_vars) {
  statistic_list[[var]] <- "{mean} ({sd})"
}

# 生成加权基线表
tbl_iptw <- tbl_svysummary(
  data = data_iptw,
  by = all_of(treatment_var),
  include = all_of(tbl_vars),
  type = list(all_continuous() ~ "continuous", all_categorical() ~ "categorical"),
  statistic = statistic_list,
  digits = list(all_continuous() ~ 2, all_categorical() ~ 0),
  label = var_labels
) %>%
  add_difference(
    test = list(all_continuous() ~ "smd", all_categorical() ~ "smd")
  ) %>%
  add_overall() %>%
  modify_header(
    label = "**Characteristic**",
    all_stat_cols() ~ "**{level}**\nN = {sprintf('%.2f', n)}",
    difference = "**SMD**"
  ) %>%
  modify_fmt_fun(
    difference = function(x) {
      ifelse(!is.na(x),
             ifelse(abs(as.numeric(x)) < 0.1, paste0(x, "*"), x),
             x)
    }
  ) %>%
  modify_footnote(difference = "*SMD < 0.1 indicates excellent balance") %>%
  modify_caption("**Table 1b. Baseline Characteristics After IPTW**")

# 保存表格
tbl_iptw %>%
  as_flex_table() %>%
  flextable::save_as_docx(
    path = file.path(outcome_dir, "tables", "Table1b_IPTW_Baseline.docx")
  )

cat("[04_iptw] IPTW 基线表已保存\n")

# 9. 协变量平衡图 ---------------------------------------------------
iptw_balance <- bal.tab(
  fml,
  data = data_select,
  weights = ipw_fit$weights_truncated,
  method = "weighting",
  un = TRUE
)

# 保存平衡图
cairo_pdf(
  file.path(outcome_dir, "figures", "PSM_Balance_Plot.pdf"),
  width = 12, height = 8
)
love.plot(
  iptw_balance,
  thresholds = c(m = 0.1),
  var.order = "unadjusted",
  title = "Standardized Mean Differences Before and After IPTW",
  sample.names = c("Before IPTW", "After IPTW"),
  colors = ggsci::pal_npg()(2),
  abs = TRUE,
  stars = "raw",
  xlab = "Standardized Mean Difference"
)
dev.off()

cat("[04_iptw] 平衡图已保存\n")

# 10. 权重分布图 ----------------------------------------------------
weight_data <- data.frame(
  Weight = ipw_fit$weights,
  Group = data_select[[treatment_var]]
)

weight_plot <- ggplot(weight_data, aes(x = Weight, fill = Group)) +
  geom_histogram(binwidth = 0.05, alpha = 0.6, position = "identity") +
  geom_density(aes(color = Group), alpha = 0.2) +
  geom_vline(xintercept = truncation_quantile, color = "darkred", 
             linetype = "dashed") +
  labs(
    title = "Distribution of IPTW Weights",
    x = "IPTW Weight",
    y = "Frequency",
    fill = "Group",
    color = "Group"
  ) +
  theme_bw() +
  facet_wrap(~Group, ncol = 2)

ggsave(
  file.path(outcome_dir, "figures", "IPTW_Weight_Distribution.pdf"),
  weight_plot, width = 10, height = 6
)

cat("[04_iptw] 权重分布图已保存\n")
cat("[04_iptw] IPTW 分析完成\n")
