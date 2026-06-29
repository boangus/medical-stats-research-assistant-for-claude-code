# logistic_family_template.R — Logistic 家族扩展模板
# =====================================================
# 适用于：各种 Logistic 回归变体及队列研究 RR 估计
#
# 覆盖方法：
#   1. 经典二元 Logistic 回归 (完整建模流程)
#   2. 条件 Logistic 回归 (1:1 / 1:N 配对)
#   3. 有序 Logistic 回归 (Brant 平行线检验)
#   4. 无序多分类 Logistic 回归
#   5. IPTW 加权 Logistic 回归
#   6. 队列 RR 估计 (Poisson / Quasi-Poisson / Binomial-log)
#
# 依赖: MASS, survival, nnet, brant, survey, ipw, epiDisplay
# 安装: install.packages(c("MASS","survival","nnet","brant","survey","ipw","epiDisplay"))
#
# 参考: 实战医学统计课程 Ch11
# 作者: MSRA Team
# 版本: 0.1.0

# ============================================================================
# 1. 经典 Logistic 回归 — 完整建模流程
# ============================================================================

#' 单因素 Logistic 回归 (批量)
#'
#' 对多个自变量逐一进行单因素 Logistic 回归，返回汇总表。
#'
#' @param data 数据框
#' @param y 结局变量名 (0/1)
#' @param vars 自变量名向量
#' @param catvars 分类变量名向量 (转为 factor)
#'
#' @return data.frame (变量、OR、CI、P值)
logistic_univariate <- function(data, y, vars, catvars = NULL) {
  if (!is.null(catvars)) {
    data[catvars] <- lapply(data[catvars], factor)
  }

  results <- do.call(rbind, lapply(vars, function(x) {
    tryCatch({
      formula <- as.formula(paste0(y, " ~ ", x))
      fit <- glm(formula, data = data, family = binomial)

      coef_tab <- coef(summary(fit))
      if (nrow(coef_tab) < 2) return(NULL)

      # 提取第二个系数 (排除截距)
      b <- coef_tab[2, 1]
      se <- coef_tab[2, 2]
      p <- coef_tab[2, 4]

      data.frame(
        Variable = x,
        OR = round(exp(b), 3),
        Lower = round(exp(b - 1.96 * se), 3),
        Upper = round(exp(b + 1.96 * se), 3),
        P = p,
        stringsAsFactors = FALSE
      )
    }, error = function(e) {
      data.frame(Variable = x, OR = NA, Lower = NA, Upper = NA, P = NA,
                 stringsAsFactors = FALSE)
    })
  }))

  # P 值格式化
  results$P_formatted <- format.pval(results$P, digits = 3)
  results <- results[order(results$P), ]

  cat("\n📊 单因素 Logistic 回归结果:\n")
  print(results, row.names = FALSE)

  return(results)
}


