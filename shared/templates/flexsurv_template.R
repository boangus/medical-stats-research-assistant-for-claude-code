# 灵活参数生存模型模板: Royston-Parmar 模型、分布族比较、RMST、风险函数
# ==========================================================================
# 核心方法: flexsurv 参数模型、AIC/BIC 分布比较、限制性平均生存时间 (RMST)
# 适用场景: 生存分析中参数模型选择、外推预测、非标准风险函数建模
#
# 依赖:
#   install.packages(c("flexsurv", "survival", "ggplot2", "dplyr", "broom"))
#
# 作者: MSRA Team | 版本: 0.1.0

# --- 依赖安装与加载 ---
for (pkg in c("flexsurv", "survival", "ggplot2", "dplyr", "broom")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}
library(flexsurv); library(survival); library(ggplot2)
library(dplyr); library(broom)


# ==============================================================================
# 1. 灵活参数生存模型拟合
# ==============================================================================

#' 拟合灵活参数生存模型
#'
#' 使用 flexsurv::flexsurvreg 拟合参数生存模型, 支持 Weibull、广义 Gamma、
#' 对数正态、Gompertz 等分布族。
#'
#' @param time      numeric vector, 随访时间
#' @param status    numeric vector, 事件指示 (1=事件, 0=删失)
#' @param covariates character vector, 协变量列名 (NULL 则拟合截距模型)
#' @param data      data.frame, 包含上述变量的数据集
#' @param dist      character, 分布族: "weibull" | "gengamma" | "lnorm" | "gompertz"
#' @return flexsurvreg 对象
#' @export
#' @examples
#' \dontrun{
#' fit <- flexsurv_fit(time = "os_time", status = "os_status",
#'                     covariates = c("age", "trt"), data = surv_data,
#'                     dist = "weibull")
#' summary(fit)
#' }
flexsurv_fit <- function(time, status, covariates = NULL, data,
                         dist = c("weibull", "gengamma", "lnorm", "gompertz")) {
  dist <- match.arg(dist)

  stopifnot(
    "data 必须是 data.frame"  = is.data.frame(data),
    "time 列必须存在"         = time %in% names(data),
    "status 列必须存在"       = status %in% names(data)
  )
  if (!is.null(covariates)) {
    missing_covs <- setdiff(covariates, names(data))
    if (length(missing_covs) > 0) {
      stop(sprintf("以下协变量不存在: %s", paste(missing_covs, collapse = ", ")))
    }
  }

  # 构建公式
  if (is.null(covariates) || length(covariates) == 0) {
    fml <- as.formula(sprintf("Surv(%s, %s) ~ 1", time, status))
  } else {
    fml <- as.formula(sprintf("Surv(%s, %s) ~ %s",
                              time, status, paste(covariates, collapse = " + ")))
  }

  message(sprintf("拟合 %s 分布参数模型...", dist))
  fit <- flexsurvreg(fml, data = data, dist = dist)

  message(sprintf("AIC: %.2f | BIC: %.2f", AIC(fit), BIC(fit)))
  fit
}


# ==============================================================================
# 2. 多分布族比较 (AIC/BIC)
# ==============================================================================

#' 比较多个分布族的拟合优度
#'
#' 对同一数据拟合多个分布族, 按 AIC/BIC 排序比较。
#'
#' @param time   character, 随访时间列名
#' @param status character, 事件指示列名
#' @param covariates character vector, 协变量列名
#' @param data   data.frame
#' @param dists  character vector, 要比较的分布族 (默认 4 种)
#' @return data.frame: 分布族、AIC、BIC、对数似然 (按 AIC 升序)
#' @export
#' @examples
#' \dontrun{
#' cmp <- flexsurv_compare("os_time", "os_status", c("age", "trt"), data)
#' print(cmp)
#' }
flexsurv_compare <- function(time, status, covariates = NULL, data,
                             dists = c("weibull", "gengamma", "lnorm", "gompertz")) {

  results <- lapply(dists, function(d) {
    message(sprintf("  拟合 %s ...", d))
    tryCatch({
      fit <- flexsurv_fit(time, status, covariates, data, dist = d)
      data.frame(
        distribution = d,
        AIC  = round(AIC(fit), 2),
        BIC  = round(BIC(fit), 2),
        logLik = round(logLik(fit), 2),
        converged = TRUE,
        stringsAsFactors = FALSE
      )
    }, error = function(e) {
      data.frame(
        distribution = d,
        AIC = NA_real_, BIC = NA_real_, logLik = NA_real_,
        converged = FALSE,
        stringsAsFactors = FALSE
      )
    })
  })

  cmp <- do.call(rbind, results)
  cmp <- cmp[order(cmp$AIC), ]
  rownames(cmp) <- NULL

  best <- cmp$distribution[1]
  message(sprintf("\n最佳分布族 (AIC 最小): %s (AIC=%.2f)", best, cmp$AIC[1]))
  cmp
}


