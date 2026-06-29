# ml_r_template.R — 机器学习分类模型 R 版模板
# ==============================================
# 端到端机器学习分类预测流程 (R 语言版)
#
# 完整工作流：
#   Phase 1: 数据准备 + Table1 + 单/多因素分析
#   Phase 2: 多模型训练 (10种ML模型)
#   Phase 3: ROC 比较 (AUC + 95%CI + DeLong)
#   Phase 4: 校准曲线
#   Phase 5: 决策曲线分析 (DCA)
#   Phase 6: 混淆矩阵 + 性能指标
#   Phase 7: 变量重要性
#   Phase 8: SHAP 可解释性分析
#
# 支持模型：
#   Logistic, SVM, GBM, NeuralNet, RandomForest, XGBoost,
#   KNN, Adaboost, LightGBM, CatBoost
#
# 依赖: caret, pROC, ggplot2, tableone, dcurves, shapviz, kernelshap
# 安装: install.packages(c("caret","pROC","ggplot2","tableone","dcurves","shapviz","kernelshap"))
#
# 参考: 实战医学统计课程 Ch30, 小庞统计机器学习分类模型2.0
# 作者: MSRA Team
# 版本: 0.1.0

library(caret)
library(pROC)
library(ggplot2)

# ============================================================================
# 1. 数据准备 + Table1
# ============================================================================

#' 数据准备 + 训练/测试集划分 + Table1
#'
#' @param data 数据框
#' @param y 结局变量名 (二分类，需为 factor)
#' @param train_ratio 训练集比例 (默认 0.7)
#' @param seed 随机种子
#' @param catvars 分类变量名向量 (可选，用于 Table1)
#'
#' @return list(train, test, table1)
ml_prepare <- function(data, y, train_ratio = 0.7, seed = 42, catvars = NULL) {
  set.seed(seed)

  # 确保结局为 factor
  if (!is.factor(data[[y]])) {
    data[[y]] <- factor(data[[y]])
  }

  # 划分
  in_train <- createDataPartition(data[[y]], p = train_ratio, list = FALSE)
  train <- data[in_train, ]
  test <- data[-in_train, ]

  # Table1
  library(tableone)
  all_vars <- setdiff(names(data), y)
  tab1 <- CreateTableOne(vars = all_vars, strata = y,
                          data = train, factorVars = catvars)

  cat(sprintf("📊 数据准备:\n"))
  cat(sprintf("   训练集: n = %d (事件 = %d)\n", nrow(train), sum(train[[y]] == levels(train[[y]])[2])))
  cat(sprintf("   测试集: n = %d (事件 = %d)\n", nrow(test), sum(test[[y]] == levels(test[[y]])[2])))

  return(list(train = train, test = test, table1 = tab1))
}


# ============================================================================
# 2. 多模型训练
# ============================================================================

