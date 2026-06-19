# prediction_model_r_template.R — 临床预测模型 R 版模板
# ========================================================
# TRIPOD 合规的预测模型开发完整流程 (R 语言版)
#
# 完整工作流：
#   Phase 1: 样本量评估 (EPV ≥ 10-20)
#   Phase 2: 模型开发 (多模型比较 + 变量选择)
#   Phase 3: 内部验证 (Bootstrap optimism correction)
#   Phase 4: ROC/AUC 评估 (训练集/测试集/DeLong检验)
#   Phase 5: 校准曲线
#   Phase 6: 决策曲线分析 (DCA)
#   Phase 7: 列线图 (Nomogram)
#
# 依赖: rms, pROC, ggplot2, dcurves (可选), caret
# 安装: install.packages(c("rms", "pROC", "ggplot2", "dcurves", "caret"))
#
# 参考: 实战医学统计课程 Ch23-26
# 作者: MSRA Team
# 版本: 0.1.0

library(rms)
library(ggplot2)

# ============================================================================
# 1. 样本量评估 (EPV)
# ============================================================================

#' EPV 样本量评估
#'
#' 计算 Events Per Variable，判断样本量是否足够。
#'
#' @param n_events 事件数
#' @param n_predictors 预测变量数
#' @param min_epv 最小 EPV 阈值 (默认 10)
#'
#' @return list(epv = EPV值, sufficient = 是否足够, min_events = 最小需要事件数)
pred_epv <- function(n_events, n_predictors, min_epv = 10) {
  epv <- n_events / n_predictors
  min_events <- min_epv * n_predictors

  cat(sprintf("\n📊 EPV 样本量评估:\n"))
  cat(sprintf("   事件数 = %d, 预测变量 = %d\n", n_events, n_predictors))
  cat(sprintf("   EPV = %.1f (阈值 ≥ %d)\n", epv, min_epv))

  if (epv >= min_epv) {
    cat("   ✅ 样本量充足\n")
  } else {
    cat(sprintf("   ⚠️ 样本量不足，需要至少 %d 个事件\n", min_events))
  }

  return(list(epv = epv, sufficient = epv >= min_epv, min_events = min_events))
}


# ============================================================================
# 2. 多模型比较开发
# ============================================================================

#' 多模型比较 (ROC + 校准)
#'
#' 比较多个预测模型的 AUC、Brier Score、校准斜率。
#'
#' @param data 数据框
#' @param y 结局变量名 (0/1)
#' @param model_list 命名列表，每个元素是变量名向量
#' @param train_idx 训练集索引 (NULL 则自动划分 80/20)
#' @param seed 随机种子
#'
#' @return list(metrics = 比较指标表, models = 拟合模型列表)
pred_compare_models <- function(data, y, model_list, train_idx = NULL, seed = 42) {
  set.seed(seed)

  if (is.null(train_idx)) {
    train_idx <- sample(nrow(data), 0.8 * nrow(data))
  }

  train <- data[train_idx, ]
  test <- data[-train_idx, ]

  results <- do.call(rbind, lapply(names(model_list), function(m_name) {
    vars <- model_list[[m_name]]
    tryCatch({
      formula_str <- paste0(y, " ~ ", paste(vars, collapse = " + "))
      fit <- glm(as.formula(formula_str), data = train, family = binomial)

      # 预测
      pred_train <- predict(fit, type = "response")
      pred_test <- predict(fit, newdata = test, type = "response")

      # AUC
      auc_train <- as.numeric(pROC::roc(train[[y]], pred_train, quiet = TRUE)$auc)
      auc_test <- as.numeric(pROC::roc(test[[y]], pred_test, quiet = TRUE)$auc)

      # Brier Score
      brier_train <- mean((train[[y]] - pred_train)^2)
      brier_test <- mean((test[[y]] - pred_test)^2)

      # 校准斜率
      logit_pred <- qlogis(pmax(pmin(pred_test, 0.999), 0.001))
      cal_fit <- glm(test[[y]] ~ logit_pred, family = binomial)
      cal_slope <- coef(summary(cal_fit))[2, 1]

      data.frame(
        Model = m_name,
        n_vars = length(vars),
        AUC_train = round(auc_train, 3),
        AUC_test = round(auc_test, 3),
        AUC_diff = round(auc_train - auc_test, 3),
        Brier_train = round(brier_train, 4),
        Brier_test = round(brier_test, 4),
        Cal_Slope = round(cal_slope, 3),
        stringsAsFactors = FALSE
      )
    }, error = function(e) {
      data.frame(Model = m_name, n_vars = length(vars),
                 AUC_train = NA, AUC_test = NA, AUC_diff = NA,
                 Brier_train = NA, Brier_test = NA, Cal_Slope = NA,
                 stringsAsFactors = FALSE)
    })
  }))

  cat("\n📊 多模型比较:\n")
  print(results, row.names = FALSE)

  return(list(metrics = results, train = train, test = test))
}


