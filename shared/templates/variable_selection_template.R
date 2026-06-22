# variable_selection_template.R — 变量选择方法模板
# =================================================
# 适用于：回归模型中的变量选择（混杂因素筛选、特征选择）
#
# 覆盖方法：
#   1. CIE 混杂效应改变 (chest包) — 观察性研究推荐
#   2. 逐步回归 (StepReg包) — forward/backward/bidirection/subset
#   3. 最优子集 (leaps包) — BIC/Cp/R² 评估
#   4. 随机森林变量重要性 (randomForest)
#   5. Boruta 特征选择 (Boruta包)
#   6. LASSO 变量筛选 (glmnet包)
#
# 依赖: chest, StepReg, leaps, randomForest, Boruta, glmnet
# 安装: install.packages(c("chest","StepReg","leaps","randomForest","Boruta","glmnet"))
#
# 参考: 实战医学统计课程 Ch9
# 作者: MSRA Team
# 版本: 0.1.0

# ============================================================================
# 1. CIE 混杂效应改变 (chest包) — 观察性研究首选
# ============================================================================

#' CIE 混杂效应改变分析
#'
#' 逐步调整协变量，观察暴露-结局关联的效应值改变。
#' 当调整某协变量后效应改变 >10% 时，该变量被视为混杂因素。
#'
#' @param data 数据框
#' @param crude 粗模型公式 (如 "y ~ exposure")
#' @param xlist 候选混杂因素名向量
#' @param type 模型类型: "glm" (Logistic), "cox" (Cox), "clogit" (条件Logistic), "lm" (线性)
#' @param time 生存时间变量 (仅 cox)
#' @param event 事件变量 (仅 cox)
#' @param strata 配对ID (仅 clogit)
#' @param plot 是否绘制图形
#'
#' @return list(results = chest结果, plot = ggplot图形)
varsel_cie <- function(data, crude, xlist, type = "glm",
                        time = NULL, event = NULL, strata = NULL,
                        plot = TRUE) {
  library(chest)

  results <- switch(type,
    "glm" = chest::chest_glm(crude = crude, xlist = xlist, data = data),
    "cox" = chest::chest_cox(crude = crude, xlist = xlist, data = data),
    "clogit" = chest::chest_clogit(crude = crude, xlist = xlist, data = data),
    "lm" = chest::chest_lm(crude = crude, xlist = xlist, data = data)
  )

  cat("\n📊 CIE 混杂效应改变分析:\n")
  print(results$data)

  # 筛选效应改变 > 10% 的变量
  if (!is.null(results$data)) {
    change_col <- grep("change|pct", names(results$data), value = TRUE)
    if (length(change_col) > 0) {
      confounders <- results$data[[change_col[1]]]
      sig_idx <- which(abs(confounders) > 10)
      if (length(sig_idx) > 0) {
        cat(sprintf("\n  ✅ 识别为混杂因素 (效应改变 > 10%%): %s\n",
                    paste(xlist[sig_idx], collapse = ", ")))
      } else {
        cat("\n  ℹ️ 无变量满足混杂因素标准 (效应改变 > 10%)\n")
      }
    }
  }

  p <- NULL
  if (plot) {
    p <- chest::chest_plot(results, nudge_y = 0, value_position = 5)
    print(p)
  }

  return(list(results = results, plot = p))
}


# ============================================================================
# 2. 逐步回归 (StepReg包)
# ============================================================================