#' 训练多个 ML 模型
#'
#' @param train 训练集数据框
#' @param y 结局变量名
#' @param models_to_train 要训练的模型名向量 (默认全部)
#' @param seed 随机种子
#' @param cv_folds 交叉验证折数 (默认 10)
#' @param cv_repeats 重复次数 (默认 5)
#'
#' @return list(models = 模型列表, predictions = 预测结果, importance = 变量重要性)
ml_train_models <- function(train, y,
                             models_to_train = c("Logistic", "SVM", "GBM", "NeuralNet",
                                                  "RandomForest", "XGBoost", "KNN", "Adaboost"),
                             seed = 42, cv_folds = 10, cv_repeats = 5) {

  # caret 模型映射
  model_map <- list(
    "Logistic" = "glm",
    "SVM" = "svmRadial",
    "GBM" = "gbm",
    "NeuralNet" = "nnet",
    "RandomForest" = "ranger",
    "XGBoost" = "xgbTree",
    "KNN" = "kknn",
    "Adaboost" = "AdaBoost.M1"
  )

  # 超参数网格
  tune_grids <- list(
    "Logistic" = NULL,
    "SVM" = expand.grid(sigma = 0.001, C = 0.09),
    "GBM" = expand.grid(n.trees = 100, interaction.depth = 5,
                         shrinkage = 0.1, n.minobsinnode = 30),
    "NeuralNet" = expand.grid(size = 6, decay = 0.6),
    "RandomForest" = expand.grid(mtry = floor(sqrt(ncol(train) - 1)),
                                  splitrule = "gini", min.node.size = 5),
    "XGBoost" = expand.grid(nrounds = 100, max_depth = 3, eta = 0.01,
                             gamma = 0.5, colsample_bytree = 0.5,
                             min_child_weight = 1, subsample = 0.6),
    "KNN" = expand.grid(kmax = 12, distance = 1, kernel = "optimal"),
    "Adaboost" = expand.grid(mfinal = 100, maxdepth = 3, coeflearn = "Zhu")
  )

  # 交叉验证控制
  train_ctrl <- trainControl(
    method = "repeatedcv",
    number = cv_folds,
    repeats = cv_repeats,
    classProbs = TRUE,
    summaryFunction = twoClassSummary,
    savePredictions = "final"
  )

  # 训练
  models <- list()
  train_pred <- data.frame(Actual = train[[y]])
  importance <- list()

  pb <- txtProgressBar(min = 0, max = length(models_to_train), style = 3)

  for (i in seq_along(models_to_train)) {
    m_name <- models_to_train[i]
    m_method <- model_map[[m_name]]

    if (is.null(m_method)) {
      cat(sprintf("\n⚠️ 未知模型: %s, 跳过\n", m_name))
      next
    }

    tryCatch({
      set.seed(seed)
      fit <- train(
        as.formula(paste0(y, " ~ .")),
        data = train,
        tuneGrid = tune_grids[[m_name]],
        metric = "ROC",
        method = m_method,
        trControl = train_ctrl
      )

      models[[m_name]] <- fit

      # 训练集预测概率
      pred_prob <- predict(fit, newdata = train, type = "prob")
      train_pred[[m_name]] <- pred_prob[[2]]

      # 变量重要性
      importance[[m_name]] <- varImp(fit, scale = TRUE)

    }, error = function(e) {
      cat(sprintf("\n⚠️ %s 训练失败: %s\n", m_name, e$message))
    })

    setTxtProgressBar(pb, i)
  }
  close(pb)

  cat(sprintf("\n📊 训练完成: %d 个模型\n", length(models)))

  return(list(
    models = models,
    train_pred = train_pred,
    importance = importance
  ))
}


# ============================================================================
# 3. 测试集预测 + ROC 比较
# ============================================================================

