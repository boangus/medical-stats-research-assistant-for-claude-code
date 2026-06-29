# 随机生存森林模板: RSF 拟合、变量重要性、偏依赖、C-index、与 Cox 比较
# ==========================================================================
# 核心方法: randomForestSRC 随机生存森林, VIMP + 最小深度变量选择,
#           个体风险预测, 偏依赖图, C-index 一致性评估
# 适用场景: 高维生存数据、非线性/交互效应建模、Cox 模型补充/比较
#
# 依赖:
#   install.packages(c("randomForestSRC", "ggRandomForests", "survival",
#                       "ggplot2", "dplyr"))
#
# 作者: MSRA Team | 版本: 0.1.0

# --- 依赖安装与加载 ---
for (pkg in c("randomForestSRC", "ggRandomForests", "survival",
              "ggplot2", "dplyr")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}
library(randomForestSRC); library(ggRandomForests); library(survival)
library(ggplot2); library(dplyr)


# ==============================================================================
# 1. 随机生存森林拟合
# ==============================================================================

#' 拟合随机生存森林
#'
#' 使用 randomForestSRC 拟合随机生存森林模型。
#'
#' @param time     character, 随访时间列名
#' @param status   character, 事件指示列名 (1=事件, 0=删失)
#' @param covariates character vector, 协变量列名
#' @param data     data.frame
#' @param ntree    integer, 树的数量 (默认 500)
#' @param nodesize integer, 终端节点最小样本量 (默认 15)
#' @param mtry     integer, 每次分裂候选变量数 (NULL 则自动)
#' @return rfsrc 对象
#' @export
#' @examples
#' \dontrun{
#' fit <- rsf_fit("os_time", "os_status",
#'                c("age", "stage", "biomarker"), data = surv_data)
#' print(fit)
#' }
rsf_fit <- function(time, status, covariates, data,
                    ntree = 500, nodesize = 15, mtry = NULL) {
  stopifnot(
    "data 必须是 data.frame"  = is.data.frame(data),
    "time 列必须存在"         = time %in% names(data),
    "status 列必须存在"       = status %in% names(data)
  )
  missing_covs <- setdiff(covariates, names(data))
  if (length(missing_covs) > 0) {
    stop(sprintf("以下协变量不存在: %s", paste(missing_covs, collapse = ", ")))
  }

  fml <- as.formula(sprintf("Surv(%s, %s) ~ %s",
                            time, status, paste(covariates, collapse = " + ")))

  message(sprintf("拟合随机生存森林: ntree=%d, nodesize=%d ...", ntree, nodesize))
  args <- list(formula = fml, data = data, ntree = ntree,
               nodesize = nodesize, importance = TRUE,
               seed = 42)
  if (!is.null(mtry)) args$mtry <- mtry

  fit <- do.call(rfsrc, args)

  cat(sprintf("RSF 拟合完成: OOB 误差 = %.4f\n", max(fit$err.rate)))
  fit
}


# ==============================================================================
# 2. 变量重要性 (VIMP + 最小深度)
# ==============================================================================

#' 变量重要性评估
#'
#' 计算并可视化变量重要性 (VIMP) 和最小深度 (Minimal Depth)。
#'
#' @param model rfsrc 对象
#' @return list: vimp_df (VIMP 数据框), depth_df (最小深度数据框), plot (ggplot)
#' @export
#' @examples
#' \dontrun{
#' imp <- rsf_importance(fit)
#' print(imp$vimp_df)
#' print(imp$plot)
#' }
rsf_importance <- function(model) {
  # --- VIMP ---
  vimp_obj <- vimp(model)
  vimp_df <- data.frame(
    variable   = names(vimp_obj$importance),
    importance = round(vimp_obj$importance, 4)
  )
  vimp_df <- vimp_df[order(-vimp_df$importance), ]
  rownames(vimp_df) <- NULL

  # --- 最小深度 ---
  depth_obj <- var.select(model, method = "md")
  depth_df <- data.frame(
    variable     = rownames(depth_obj$topvars),
    minimal_depth = round(depth_obj$topvars[, "depth"], 4),
    stringsAsFactors = FALSE
  )

  # --- 可视化 (VIMP 条形图) ---
  vimp_df$variable <- factor(vimp_df$variable,
                             levels = rev(vimp_df$variable))
  p <- ggplot(vimp_df, aes(x = variable, y = importance,
                            fill = importance > 0)) +
    geom_col(width = 0.7) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "grey50") +
    scale_fill_manual(values = c("TRUE" = "#2166AC", "FALSE" = "#B2182B"),
                      guide = "none") +
    coord_flip() +
    labs(
      title = "随机生存森林: 变量重要性 (VIMP)",
      x = NULL, y = "VIMP (负值 = 删除后模型改善)"
    ) +
    theme_minimal(base_size = 12)

  list(vimp_df = vimp_df, depth_df = depth_df, plot = p)
}


# ==============================================================================
# 3. 个体风险预测
# ==============================================================================

