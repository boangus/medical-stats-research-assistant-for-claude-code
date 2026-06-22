# =============================================================================
# DAG 引导的变量筛选模板 (DAG-Guided Variable Selection)
# 整合 dagitty + CIE (chest) 的工作流
# 来源：实战医学统计课程第9章 CIE+DAG 文献 + dagitty 包
# =============================================================================

# 依赖：dagitty, ggdag, chest, ggplot2

# ---- S1 DAG 构建 ----

#' 从文本描述构建 DAG
#' @param exposure 暴露变量名
#' @param outcome 结局变量名
#' @param confounders 混杂因素向量（共同影响暴露和结局）
#' @param mediators 中介变量向量（暴露→中介→结局）
#' @param colliders 对撞变量向量（暴露和结局共同影响）
#' @param effect_modifiers 效应修饰因子向量
#' @return dagitty 对象
dag_build <- function(exposure, outcome,
                      confounders = NULL,
                      mediators = NULL,
                      colliders = NULL,
                      effect_modifiers = NULL) {

  # 构建 DAG 边
  edges <- c()

  # 混杂因素 → 暴露 和 混杂因素 → 结局
  if (!is.null(confounders)) {
    for (c in confounders) {
      edges <- c(edges, sprintf("%s -> %s", c, exposure))
      edges <- c(edges, sprintf("%s -> %s", c, outcome))
    }
  }

  # 暴露 → 中介 → 结局
  if (!is.null(mediators)) {
    for (m in mediators) {
      edges <- c(edges, sprintf("%s -> %s", exposure, m))
      edges <- c(edges, sprintf("%s -> %s", m, outcome))
    }
  }

  # 暴露 → 对撞 ← 结局 (不应调整)
  if (!is.null(colliders)) {
    for (co in colliders) {
      edges <- c(edges, sprintf("%s -> %s", exposure, co))
      edges <- c(edges, sprintf("%s -> %s", outcome, co))
    }
  }

  # 效应修饰因子 → 结局
  if (!is.null(effect_modifiers)) {
    for (em in effect_modifiers) {
      edges <- c(edges, sprintf("%s -> %s", em, outcome))
    }
  }

  # 暴露 → 结局
  edges <- c(edges, sprintf("%s -> %s", exposure, outcome))

  # 创建 dagitty 对象
  dag_text <- sprintf("dag {\n  %s\n}", paste(edges, collapse = "\n  "))
  dag <- dagitty::dagitty(dag_text)

  # 设置暴露和结局
  dagitty::exposures(dag) <- exposure
  dagitty::outcomes(dag) <- outcome

  cat("========== DAG 构建完成 ==========\n")
  cat(sprintf("暴露: %s, 结局: %s\n", exposure, outcome))
  cat(sprintf("混杂因素: %s\n", paste(confounders, collapse = ", ")))
  cat(sprintf("中介变量: %s\n", paste(mediators, collapse = ", ")))
  cat(sprintf("对撞变量: %s (不应调整!)\n", paste(colliders, collapse = ", ")))

  return(dag)
}

# ---- S2 DAG 可视化 ----

#' DAG 可视化
#' @param dag dagitty 对象
#' @param exposure 暴露变量
#' @param outcome 结局变量
dag_visualize <- function(dag, exposure = NULL, outcome = NULL) {
  cat("========== DAG 可视化 ==========\n")

  tryCatch({
    p <- ggdag::ggdag(dag) +
      ggdag::theme_dag() +
      ggplot2::labs(title = "Causal DAG")
    print(p)
  }, error = function(e) {
    cat("ggdag 可视化失败，使用文本输出:\n")
    cat(dagitty::toString(dag))
  })
}

# ---- S3 计算调整集 ----

