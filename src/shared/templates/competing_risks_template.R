# 竞争风险分析模板: CIF、原因别风险、Fine-Gray 亚分布模型
# =============================================================
# 事件编码: 0=删失, 1=目标事件, 2=竞争事件
# 核心方法: CIF (Aalen-Johansen + Gray 检验), CSH (Cox), Fine-Gray (SHR)
#
# 依赖:
#   install.packages(c("tidycmprsk", "cmprsk", "survival", "broom", "ggplot2", "dplyr"))
#
# 作者: MSRA Team | 版本: 0.1.0

# --- 依赖安装与加载 ---
for (pkg in c("tidycmprsk","cmprsk","survival","broom","ggplot2","dplyr")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}
library(tidycmprsk); library(cmprsk); library(survival)
library(broom); library(ggplot2); library(dplyr)


# ==============================================================================
# 1. 累积发病率函数 (CIF) 估计 + Gray 检验
# ==============================================================================

#' CIF 估计 + Gray 检验
#'
#' @param time 数值向量, 随访时间
#' @param status 数值向量, 0=删失 1=目标事件 2=竞争事件
#' @param group 分组变量 (NULL 时不比较组间差异)
#' @param failcode 感兴趣事件编码 (默认 1)
#' @param cencode 删失编码 (默认 0)
#' @return list: cuminc (cmprsk 对象), gray_test (p值), cif_estimates (数据框)
cuminc_analysis <- function(time, status, group = NULL,
                            failcode = 1, cencode = 0) {

  stopifnot(
    "time 不能有缺失值" = !any(is.na(time)),
    "status 不能有缺失值" = !any(is.na(status)),
    "长度一致" = length(time) == length(status),
    "status 编码必须为 0,1,2" = all(status %in% c(0, 1, 2))
  )

  if (is.null(group)) group <- rep("Overall", length(time))
  group <- as.factor(group)

  cuminc_obj <- cmprsk::cuminc(ftime = time, fstatus = status,
                                group = group, cencode = cencode)

  # --- Gray 检验 (cuminc 自带 $Tests) ---
  gray_tests <- cuminc_obj$Tests
  if (!is.null(gray_tests)) {
    gray_df <- data.frame(
      comparison = rownames(gray_tests),
      statistic  = gray_tests[, 1],
      df         = gray_tests[, 2],
      p_value    = gray_tests[, 3],
      stringsAsFactors = FALSE
    )
  } else {
    gray_df <- NULL
  }

  # --- 提取 CIF 估计值 ---
  cif_list <- list()
  for (nm in names(cuminc_obj)) {
    if (nm == "Tests") next
    parts <- strsplit(nm, " ")[[1]]
    grp_name   <- paste(parts[-length(parts)], collapse = " ")
    cause_code <- parts[length(parts)]

    cif_list[[nm]] <- data.frame(
      group  = grp_name,
      cause  = as.integer(cause_code),
      time   = cuminc_obj[[nm]]$time,
      cif    = cuminc_obj[[nm]]$est,
      # CIF 的标准误 (来自 variance component)
      se     = sqrt(cuminc_obj[[nm]]$var),
      stringsAsFactors = FALSE
    )
  }
  cif_df <- bind_rows(cif_list)

  return(list(
    cuminc      = cuminc_obj,
    gray_test   = gray_df,
    cif_estimates = cif_df
  ))
}


# ==============================================================================
# 2. 原因别风险模型 (Cause-Specific Hazards, CSH)
# ==============================================================================