#' 多因素 Logistic 回归 — 变量筛选
#'
#' 支持多种变量筛选策略: 逐步回归 (AIC/BIC)、单因素筛选 (P<0.1)、
#' DAG 指定、全部纳入。
#'
#' @param data 数据框
#' @param y 结局变量名
#' @param vars 候选自变量名向量
#' @param catvars 分类变量名向量
#' @param method 筛选方法: "stepwise", "univariate", "dag", "all"
#' @param p_threshold 单因素筛选的 P 值阈值 (默认 0.1)
#' @param forced_vars 强制纳入的变量 (不参与筛选)
#' @param direction 逐步回归方向: "both", "backward", "forward"
#'
#' @return list(model = glm对象, selected_vars = 入选变量, summary = 汇总表)
logistic_multivariable <- function(data, y, vars, catvars = NULL,
                                    method = "stepwise",
                                    p_threshold = 0.1,
                                    forced_vars = NULL,
                                    direction = "both") {
  method <- match.arg(method, c("stepwise", "univariate", "dag", "all"))

  if (!is.null(catvars)) {
    data[catvars] <- lapply(data[catvars], factor)
  }

  # 确定纳入变量
  if (method == "all") {
    selected <- vars
  } else if (method == "dag") {
    selected <- if (!is.null(forced_vars)) forced_vars else vars
  } else if (method == "univariate") {
    # 单因素筛选 P < threshold
    uni_results <- logistic_univariate(data, y, vars, catvars)
    selected <- uni_results$Variable[uni_results$P < p_threshold]
    cat(sprintf("\n  单因素筛选 (P < %.2f): %d 个变量入选\n",
                p_threshold, length(selected)))
  } else {
    selected <- vars
  }

  if (length(selected) == 0) {
    warning("没有变量通过筛选")
    return(NULL)
  }

  # 构建模型公式
  covs_str <- paste(selected, collapse = " + ")
  formula_full <- as.formula(paste0(y, " ~ ", covs_str))
  fit_full <- glm(formula_full, data = data, family = binomial)

  # 逐步回归
  if (method == "stepwise") {
    k_val <- if (direction == "both") 2 else log(nrow(data))  # AIC vs BIC
    fit_step <- step(fit_full, direction = direction, k = k_val, trace = 0)
    selected <- names(coef(fit_step))[-1]  # 排除截距
    fit_final <- fit_step
    cat(sprintf("\n  逐步回归 (%s): %d 个变量入选\n", direction, length(selected)))
  } else {
    fit_final <- fit_full
  }

  # 提取结果
  coef_tab <- coef(summary(fit_final))
  results <- data.frame(
    Variable = rownames(coef_tab)[-1],
    OR = round(exp(coef_tab[-1, 1]), 3),
    Lower = round(exp(coef_tab[-1, 1] - 1.96 * coef_tab[-1, 2]), 3),
    Upper = round(exp(coef_tab[-1, 1] + 1.96 * coef_tab[-1, 2]), 3),
    P = coef_tab[-1, 4],
    stringsAsFactors = FALSE
  )
  results$P_formatted <- format.pval(results$P, digits = 3)

  cat("\n📊 多因素 Logistic 回归结果:\n")
  print(results, row.names = FALSE)

  return(list(
    model = fit_final,
    selected_vars = selected,
    summary = results
  ))
}


#' Logistic 回归诊断
#'
#' 共线性诊断 (VIF)、Hosmer-Lemeshow 拟合优度检验、
#' 完全分离检测、Firth 校正。
#'
#' @param model glm 对象 (binomial)
#' @param data 数据框
#' @param firth_if_separated 是否在完全分离时自动切换 Firth (默认 TRUE)
#'
#' @return list(vif, hosmer, separation, model_final)
logistic_diagnostics <- function(model, data = NULL, firth_if_separated = TRUE) {
  cat("\n📊 Logistic 回归诊断:\n")

  # 1. 共线性诊断 (VIF)
  vif_result <- NULL
  tryCatch({
    vif_result <- car::vif(model)
    cat("\n  VIF (多重共线性):\n")
    print(round(vif_result, 2))
    if (any(vif_result > 10)) {
      cat("  ⚠️ VIF > 10 的变量存在严重共线性\n")
    } else {
      cat("  ✅ 无严重共线性 (VIF < 10)\n")
    }
  }, error = function(e) cat("  VIF 计算失败:", e$message, "\n"))

  # 2. Hosmer-Lemeshow 拟合优度检验
  hl_result <- NULL
  tryCatch({
    hl_result <- ResourceSelection::hoslem.test(model$y, fitted(model), g = 10)
    cat(sprintf("\n  Hosmer-Lemeshow 检验: P = %s\n",
                format.pval(hl_result$p.value, digits = 3)))
    if (hl_result$p.value > 0.05) {
      cat("  ✅ 模型拟合良好 (P > 0.05)\n")
    } else {
      cat("  ⚠️ 模型拟合不佳 (P < 0.05)\n")
    }
  }, error = function(e) cat("  H-L 检验失败:", e$message, "\n"))

  # 3. 完全分离检测
  separation <- FALSE
  model_final <- model
  tryCatch({
    # 检查是否有系数趋向无穷
    coef_vals <- coef(model)
    if (any(abs(coef_vals) > 10) || any(is.na(coef_vals))) {
      separation <- TRUE
      cat("\n  ⚠️ 检测到完全/准完全分离\n")

      if (firth_if_separated) {
        # Firth 惩罚 Logistic
        tryCatch({
          model_final <- brglm2::glm(update.formula(model$formula, . ~ .),
                                      data = model$data, family = binomial,
                                      method = "brglmFit")
          cat("  ✅ 已自动切换为 Firth 惩罚 Logistic\n")
        }, error = function(e) {
          cat("  Firth 校正失败:", e$message, "\n")
        })
      }
    } else {
      cat("\n  ✅ 未检测到完全分离\n")
    }
  })

  return(list(
    vif = vif_result,
    hosmer = hl_result,
    separation = separation,
    model_final = model_final
  ))
}