# ==============================================================================
# 3. 预测生存曲线 (含置信区间)
# ==============================================================================

#' 预测生存曲线
#'
#' 对给定新协变量预测生存概率随时间变化的曲线及置信区间。
#'
#' @param model   flexsurvreg 对象
#' @param newdata data.frame, 新数据 (一行或多行)
#' @param times   numeric vector, 预测时间点 (NULL 则自动选择)
#' @param ci_level numeric, 置信水平 (默认 0.95)
#' @return ggplot 对象 + 数据框 (存于 $data)
#' @export
#' @examples
#' \dontrun{
#' new_pt <- data.frame(age = 65, trt = 1)
#' p <- flexsurv_survival_curves(fit, newdata = new_pt)
#' print(p)
#' }
flexsurv_survival_curves <- function(model, newdata, times = NULL,
                                     ci_level = 0.95) {
  if (is.null(times)) {
    max_time <- max(model$data$Y[, 1]) * 1.2
    times <- seq(0.01, max_time, length.out = 100)
  }

  pred <- summary(model, newdata = newdata, t = times, ci = TRUE,
                  cl = ci_level, type = "survival")

  # 提取并整合为数据框
  pred_df <- do.call(rbind, lapply(seq_along(pred), function(i) {
    df_i <- as.data.frame(pred[[i]])
    df_i$profile <- paste0("Profile_", i)
    df_i
  }))
  names(pred_df)[names(pred_df) %in% c("time", "est", "lcl", "ucl")] <-
    c("time", "survival", "lower", "upper")[1:ncol(pred_df)]

  p <- ggplot(pred_df, aes(x = time, y = survival, color = profile)) +
    geom_line(linewidth = 1) +
    geom_ribbon(aes(ymin = lower, ymax = upper, fill = profile),
                alpha = 0.2, colour = NA) +
    scale_y_continuous(labels = scales::percent, limits = c(0, 1)) +
    scale_color_brewer(palette = "Set1") +
    scale_fill_brewer(palette = "Set1") +
    labs(
      title = "灵活参数模型: 预测生存曲线",
      x = "时间", y = "生存概率",
      color = "个体", fill = "个体"
    ) +
    theme_minimal(base_size = 12) +
    theme(legend.position = "bottom")

  list(plot = p, data = pred_df)
}


# ==============================================================================
# 4. 限制性平均生存时间 (RMST)
# ==============================================================================

#' 限制性平均生存时间估计
#'
#' 基于拟合模型计算 RMST (曲线下面积), 可选两组比较。
#'
#' @param model   flexsurvreg 对象
#' @param tau     numeric, 截断时间点
#' @param newdata data.frame, 用于预测的协变量 (NULL 则使用截距模型)
#' @param group_var  character, 分组变量列名 (NULL 则仅输出整体 RMST)
#' @return list: rmst (数据框), group_comparison (若指定 group_var)
#' @export
#' @examples
#' \dontrun{
#' rmst_res <- flexsurv_rmst(fit, tau = 60, newdata = data,
#'                            group_var = "trt")
#' print(rmst_res$rmst)
#' }
flexsurv_rmst <- function(model, tau, newdata = NULL, group_var = NULL) {
  stopifnot("tau 必须为正数" = tau > 0)

  # 整体 RMST (基于模型)
  rmst_overall <- rmst_flexsurvreg(model, newdata = newdata, t = tau)

  result <- list(
    rmst = data.frame(
      tau       = tau,
      rmst      = round(rmst_overall[, "est"], 4),
      se        = round(rmst_overall[, "se"], 4),
      lower     = round(rmst_overall[, "lcl"], 4),
      upper     = round(rmst_overall[, "ucl"], 4)
    )
  )

  # 分组比较
  if (!is.null(group_var) && !is.null(newdata) &&
      group_var %in% names(newdata)) {
    groups <- unique(newdata[[group_var]])
    grp_results <- lapply(groups, function(g) {
      idx <- which(newdata[[group_var]] == g)
      nd_g <- newdata[idx[1], , drop = FALSE]
      res_g <- rmst_flexsurvreg(model, newdata = nd_g, t = tau)
      data.frame(
        group  = as.character(g),
        rmst   = round(res_g[, "est"], 4),
        se     = round(res_g[, "se"], 4),
        lower  = round(res_g[, "lcl"], 4),
        upper  = round(res_g[, "ucl"], 4)
      )
    })
    grp_df <- do.call(rbind, grp_results)
    result$group_comparison <- grp_df

    if (nrow(grp_df) == 2) {
      diff_val <- grp_df$rmst[2] - grp_df$rmst[1]
      diff_se  <- sqrt(grp_df$se[1]^2 + grp_df$se[2]^2)
      result$rmst_difference <- data.frame(
        groups = paste(grp_df$group, collapse = " vs "),
        difference = round(diff_val, 4),
        se         = round(diff_se, 4),
        lower      = round(diff_val - 1.96 * diff_se, 4),
        upper      = round(diff_val + 1.96 * diff_se, 4)
      )
      message(sprintf("RMST 差异 (%s): %.4f [%.4f, %.4f]",
                      paste(grp_df$group, collapse = " vs "),
                      diff_val, diff_val - 1.96 * diff_se,
                      diff_val + 1.96 * diff_se))
    }
  }

  result
}