#' 个体风险预测
#'
#' 对新数据进行个体生存概率和风险评分预测。
#'
#' @param model   rfsrc 对象
#' @param newdata data.frame, 新数据 (需含相同协变量)
#' @return data.frame: 个体 ID、风险评分、时间点生存概率
#' @export
#' @examples
#' \dontrun{
#' pred <- rsf_predict(fit, newdata = test_data)
#' head(pred)
#' }
rsf_predict <- function(model, newdata) {
  pred <- predict(model, newdata = newdata)

  n <- nrow(newdata)
  times <- pred$time.interest

  # 构建生存概率矩阵
  surv_mat <- pred$survival
  colnames(surv_mat) <- sprintf("S_t%.1f", times)

  # 风险评分: 预测的累积风险 (1 - 最终生存概率)
  risk_scores <- 1 - surv_mat[, ncol(surv_mat)]

  result <- data.frame(
    id          = seq_len(n),
    risk_score  = round(risk_scores, 4),
    surv_mat,
    check.names = FALSE
  )
  rownames(result) <- NULL

  message(sprintf("预测完成: %d 个体, %d 时间点", n, length(times)))
  result
}


# ==============================================================================
# 4. 偏依赖图 (Partial Dependence)
# ==============================================================================

#' 偏依赖图
#'
#' 绘制指定变量的偏依赖图, 展示该变量对预测风险的边际效应。
#'
#' @param model rfsrc 对象
#' @param var   character, 目标变量名
#' @param n_pts integer, 网格点数 (默认 50)
#' @return ggplot 对象
#' @export
#' @examples
#' \dontrun{
#' p <- rsf_partial_effect(fit, var = "age")
#' print(p)
#' }
rsf_partial_effect <- function(model, var, n_pts = 50) {
  stopifnot("var 必须是模型变量" = var %in% model$xvar.names)

  # 使用 randomForestSRC 内置 partial 函数
  pd_obj <- partial(model, partial.type = "surv",
                    partial.xvar = var, partial.time = model$time.interest,
                    partial.npts = n_pts, seed = 42)

  pd_df <- data.frame(
    x_val    = pd_obj$x.unq,
    surv_avg = apply(pd_obj$yhat, 1, mean, na.rm = TRUE)
  )
  names(pd_df) <- c("x_val", "surv_avg")

  p <- ggplot(pd_df, aes(x = x_val, y = surv_avg)) +
    geom_line(linewidth = 1, color = "#2166AC") +
    geom_point(size = 1.5, color = "#2166AC") +
    labs(
      title = sprintf("偏依赖图: %s", var),
      x = var, y = "平均预测生存概率"
    ) +
    theme_minimal(base_size = 12)

  p
}


# ==============================================================================
# 5. C-index (一致性指数)
# ==============================================================================

#' 计算 C-index
#'
#' 基于模型 OOB 预测计算 Harrell's C-index。
#'
#' @param model rfsrc 对象
#' @return list: cindex (数值), se (标准误), ci (95% CI)
#' @export
#' @examples
#' \dontrun{
#' ci_res <- rsf_cindex(fit)
#' cat(sprintf("C-index: %.4f [%.4f, %.4f]\n",
#'             ci_res$cindex, ci_res$ci[1], ci_res$ci[2]))
#' }
rsf_cindex <- function(model) {
  pred <- predict(model)

  # 从 OOB 预测获取
  surv_oob <- pred$survival.oob
  if (is.null(surv_oob)) {
    message("OOB 预测不可用, 使用训练集预测替代")
    surv_oob <- pred$survival
  }

  # 使用最后时间点生存概率作为风险评分
  risk_scores <- 1 - surv_oob[, ncol(surv_oob)]

  time   <- model$yvar[, 1]
  status <- model$yvar[, 2]

  # Harrell's C-index via survival package
  concordance_obj <- concordance(Surv(time, status) ~ risk_scores)

  cindex_val <- concordance_obj$concordance
  se_val     <- sqrt(concordance_obj$var)

  ci_lower <- max(0, cindex_val - 1.96 * se_val)
  ci_upper <- min(1, cindex_val + 1.96 * se_val)

  cat(sprintf("C-index: %.4f (SE=%.4f) [%.4f, %.4f]\n",
              cindex_val, se_val, ci_lower, ci_upper))

  list(cindex = round(cindex_val, 4), se = round(se_val, 4),
       ci = round(c(ci_lower, ci_upper), 4))
}


# ==============================================================================
# 6. RSF vs Cox C-index 比较
# ==============================================================================

