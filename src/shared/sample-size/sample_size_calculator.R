# sample_size_calculator.R — 样本量计算模板
# ============================================
# 适用于：临床试验和观察性研究的样本量/把握度计算
#
# 依赖: pwr, survival (可选)
# 安装: install.packages(c("pwr", "survival"))
#
# 作者: MSRA Team
# 版本: 0.1.0

# ============================================================================
# 1. 连续变量（t 检验）
# ============================================================================

#' 两独立样本 t 检验的样本量计算
#'
#' @param delta 组间均值差
#' @param sd 标准差
#' @param alpha 显著性水平（默认 0.05）
#' @param power 把握度（默认 0.80）
#' @param ratio 对照组:试验组比例（默认 1）
#' @param sided 单/双侧检验（默认 "two.sided"）
#'
#' @return list(n_total, n1, n2, power)
calc_sample_size_t <- function(delta, sd,
                               alpha = 0.05,
                               power = 0.80,
                               ratio = 1,
                               sided = "two.sided") {

  if (!requireNamespace("pwr", quietly = TRUE)) {
    install.packages("pwr")
  }
  library(pwr)

  # 效应量 Cohen's d
  d <- delta / sd

  # 计算
  result <- pwr.t.test(
    d = d,
    sig.level = alpha,
    power = power,
    type = "two.sample",
    alternative = sided
  )

  n_per_group <- ceiling(result$n)
  n1 <- n_per_group
  n2 <- ceiling(n_per_group * ratio)

  return(list(
    n_total = n1 + n2,
    n1 = n1,
    n2 = n2,
    n_per_group = n_per_group,
    power = power,
    delta = delta,
    sd = sd,
    d = d,
    alpha = alpha,
    method = "Two-sample t-test"
  ))
}


#' 配对 t 检验的样本量计算
#'
#' @param delta 配对差值均值
#' @param sd_diff 差值标准差
#' @param alpha,power,sided 同上
calc_sample_size_paired_t <- function(delta, sd_diff,
                                       alpha = 0.05,
                                       power = 0.80,
                                       sided = "two.sided") {
  library(pwr)
  d <- delta / sd_diff

  result <- pwr.t.test(
    d = d,
    sig.level = alpha,
    power = power,
    type = "paired",
    alternative = sided
  )

  return(list(
    n = ceiling(result$n),
    power = power,
    d = d,
    alpha = alpha,
    method = "Paired t-test"
  ))
}


# ============================================================================
# 2. 分类变量（卡方检验）
# ============================================================================

#' 两样本率比较的样本量计算
#'
#' @param p1 对照组率
#' @param p2 试验组率
#' @param alpha,power,ratio,sided
calc_sample_size_prop <- function(p1, p2,
                                   alpha = 0.05,
                                   power = 0.80,
                                   ratio = 1,
                                   sided = "two.sided") {

  library(pwr)

  # 效应量 h
  h <- ES.h(p1, p2)

  result <- pwr.2p.test(
    h = h,
    sig.level = alpha,
    power = power,
    alternative = sided
  )

  n_per_group <- ceiling(result$n)
  n1 <- n_per_group
  n2 <- ceiling(n_per_group * ratio)

  return(list(
    n_total = n1 + n2,
    n1 = n1,
    n2 = n2,
    n_per_group = n_per_group,
    power = power,
    p1 = p1,
    p2 = p2,
    h = h,
    alpha = alpha,
    method = "Two-sample proportion test"
  ))
}


# ============================================================================
# 3. 方差分析 (ANOVA)
# ============================================================================

#' ANOVA 的样本量计算
#'
#' @param k 组数
#' @param f 效应量 f (Cohen's f, 小=0.1, 中=0.25, 大=0.4)
#' @param alpha,power
calc_sample_size_anova <- function(k, f,
                                    alpha = 0.05,
                                    power = 0.80) {
  library(pwr)

  result <- pwr.anova.test(
    k = k,
    f = f,
    sig.level = alpha,
    power = power
  )

  return(list(
    n_per_group = ceiling(result$n),
    n_total = ceiling(result$n) * k,
    power = power,
    f = f,
    alpha = alpha,
    method = "One-way ANOVA"
  ))
}


# ============================================================================
# 4. 生存分析（Log-rank 检验）
# ============================================================================

#' 生存分析的样本量计算（Freedman 方法）
#'
#' @param hr 风险比 (Hazard Ratio)
#' @param prop_event 事件发生率（总受试者中发生事件的比例）
#' @param alpha,power,sided
calc_sample_size_survival <- function(hr,
                                       prop_event = 0.5,
                                       alpha = 0.05,
                                       power = 0.80,
                                       sided = "two.sided") {

  z_alpha <- ifelse(sided == "two.sided",
                    qnorm(1 - alpha / 2), qnorm(1 - alpha))
  z_beta <- qnorm(power)

  # 所需事件数 (Schoenfeld 公式)
  n_events <- ((z_alpha + z_beta)^2) / ((log(hr))^2 * prop_event * (1 - prop_event))

  # 总样本量
  n_total <- ceiling(n_events / prop_event)

  # 每组的样本量（假设 1:1 分配）
  n_per_group <- ceiling(n_total / 2)

  return(list(
    n_events = ceiling(n_events),
    n_total = n_total,
    n_per_group = n_per_group,
    hr = hr,
    prop_event = prop_event,
    power = power,
    alpha = alpha,
    method = "Survival analysis (Schoenfeld)"
  ))
}