#' 计算最小充分调整集
#' 使用 dagitty 的 adjustmentSets 功能
#' @param dag dagitty 对象
#' @param exposure 暴露变量（可选，已在DAG中设置）
#' @param outcome 结局变量（可选，已在DAG中设置）
#' @return 调整集列表
dag_adjustment_set <- function(dag, exposure = NULL, outcome = NULL) {
  cat("========== 最小充分调整集 ==========\n")

  if (!is.null(exposure)) dagitty::exposures(dag) <- exposure
  if (!is.null(outcome)) dagitty::outcomes(dag) <- outcome

  # 后门准则调整集
  adj_sets <- dagitty::adjustmentSets(dag, type = "canonical")

  if (length(adj_sets) == 0) {
    cat("警告: 无法找到有效的调整集！请检查 DAG 结构。\n")
    return(NULL)
  }

  cat(sprintf("找到 %d 个调整集:\n", length(adj_sets)))
  for (i in seq_along(adj_sets)) {
    cat(sprintf("  集合 %d: {%s}\n", i, paste(adj_sets[[i]], collapse = ", ")))
  }

  # 推荐最小调整集
  min_set <- adj_sets[[which.min(sapply(adj_sets, length))]]
  cat(sprintf("\n推荐最小调整集: {%s}\n", paste(min_set, collapse = ", ")))

  # 检查不应调整的变量（中介和对撞）
  all_vars <- unique(unlist(adj_sets))
  cat("\n注意: 中介变量和对撞变量不应纳入调整集\n")
  cat("  如需估计直接效应，可调整中介变量\n")
  cat("  对撞变量绝对不应调整（会引入偏倚）\n")

  invisible(list(
    all_sets = adj_sets,
    recommended = min_set
  ))
}

# ---- S4 DAG 引导的 CIE 筛选 ----

#' 基于 DAG 的 CIE (Change-in-Estimate) 变量筛选
#' 流程: DAG识别候选混杂 → 逐个添加 → 效应改变>10%判定为混杂
#' @param data 数据框
#' @param exposure 暴露变量名
#' @param outcome 结局变量名
#' @param dag_candidates DAG 识别的候选混杂因素向量
#' @param model_type 模型类型: "glm"(默认), "cox", "lm"
#' @param threshold CIE 阈值，默认10%
#' @param family glm 的族函数（仅 glm 时需要）
#' @return 筛选结果
dag_cie_screen <- function(data, exposure, outcome, dag_candidates,
                           model_type = "glm", threshold = 10,
                           family = binomial()) {
  cat("========== DAG + CIE 联合筛选 ==========\n")
  cat(sprintf("暴露: %s, 结局: %s\n", exposure, outcome))
  cat(sprintf("DAG候选混杂: %s\n", paste(dag_candidates, collapse = ", ")))
  cat(sprintf("CIE阈值: >%d%% 效应改变\n\n", threshold))

  # 粗效应 (Crude model)
  crude_formula <- as.formula(paste(outcome, "~", exposure))
  crude_model <- switch(model_type,
    glm = glm(crude_formula, data = data, family = family),
    lm = lm(crude_formula, data = data),
    cox = survival::coxph(crude_formula, data = data)
  )

  crude_effect <- exp(coef(crude_model)[exposure])
  cat(sprintf("粗效应 (OR/HR/β): %.4f\n\n", crude_effect))

  # 逐个添加候选变量
  results <- data.frame(
    variable = character(),
    adjusted_effect = numeric(),
    change_pct = numeric(),
    is_confounder = logical(),
    stringsAsFactors = FALSE
  )

  for (var in dag_candidates) {
    adj_formula <- as.formula(paste(outcome, "~", exposure, "+", var))
    adj_model <- tryCatch({
      switch(model_type,
        glm = glm(adj_formula, data = data, family = family),
        lm = lm(adj_formula, data = data),
        cox = survival::coxph(adj_formula, data = data)
      )
    }, error = function(e) NULL)

    if (!is.null(adj_model)) {
      adj_effect <- exp(coef(adj_model)[exposure])
      change_pct <- abs(adj_effect - crude_effect) / crude_effect * 100
      is_conf <- change_pct > threshold

      results <- rbind(results, data.frame(
        variable = var,
        adjusted_effect = round(adj_effect, 4),
        change_pct = round(change_pct, 1),
        is_confounder = is_conf,
        stringsAsFactors = FALSE
      ))
    }
  }

  # 输出结果
  results <- results[order(-results$change_pct), ]
  cat("CIE 筛选结果:\n")
  print(results)

  confounders <- results$variable[results$is_confounder]
  cat(sprintf("\n确认的混杂因素 (CIE>%d%%): {%s}\n",
              threshold, paste(confounders, collapse = ", ")))
  cat(sprintf("建议纳入调整集的变量: %s + %s\n", exposure,
              paste(confounders, collapse = " + ")))

  invisible(list(
    crude_effect = crude_effect,
    results = results,
    confirmed_confounders = confounders,
    adjustment_formula = paste(outcome, "~", exposure, "+",
                               paste(confounders, collapse = " + "))
  ))
}