# ==============================================================================
# 5. 风险函数可视化
# ==============================================================================

#' 风险函数 (Hazard Function) 可视化
#'
#' 绘制拟合模型的瞬时风险函数曲线。
#'
#' @param model  flexsurvreg 对象
#' @param newdata data.frame, 协变量取值 (NULL 则截距模型)
#' @param times  numeric vector, 时间点 (NULL 则自动)
#' @return ggplot 对象
#' @export
#' @examples
#' \dontrun{
#' p <- flexsurv_hazard_plot(fit)
#' print(p)
#' }
flexsurv_hazard_plot <- function(model, newdata = NULL, times = NULL) {
  if (is.null(times)) {
    max_time <- max(model$data$Y[, 1]) * 1.1
    times <- seq(0.01, max_time, length.out = 200)
  }

  haz <- summary(model, newdata = newdata, t = times, type = "hazard")

  haz_df <- do.call(rbind, lapply(seq_along(haz), function(i) {
    df_i <- as.data.frame(haz[[i]])
    df_i$profile <- paste0("Profile_", i)
    df_i
  }))
  names(haz_df)[1:2] <- c("time", "hazard")

  p <- ggplot(haz_df, aes(x = time, y = hazard, color = profile)) +
    geom_line(linewidth = 1) +
    scale_color_brewer(palette = "Set1") +
    labs(
      title = "灵活参数模型: 风险函数 (Hazard)",
      x = "时间", y = "瞬时风险率", color = "个体"
    ) +
    theme_minimal(base_size = 12) +
    theme(legend.position = "bottom")

  p
}


# ==============================================================================
# 6. 完整工作流演示
# ==============================================================================

#' 灵活参数生存模型完整工作流
#'
#' 使用模拟生存数据演示: 分布比较 -> 最佳模型拟合 -> 生存曲线预测 ->
#' RMST 估计 -> 风险函数可视化。
#'
#' @return 无 (控制台输出 + ggplot 图形)
#' @export
full_flexsurv_workflow <- function() {
  set.seed(2024)
  n <- 500

  # --- 模拟数据 ---
  trt  <- rbinom(n, 1, 0.5)
  age  <- rnorm(n, 60, 10)
  shape <- 1.2
  scale <- exp(3 - 0.4 * trt + 0.01 * age)
  surv_time <- rweibull(n, shape = shape, scale = scale)
  censor    <- runif(n, 0, quantile(surv_time, 0.85))
  os_time   <- pmin(surv_time, censor)
  os_status <- as.integer(surv_time <= censor)

  surv_data <- data.frame(os_time, os_status, trt = factor(trt), age)
  cat(sprintf("模拟数据: n=%d, 事件数=%d, 中位随访=%.1f\n",
              n, sum(os_status), median(os_time)))

  cat("\n====== 工作流 1: 分布族比较 ======\n")
  cmp <- flexsurv_compare("os_time", "os_status", c("trt", "age"),
                          surv_data,
                          dists = c("weibull", "gengamma", "lnorm", "gompertz"))
  print(cmp)

  cat("\n====== 工作流 2: 最佳分布拟合 ======\n")
  best_dist <- cmp$distribution[1]
  fit <- flexsurv_fit("os_time", "os_status", c("trt", "age"),
                      surv_data, dist = best_dist)
  print(summary(fit))

  cat("\n====== 工作流 3: 预测生存曲线 ======\n")
  new_pt <- data.frame(trt = factor(c(0, 1), levels = levels(surv_data$trt)),
                       age = c(65, 65))
  surv_plot <- flexsurv_survival_curves(fit, newdata = new_pt)
  print(surv_plot$plot)

  cat("\n====== 工作流 4: RMST 估计 ======\n")
  tau_val <- quantile(surv_data$os_time, 0.7)
  rmst_res <- flexsurv_rmst(fit, tau = tau_val, newdata = surv_data,
                            group_var = "trt")
  print(rmst_res$rmst)
  if (!is.null(rmst_res$group_comparison)) print(rmst_res$group_comparison)
  if (!is.null(rmst_res$rmst_difference)) print(rmst_res$rmst_difference)

  cat("\n====== 工作流 5: 风险函数可视化 ======\n")
  haz_p <- flexsurv_hazard_plot(fit, newdata = new_pt)
  print(haz_p)

  cat("\n灵活参数生存模型工作流演示完成。\n")
  invisible(NULL)
}


# --- 运行演示 ---
# full_flexsurv_workflow()