# ============================================================================
# 2. 条件 Logistic 回归 (配对研究)
# ============================================================================

#' 条件 Logistic 回归 (1:1 或 1:N 配对)
#'
#' 使用 survival::clogit 拟合条件 Logistic 回归。
#'
#' @param data 数据框
#' @param y 结局变量名 (0/1)
#' @param vars 自变量名向量
#' @param strata 配对ID变量名 (对子号)
#'
#' @return list(model = clogit对象, summary = 汇总表)
logistic_conditional <- function(data, y, vars, strata) {
  library(survival)

  formula_str <- paste0("Surv(rep(1, nrow(data)), ", y, ") ~ ",
                         paste(vars, collapse = " + "),
                         " + strata(", strata, ")")
  fit <- clogit(as.formula(formula_str), data = data)

  cat("\n📊 条件 Logistic 回归结果:\n")

  coef_tab <- coef(summary(fit))
  results <- data.frame(
    Variable = rownames(coef_tab),
    OR = round(exp(coef_tab[, "coef"]), 3),
    Lower = round(exp(coef_tab[, "coef"] - 1.96 * coef_tab[, "se(coef)"]), 3),
    Upper = round(exp(coef_tab[, "coef"] + 1.96 * coef_tab[, "se(coef)"]), 3),
    P = coef_tab[, "Pr(>|z|)"],
    stringsAsFactors = FALSE
  )
  results$P_formatted <- format.pval(results$P, digits = 3)
  print(results, row.names = FALSE)

  return(list(model = fit, summary = results))
}


# ============================================================================
# 3. 有序 Logistic 回归
# ============================================================================

#' 有序 Logistic 回归 (比例优势模型)
#'
#' 使用 MASS::polr 拟合有序 Logistic 回归，包含 Brant 平行线检验。
#'
#' @param data 数据框
#' @param y 结局变量名 (有序因子)
#' @param vars 自变量名向量
#' @param y_levels 结局水平 (从低到高)
#' @param y_labels 结局标签
#'
#' @return list(model = polr对象, brant = Brant检验结果, summary = 汇总表)
logistic_ordinal <- function(data, y, vars, y_levels = NULL, y_labels = NULL) {
  library(MASS)

  # 确保 Y 为有序因子
  if (!is.ordered(data[[y]])) {
    if (!is.null(y_levels) && !is.null(y_labels)) {
      data[[y]] <- factor(data[[y]], levels = y_levels,
                           labels = y_labels, ordered = TRUE)
    } else {
      data[[y]] <- factor(data[[y]], ordered = TRUE)
    }
  }

  formula_str <- paste0(y, " ~ ", paste(vars, collapse = " + "))
  fit <- polr(as.formula(formula_str), data = data, Hess = TRUE, method = "logistic")

  # Brant 平行线检验
  brant_result <- NULL
  tryCatch({
    brant_result <- brant::brant(fit)
    cat("\n📊 Brant 平行线检验:\n")
    print(brant_result)

    omnibus_p <- brant_result["Omnibus", "p.value"]
    if (omnibus_p > 0.05) {
      cat("  ✅ 平行线假设成立 (P > 0.05)，可使用有序 Logistic\n")
    } else {
      cat("  ⚠️ 平行线假设违反 (P < 0.05)，考虑无序多分类 Logistic\n")
    }
  }, error = function(e) cat("  Brant 检验失败:", e$message, "\n"))

  # 提取 OR 和 CI
  ctable <- coef(summary(fit))
  p_values <- pnorm(abs(ctable[, "t value"]), lower.tail = FALSE) * 2
  ci <- confint.default(fit)

  results <- data.frame(
    Variable = rownames(ctable),
    OR = round(exp(ctable[, "Value"]), 3),
    Lower = round(exp(ci[, 1]), 3),
    Upper = round(exp(ci[, 2]), 3),
    P = p_values,
    stringsAsFactors = FALSE
  )
  results$P_formatted <- format.pval(results$P, digits = 3)

  cat("\n📊 有序 Logistic 回归结果:\n")
  print(results, row.names = FALSE)

  return(list(model = fit, brant = brant_result, summary = results))
}