# ---- S5 完整 DAG+CIE 工作流 ----

#' DAG 引导变量筛选完整工作流
#' @param data 数据框
#' @param exposure 暴露变量
#' @param outcome 结局变量
#' @param confounders 基于文献/专家知识的先验混杂因素
#' @param mediators 中介变量（可选）
#' @param colliders 对撞变量（可选，用于警告）
#' @param additional_candidates 数据驱动的额外候选变量
#' @param model_type 模型类型
#' @param cie_threshold CIE 阈值
#' @return 完整结果
dag_full_workflow <- function(data, exposure, outcome,
                              confounders, mediators = NULL,
                              colliders = NULL,
                              additional_candidates = NULL,
                              model_type = "glm",
                              cie_threshold = 10) {
  cat("╔══════════════════════════════════════════════╗\n")
  cat("║  DAG 引导的变量筛选完整工作流                  ║\n")
  cat("╚══════════════════════════════════════════════╝\n\n")

  # Step 1: 构建 DAG
  cat("【Step 1/5】构建因果 DAG\n")
  dag <- dag_build(exposure, outcome, confounders, mediators, colliders)

  # Step 2: 可视化
  cat("\n【Step 2/5】DAG 可视化\n")
  dag_visualize(dag)

  # Step 3: 计算调整集
  cat("\n【Step 3/5】计算最小充分调整集\n")
  adj <- dag_adjustment_set(dag)

  # Step 4: CIE 验证
  cat("\n【Step 4/5】CIE 效应改变验证\n")
  all_candidates <- unique(c(confounders, additional_candidates))
  all_candidates <- all_candidates[all_candidates != exposure &
                                    all_candidates != outcome]

  cie_result <- dag_cie_screen(data, exposure, outcome, all_candidates,
                                model_type = model_type,
                                threshold = cie_threshold)

  # Step 5: 最终变量集
  cat("\n【Step 5/5】最终变量集确定\n")
  final_vars <- cie_result$confirmed_confounders

  cat(sprintf("\n最终调整变量集: {%s}\n", paste(final_vars, collapse = ", ")))
  cat(sprintf("分析公式: %s\n", cie_result$adjustment_formula))

  if (!is.null(colliders)) {
    cat(sprintf("\n⚠️ 对撞变量警告: {%s} 不应纳入调整集！\n",
                paste(colliders, collapse = ", ")))
  }

  cat("\n参照: CIE方法 (Talbot 2021), DAG (Hernán & Robins)\n")

  invisible(list(
    dag = dag,
    adjustment_sets = adj,
    cie_result = cie_result,
    final_variables = final_vars,
    formula = cie_result$adjustment_formula
  ))
}

# ---- 使用示例 ----
# # 完整工作流: 探索降压药→心血管事件的因果效应
# result <- dag_full_workflow(
#   data = mydata,
#   exposure = "treatment",
#   outcome = "cv_event",
#   confounders = c("age", "sex", "bmi", "smoking", "diabetes"),
#   mediators = c("sbp_reduction"),    # 血压降低是中介
#   colliders = c("hospitalization"),  # 住院是对撞，不应调整
#   additional_candidates = c("cholesterol", "egfr", "family_history"),
#   model_type = "glm",
#   cie_threshold = 10
# )