#' 比较 RSF 与 Cox 模型的 C-index
#'
#' 对同一数据分别拟合 RSF 和 Cox 模型, 比较两者 C-index。
#'
#' @param model_rsf rfsrc 对象 (已拟合)
#' @param model_cox coxph 对象 (已拟合)
#' @param data      data.frame (测试集)
#' @return list: rsf_cindex, cox_cindex, comparison (数据框)
#' @export
#' @examples
#' \dontrun{
#' rsf_fit <- rsf_fit("os_time", "os_status", covariates, train_data)
#' cox_fit <- coxph(Surv(os_time, os_status) ~ ., data = train_data)
#' cmp <- rsf_compare_cox(rsf_fit, cox_fit, test_data)
#' print(cmp$comparison)
#' }
rsf_compare_cox <- function(model_rsf, model_cox, data) {
  # --- RSF C-index ---
  rsf_pred <- predict(model_rsf, newdata = data)
  rsf_risk <- 1 - rsf_pred$survival[, ncol(rsf_pred$survival)]

  time   <- data[[model_rsf$yvar.names[1]]]
  status <- data[[model_rsf$yvar.names[2]]]

  rsf_c <- concordance(Surv(time, status) ~ rsf_risk)
  rsf_cindex <- rsf_c$concordance
  rsf_se     <- sqrt(rsf_c$var)

  # --- Cox C-index ---
  cox_risk <- predict(model_cox, newdata = data, type = "risk")
  cox_c    <- concordance(Surv(time, status) ~ cox_risk)
  cox_cindex <- cox_c$concordance
  cox_se     <- sqrt(cox_c$var)

  # --- 汇总 ---
  comparison <- data.frame(
    Model    = c("Random Survival Forest", "Cox PH"),
    C_index  = round(c(rsf_cindex, cox_cindex), 4),
    SE       = round(c(rsf_se, cox_se), 4),
    CI_lower = round(c(rsf_cindex - 1.96 * rsf_se,
                       cox_cindex - 1.96 * cox_se), 4),
    CI_upper = round(c(rsf_cindex + 1.96 * rsf_se,
                       cox_cindex + 1.96 * cox_se), 4)
  )

  cat("=== RSF vs Cox C-index 比较 ===\n")
  print(comparison)

  diff_val <- rsf_cindex - cox_cindex
  diff_se  <- sqrt(rsf_se^2 + cox_se^2)
  cat(sprintf("\nC-index 差异 (RSF - Cox): %.4f (SE=%.4f) [%.4f, %.4f]\n",
              diff_val, diff_se,
              diff_val - 1.96 * diff_se,
              diff_val + 1.96 * diff_se))

  list(rsf_cindex = rsf_cindex, cox_cindex = cox_cindex,
       comparison = comparison,
       difference = round(c(diff_val, diff_se), 4))
}


# ==============================================================================
# 7. 完整工作流演示
# ==============================================================================

#' 随机生存森林完整工作流
#'
#' 使用模拟生存数据演示: RSF 拟合 -> 变量重要性 -> 风险预测 ->
#' 偏依赖 -> C-index -> 与 Cox 比较。
#'
#' @return 无 (控制台输出 + ggplot 图形)
#' @export
full_rsf_workflow <- function() {
  set.seed(2024)
  n <- 400

  # --- 模拟数据 ---
  age    <- rnorm(n, 60, 10)
  stage  <- sample(1:4, n, replace = TRUE, prob = c(0.3, 0.3, 0.25, 0.15))
  biomarker <- rnorm(n, mean = 5, sd = 2)
  treatment <- rbinom(n, 1, 0.5)

  # 生存时间 (含非线性效应)
  lp <- 0.03 * age + 0.5 * (stage >= 3) + 0.15 * biomarker^2 / 10 -
        0.4 * treatment + rnorm(n, 0, 0.3)
  surv_time <- rexp(n, rate = exp(lp - 3))
  censor    <- runif(n, 0, quantile(surv_time, 0.80))
  os_time   <- pmin(surv_time, censor)
  os_status <- as.integer(surv_time <= censor)

  surv_data <- data.frame(os_time, os_status, age, stage, biomarker,
                          treatment = factor(treatment))
  covariates <- c("age", "stage", "biomarker", "treatment")

  cat(sprintf("模拟数据: n=%d, 事件数=%d, 中位随访=%.1f\n",
              n, sum(os_status), median(os_time)))

  # --- 训练/测试分割 ---
  idx_train <- sample(seq_len(n), size = floor(n * 0.7))
  train_data <- surv_data[idx_train, ]
  test_data  <- surv_data[-idx_train, ]

  cat("\n====== 工作流 1: RSF 拟合 ======\n")
  fit <- rsf_fit("os_time", "os_status", covariates, train_data,
                 ntree = 300, nodesize = 10)

  cat("\n====== 工作流 2: 变量重要性 ======\n")
  imp <- rsf_importance(fit)
  print(imp$vimp_df)
  print(imp$plot)

  cat("\n====== 工作流 3: 个体风险预测 ======\n")
  pred <- rsf_predict(fit, newdata = test_data)
  print(head(pred))

  cat("\n====== 工作流 4: 偏依赖图 ======\n")
  p_pd <- rsf_partial_effect(fit, var = "age")
  print(p_pd)

  cat("\n====== 工作流 5: C-index ======\n")
  ci_res <- rsf_cindex(fit)

  cat("\n====== 工作流 6: RSF vs Cox 比较 ======\n")
  cox_fit <- coxph(Surv(os_time, os_status) ~ age + stage + biomarker +
                   treatment, data = train_data)
  cmp <- rsf_compare_cox(fit, cox_fit, test_data)

  cat("\n随机生存森林工作流演示完成。\n")
  invisible(NULL)
}


# --- 运行演示 ---
# full_rsf_workflow()