# ============================================================================
# 4. 无序多分类 Logistic 回归
# ============================================================================

#' 无序多分类 Logistic 回归
#'
#' 使用 nnet::multinom 拟合无序多分类 Logistic 回归。
#'
#' @param data 数据框
#' @param y 结局变量名 (无序多分类)
#' @param vars 自变量名向量
#' @param ref_level 参照水平
#'
#' @return list(model = multinom对象, summary = 汇总表)
logistic_multinomial <- function(data, y, vars, ref_level = NULL) {
  library(nnet)

  # 设置参照水平
  if (!is.factor(data[[y]])) data[[y]] <- as.factor(data[[y]])
  if (!is.null(ref_level)) {
    data[[y]] <- relevel(data[[y]], ref = ref_level)
  }

  formula_str <- paste0(y, " ~ ", paste(vars, collapse = " + "))
  fit <- multinom(as.formula(formula_str), data = data, trace = FALSE)

  # 提取结果
  coef_tab <- coef(fit)
  se_tab <- summary(fit)$standard.errors
  z_tab <- coef_tab / se_tab
  p_tab <- (1 - pnorm(abs(z_tab))) * 2

  # 构建结果表
  results <- do.call(rbind, lapply(rownames(coef_tab), function(level) {
    data.frame(
      Outcome = level,
      Variable = colnames(coef_tab),
      OR = round(exp(coef_tab[level, ]), 3),
      Lower = round(exp(coef_tab[level, ] - 1.96 * se_tab[level, ]), 3),
      Upper = round(exp(coef_tab[level, ] + 1.96 * se_tab[level, ]), 3),
      P = p_tab[level, ],
      stringsAsFactors = FALSE
    )
  }))

  results$P_formatted <- format.pval(results$P, digits = 3)

  cat("\n📊 无序多分类 Logistic 回归结果:\n")
  print(results, row.names = FALSE)

  return(list(model = fit, summary = results))
}


# ============================================================================
# 5. IPTW 加权 Logistic 回归
# ============================================================================