#' 逐步回归变量选择
#'
#' 支持 6 种策略 × 6 种模型 × 多种指标。
#'
#' @param data 数据框
#' @param formula 模型公式
#' @param type 模型类型: "linear", "logit", "cox", "poisson", "gamma", "negbin"
#' @param strategy 策略向量: "forward", "backward", "bidirection", "subset"
#' @param metric 指标向量: "AIC", "AICc", "BIC", "CP", "HQ", "Rsq", "adjRsq", "SL", "SBC"
#' @param sle 进入阈值 (默认 0.15)
#' @param sls 留下阈值 (默认 0.15)
#' @param plot 是否绘制结果
#'
#' @return list(results = 逐步回归结果, plot = 图形)
varsel_stepwise <- function(data, formula, type = "logit",
                             strategy = c("forward", "backward", "bidirection"),
                             metric = c("AIC", "BIC"),
                             sle = 0.15, sls = 0.15,
                             plot = TRUE) {
  library(StepReg)

  results <- stepwise(
    formula = formula,
    data = data,
    type = type,
    strategy = strategy,
    metric = metric,
    sle = sle,
    sls = sls
  )

  cat("\n📊 逐步回归结果:\n")
  print(results)

  p <- NULL
  if (plot) {
    p <- plot(results)
    print(p)
  }

  return(list(results = results, plot = p))
}


# ============================================================================
# 3. 最优子集 (leaps包)
# ============================================================================

#' 最优子集变量选择
#'
#' 使用穷举法或向前/向后搜索找到最优变量子集。
#'
#' @param data 数据框
#' @param formula 模型公式
#' @param method 搜索方法: "exhaustive" (穷举), "backward", "forward", "seqrep"
#' @param n_best 每个变量数量的最佳模型数 (默认 5)
#' @param plot 是否绘制 BIC/Cp/R² 图
#'
#' @return list(model = regsubsets对象, summary = 汇总, plot = 图形)
varsel_subset <- function(data, formula, method = "exhaustive",
                           n_best = 5, plot = TRUE) {
  library(leaps)

  model <- regsubsets(formula, data = data, method = method,
                      nbest = n_best, nvmax = NULL)
  model_summary <- summary(model)

  cat("\n📊 最优子集结果:\n")
  cat(sprintf("  最优变量数 (BIC 最小): %d\n",
              which.min(model_summary$bic)))
  cat(sprintf("  最优变量数 (Cp 最小):  %d\n",
              which.min(model_summary$cp)))

  # 提取 BIC 最优的变量
  best_bic <- which.min(model_summary$bic)
  best_vars <- names(which(model_summary$which[best_bic, ])[-1])  # 排除截距
  cat(sprintf("  BIC 最优变量: %s\n", paste(best_vars, collapse = ", ")))

  p <- NULL
  if (plot) {
    library(ggplot2)
    # 构建指标数据
    metric_df <- data.frame(
      n_vars = 1:length(model_summary$bic),
      BIC = model_summary$bic,
      Cp = model_summary$cp,
      R2 = model_summary$rsq,
      AdjR2 = model_summary$adjr2
    )

    metric_long <- tidyr::pivot_longer(metric_df, cols = -n_vars,
                                        names_to = "metric", values_to = "value")

    p <- ggplot(metric_long, aes(x = n_vars, y = value)) +
      geom_point(size = 2, color = "#2E86C1") +
      geom_line(linewidth = 0.8, color = "#2E86C1") +
      geom_vline(data = metric_long %>%
                   group_by(metric) %>%
                   filter(value == ifelse(metric == "R2" | metric == "AdjR2",
                                          max(value), min(value))),
                 aes(xintercept = n_vars), linetype = "dashed", color = "#E74C3C") +
      facet_wrap(~ metric, scales = "free_y") +
      theme_classic(base_size = 11) +
      theme(strip.background = element_rect(fill = "#F0F0F0")) +
      labs(title = "Best Subset Selection Metrics",
           x = "Number of Variables", y = "Value")
    print(p)
  }

  return(list(model = model, summary = model_summary, plot = p,
              best_vars = best_vars))
}


# ============================================================================
# 4. 随机森林变量重要性
# ============================================================================