# ============================================================================
# 5. 回归分析
# ============================================================================

#' 多元线性回归的样本量计算
#'
#' @param n_predictors 预测变量数
#' @param effect_size 效应量 f² (小=0.02, 中=0.15, 大=0.35)
#' @param alpha,power
calc_sample_size_regression <- function(n_predictors,
                                         effect_size = 0.15,
                                         alpha = 0.05,
                                         power = 0.80) {
  library(pwr)

  result <- pwr.f2.test(
    u = n_predictors,
    f2 = effect_size,
    sig.level = alpha,
    power = power
  )

  n_total <- ceiling(result$v) + n_predictors + 1

  return(list(
    n_total = n_total,
    n_predictors = n_predictors,
    f2 = effect_size,
    power = power,
    alpha = alpha,
    method = "Multiple linear regression"
  ))
}


#' Logistic 回归的样本量计算（EPV 规则）
#'
#' @param n_predictors 预测变量数
#' @param prop_events 事件比例
#' @param epv Events Per Variable，默认 10
#'
#' @return list(n_total, n_events, epv)
calc_sample_size_logistic <- function(n_predictors,
                                       prop_events,
                                       epv = 10) {

  n_events <- n_predictors * epv
  n_total <- ceiling(n_events / prop_events)

  return(list(
    n_total = n_total,
    n_events = n_events,
    n_predictors = n_predictors,
    epv = epv,
    prop_events = prop_events,
    method = "Logistic regression (EPV rule)"
  ))
}


# ============================================================================
# 6. 等效性/非劣效性试验
# ============================================================================

#' 非劣效性试验的样本量计算（连续变量）
#'
#' @param delta 非劣效界值
#' @param sd 标准差
#' @param alpha 通常 0.025（单侧）
#' @param power 把握度
calc_sample_size_noninf <- function(delta, sd,
                                     alpha = 0.025,
                                     power = 0.80) {
  z_alpha <- qnorm(1 - alpha)
  z_beta <- qnorm(power)

  n_per_group <- ceiling(2 * (z_alpha + z_beta)^2 * sd^2 / delta^2)

  return(list(
    n_per_group = n_per_group,
    n_total = n_per_group * 2,
    delta = delta,
    sd = sd,
    alpha = alpha,
    power = power,
    method = "Non-inferiority trial"
  ))
}


# ============================================================================
# 7. 把握度计算（反向计算）
# ============================================================================

#' 已知样本量反向计算把握度（t 检验）
#'
#' @param n 每组样本量
#' @param delta 组间均值差
#' @param sd 标准差
#' @param alpha
calc_power_t <- function(n, delta, sd, alpha = 0.05, sided = "two.sided") {
  library(pwr)
  d <- delta / sd

  result <- pwr.t.test(
    n = n,
    d = d,
    sig.level = alpha,
    type = "two.sample",
    alternative = sided
  )

  return(list(
    power = result$power,
    n = n,
    d = d,
    alpha = alpha,
    method = "Power calculation (t-test)"
  ))
}


# ============================================================================
# 示例
# ============================================================================
if (FALSE) {
  # t 检验
  print(calc_sample_size_t(delta = 5, sd = 10))

  # 率的比较
  print(calc_sample_size_prop(p1 = 0.3, p2 = 0.5))

  # 生存分析
  print(calc_sample_size_survival(hr = 0.7))

  # Logistic 回归
  print(calc_sample_size_logistic(n_predictors = 5, prop_events = 0.3))

  # 非劣效性
  print(calc_sample_size_noninf(delta = 3, sd = 8))
}

cat("✅ sample_size_calculator.R 已加载\n")
cat("可用函数:\n")
cat("  calc_sample_size_t()           - t 检验样本量\n")
cat("  calc_sample_size_paired_t()    - 配对 t 检验样本量\n")
cat("  calc_sample_size_prop()        - 率比较样本量\n")
cat("  calc_sample_size_anova()       - ANOVA 样本量\n")
cat("  calc_sample_size_survival()    - 生存分析样本量\n")
cat("  calc_sample_size_regression()  - 回归分析样本量\n")
cat("  calc_sample_size_logistic()    - Logistic EPV 样本量\n")
cat("  calc_sample_size_noninf()      - 非劣效性试验样本量\n")
cat("  calc_power_t()                 - 反向把握度计算\n")
