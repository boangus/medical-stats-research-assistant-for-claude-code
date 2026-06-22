# calibration_runner.R — 度量校准引擎（R） — ⚠️ 实验性功能
# =========================================
# 用户提供金标准分析结果 → 系统对比 → 输出 FNR/FPR/准确率报告
#
# 作者: MSRA Team
# 版本: 0.1.0

library(dplyr)

# ============================================================================
# 校准引擎
# ============================================================================

#' 运行度量校准
#'
#' @param gold_data 金标准数据框，需包含：
#'   - gold_method, gold_estimate, gold_lower, gold_upper, gold_p, gold_significant
#' @param msra_data MSRA 输出数据框，需包含：
#'   - msra_method, msra_estimate, msra_lower, msra_upper, msra_p, msra_significant
#' @param analysis_id_col 分析 ID 列名（用于匹配两条数据）
#' @param alpha 显著性水平（默认 0.05）
#'
#' @return list 包含所有校准指标
run_calibration <- function(gold_data, msra_data,
                              analysis_id_col = "analysis_id",
                              alpha = 0.05) {

  # 合并数据
  merged <- merge(
    gold_data, msra_data,
    by = analysis_id_col,
    suffixes = c(".gold", ".msra")
  )

  n_total <- nrow(merged)
  if (n_total == 0) {
    stop("No matching records found between gold and MSRA data")
  }

  # 1. 混淆矩阵
  tp <- sum(merged$gold_significant == TRUE & merged$msra_significant == TRUE, na.rm = TRUE)
  tn <- sum(merged$gold_significant == FALSE & merged$msra_significant == FALSE, na.rm = TRUE)
  fp <- sum(merged$gold_significant == FALSE & merged$msra_significant == TRUE, na.rm = TRUE)
  fn <- sum(merged$gold_significant == TRUE & merged$msra_significant == FALSE, na.rm = TRUE)

  n_pos <- tp + fn
  n_neg <- tn + fp

  # 2. 分类指标
  sensitivity <- ifelse(n_pos > 0, tp / n_pos, NA)
  specificity <- ifelse(n_neg > 0, tn / n_neg, NA)
  fpr <- ifelse(n_neg > 0, fp / n_neg, NA)
  fnr <- ifelse(n_pos > 0, fn / n_pos, NA)
  ppv <- ifelse(tp + fp > 0, tp / (tp + fp), NA)
  npv <- ifelse(tn + fn > 0, tn / (tn + fn), NA)
  accuracy <- (tp + tn) / n_total
  f1 <- ifelse(2 * tp + fp + fn > 0, 2 * tp / (2 * tp + fp + fn), NA)

  # 3. 方法匹配率
  method_match <- sum(merged$gold_method == merged$msra_method, na.rm = TRUE)
  method_match_rate <- method_match / n_total

  # 方法不匹配详情
  mismatches <- merged[merged$gold_method != merged$msra_method, ]

  # 4. 数值偏差
  errors <- merged$msra_estimate - merged$gold_estimate
  abs_errors <- abs(errors)
  mae <- mean(abs_errors, na.rm = TRUE)
  rmse <- sqrt(mean(errors^2, na.rm = TRUE))

  # MAPE
  nonzero <- merged$gold_estimate != 0
  mape <- ifelse(
    any(nonzero),
    mean(abs(errors[nonzero] / merged$gold_estimate[nonzero]) * 100, na.rm = TRUE),
    NA
  )

  # 相关系数
  pcc <- ifelse(
    n_total >= 3,
    cor(merged$msra_estimate, merged$gold_estimate,
        use = "complete.obs", method = "pearson"),
    NA
  )

  return(list(
    n_total = n_total,
    confusion_matrix = list(tp = tp, tn = tn, fp = fp, fn = fn),
    sensitivity = sensitivity,
    specificity = specificity,
    fpr = fpr,
    fnr = fnr,
    ppv = ppv,
    npv = npv,
    accuracy = accuracy,
    f1_score = f1,
    method_match_rate = method_match_rate,
    mismatches = mismatches,
    mae = mae,
    rmse = rmse,
    mape = mape,
    pcc = pcc
  ))
}