#' 原因别风险模型 (Cox, 竞争事件视为删失)
#'
#' @param time 随访时间
#' @param status 事件类型 (0/1/2)
#' @param covariates 协变量数据框
#' @param cause_of_interest 感兴趣事件编码 (默认 1)
#' @return list: model (coxph), tidy (HR+CI+p), summary_text
csh_fit <- function(time, status, covariates, cause_of_interest = 1) {

  # --- 输入验证 ---
  stopifnot(
    "covariates 必为数据框" = is.data.frame(covariates),
    "长度一致" = length(time) == nrow(covariates)
  )

  csh_status <- ifelse(status == cause_of_interest, 1, 0)
  surv_obj <- Surv(time, csh_status)
  formula  <- as.formula(paste("surv_obj ~", paste(names(covariates), collapse = " + ")))

  csh_model <- coxph(formula, data = covariates)

  tidy_tbl <- broom::tidy(csh_model, exponentiate = TRUE, conf.int = TRUE) %>%
    select(term, estimate, conf.low, conf.high, p.value) %>%
    rename(HR = estimate, CI_low = conf.low, CI_high = conf.high, p = p.value)

  summary_text <- sprintf(
    "CSH 模型 (cause = %d): 共 %d 事件, C-index = %.3f",
    cause_of_interest,
    sum(csh_status),
    summary(csh_model)$concordance["C"]
  )

  return(list(
    model        = csh_model,
    tidy         = tidy_tbl,
    summary_text = summary_text
  ))
}


# ==============================================================================
# 3. Fine-Gray 亚分布风险模型
# ==============================================================================

#' Fine-Gray 亚分布风险模型
#'
#' @param time 随访时间
#' @param status 事件类型 (0/1/2)
#' @param covariates 协变量数据框
#' @param cause_of_interest 感兴趣事件编码 (默认 1)
#' @return list: model (tidycmprsk::crr), tidy (SHR+CI+p), summary_text
fgr_fit <- function(time, status, covariates, cause_of_interest = 1) {

  # --- 输入验证 ---
  stopifnot(
    "covariates 必为数据框" = is.data.frame(covariates),
    "长度一致" = length(time) == nrow(covariates)
  )

  formula <- as.formula(paste(
    "Surv(time, factor(status)) ~", paste(names(covariates), collapse = " + ")
  ))
  model_data <- cbind(data.frame(time = time, status = factor(status)), covariates)

  fg_model <- tidycmprsk::crr(
    formula,
    data    = model_data,
    failcode = cause_of_interest,
    cencode  = 0
  )

  tidy_tbl <- broom::tidy(fg_model, exponentiate = TRUE, conf.int = TRUE) %>%
    select(term, estimate, conf.low, conf.high, p.value) %>%
    rename(SHR = estimate, CI_low = conf.low, CI_high = conf.high, p = p.value)

  summary_text <- sprintf(
    "Fine-Gray 模型 (cause = %d): %d 个协变量纳入",
    cause_of_interest,
    ncol(covariates)
  )

  return(list(
    model        = fg_model,
    tidy         = tidy_tbl,
    summary_text = summary_text
  ))
}


# ==============================================================================
# 4. 竞争风险汇总表
# ==============================================================================

#' 竞争风险汇总表
#'
#' @param time, status, group 数据列
#' @param cause_labels 长度 2 的事件标签
#' @param timepoints CIF 报告时间点 (默认 12/36/60)
#' @return list: cif_table, gray_test, raw_cif
competing_risks_table <- function(time, status, group,
                                   cause_labels = c("Event of Interest", "Competing Event"),
                                   timepoints = c(12, 36, 60)) {

  cr <- cuminc_analysis(time, status, group)
  cif_df <- cr$cif_estimates
  groups <- unique(cif_df$group)

  table_rows <- list()
  for (g in groups) {
    for (i in seq_along(timepoints)) {
      tp <- timepoints[i]
      for (cause_code in c(1, 2)) {
        label <- ifelse(cause_code == 1, cause_labels[1], cause_labels[2])
        sub <- cif_df %>%
          filter(group == g, cause == cause_code, time <= tp) %>%
          arrange(desc(time))

        cif_val <- if (nrow(sub) > 0) sub$cif[1] else NA

        table_rows[[length(table_rows) + 1]] <- data.frame(
          group      = g,
          timepoint  = tp,
          cause      = label,
          cif        = round(cif_val, 4),
          stringsAsFactors = FALSE
        )
      }
    }
  }

  summary_table <- bind_rows(table_rows) %>%
    tidyr::pivot_wider(names_from = timepoint, values_from = cif, names_prefix = "CIF_t")

  return(list(cif_table = summary_table, gray_test = cr$gray_test, raw_cif = cif_df))
}