# ============================================================================
# 3. 内部验证 (Bootstrap Optimism Correction)
# ============================================================================

#' Bootstrap 乐观度校正
#'
#' 使用 Harrell 的 Bootstrap 方法校正模型的乐观偏差。
#'
#' @param model glm 对象
#' @param B Bootstrap 次数 (默认 200)
#'
#' @return list(optimism = 乐观度, apparent_c = 表观C统计量, validated_c = 校正C统计量)
pred_bootstrap_validate <- function(model, B = 200) {
  library(rms)

  # 使用 rms::validate 进行 Bootstrap 校正
  val <- validate(model, method = "boot", B = B)

  cat(sprintf("\n📊 Bootstrap 乐观度校正 (B = %d):\n", B))
  print(val)

  # 提取 C 统计量
  dxy_row <- grep("Dxy", rownames(val), value = TRUE)
  if (length(dxy_row) > 0) {
    optimism <- val[dxy_row, "optimism"]
    apparent_dxy <- val[dxy_row, "index.orig"]
    validated_dxy <- val[dxy_row, "index.corrected"]

    apparent_c <- 0.5 + apparent_dxy / 2
    validated_c <- 0.5 + validated_dxy / 2

    cat(sprintf("\n   表观 C-statistic:  %.3f\n", apparent_c))
    cat(sprintf("   校正 C-statistic:  %.3f\n", validated_c))
    cat(sprintf("   乐观度:           %.3f\n", optimism))
  }

  return(list(optimism = val))
}


# ============================================================================
# 4. ROC/AUC 评估
# ============================================================================

#' 多模型 ROC 曲线比较
#'
#' @param y_true 真实标签
#' @param model_preds 命名列表，每个元素是预测概率向量
#' @param title 标题
#'
#' @return list(plot = ggplot, auc_table = AUC比较表, delong = DeLong检验结果)
pred_roc_compare <- function(y_true, model_preds, title = "ROC Comparison") {
  library(pROC)

  # 拟合各模型 ROC
  roc_list <- lapply(model_preds, function(pred) {
    roc(y_true, pred, quiet = TRUE)
  })

  # AUC 表
  auc_table <- data.frame(
    Model = names(roc_list),
    AUC = sapply(roc_list, function(r) round(as.numeric(r$auc), 3)),
    stringsAsFactors = FALSE
  )

  # DeLong 检验 (第一个 vs 其他)
  delong_results <- NULL
  if (length(roc_list) > 1) {
    delong_results <- lapply(2:length(roc_list), function(i) {
      test <- roc.test(roc_list[[1]], roc_list[[i]], method = "delong")
      data.frame(
        Comparison = paste0(names(roc_list)[1], " vs ", names(roc_list)[i]),
        AUC_1 = round(as.numeric(roc_list[[1]]$auc), 3),
        AUC_2 = round(as.numeric(roc_list[[i]]$auc), 3),
        Z = round(test$statistic, 3),
        P = test$p.value,
        stringsAsFactors = FALSE
      )
    })
    delong_results <- do.call(rbind, delong_results)
    delong_results$P_formatted <- format.pval(delong_results$P, digits = 3)
  }

  # 绘图
  colors <- c("#2E86C1", "#E74C3C", "#27AE60", "#F39C12", "#8E44AD")

  roc_df <- do.call(rbind, lapply(seq_along(roc_list), function(i) {
    r <- roc_list[[i]]
    data.frame(
      Model = paste0(names(roc_list)[i], " (AUC=", sprintf("%.3f", r$auc), ")"),
      fpr = 1 - r$specificities,
      tpr = r$sensitivities,
      stringsAsFactors = FALSE
    )
  }))

  p <- ggplot(roc_df, aes(x = fpr, y = tpr, color = Model)) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "grey60") +
    geom_line(linewidth = 1) +
    coord_equal() +
    scale_color_manual(values = colors[1:length(roc_list)]) +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = c(0.7, 0.25),
      legend.background = element_rect(fill = "white", color = "grey80")
    ) +
    labs(title = title, x = "1 - Specificity", y = "Sensitivity", color = "")

  cat("\n📊 ROC 比较:\n")
  print(auc_table, row.names = FALSE)

  if (!is.null(delong_results)) {
    cat("\n  DeLong 检验:\n")
    print(delong_results, row.names = FALSE)
  }

  return(list(plot = p, auc_table = auc_table, delong = delong_results))
}