#' 格式化校准报告
#'
#' @param result run_calibration 的返回值
print_calibration_report <- function(result) {

  check_val <- function(val, threshold, higher_is_better = TRUE) {
    if (is.na(val)) return("N/A")
    if (higher_is_better) {
      if (val >= threshold) return("✅")
      if (val >= threshold * 0.8) return("⚠️")
      return("❌")
    } else {
      if (val <= threshold) return("✅")
      if (val <= threshold * 1.5) return("⚠️")
      return("❌")
    }
  }

  cat("\n")
  cat(strrep("═", 60), "\n")
  cat("  MSRA 度量校准报告\n")
  cat(strrep("═", 60), "\n\n")
  cat(sprintf("  校准条目数: %d\n", result$n_total))
  cat("  显著性水平: α = 0.05\n\n")

  cm <- result$confusion_matrix
  cat("  ┌─────────────── 混淆矩阵 ───────────────┐\n")
  cat(sprintf("  │                  Gold: Sig  Gold: Non  │\n"))
  cat(sprintf("  │  MSRA: Sig       TP=%-3d     FP=%-3d    │\n", cm$tp, cm$fp))
  cat(sprintf("  │  MSRA: Non-Sig   FN=%-3d     TN=%-3d    │\n", cm$fn, cm$tn))
  cat("  └─────────────────────────────────────────┘\n\n")

  cat("  ┌─────────────── 关键指标 ───────────────┐\n")
  cat(sprintf("  │  灵敏度 (TPR):     %5.1f%%  %s  │\n", result$sensitivity * 100, check_val(result$sensitivity, 0.90)))
  cat(sprintf("  │  特异度 (TNR):     %5.1f%%  %s  │\n", result$specificity * 100, check_val(result$specificity, 0.90)))
  cat(sprintf("  │  假阳性率 (FPR):   %5.1f%%  %s  │\n", result$fpr * 100, check_val(result$fpr, 0.10, FALSE)))
  cat(sprintf("  │  假阴性率 (FNR):   %5.1f%%  %s  │\n", result$fnr * 100, check_val(result$fnr, 0.10, FALSE)))
  cat(sprintf("  │  阳性预测值(PPV):  %5.1f%%  %s  │\n", result$ppv * 100, check_val(result$ppv, 0.85)))
  cat(sprintf("  │  阴性预测值(NPV):  %5.1f%%  %s  │\n", result$npv * 100, check_val(result$npv, 0.85)))
  cat(sprintf("  │  F1 分数:          %6.3f  %s  │\n", result$f1_score, check_val(result$f1_score, 0.85)))
  cat(sprintf("  │  整体准确率:       %5.1f%%  %s  │\n", result$accuracy * 100, check_val(result$accuracy, 0.90)))
  cat("  └─────────────────────────────────────────┘\n\n")

  cat("  ┌─────────── 方法匹配率 ───────────┐\n")
  cat(sprintf("  │  方法选择一致:     %d/%d = %5.1f%%  │\n",
      result$n_total - nrow(result$mismatches), result$n_total,
      result$method_match_rate * 100))
  if (nrow(result$mismatches) > 0) {
    cat("  │  方法不匹配:                      │\n")
    for (i in seq_len(min(5, nrow(result$mismatches)))) {
      r <- result$mismatches[i, ]
      cat(sprintf("  │    %s: Gold=%s -> MSRA=%s  │\n",
          r[[1]], r$gold_method, r$msra_method))
    }
    if (nrow(result$mismatches) > 5) {
      cat(sprintf("  │   ...还有 %d 条  │\n", nrow(result$mismatches) - 5))
    }
  }
  cat("  └───────────────────────────────────┘\n\n")

  cat("  ┌─────────── 数值偏差 ───────────────┐\n")
  cat(sprintf("  │  MAE:          %8.4f  %s  │\n", result$mae, check_val(result$mae, 0.10, FALSE)))
  cat(sprintf("  │  RMSE:         %8.4f  %s  │\n", result$rmse, check_val(result$rmse, 0.15, FALSE)))
  cat(sprintf("  │  MAPE:          %6.2f%%  %s  │\n", result$mape, check_val(result$mape, 0.20, FALSE)))
  cat(sprintf("  │  Pearson r:    %8.4f  %s  │\n", result$pcc, check_val(abs(result$pcc), 0.95)))
  cat("  └─────────────────────────────────────┘\n\n")
  cat("  ", strrep("═", 56), "\n\n")
}


# ============================================================================
# 示例
# ============================================================================
if (FALSE) {
  set.seed(42)
  n <- 20

  gold_data <- data.frame(
    analysis_id = sprintf("ANALYSIS_%03d", 1:n),
    gold_method = rep(c("Logistic", "Cox"), each = n/2),
    gold_estimate = runif(n, 0.5, 2.0),
    gold_lower = runif(n, 0.3, 1.0),
    gold_upper = runif(n, 1.5, 3.0),
    gold_p = runif(n, 0.001, 0.5),
    gold_significant = runif(n) < 0.5,
    stringsAsFactors = FALSE
  )

  msra_data <- gold_data
  names(msra_data) <- gsub("gold_", "msra_", names(msra_data))

  # 引入误差
  msra_data$msra_estimate <- msra_data$msra_estimate * runif(n, 0.9, 1.1)
  flip_idx <- sample(n, 2)
  msra_data$msra_significant[flip_idx] <- !msra_data$msra_significant[flip_idx]

  result <- run_calibration(gold_data, msra_data)
  print_calibration_report(result)
}

cat("✅ calibration_runner.R 已加载\n")
cat("可用函数:\n")
cat("  run_calibration()          - 运行度量校准\n")
cat("  print_calibration_report() - 打印校准报告\n")