# ==============================================================================
# 5. 堆叠式累积发病率图 (Stacked CIF Plot)
# ==============================================================================

#' 堆叠式 CIF 图 (各事件类型叠加, 总高度 <= 1)
#'
#' @param cuminc_obj cmprsk::cuminc 对象 (cuminc_analysis()$cuminc)
#' @param title, colors, cause_labels 图形参数
#' @return ggplot 对象
stacked_cif_plot <- function(cuminc_obj,
                              title = "Stacked Cumulative Incidence Function",
                              colors = c("#E74C3C", "#3498DB"),
                              cause_labels = c("Event of Interest", "Competing Event")) {

  plot_data <- list()
  for (nm in names(cuminc_obj)) {
    if (nm == "Tests") next
    parts <- strsplit(nm, " ")[[1]]
    grp   <- paste(parts[-length(parts)], collapse = " ")
    cause <- as.integer(parts[length(parts)])

    raw_cif <- cuminc_obj[[nm]]$est
    if (cause == 1) {
      stacked <- raw_cif
    } else {
      key1 <- paste(grp, "1")
      if (key1 %in% names(cuminc_obj)) {
        cif1 <- cuminc_obj[[key1]]$est
        min_len <- min(length(cif1), length(raw_cif))
        stacked <- cif1[1:min_len] + raw_cif[1:min_len]
      } else {
        stacked <- raw_cif
      }
    }

    cause_label <- ifelse(cause == 1, cause_labels[1], cause_labels[2])
    n <- length(cuminc_obj[[nm]]$time)

    plot_data[[nm]] <- data.frame(
      group  = grp,
      cause  = cause_label,
      time   = cuminc_obj[[nm]]$time,
      cif    = raw_cif[1:n],
      stacked = stacked[1:n],
      stringsAsFactors = FALSE
    )
  }

  df <- bind_rows(plot_data)

  p <- ggplot(df, aes(x = time, y = stacked, fill = cause)) +
    geom_area(position = "identity", alpha = 0.85) +
    facet_wrap(~ group, ncol = 1) +
    scale_fill_manual(values = colors, name = "Event Type") +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1),
                       limits = c(0, 1)) +
    labs(
      title = title,
      x = "Time",
      y = "Cumulative Incidence"
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title    = element_text(face = "bold", hjust = 0.5),
      legend.position = "bottom",
      strip.text    = element_text(face = "bold")
    )

  return(p)
}


# ==============================================================================
# 6. 完整竞争风险工作流（编排器 + 演示）
# ==============================================================================