# ============================================================================
# 5. 校准曲线
# ============================================================================

#' 校准曲线 (R 版)
#'
#' @param y_true 真实标签
#' @param y_pred 预测概率
#' @param n_bins 分箱数 (默认 10)
#' @param title 标题
#'
#' @return list(plot = ggplot, metrics = 校准指标)
pred_calibration <- function(y_true, y_pred, n_bins = 10, title = "Calibration Curve") {
  df <- data.frame(y_true = y_true, y_pred = y_pred)

  # 分箱
  df$bin <- cut(y_pred,
                 breaks = quantile(y_pred, probs = seq(0, 1, 1/n_bins), na.rm = TRUE),
                 include.lowest = TRUE, labels = FALSE)

  cal_df <- df %>%
    group_by(bin) %>%
    summarise(
      n = n(),
      predicted = mean(y_pred, na.rm = TRUE),
      observed = mean(y_true, na.rm = TRUE),
      observed_se = sqrt(observed * (1 - observed) / n()),
      .groups = "drop"
    )

  # 校准指标
  logit_pred <- qlogis(pmax(pmin(y_pred, 0.999), 0.001))
  cal_int <- coef(summary(glm(y_true ~ 1 + offset(logit_pred), family = binomial)))[1, 1]
  cal_slope <- coef(summary(glm(y_true ~ logit_pred, family = binomial)))[2, 1]
  brier <- mean((y_true - y_pred)^2)

  p <- ggplot(cal_df, aes(x = predicted, y = observed)) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "grey50") +
    geom_point(size = 3, color = "#2E86C1") +
    geom_line(color = "#2E86C1", linewidth = 1) +
    geom_errorbar(aes(ymin = observed - 1.96 * observed_se,
                       ymax = observed + 1.96 * observed_se),
                   width = 0.02, color = "#2E86C1", alpha = 0.5) +
    coord_equal(xlim = c(0, 1), ylim = c(0, 1)) +
    theme_classic(base_size = 12) +
    theme(plot.title = element_text(face = "bold", hjust = 0.5)) +
    labs(
      title = title,
      subtitle = sprintf("Intercept = %.3f | Slope = %.3f | Brier = %.4f",
                          cal_int, cal_slope, brier),
      x = "Predicted Probability",
      y = "Observed Proportion"
    )

  cat(sprintf("\n📊 校准指标:\n"))
  cat(sprintf("   校准截距 = %.3f\n", cal_int))
  cat(sprintf("   校准斜率 = %.3f (理想值 = 1)\n", cal_slope))
  cat(sprintf("   Brier Score = %.4f\n", brier))

  return(list(plot = p, metrics = list(intercept = cal_int, slope = cal_slope, brier = brier)))
}


# ============================================================================
# 6. 决策曲线分析 (DCA)
# ============================================================================

#' 决策曲线分析
#'
#' @param y_true 真实标签
#' @param y_pred 预测概率
#' @param thresholds 阈值概率范围 (默认 0.01 ~ 0.99)
#' @param title 标题
#'
#' @return list(plot = ggplot, data = DCA数据)
pred_dca <- function(y_true, y_pred, thresholds = seq(0.01, 0.99, 0.01),
                      title = "Decision Curve Analysis") {

  prevalence <- mean(y_true)

  dca_df <- do.call(rbind, lapply(thresholds, function(pt) {
    # 模型净获益
    tp <- sum(y_pred >= pt & y_true == 1) / length(y_true)
    fp <- sum(y_pred >= pt & y_true == 0) / length(y_true)
    nb_model <- tp - fp * (pt / (1 - pt))

    # 全部治疗净获益
    nb_all <- prevalence - (1 - prevalence) * (pt / (1 - pt))

    # 全不治疗净获益
    nb_none <- 0

    data.frame(
      threshold = pt,
      Model = nb_model,
      Treat_All = nb_all,
      Treat_None = nb_none,
      stringsAsFactors = FALSE
    )
  }))

  dca_long <- tidyr::pivot_longer(dca_df, cols = -threshold,
                                    names_to = "Strategy", values_to = "Net_Benefit")

  p <- ggplot(dca_long, aes(x = threshold, y = Net_Benefit, color = Strategy)) +
    geom_line(linewidth = 1) +
    scale_color_manual(values = c("Model" = "#2E86C1",
                                   "Treat_All" = "#E74C3C",
                                   "Treat_None" = "grey50")) +
    coord_cartesian(ylim = c(-0.05, max(dca_df$Model, dca_df$Treat_All, na.rm = TRUE) * 1.1)) +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = "bottom"
    ) +
    labs(
      title = title,
      x = "Threshold Probability",
      y = "Net Benefit",
      color = ""
    )

  cat(sprintf("\n📊 DCA: 模型在 %.0f%% ~ %.0f%% 阈值范围内有正净获益\n",
              min(dca_df$threshold[dca_df$Model > 0]) * 100,
              max(dca_df$threshold[dca_df$Model > 0]) * 100))

  return(list(plot = p, data = dca_df))
}