#' 随机森林变量重要性排序
#'
#' 使用随机森林评估变量重要性，适用于分类和回归问题。
#'
#' @param data 数据框
#' @param formula 模型公式
#' @param ntree 树的数量 (默认 500)
#' @param top_n 显示前 N 个重要变量 (默认全部)
#' @param plot 是否绘制重要性图
#'
#' @return list(model = randomForest对象, importance = 重要性表, plot = 图形)
varsel_randomforest <- function(data, formula, ntree = 500,
                                 top_n = NULL, plot = TRUE) {
  library(randomForest)

  set.seed(42)
  fit <- randomForest(formula, data = data, ntree = ntree, importance = TRUE)

  imp <- importance(fit)
  imp_df <- data.frame(
    Variable = rownames(imp),
    MeanDecreaseAccuracy = imp[, "%IncMSE"],
    MeanDecreaseGini = imp[, "IncNodePurity"],
    stringsAsFactors = FALSE
  )
  imp_df <- imp_df[order(-imp_df$MeanDecreaseGini), ]

  if (!is.null(top_n)) imp_df <- head(imp_df, top_n)

  cat("\n📊 随机森林变量重要性:\n")
  print(imp_df, row.names = FALSE)

  p <- NULL
  if (plot) {
    library(ggplot2)
    p <- ggplot(imp_df, aes(x = reorder(Variable, MeanDecreaseGini),
                             y = MeanDecreaseGini)) +
      geom_col(fill = "#2E86C1", alpha = 0.7, width = 0.6) +
      coord_flip() +
      theme_classic(base_size = 12) +
      theme(plot.title = element_text(face = "bold", hjust = 0.5)) +
      labs(title = "Random Forest Variable Importance",
           x = "", y = "Mean Decrease Gini")
    print(p)
  }

  return(list(model = fit, importance = imp_df, plot = p))
}


# ============================================================================
# 5. Boruta 特征选择
# ============================================================================

#' Boruta 特征选择
#'
#' 基于随机森林的全特征选择算法，通过与随机打乱特征比较
#' 确定每个特征的重要性。
#'
#' @param data 数据框
#' @param formula 模型公式
#' @param maxRuns 最大迭代次数 (默认 100)
#' @param plot 是否绘制结果
#'
#' @return list(model = Boruta对象, selected = 选中变量, tentative = 待定变量)
varsel_boruta <- function(data, formula, maxRuns = 100, plot = TRUE) {
  library(Boruta)

  set.seed(42)
  fit <- Boruta(formula, data = data, doTrace = 0, maxRuns = maxRuns)

  selected <- getSelectedAttributes(fit, withTentative = FALSE)
  tentative <- getSelectedAttributes(fit, withTentative = TRUE)
  tentative_only <- setdiff(tentative, selected)

  cat("\n📊 Boruta 特征选择结果:\n")
  cat(sprintf("  ✅ 确认重要: %s\n",
              if (length(selected) > 0) paste(selected, collapse = ", ") else "无"))
  cat(sprintf("  ⏳ 待定:     %s\n",
              if (length(tentative_only) > 0) paste(tentative_only, collapse = ", ") else "无"))
  cat(sprintf("  ❌ 不重要:   %s\n",
              paste(setdiff(names(fit$finalDecision[fit$finalDecision == "Rejected"]),
                            ""), collapse = ", ")))

  p <- NULL
  if (plot) {
    par(mar = c(7, 5, 4, 2), cex.axis = 0.6)
    plot(fit, las = 2, xlab = "", main = "Boruta Feature Selection", margin = 0.1)
  }

  return(list(model = fit, selected = selected, tentative = tentative_only))
}


# ============================================================================
# 6. LASSO 变量筛选 (glmnet包)
# ============================================================================

