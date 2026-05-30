# 生存分析模板 (Survival Analysis Template)
# 适用于时间-事件数据分析

# 加载必要的包
if (!require("survival")) install.packages("survival")
if (!require("survminer")) install.packages("survminer")
if (!require("gtsummary")) install.packages("gtsummary")
library(survival)
library(survminer)
library(gtsummary)

# ==================== 1. Kaplan-Meier 生存曲线 ====================

# 创建生存对象
# time: 随访时间
# status: 事件状态 (1=事件发生, 0=删失)
surv_obj <- Surv(time = data$time, event = data$status)

# 拟合 KM 曲线 (按分组)
fit_km <- survfit(surv_obj ~ group, data = data)

# 绘制 KM 曲线
km_plot <- ggsurvplot(
  fit_km,
  data = data,
  pval = TRUE,                    # 显示 log-rank 检验 p 值
  pval.method = TRUE,             # 显示检验方法
  conf.int = TRUE,                # 显示置信区间
  risk.table = TRUE,              # 显示风险表
  risk.table.col = "strata",      # 风险表按分层着色
  linetype = 1,                   # 线型
  surv.median.line = "hv",        # 显示中位生存时间线
  ggtheme = theme_bw(),           # 主题
  palette = "jco",                # 配色方案
  title = "Kaplan-Meier Survival Curve",
  xlab = "Time (months)",
  ylab = "Survival Probability",
  ncensor.plot = TRUE,            # 显示删失数量
  ncensor.plot.height = 0.25
)

# 打印图形
print(km_plot)

# 保存图形
# ggsave("KM_curve.png", km_plot$plot, width = 8, height = 6, dpi = 300)

# ==================== 2. Log-rank 检验 ====================

# 比较组间生存差异
logrank_test <- survdiff(surv_obj ~ group, data = data)
print(logrank_test)

# 提取 p 值
logrank_pvalue <- 1 - pchisq(logrank_test$chisq, length(logrank_test$n) - 1)
cat("Log-rank test p-value:", format.pval(logrank_pvalue, eps = 0.001), "\n")

# ==================== 3. Cox 比例风险模型 ====================

# 单变量 Cox 回归
uni_cox <- coxph(surv_obj ~ age, data = data)
summary(uni_cox)

# 多变量 Cox 回归
multi_cox <- coxph(surv_obj ~ age + sex + treatment + stage, data = data)
summary(multi_cox)

# 使用 gtsummary 创建漂亮的表格
cox_table <- tbl_regression(
  multi_cox,
  exponentiate = TRUE,           # 显示 HR 而不是 log(HR)
  label = list(
    age ~ "Age (years)",
    sex ~ "Sex",
    treatment ~ "Treatment Group",
    stage ~ "Disease Stage"
  )
) %>%
  add_global_p() %>%              # 添加全局 p 值
  add_n() %>%                     # 添加样本量
  modify_header(label = "**Variable**") %>%
  modify_caption("**Table 2. Cox Proportional Hazards Model**")

print(cox_table)

# ==================== 4. 比例风险假设检验 ====================

# Schoenfeld 残差检验
ph_test <- cox.zph(multi_cox)
print(ph_test)

# 绘制 Schoenfeld 残差图
par(mfrow = c(2, 2))
plot(ph_test)
par(mfrow = c(1, 1))

# 如果比例风险假设违反，考虑:
# 1. 分层 Cox 模型
# 2. 时依系数模型
# 3. 加速失效时间模型 (AFT)

# ==================== 5. 分层 Cox 模型 (如果 PH 假设违反) ====================

# 按违反 PH 假设的变量分层
stratified_cox <- coxph(surv_obj ~ age + sex + strata(stage), data = data)
summary(stratified_cox)

# ==================== 6. 时依 Cox 模型 ====================

# 创建时依系数
# 例如: 治疗效应随时间变化
tdc_cox <- coxph(
  surv_obj ~ age + sex + treatment + tt(treatment), 
  data = data,
  tt = function(x, t, ...) x * log(t + 1)  # 时间变换函数
)
summary(tdc_cox)

# ==================== 7. 竞争风险分析 (Fine-Gray 模型) ====================

if (!require("cmprsk")) install.packages("cmprsk")
library(cmprsk)

# 假设有两种事件: 1=目标事件, 2=竞争事件
# 估计累积发生率函数 (CIF)
cif_fit <- cuminc(
  ftime = data$time,
  fstatus = data$event_type,  # 1=目标事件, 2=竞争事件, 0=删失
  group = data$group
)

# 绘制 CIF 曲线
plot(cif_fit, 
     curvlab = c("Group 1 - Event", "Group 1 - Competing", 
                 "Group 2 - Event", "Group 2 - Competing"),
     xlab = "Time (months)",
     ylab = "Cumulative Incidence",
     col = c("red", "pink", "blue", "lightblue"),
     lty = c(1, 2, 1, 2))

# Fine-Gray 模型 (次分布风险模型)
fg_model <- crr(
  ftime = data$time,
  fstatus = data$event_type,
  cov1 = cbind(data$age, data$sex, data$treatment),
  failcode = 1,      # 目标事件编码
  cencode = 0        # 删失编码
)
summary(fg_model)

# ==================== 8. 生存预测 ====================

# 预测特定时间点的生存概率
new_data <- data.frame(
  age = c(50, 60, 70),
  sex = c("Male", "Female", "Male"),
  treatment = c("A", "B", "A"),
  stage = c("I", "II", "III")
)

# 预测生存概率
surv_pred <- survfit(multi_cox, newdata = new_data)

# 提取 1年、3年、5年生存率
time_points <- c(12, 36, 60)  # 月份
surv_summary <- summary(surv_pred, times = time_points)

# 创建预测表格
pred_table <- data.frame(
  Patient = 1:nrow(new_data),
  Time_1yr = surv_summary$surv[1:nrow(new_data)],
  Time_3yr = surv_summary$surv[nrow(new_data) + 1:nrow(new_data)],
  Time_5yr = surv_summary$surv[2*nrow(new_data) + 1:nrow(new_data)]
)
print(pred_table)

# ==================== 9. 模型评估 ====================

# C-index (Harrell's C)
c_index <- survConcordance(surv_obj ~ predict(multi_cox))
cat("C-index:", c_index$concordance, "\n")

# 时间依赖 ROC (如果安装 timeROC 包)
# if (!require("timeROC")) install.packages("timeROC")
# library(timeROC)
# td_roc <- timeROC(
#   T = data$time,
#   delta = data$status,
#   marker = predict(multi_cox),
#   cause = 1,
#   times = c(12, 36, 60)
# )

# ==================== 10. 结果汇总函数 ====================

survival_summary <- function(fit, times = c(12, 36, 60)) {
  
  # 提取特定时间点的生存估计
  summary_fit <- summary(fit, times = times, extend = TRUE)
  
  # 创建结果表格
  result <- data.frame(
    Time = summary_fit$time,
    Survival = summary_fit$surv,
    Lower_CI = summary_fit$lower,
    Upper_CI = summary_fit$upper,
    At_Risk = summary_fit$n.risk
  )
  
  return(result)
}

# 使用示例
# summary_results <- survival_summary(fit_km, times = c(12, 24, 36, 60))
# print(summary_results)