# ============================================================================
# 7. 列线图 (Nomogram)
# ============================================================================

#' 列线图可视化
#'
#' 使用 rms 包绘制列线图。
#'
#' @param model rms::lrm 对象
#' @param title 标题
#'
#' @return 列线图对象
pred_nomogram <- function(model, title = "Nomogram") {
  nom <- nomogram(model, fun = plogis,
                   fun.at = c(0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99),
                   funlabel = "Risk",
                   lp = FALSE)

  plot(nom, xfrac = 0.3, main = title)

  cat("\n📊 列线图已绘制\n")

  return(nom)
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # 模拟数据
  set.seed(42)
  n <- 500
  df <- data.frame(
    age = rnorm(n, 60, 10),
    sex = rbinom(n, 1, 0.5),
    bmi = rnorm(n, 25, 4),
    smoking = rbinom(n, 1, 0.3),
    diabetes = rbinom(n, 1, 0.2),
    biomarker = rnorm(n, 5, 2)
  )
  df$outcome <- rbinom(n, 1, plogis(-3 + 0.03 * df$age + 0.5 * df$sex +
                                      0.05 * df$bmi + 0.8 * df$smoking +
                                      0.1 * df$biomarker))

  # ------ EPV 评估 ------
  epv <- pred_epv(sum(df$outcome == 1), 6)

  # ------ 多模型比较 ------
  models <- list(
    "Base" = c("age", "sex"),
    "Clinical" = c("age", "sex", "bmi", "smoking", "diabetes"),
    "Full" = c("age", "sex", "bmi", "smoking", "diabetes", "biomarker")
  )
  comp <- pred_compare_models(df, "outcome", models)

  # ------ ROC 比较 ------
  train <- df[comp$train_idx %||% sample(n, 0.8 * n), ]
  test <- df[-(comp$train_idx %||% sample(n, 0.8 * n)), ]

  model_preds <- list(
    "Base" = predict(glm(outcome ~ age + sex, data = train, family = binomial),
                      newdata = test, type = "response"),
    "Full" = predict(glm(outcome ~ age + sex + bmi + smoking + diabetes + biomarker,
                          data = train, family = binomial),
                      newdata = test, type = "response")
  )
  roc_res <- pred_roc_compare(test$outcome, model_preds)

  # ------ 校准曲线 ------
  cal_res <- pred_calibration(test$outcome, model_preds[["Full"]])

  # ------ DCA ------
  dca_res <- pred_dca(test$outcome, model_preds[["Full"]])

  # ------ 列线图 ------
  dd <- datadist(df); options(datadist = "dd")
  fit_lrm <- lrm(outcome ~ age + sex + bmi + smoking + diabetes + biomarker, data = df)
  pred_nomogram(fit_lrm)

  cat("✅ 预测模型 R 版模板示例完成\n")
}

cat("✅ prediction_model_r_template.R 已加载\n")
cat("可用函数:\n")
cat("  pred_epv()               - EPV 样本量评估\n")
cat("  pred_compare_models()    - 多模型比较\n")
cat("  pred_bootstrap_validate() - Bootstrap 乐观度校正\n")
cat("  pred_roc_compare()       - ROC/AUC 多模型比较 + DeLong\n")
cat("  pred_calibration()       - 校准曲线\n")
cat("  pred_dca()               - 决策曲线分析\n")
cat("  pred_nomogram()          - 列线图\n")