#' LASSO 变量筛选
#'
#' 使用 L1 惩罚的 LASSO 回归进行变量筛选。
#' 适用于高维数据或多重共线性场景。
#'
#' @param data 数据框
#' @param y 结局变量名
#' @param vars 自变量名向量
#' @param family 分布族: "binomial", "gaussian", "poisson", "cox"
#' @param alpha 弹性网混合参数 (1=LASSO, 0=Ridge, 默认 1)
#' @param nfolds 交叉验证折数 (默认 10)
#' @param plot 是否绘制交叉验证图
#'
#' @return list(cv_model = cv.glmnet对象, selected_vars = 选中变量, coef = 系数)
varsel_lasso <- function(data, y, vars, family = "binomial",
                          alpha = 1, nfolds = 10, plot = TRUE) {
  library(glmnet)

  # 构建模型矩阵
  formula_str <- paste0(y, " ~ ", paste(vars, collapse = " + "))
  x_mat <- model.matrix(as.formula(formula_str), data = data)[, -1]
  y_vec <- data[[y]]

  if (family == "cox") {
    y_vec <- Surv(data$time, data[[y]])
  }

  # 交叉验证
  set.seed(42)
  cv_fit <- cv.glmnet(x_mat, y_vec, family = family, alpha = alpha,
                       nfolds = nfolds)

  # 最优 lambda
  lambda_min <- cv_fit$lambda.min
  lambda_1se <- cv_fit$lambda.1se

  # 提取非零系数
  coef_min <- coef(cv_fit, s = "lambda.min")
  coef_1se <- coef(cv_fit, s = "lambda.1se")

  # 选中变量
  selected_min <- rownames(coef_min)[which(coef_min[, 1] != 0)]
  selected_min <- selected_min[selected_min != "(Intercept)"]

  selected_1se <- rownames(coef_1se)[which(coef_1se[, 1] != 0)]
  selected_1se <- selected_1se[selected_1se != "(Intercept)"]

  cat("\n📊 LASSO 变量筛选结果:\n")
  cat(sprintf("  lambda.min = %.6f, lambda.1se = %.6f\n", lambda_min, lambda_1se))
  cat(sprintf("  lambda.min 选中 %d 个变量: %s\n",
              length(selected_min), paste(selected_min, collapse = ", ")))
  cat(sprintf("  lambda.1se 选中 %d 个变量: %s\n",
              length(selected_1se), paste(selected_1se, collapse = ", ")))

  # 系数表
  coef_df <- data.frame(
    Variable = rownames(coef_min),
    Coef_min = coef_min[, 1],
    Coef_1se = coef_1se[, 1],
    stringsAsFactors = FALSE
  )
  coef_df <- coef_df[coef_df$Variable != "(Intercept)", ]
  coef_df$OR_min <- round(exp(coef_df$Coef_min), 3)
  coef_df <- coef_df[order(-abs(coef_df$Coef_min)), ]

  cat("\n  非零系数:\n")
  print(coef_df[coef_df$Coef_min != 0, ], row.names = FALSE)

  p <- NULL
  if (plot) {
    plot(cv_fit, main = "LASSO Cross-Validation")
  }

  return(list(
    cv_model = cv_fit,
    selected_vars = selected_min,
    selected_vars_1se = selected_1se,
    coef = coef_df,
    lambda_min = lambda_min,
    lambda_1se = lambda_1se
  ))
}


# ============================================================================
# 7. 变量选择汇总比较
# ============================================================================

#' 比较多种变量选择方法的结果
#'
#' @param results_list 命名列表，每个元素是不同方法的选中变量向量
#' @param all_vars 所有候选变量
#'
#' @return data.frame (变量 × 方法的入选矩阵)
varsel_compare <- function(results_list, all_vars) {
  # 构建比较矩阵
  compare_mat <- do.call(cbind, lapply(names(results_list), function(method) {
    selected <- results_list[[method]]
    ifelse(all_vars %in% selected, "✅", "❌")
  }))
  colnames(compare_mat) <- names(results_list)

  result_df <- data.frame(
    Variable = all_vars,
    compare_mat,
    Selected_Count = rowSums(compare_mat == "✅"),
    stringsAsFactors = FALSE
  )
  result_df <- result_df[order(-result_df$Selected_Count), ]

  cat("\n📊 变量选择方法比较:\n")
  print(result_df, row.names = FALSE)

  # 共识变量 (被多数方法选中)
  n_methods <- length(results_list)
  consensus <- result_df$Variable[result_df$Selected_Count >= ceiling(n_methods / 2)]
  cat(sprintf("\n  共识变量 (≥%d/%d 方法选中): %s\n",
              ceiling(n_methods / 2), n_methods,
              paste(consensus, collapse = ", ")))

  return(result_df)
}