#' 完整竞争风险工作流 (含数据模拟和所有分析步骤)
#'
#' @param n 样本量 (默认 300)
#' @param seed 随机种子 (默认 42)
#' @return list: data, cuminc, cif_table, csh, fine_gray, plot_stacked
full_competing_risks_workflow <- function(n = 300, seed = 42) {

  set.seed(seed)
  cat("====== 竞争风险分析完整工作流 ======\n\n")

  # ---- 步骤 1: 模拟临床数据 ----
  cat("[1/6] 生成模拟数据...\n")
  group <- sample(c("Treatment", "Control"), n, replace = TRUE)
  age   <- round(rnorm(n, mean = 60, sd = 10))
  sex   <- sample(c("Male", "Female"), n, replace = TRUE)

  # 生存时间（指数分布，组间有差异）
  rate_event     <- ifelse(group == "Treatment", 0.02, 0.03)
  rate_competing <- 0.015  # 竞争事件率（与治疗无关）

  t_event     <- rexp(n, rate = rate_event)
  t_competing <- rexp(n, rate = rate_competing)

  # 取较早发生的事件
  time   <- pmin(t_event, t_competing)
  status <- ifelse(t_event < t_competing, 1, 2)

  # 随机删失（10%）
  censored <- sample(n, size = round(n * 0.1))
  time[censored]   <- time[censored] * runif(length(censored), 0.5, 0.9)
  status[censored] <- 0

  # 随访时间转月
  time <- round(time / 30, 1)

  sim_data <- data.frame(
    time   = time,
    status = status,
    group  = factor(group),
    age    = age,
    sex    = factor(sex)
  )

  cat(sprintf("  N=%d | 目标事件=%d (%.1f%%) | 竞争事件=%d | 删失=%d\n\n",
              n, sum(status == 1), mean(status == 1) * 100,
              sum(status == 2), sum(status == 0)))

  # ---- 步骤 2: CIF + Gray 检验 ----
  cat("[2/6] 累积发病率 + Gray 检验\n")
  cuminc_res <- cuminc_analysis(sim_data$time, sim_data$status, sim_data$group)
  if (!is.null(cuminc_res$gray_test)) print(cuminc_res$gray_test)

  # ---- 步骤 3: 汇总表 ----
  cat("\n[3/6] 竞争风险汇总表\n")
  cr_table <- competing_risks_table(
    sim_data$time, sim_data$status, sim_data$group,
    timepoints = c(12, 24, 36, 60)
  )
  print(cr_table$cif_table)

  # ---- 步骤 4: CSH ----
  cat("\n[4/6] 原因别风险模型 (CSH)\n")
  csh <- csh_fit(sim_data$time, sim_data$status,
                 sim_data[, c("group", "age", "sex")])
  cat(sprintf("  %s\n", csh$summary_text))
  print(csh$tidy)

  # ---- 步骤 5: Fine-Gray ----
  cat("\n[5/6] Fine-Gray 亚分布模型\n")
  fg <- fgr_fit(sim_data$time, sim_data$status,
                sim_data[, c("group", "age", "sex")])
  cat(sprintf("  %s\n", fg$summary_text))
  print(fg$tidy)

  # ---- 步骤 6: 堆叠 CIF 图 ----
  cat("\n[6/6] 堆叠 CIF 图\n")
  p_stacked <- stacked_cif_plot(cuminc_res$cuminc)

  cat("====== 工作流完成 ======\n")
  cat(sprintf("  CSH HR=%.3f | Fine-Gray SHR=%.3f\n", csh$tidy$HR[1], fg$tidy$SHR[1]))
  cat("  (SHR 通常比 HR 更接近 1 -- 竞争事件稀释效应)\n")

  return(list(
    data        = sim_data,
    cuminc      = cuminc_res,
    cif_table   = cr_table,
    csh         = csh,
    fine_gray   = fg,
    plot_stacked = p_stacked
  ))
}


# ==============================================================================
# 使用示例
# ==============================================================================

if (FALSE) {

  results <- full_competing_risks_workflow(n = 300, seed = 42)

  # 查看关键结果
  results$cuminc$gray_test     # Gray 检验 p 值
  results$cif_table$cif_table  # CIF 汇总表
  results$csh$tidy             # CSH HR (95% CI)
  results$fine_gray$tidy       # Fine-Gray SHR (95% CI)
  results$plot_stacked         # 堆叠 CIF 图

  # 单独调用示例
  cr <- cuminc_analysis(results$data$time, results$data$status, results$data$group)
  fg <- fgr_fit(results$data$time, results$data$status,
                results$data[, c("group", "age")])
  # ggsave("stacked_cif.png", results$plot_stacked, width = 8, height = 6, dpi = 300)
}

cat("✅ competing_risks_template.R 已加载\n")
cat("可用函数:\n")
cat("  cuminc_analysis()             - CIF 估计 + Gray 检验\n")
cat("  csh_fit()                     - 原因别风险模型 (Cox HR)\n")
cat("  fgr_fit()                     - Fine-Gray 亚分布模型 (SHR)\n")
cat("  competing_risks_table()       - CIF 汇总表\n")
cat("  stacked_cif_plot()            - 堆叠 CIF 图\n")
cat("  full_competing_risks_workflow() - 完整工作流演示\n")