#' IPTW 加权 Logistic 回归
#'
#' 使用逆概率处理权重 (IPTW) 进行加权 Logistic 回归。
#' 适用于观察性研究中的因果推断。
#'
#' @param data 数据框
#' @param y 结局变量名
#' @param treatment 处理/暴露变量名
#' @param covs 用于计算权重的协变量名向量
#' @param method 权重计算方法: "ipw" (ipw包) 或 "manual" (手动)
#' @param weight_type 权重类型: "ate" (平均处理效应) 或 "att" (处理组平均)
#'
#' @return list(model = svyglm对象, weights = 权重向量, balance = 平衡性检查)
logistic_iptw <- function(data, y, treatment, covs,
                           method = "ipw", weight_type = "ate") {
  method <- match.arg(method, c("ipw", "manual"))

  covs_str <- paste(covs, collapse = " + ")

  if (method == "ipw") {
    library(ipw)

    # 计算 IPTW 权重
    weight_formula <- as.formula(paste0("~ ", covs_str))
    weight_model <- ipwpoint(
      exposure = data[[treatment]],
      family = "binomial",
      link = "logit",
      numerator = ~ 1,
      denominator = weight_formula,
      data = data
    )

    data$wt <- weight_model$ipw.weights
  } else {
    # 手动计算
    ps_formula <- as.formula(paste0(treatment, " ~ ", covs_str))
    ps_model <- glm(ps_formula, data = data, family = binomial)
    ps <- fitted(ps_model)

    if (weight_type == "ate") {
      data$wt <- ifelse(data[[treatment]] == 1, 1 / ps, 1 / (1 - ps))
    } else {
      data$wt <- ifelse(data[[treatment]] == 1, 1, ps / (1 - ps))
    }
  }

  # 截断极端权重 (99% 分位)
  wt_99 <- quantile(data$wt, 0.99, na.rm = TRUE)
  data$wt <- pmin(data$wt, wt_99)

  # 加权 Logistic 回归
  library(survey)
  design <- svydesign(~ 1, weights = ~ wt, data = data)
  formula_y <- as.formula(paste0(y, " ~ ", treatment))
  fit <- svyglm(formula_y, design = design, family = binomial)

  # 提取结果
  coef_tab <- coef(summary(fit))
  or_result <- exp(coef(fit)[2])
  ci_result <- exp(confint(fit)[2, ])

  cat("\n📊 IPTW 加权 Logistic 回归结果:\n")
  cat(sprintf("   %s: OR = %.3f (95%% CI: %.3f ~ %.3f)\n",
              treatment, or_result, ci_result[1], ci_result[2]))

  # 平衡性检查 (SMD)
  balance <- NULL
  tryCatch({
    balance <- data.frame(
      Variable = covs,
      SMD_before = sapply(covs, function(v) {
        if (is.numeric(data[[v]])) {
          abs(mean(data[[v]][data[[treatment]] == 1], na.rm = TRUE) -
              mean(data[[v]][data[[treatment]] == 0], na.rm = TRUE)) /
            sqrt((var(data[[v]][data[[treatment]] == 1], na.rm = TRUE) +
                  var(data[[v]][data[[treatment]] == 0], na.rm = TRUE)) / 2)
        } else NA
      }),
      SMD_after = sapply(covs, function(v) {
        if (is.numeric(data[[v]])) {
          abs(weighted.mean(data[[v]][data[[treatment]] == 1],
                            data$wt[data[[treatment]] == 1], na.rm = TRUE) -
              weighted.mean(data[[v]][data[[treatment]] == 0],
                            data$wt[data[[treatment]] == 0], na.rm = TRUE)) /
            sqrt((var(data[[v]][data[[treatment]] == 1], na.rm = TRUE) +
                  var(data[[v]][data[[treatment]] == 0], na.rm = TRUE)) / 2)
        } else NA
      })
    )
    cat("\n  平衡性检查 (SMD):\n")
    print(balance, row.names = FALSE)
    if (all(balance$SMD_after < 0.1, na.rm = TRUE)) {
      cat("  ✅ 加权后所有 SMD < 0.1，平衡性良好\n")
    } else {
      cat("  ⚠️ 部分变量 SMD > 0.1，需进一步调整\n")
    }
  })

  return(list(
    model = fit,
    weights = data$wt,
    balance = balance
  ))
}


# ============================================================================
# 6. 队列 RR 估计
# ============================================================================