# ============================================================================
# 使用示例
# ============================================================================
if (FALSE) {

  # 模拟数据
  set.seed(42)
  n <- 500
  df <- data.frame(
    age = rnorm(n, 55, 10),
    sex = rbinom(n, 1, 0.5),
    bmi = rnorm(n, 25, 4),
    smoking = rbinom(n, 1, 0.3),
    drinking = rbinom(n, 1, 0.2),
    exercise = rbinom(n, 1, 0.4),
    diabetes = rbinom(n, 1, 0.15),
    hypertension = rbinom(n, 1, 0.3)
  )
  df$y <- rbinom(n, 1, plogis(-3 + 0.03 * df$age + 0.5 * df$sex +
                                0.05 * df$bmi + 0.8 * df$smoking))

  vars <- c("age", "sex", "bmi", "smoking", "drinking",
            "exercise", "diabetes", "hypertension")

  # ------ 方法 1: CIE ------
  cie_res <- varsel_cie(df, crude = "y ~ smoking", xlist = vars, type = "glm")

  # ------ 方法 2: 逐步回归 ------
  step_res <- varsel_stepwise(df, formula = y ~ age + sex + bmi + smoking +
                               drinking + exercise + diabetes + hypertension,
                               type = "logit")

  # ------ 方法 3: 最优子集 ------
  subset_res <- varsel_subset(df, formula = y ~ age + sex + bmi + smoking +
                               drinking + exercise + diabetes + hypertension)

  # ------ 方法 4: 随机森林 ------
  rf_res <- varsel_randomforest(df, formula = factor(y) ~ age + sex + bmi +
                                 smoking + drinking + exercise + diabetes + hypertension)

  # ------ 方法 5: Boruta ------
  boruta_res <- varsel_boruta(df, formula = factor(y) ~ age + sex + bmi +
                                smoking + drinking + exercise + diabetes + hypertension)

  # ------ 方法 6: LASSO ------
  lasso_res <- varsel_lasso(df, y = "y", vars = vars, family = "binomial")

  # ------ 汇总比较 ------
  compare <- varsel_compare(
    list(
      CIE = cie_res$results$data$Variable,
      Stepwise = step_res$results$selected,
      Subset = subset_res$best_vars,
      RF = rf_res$importance$Variable[1:5],
      Boruta = boruta_res$selected,
      LASSO = lasso_res$selected_vars
    ),
    all_vars = vars
  )

  cat("✅ 变量选择模板示例完成\n")
}

cat("✅ variable_selection_template.R 已加载\n")
cat("可用函数:\n")
cat("  varsel_cie()          - CIE 混杂效应改变 (chest包)\n")
cat("  varsel_stepwise()     - 逐步回归 (StepReg包)\n")
cat("  varsel_subset()       - 最优子集 (leaps包)\n")
cat("  varsel_randomforest() - 随机森林变量重要性\n")
cat("  varsel_boruta()       - Boruta 特征选择\n")
cat("  varsel_lasso()        - LASSO 变量筛选 (glmnet包)\n")
cat("  varsel_compare()      - 多方法汇总比较\n")
cat("  varsel_cie_dag()      - DAG引导的CIE筛选 (dagitty+chest)\n")
cat("\nDAG引导变量筛选模板: dag_variable_selection_template.R\n")
cat("  dag_build()           - 构建因果DAG\n")
cat("  dag_adjustment_set()  - 计算最小充分调整集\n")
cat("  dag_cie_screen()      - DAG+CIE联合筛选\n")
cat("  dag_full_workflow()   - 完整DAG+CIE工作流\n")
cat("\n多重插补模板: multiple_imputation_template.R\n")
cat("  mi_diagnose()         - 缺失模式诊断\n")
cat("  mi_impute()           - 多重插补\n")
cat("  mi_pool()             - 汇总分析\n")
cat("  mi_report()           - 完整MI报告\n")
cat("\n异常值决策模板: outlier_decision_template.R\n")
cat("  outlier_inspect()     - 综合异常值仪表盘\n")
cat("  outlier_decide()      - 交互式异常值决策\n")
cat("  outlier_kmeans()      - KM聚类多维异常检测\n")
cat("  outlier_report()      - 异常值处理报告\n")