#' 测试集预测 + 多模型 ROC 比较
#'
#' @param models 训练好的模型列表
#' @param test 测试集数据框
#' @param y 结局变量名
#' @param title 标题
#'
#' @return list(test_pred, roc_plot, auc_table, delong)
ml_predict_and_roc <- function(models, test, y, title = "ROC Comparison") {

  levels_y <- levels(test[[y]])
  positive_level <- levels_y[2]

  test_pred <- data.frame(Actual = test[[y]])
  roc_list <- list()
  auc_results <- data.frame()

  for (m_name in names(models)) {
    tryCatch({
      pred_prob <- predict(models[[m_name]], newdata = test, type = "prob")
      test_pred[[m_name]] <- pred_prob[[positive_level]]

      roc_obj <- roc(test[[y]], pred_prob[[positive_level]], quiet = TRUE)
      roc_list[[m_name]] <- roc_obj

      ci <- ci.auc(roc_obj)
      auc_results <- rbind(auc_results, data.frame(
        Model = m_name,
        AUC = round(as.numeric(roc_obj$auc), 3),
        CI_lower = round(ci[1], 3),
        CI_upper = round(ci[3], 3),
        stringsAsFactors = FALSE
      ))
    }, error = function(e) {
      cat(sprintf("⚠️ %s 预测失败: %s\n", m_name, e$message))
    })
  }

  # DeLong 检验
  delong_results <- NULL
  if (length(roc_list) > 1) {
    delong_results <- do.call(rbind, lapply(2:length(roc_list), function(i) {
      test_res <- roc.test(roc_list[[1]], roc_list[[i]], method = "delong")
      data.frame(
        Comparison = paste0(names(roc_list)[1], " vs ", names(roc_list)[i]),
        AUC_1 = round(as.numeric(roc_list[[1]]$auc), 3),
        AUC_2 = round(as.numeric(roc_list[[i]]$auc), 3),
        P = test_res$p.value,
        stringsAsFactors = FALSE
      )
    }))
    delong_results$P_formatted <- format.pval(delong_results$P, digits = 3)
  }

  # ROC 图
  colors <- c("#2E86C1", "#E74C3C", "#27AE60", "#F39C12",
              "#8E44AD", "#1ABC9C", "#E67E22", "#2C3E50")

  roc_df <- do.call(rbind, lapply(seq_along(roc_list), function(i) {
    r <- roc_list[[i]]
    auc_val <- round(as.numeric(r$auc), 3)
    ci <- ci.auc(r)
    data.frame(
      Model = paste0(names(roc_list)[i], " (AUC=", auc_val,
                      ", 95%CI: ", sprintf("%.3f", ci[1]), "-",
                      sprintf("%.3f", ci[3]), ")"),
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
      legend.position = c(0.65, 0.25),
      legend.background = element_rect(fill = "white", color = "grey80"),
      legend.text = element_text(size = 8)
    ) +
    labs(title = title, x = "1 - Specificity", y = "Sensitivity", color = "")

  cat("\n📊 AUC 比较:\n")
  print(auc_results[order(-auc_results$AUC), ], row.names = FALSE)

  if (!is.null(delong_results)) {
    cat("\n  DeLong 检验:\n")
    print(delong_results, row.names = FALSE)
  }

  return(list(
    test_pred = test_pred,
    roc_plot = p,
    auc_table = auc_results,
    delong = delong_results
  ))
}


# ============================================================================
# 4. 校准曲线
# ============================================================================

#' 多模型校准曲线
#'
#' @param test_pred ml_predict_and_roc 返回的 test_pred
#' @param y 结局变量名
#' @param n_bins 分箱数
#'
#' @return ggplot 对象
ml_calibration <- function(test_pred, y = "Actual", n_bins = 10) {

  model_names <- setdiff(names(test_pred), y)

  cal_all <- do.call(rbind, lapply(model_names, function(m) {
    pred <- test_pred[[m]]
    actual <- as.numeric(test_pred[[y]] == levels(test_pred[[y]])[2])

    bins <- cut(pred, breaks = quantile(pred, probs = seq(0, 1, 1/n_bins), na.rm = TRUE),
                include.lowest = TRUE, labels = FALSE)

    df <- data.frame(
      predicted = tapply(pred, bins, mean),
      observed = tapply(actual, bins, mean),
      Model = m,
      stringsAsFactors = FALSE
    )
    df
  }))

  colors <- c("#2E86C1", "#E74C3C", "#27AE60", "#F39C12",
              "#8E44AD", "#1ABC9C", "#E67E22", "#2C3E50")

  p <- ggplot(cal_all, aes(x = predicted, y = observed, color = Model)) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed", color = "grey50") +
    geom_point(size = 2) +
    geom_line(linewidth = 0.8) +
    coord_equal(xlim = c(0, 1), ylim = c(0, 1)) +
    scale_color_manual(values = colors[1:length(model_names)]) +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = c(0.15, 0.85),
      legend.background = element_rect(fill = "white", color = "grey80")
    ) +
    labs(title = "Calibration Curves",
         x = "Predicted Probability", y = "Observed Proportion", color = "")

  return(p)
}


# ============================================================================
# 5. 决策曲线分析 (DCA)
# ============================================================================

#' 多模型 DCA
#'
#' @param test_pred ml_predict_and_roc 返回的 test_pred
#' @param y 结局变量名
#'
#' @return ggplot 对象
ml_dca <- function(test_pred, y = "Actual") {
  library(dcurves)

  model_names <- setdiff(names(test_pred), y)

  # 准备数据
  dca_data <- test_pred
  dca_data[[y]] <- as.numeric(dca_data[[y]] == levels(dca_data[[y]])[2])

  # 构建公式
  formulas <- paste0(y, " ~ ", model_names)

  # DCA
  dca_obj <- dcurves::dca(as.formula(paste0(y, " ~ ", paste(model_names, collapse = " + "))),
                            data = dca_data,
                            thresholds = seq(0.01, 0.99, by = 0.01))

  p <- plot(dca_obj, smooth = TRUE) +
    theme_classic(base_size = 12) +
    theme(
      plot.title = element_text(face = "bold", hjust = 0.5),
      legend.position = "bottom"
    ) +
    labs(title = "Decision Curve Analysis")

  return(p)
}


# ============================================================================
# 6. 混淆矩阵 + 性能指标
# ============================================================================

#' 多模型混淆矩阵 + 性能指标
#'
#' @param test_pred ml_predict_and_roc 返回的 test_pred
#' @param y 结局变量名
#'
#' @return data.frame (Model, Threshold, Accuracy, Sensitivity, Specificity, Precision, F1)
ml_performance <- function(test_pred, y = "Actual") {

  model_names <- setdiff(names(test_pred), y)
  positive_level <- levels(test_pred[[y]])[2]

  results <- do.call(rbind, lapply(model_names, function(m) {
    roc_obj <- roc(test_pred[[y]], test_pred[[m]], quiet = TRUE)

    # 最优阈值 (Youden)
    best_thresh <- roc_obj$thresholds[which.max(roc_obj$sensitivities + roc_obj$specificities - 1)]

    pred_class <- factor(ifelse(test_pred[[m]] >= best_thresh, positive_level,
                                 levels(test_pred[[y]])[1]),
                          levels = levels(test_pred[[y]]))

    cm <- confusionMatrix(pred_class, test_pred[[y]], positive = positive_level)

    data.frame(
      Model = m,
      Threshold = round(best_thresh, 3),
      Accuracy = round(cm$overall["Accuracy"], 3),
      Sensitivity = round(cm$byClass["Sensitivity"], 3),
      Specificity = round(cm$byClass["Specificity"], 3),
      Precision = round(cm$byClass["Precision"], 3),
      F1 = round(cm$byClass["F1"], 3),
      stringsAsFactors = FALSE
    )
  }))

  cat("\n📊 模型性能指标 (最优阈值):\n")
  print(results[order(-results$AUC %||% results$F1), ], row.names = FALSE)

  return(results)
}


# ============================================================================
# 7. 变量重要性图
# ============================================================================

#' 绘制变量重要性图 (所有模型)
#'
#' @param importance ml_train_models 返回的 importance 列表
#' @param top_n 显示前 N 个变量 (默认全部)
#'
#' @return ggplot 对象列表
ml_importance_plot <- function(importance, top_n = NULL) {
  plots <- lapply(names(importance), function(m_name) {
    imp <- importance[[m_name]]
    imp_df <- as.data.frame(imp$importance)

    # 取第一个列 (或 Overall)
    if ("Yes" %in% colnames(imp_df)) {
      imp_df$Score <- imp_df$Yes
    } else if ("Overall" %in% colnames(imp_df)) {
      imp_df$Score <- imp_df$Overall
    } else {
      imp_df$Score <- imp_df[, 1]
    }

    imp_df$Feature <- rownames(imp_df)
    imp_df <- imp_df[order(-imp_df$Score), ]

    if (!is.null(top_n)) imp_df <- head(imp_df, top_n)

    ggplot(imp_df, aes(x = Score, y = reorder(Feature, Score))) +
      geom_col(fill = "#2E86C1", alpha = 0.7, width = 0.6) +
      theme_classic(base_size = 10) +
      theme(plot.title = element_text(face = "bold", hjust = 0.5, size = 11)) +
      labs(title = m_name, x = "Importance", y = NULL)
  })

  names(plots) <- names(importance)
  return(plots)
}


# ============================================================================
# 8. SHAP 可解释性分析
# ============================================================================

#' SHAP 分析 (最优模型)
#'
#' 使用 kernelshap + shapviz 进行 SHAP 可解释性分析。
#'
#' @param model 最优模型对象
#' @param train 训练集
#' @param test 测试集 (作为背景数据)
#' @param y 结局变量名
#' @param n_sample 计算 SHAP 的样本数 (默认 100)
#' @param output_dir 输出目录
#'
#' @return shapviz 对象
ml_shap <- function(model, train, test, y, n_sample = 100, output_dir = ".") {
  library(kernelshap)
  library(shapviz)

  # 准备数据 (排除结局变量)
  x_train <- train[, setdiff(names(train), y)]
  x_test <- test[, setdiff(names(test), y)]

  n_sample <- min(n_sample, nrow(x_train))

  # SHAP 计算
  cat(sprintf("\n📊 SHAP 分析 (n = %d)...\n", n_sample))
  explain <- kernelshap(model, X = x_train[1:n_sample, ], bg_X = x_test[1:min(50, nrow(x_test)), ])

  positive_level <- levels(train[[y]])[2]
  sv <- shapviz(explain, X_pred = x_train[1:n_sample, ])

  # 蜂群图 (最重要)
  p_beeswarm <- sv_importance(sv[[positive_level]], kind = "beeswarm",
                               viridis_args = list(begin = 0.25, end = 0.85, option = "B"),
                               show_numbers = FALSE) +
    theme_bw() +
    ggtitle("SHAP Importance (Beeswarm)") +
    theme(plot.title = element_text(hjust = 0.5, face = "bold"))

  # 条形图
  p_bar <- sv_importance(sv[[positive_level]], kind = "bar",
                          fill = "#fca50a", show_numbers = FALSE) +
    theme_bw() +
    ggtitle("SHAP Importance (Bar)") +
    theme(plot.title = element_text(hjust = 0.5, face = "bold"))

  # 瀑布图 (单样本)
  p_waterfall <- sv_waterfall(sv[[positive_level]], row_id = 1,
                               fill_colors = c("#f7d13d", "#a52c60")) +
    theme_bw() +
    ggtitle("SHAP Waterfall (Sample 1)") +
    theme(plot.title = element_text(hjust = 0.5, face = "bold"))

  cat("📊 SHAP 分析完成\n")

  return(list(
    shap_values = sv,
    plots = list(
      beeswarm = p_beeswarm,
      bar = p_bar,
      waterfall = p_waterfall
    )
  ))
}


# ============================================================================
# 9. 完整流程一键运行
# ============================================================================

#' 一键运行完整 ML 流程
#'
#' @param data 数据框
#' @param y 结局变量名
#' @param catvars 分类变量名向量
#' @param models_to_train 要训练的模型名向量
#' @param output_dir 输出目录
#'
#' @return list(所有结果)
ml_full_pipeline <- function(data, y, catvars = NULL,
                              models_to_train = c("Logistic", "SVM", "GBM", "NeuralNet",
                                                   "RandomForest", "XGBoost", "KNN", "Adaboost"),
                              output_dir = ".") {

  cat("🚀 ML 完整流程开始\n")
  cat("=" |> rep(60) |> paste(collapse = ""), "\n")

  # Phase 1: 数据准备
  cat("\n📦 Phase 1: 数据准备\n")
  prep <- ml_prepare(data, y, catvars = catvars)

  # Phase 2: 模型训练
  cat("\n🏋️ Phase 2: 模型训练\n")
  trained <- ml_train_models(prep$train, y, models_to_train)

  # Phase 3: ROC 比较
  cat("\n📈 Phase 3: ROC 比较\n")
  roc_res <- ml_predict_and_roc(trained$models, prep$test, y)

  # Phase 4: 校准曲线
  cat("\n📊 Phase 4: 校准曲线\n")
  cal_plot <- ml_calibration(roc_res$test_pred)

  # Phase 5: DCA
  cat("\n📊 Phase 5: DCA\n")
  dca_plot <- ml_dca(roc_res$test_pred)

  # Phase 6: 性能指标
  cat("\n📊 Phase 6: 性能指标\n")
  perf <- ml_performance(roc_res$test_pred)

  # Phase 7: 变量重要性
  cat("\n📊 Phase 7: 变量重要性\n")
  imp_plots <- ml_importance_plot(trained$importance)

  # Phase 8: SHAP (最优模型)
  cat("\n📊 Phase 8: SHAP 分析\n")
  best_model_name <- perf$Model[which.max(perf$F1)]
  shap_res <- ml_shap(trained$models[[best_model_name]],
                       prep$train, prep$test, y)

  cat("\n" |> rep(60) |> paste(collapse = ""), "\n")
  cat("✅ ML 完整流程完成\n")

  return(list(
    data_prep = prep,
    models = trained,
    roc = roc_res,
    calibration = cal_plot,
    dca = dca_plot,
    performance = perf,
    importance = imp_plots,
    shap = shap_res
  ))
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # 模拟数据
  set.seed(42)
  n <- 500
  df <- data.frame(
    Age = rnorm(n, 60, 10),
    Gender = factor(rbinom(n, 1, 0.5), labels = c("Female", "Male")),
    BMI = rnorm(n, 25, 4),
    Smoking = factor(rbinom(n, 1, 0.3), labels = c("No", "Yes")),
    Diabetes = factor(rbinom(n, 1, 0.2), labels = c("No", "Yes")),
    Biomarker = rnorm(n, 5, 2)
  )
  df$Outcome <- factor(rbinom(n, 1, plogis(-3 + 0.03 * df$Age + 0.5 * as.numeric(df$Gender) +
                                             0.05 * df$BMI + 0.8 * as.numeric(df$Smoking))),
                        labels = c("No", "Yes"))

  # 一键运行
  results <- ml_full_pipeline(
    data = df, y = "Outcome",
    catvars = c("Gender", "Smoking", "Diabetes"),
    models_to_train = c("Logistic", "GBM", "XGBoost", "RandomForest")
  )

  # 单独使用
  prep <- ml_prepare(df, "Outcome", catvars = c("Gender", "Smoking"))
  trained <- ml_train_models(prep$train, "Outcome",
                              models_to_train = c("Logistic", "XGBoost"))

  cat("✅ ML R 版模板示例完成\n")
}

cat("✅ ml_r_template.R 已加载\n")
cat("可用函数:\n")
cat("  ml_prepare()           - 数据准备 + Table1\n")
cat("  ml_train_models()      - 多模型训练\n")
cat("  ml_predict_and_roc()   - 测试集ROC比较\n")
cat("  ml_calibration()       - 校准曲线\n")
cat("  ml_dca()               - DCA\n")
cat("  ml_performance()       - 性能指标\n")
cat("  ml_importance_plot()   - 变量重要性\n")
cat("  ml_shap()              - SHAP分析\n")
cat("  ml_full_pipeline()     - 一键完整流程\n")