#' 队列研究 RR 估计 (三种方法)
#'
#' 使用 Poisson、Quasi-Poisson 或 Binomial-log 回归估计相对危险度 (RR)。
#'
#' @param data 数据框
#' @param y 结局变量名 (发生率或事件数)
#' @param x 暴露变量名
#' @param covs 协变量名向量
#' @param method RR 估计方法: "quasipoisson" (推荐), "poisson", "binomial_log"
#'
#' @return list(model, RR, CI, P)
rr_estimation <- function(data, y, x, covs = NULL,
                           method = "quasipoisson") {
  method <- match.arg(method, c("quasipoisson", "poisson", "binomial_log"))

  covs_str <- if (!is.null(covs)) paste0(" + ", paste(covs, collapse = " + ")) else ""
  formula_str <- paste0(y, " ~ ", x, covs_str)

  fit <- switch(method,
    "poisson" = glm(as.formula(formula_str), data = data, family = poisson()),
    "quasipoisson" = glm(as.formula(formula_str), data = data, family = quasipoisson()),
    "binomial_log" = glm(as.formula(formula_str), data = data, family = binomial(link = "log"))
  )

  coef_tab <- coef(summary(fit))
  rr <- exp(coef_tab[2, 1])
  ci <- exp(coef_tab[2, 1] + c(-1, 1) * 1.96 * coef_tab[2, 2])
  p <- coef_tab[2, 4]

  cat(sprintf("\n📊 RR 估计 (%s):\n", method))
  cat(sprintf("   RR = %.3f (95%% CI: %.3f ~ %.3f), P = %s\n",
              rr, ci[1], ci[2], format.pval(p, digits = 3)))

  return(list(model = fit, RR = rr, CI = ci, P = p))
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # ------ 示例 1: 经典 Logistic 流程 ------
  # 模拟数据
  set.seed(42)
  n <- 300
  df <- data.frame(
    age = rnorm(n, 55, 10),
    sex = rbinom(n, 1, 0.5),
    bmi = rnorm(n, 25, 4),
    smoking = rbinom(n, 1, 0.3),
    diabetes = rbinom(n, 1, 0.2)
  )
  df$outcome <- rbinom(n, 1, plogis(-3 + 0.03 * df$age + 0.5 * df$sex +
                                      0.05 * df$bmi + 0.8 * df$smoking))

  # 单因素
  uni <- logistic_univariate(df, "outcome",
                              c("age", "sex", "bmi", "smoking", "diabetes"))

  # 多因素 (逐步回归)
  multi <- logistic_multivariable(df, "outcome",
                                   c("age", "sex", "bmi", "smoking", "diabetes"),
                                   method = "stepwise")

  # 诊断
  diag <- logistic_diagnostics(multi$model)

  # ------ 示例 2: 条件 Logistic ------
  # df_match: 配对数据, id为对子号
  # cond <- logistic_conditional(df_match, "case", c("exposure1", "exposure2"), "id")

  # ------ 示例 3: 有序 Logistic ------
  # df$Y <- factor(df$Y, levels = c(1,2,3), labels = c("无效","有效","痊愈"), ordered = TRUE)
  # ord <- logistic_ordinal(df, "Y", c("X1", "X2"))

  # ------ 示例 4: IPTW ------
  # iptw_res <- logistic_iptw(df, "outcome", "treatment",
  #                            covs = c("age", "sex", "bmi"))

  # ------ 示例 5: RR 估计 ------
  # rr_res <- rr_estimation(df, "pro", "exposure", method = "quasipoisson")

  cat("✅ Logistic 家族模板示例完成\n")
}

cat("✅ logistic_family_template.R 已加载\n")
cat("可用函数:\n")
cat("  logistic_univariate()      - 单因素 Logistic (批量)\n")
cat("  logistic_multivariable()   - 多因素 Logistic (多种筛选策略)\n")
cat("  logistic_diagnostics()     - Logistic 诊断 (VIF/H-L/Firth)\n")
cat("  logistic_conditional()     - 条件 Logistic (配对)\n")
cat("  logistic_ordinal()         - 有序 Logistic (Brant检验)\n")
cat("  logistic_multinomial()     - 无序多分类 Logistic\n")
cat("  logistic_iptw()            - IPTW 加权 Logistic\n")
cat("  rr_estimation()            - 队列 RR 估计 (Poisson/QP/BinLog)\n")
