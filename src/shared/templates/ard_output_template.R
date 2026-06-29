# ARD (Analysis Results Dataset) 输出模板
# =================================================
# 基于 Pharmaverse cards 生态，生成符合监管标准的分析结果数据集
# ARD 是临床试验统计分析结果的标准化结构，便于追溯与复现
#
# 核心概念:
#   - ARD 将每项统计结果存储为一行记录（变量名、统计量、值、分组等）
#   - 与 gtsummary 可无缝集成，生成 publication-ready 表格
#   - 符合 CDISC Analysis Results Data Model
#
# 依赖:
#   install.packages("cards")       # Pharmaverse ARD 引擎
#   install.packages("gtsummary")   # 表格渲染
#   install.packages("dplyr")
#   install.packages("tidyr")
#   install.packages("haven")       # XPT 导出

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
})

# 可选依赖检测
.has_cards     <- requireNamespace("cards", quietly = TRUE)
.has_gtsummary <- requireNamespace("gtsummary", quietly = TRUE)
.has_haven     <- requireNamespace("haven", quietly = TRUE)

if (.has_cards)     library(cards)
if (.has_gtsummary) library(gtsummary)

# ==============================================================================
# 1. ard_continuous() — 连续变量的 ARD
# ==============================================================================

#' 创建连续变量的 ARD（均值、SD、中位数、IQR、N、缺失数）
#'
#' @param data 数据框
#' @param variables 连续变量名（字符向量）
#' @param by 分组变量名（字符，可选）
#' @param statistics 统计量列表，可自定义
#'
#' @return ARD 数据框，包含 variable、stat_name、stat_value、group 等列
#'
#' @examples
#' ard_continuous(mtcars, variables = c("mpg", "hp"), by = "cyl")
ard_continuous <- function(data,
                           variables,
                           by = NULL,
                           statistics = NULL) {
  if (.has_cards) {
    # 使用 cards 包原生实现
    if (!is.null(by)) {
      ard <- cards::ard_continuous(
        data = data,
        variables = all_of(variables),
        by = all_of(by),
        statistics = statistics %||% list(
          everything() ~ list(
            N     = ~ length(.),
            mean  = ~ mean(., na.rm = TRUE),
            sd    = ~ sd(., na.rm = TRUE),
            median = ~ median(., na.rm = TRUE),
            q1    = ~ quantile(., 0.25, na.rm = TRUE),
            q3    = ~ quantile(., 0.75, na.rm = TRUE),
            missing = ~ sum(is.na(.))
          )
        )
      )
    } else {
      ard <- cards::ard_continuous(
        data = data,
        variables = all_of(variables),
        statistics = statistics %||% list(
          everything() ~ list(
            N     = ~ length(.),
            mean  = ~ mean(., na.rm = TRUE),
            sd    = ~ sd(., na.rm = TRUE),
            median = ~ median(., na.rm = TRUE),
            q1    = ~ quantile(., 0.25, na.rm = TRUE),
            q3    = ~ quantile(., 0.75, na.rm = TRUE),
            missing = ~ sum(is.na(.))
          )
        )
      )
    }
    return(ard)
  }

  # --- 回退方案：不依赖 cards，使用 base R + data.frame ---
  message("[ard_continuous] cards 包不可用，使用 data.frame 回退方案。")

  calc_stats <- function(x) {
    data.frame(
      N       = length(x),
      mean    = mean(x, na.rm = TRUE),
      sd      = sd(x, na.rm = TRUE),
      median  = median(x, na.rm = TRUE),
      q1      = quantile(x, 0.25, na.rm = TRUE),
      q3      = quantile(x, 0.75, na.rm = TRUE),
      missing = sum(is.na(x)),
      stringsAsFactors = FALSE
    )
  }

  results <- list()
  groups  <- if (!is.null(by)) unique(data[[by]]) else "Overall"

  for (var in variables) {
    for (grp in groups) {
      if (grp == "Overall") {
        sub <- data[[var]]
      } else {
        sub <- data[data[[by]] == grp, var]
      }
      stats <- calc_stats(sub)
      stats$variable <- var
      stats$group    <- grp
      results[[length(results) + 1]] <- stats
    }
  }

  out <- do.call(rbind, results)
  out <- tidyr::pivot_longer(
    out,
    cols = c("N", "mean", "sd", "median", "q1", "q3", "missing"),
    names_to  = "stat_name",
    values_to = "stat_value"
  )
  out <- as.data.frame(out)
  attr(out, "ard_type") <- "continuous"
  out
}

# ==============================================================================
# 2. ard_categorical() — 分类变量的 ARD
# ==============================================================================

#' 创建分类变量的 ARD（n, %, N）
#'
#' @param data 数据框
#' @param variables 分类变量名（字符向量）
#' @param by 分组变量名（字符，可选）
#'
#' @return ARD 数据框
#'
#' @examples
#' ard_categorical(mtcars, variables = c("gear", "carb"), by = "cyl")
ard_categorical <- function(data, variables, by = NULL) {
  if (.has_cards) {
    if (!is.null(by)) {
      ard <- cards::ard_categorical(
        data = data,
        variables = all_of(variables),
        by = all_of(by)
      )
    } else {
      ard <- cards::ard_categorical(
        data = data,
        variables = all_of(variables)
      )
    }
    return(ard)
  }

  # --- 回退方案 ---
  message("[ard_categorical] cards 包不可用，使用 data.frame 回退方案。")

  results <- list()
  groups  <- if (!is.null(by)) unique(data[[by]]) else "Overall"

  for (var in variables) {
    for (grp in groups) {
      if (grp == "Overall") {
        sub <- data[[var]]
      } else {
        sub <- data[data[[by]] == grp, var]
      }
      tab  <- table(sub, useNA = "no")
      N    <- sum(tab)
      freq <- as.numeric(tab)
      pct  <- round(100 * freq / N, 2)

      df <- data.frame(
        variable   = var,
        category   = names(tab),
        n          = freq,
        pct        = pct,
        N          = N,
        group      = grp,
        stringsAsFactors = FALSE
      )
      results[[length(results) + 1]] <- df
    }
  }

  out <- do.call(rbind, results)
  rownames(out) <- NULL
  attr(out, "ard_type") <- "categorical"
  out
}

# ==============================================================================
# 3. ard_comparison() — 组间比较的 ARD
# ==============================================================================

#' 创建组间比较的 ARD（t 检验、卡方检验等）
#'
#' @param data 数据框
#' @param variables 分析变量名（字符向量）
#' @param by 分组变量名（字符，仅允许两水平因子）
#' @param methods 检验方法：auto | t.test | wilcox | chisq | fisher
#'
#' @return ARD 数据框，含 statistic, p_value, method 等
#'
#' @examples
#' ard_comparison(mtcars, variables = c("mpg", "hp"), by = "am")
ard_comparison <- function(data, variables, by, methods = "auto") {
  stopifnot(length(unique(data[[by]])) == 2)

  grp_levels <- sort(unique(data[[by]]))
  g1 <- data[data[[by]] == grp_levels[1], ]
  g2 <- data[data[[by]] == grp_levels[2], ]

  results <- list()

  for (var in variables) {
    x1 <- g1[[var]]
    x2 <- g2[[var]]

    # 自动选择检验方法
    method <- methods
    if (method == "auto") {
      if (is.numeric(x1)) {
        # Shapiro 正态性检验（小样本时）
        if (length(x1) > 3 && length(x2) > 3) {
          p_norm <- tryCatch(
            shapiro.test(c(x1, x2))$p.value,
            error = function(e) 0
          )
          method <- ifelse(p_norm > 0.05, "t.test", "wilcox")
        } else {
          method <- "wilcox"
        }
      } else {
        method <- "chisq"
      }
    }

    # 执行检验
    if (method == "t.test") {
      tt <- t.test(x1, x2)
      stat_row <- data.frame(
        variable  = var,
        method    = "t-test",
        statistic = tt$statistic,
        df        = tt$parameter,
        p_value   = tt$p.value,
        estimate  = diff(tt$estimate),
        ci_lower  = tt$conf.int[1],
        ci_upper  = tt$conf.int[2],
        stringsAsFactors = FALSE
      )
    } else if (method == "wilcox") {
      wt <- wilcox.test(x1, x2)
      stat_row <- data.frame(
        variable  = var,
        method    = "Wilcoxon rank-sum",
        statistic = wt$statistic,
        df        = NA_real_,
        p_value   = wt$p.value,
        estimate  = NA_real_,
        ci_lower  = NA_real_,
        ci_upper  = NA_real_,
        stringsAsFactors = FALSE
      )
    } else if (method == "chisq") {
      tbl <- table(data[[var]], data[[by]])
      ct  <- chisq.test(tbl)
      stat_row <- data.frame(
        variable  = var,
        method    = "Chi-squared",
        statistic = ct$statistic,
        df        = ct$parameter,
        p_value   = ct$p.value,
        estimate  = NA_real_,
        ci_lower  = NA_real_,
        ci_upper  = NA_real_,
        stringsAsFactors = FALSE
      )
    } else if (method == "fisher") {
      tbl <- table(data[[var]], data[[by]])
      ft  <- fisher.test(tbl)
      stat_row <- data.frame(
        variable  = var,
        method    = "Fisher exact",
        statistic = NA_real_,
        df        = NA_real_,
        p_value   = ft$p.value,
        estimate  = ft$estimate,
        ci_lower  = ft$conf.int[1],
        ci_upper  = ft$conf.int[2],
        stringsAsFactors = FALSE
      )
    }
    results[[length(results) + 1]] <- stat_row
  }

  out <- do.call(rbind, results)
  rownames(out) <- NULL
  attr(out, "ard_type") <- "comparison"
  out
}

# ==============================================================================
# 4. ard_regression() — 回归结果的 ARD
# ==============================================================================

#' 创建回归结果的 ARD（OR/HR/Coef 及 CI）
#'
#' @param model 回归模型对象（glm/coxph/lm）
#' @param exponentiate 是否指数化（logistic 回归 → OR, Cox → HR）
#' @param ci_level 置信水平（默认 0.95）
#'
#' @return ARD 数据框，含 variable, estimate, ci_lower, ci_upper, p_value
#'
#' @examples
#' m <- glm(am ~ mpg + hp, data = mtcars, family = binomial)
#' ard_regression(m, exponentiate = TRUE)
ard_regression <- function(model, exponentiate = FALSE, ci_level = 0.95) {
  # 提取系数表
  cf <- summary(model)$coefficients
  if (is.null(cf)) stop("无法从模型中提取系数。")

  # 计算 CI
  z    <- qnorm(1 - (1 - ci_level) / 2)
  est  <- cf[, 1]
  se   <- cf[, 2]
  pv   <- cf[, ncol(cf)]

  ci_lo <- est - z * se
  ci_hi <- est + z * se

  if (exponentiate) {
    est   <- exp(est)
    ci_lo <- exp(ci_lo)
    ci_hi <- exp(ci_hi)
  }

  # 确定指标名称
  if (inherits(model, "coxph")) {
    est_label <- "HR"
  } else if (inherits(model, "glm") &&
             grepl("binomial", family(model)$family)) {
    est_label <- "OR"
  } else {
    est_label <- "Coef"
  }

  out <- data.frame(
    variable  = rownames(cf),
    estimate  = round(est, 4),
    ci_lower  = round(ci_lo, 4),
    ci_upper  = round(ci_hi, 4),
    p_value   = round(pv, 6),
    est_label = est_label,
    stringsAsFactors = FALSE
  )
  rownames(out) <- NULL
  attr(out, "ard_type") <- "regression"
  out
}

# ==============================================================================
# 5. ard_merge() — 合并多个 ARD
# ==============================================================================

#' 合并多个 ARD 数据集为一个统一的 ARD
#'
#' @param ... 多个 ARD 数据框，或 ARD 列表
#'
#' @return 合并后的 ARD 数据框
#'
#' @examples
#' ard1 <- ard_continuous(mtcars, "mpg")
#' ard2 <- ard_categorical(mtcars, "cyl")
#' merged <- ard_merge(ard1, ard2)
ard_merge <- function(...) {
  dots <- list(...)
  # 支持列表输入
  if (length(dots) == 1 && is.list(dots[[1]])) {
    dots <- dots[[1]]
  }
  # 统一列名后再合并
  all_cols <- Reduce(union, lapply(dots, names))
  aligned  <- lapply(dots, function(df) {
    missing <- setdiff(all_cols, names(df))
    for (col in missing) df[[col]] <- NA
    df[, all_cols, drop = FALSE]
  })
  out <- do.call(rbind, aligned)
  rownames(out) <- NULL
  out
}

# ==============================================================================
# 6. ard_to_gtsummary() — ARD 转 gtsummary 表格
# ==============================================================================

#' 将 ARD 转换为 gtsummary 格式化表格
#'
#' @param ard ARD 数据框（由 ard_continuous 或 ard_categorical 生成）
#' @param title 表格标题
#'
#' @return gtsummary 表格对象（或回退方案的 data.frame）
#'
#' @examples
#' ard <- ard_continuous(mtcars, c("mpg", "hp"), by = "cyl")
#' ard_to_gtsummary(ard, title = "连续变量汇总")
ard_to_gtsummary <- function(ard, title = NULL) {
  ard_type <- attr(ard, "ard_type")

  if (.has_gtsummary && .has_cards) {
    # 使用 gtsummary 原生流程
    if (inherits(ard, "card")) {
      tbl <- gtsummary::tbl_ard_summary(ard)
      if (!is.null(title)) tbl <- gtsummary::modify_header(tbl, label = title)
      return(tbl)
    }
  }

  # --- 回退方案：输出格式化 data.frame ---
  message("[ard_to_gtsummary] gtsummary/cards 不可用，返回格式化 data.frame。")

  if (!is.null(ard_type) && ard_type == "continuous") {
    # 重组连续变量统计
    out <- ard %>%
      tidyr::pivot_wider(
        names_from  = stat_name,
        values_from = stat_value
      ) %>%
      mutate(
        summary = sprintf("%.1f +/- %.1f", mean, sd)
      )
  } else if (!is.null(ard_type) && ard_type == "categorical") {
    out <- ard %>%
      mutate(summary = sprintf("%d (%.1f%%)", n, pct))
  } else {
    out <- ard
  }

  if (!is.null(title)) attr(out, "title") <- title
  out
}

# ==============================================================================
# 7. ard_export() — 导出 ARD 为 CSV/XPT
# ==============================================================================

#' 将 ARD 导出为 CSV 或 XPT 文件（用于监管递交）
#'
#' @param ard ARD 数据框
#' @param file 输出文件路径（.csv 或 .xpt）
#' @param dataset_name XPT 数据集名称（仅 .xpt 时需要）
#'
#' @return 无（副作用：写入文件）
#'
#' @examples
#' \dontrun{
#' ard <- ard_continuous(mtcars, "mpg", by = "cyl")
#' ard_export(ard, "ard_continuous.csv")
#' ard_export(ard, "ard_continuous.xpt", dataset_name = "ARD_CONT")
#' }
ard_export <- function(ard, file, dataset_name = "ARD") {
  ext <- tolower(tools::file_ext(file))

  if (ext == "csv") {
    write.csv(ard, file, row.names = FALSE)
    message(sprintf("[ard_export] 已导出 CSV: %s", file))
  } else if (ext == "xpt") {
    if (!.has_haven) stop("导出 XPT 需要 haven 包: install.packages('haven')")
    haven::write_xpt(ard, path = file, version = 8)
    message(sprintf("[ard_export] 已导出 XPT v8: %s", file))
  } else {
    stop("不支持的文件格式，请使用 .csv 或 .xpt")
  }
  invisible(NULL)
}

# ==============================================================================
# 8. full_ard_workflow() — 完整工作流演示
# ==============================================================================

#' ARD 完整工作流演示
#'
#' 使用 mtcars 数据集演示从数据到 ARD 输出的全流程
full_ard_workflow <- function() {
  message("=== ARD 完整工作流 ===")

  # Step 1: 连续变量 ARD
  message("\n[Step 1] 创建连续变量 ARD ...")
  ard_cont <- ard_continuous(mtcars, variables = c("mpg", "hp", "wt"), by = "cyl")
  print(head(ard_cont))

  # Step 2: 分类变量 ARD
  message("\n[Step 2] 创建分类变量 ARD ...")
  ard_cat <- ard_categorical(mtcars, variables = c("gear", "am"), by = "cyl")
  print(head(ard_cat))

  # Step 3: 组间比较 ARD
  message("\n[Step 3] 创建组间比较 ARD ...")
  mtcars_binary <- mtcars[mtcars$am %in% c(0, 1), ]
  ard_comp <- ard_comparison(mtcars_binary, variables = c("mpg", "hp"), by = "am")
  print(ard_comp)

  # Step 4: 回归结果 ARD
  message("\n[Step 4] 创建回归结果 ARD ...")
  m_glm <- glm(am ~ mpg + hp, data = mtcars, family = binomial)
  ard_reg <- ard_regression(m_glm, exponentiate = TRUE)
  print(ard_reg)

  # Step 5: 合并 ARD
  message("\n[Step 5] 合并所有 ARD ...")
  merged <- ard_merge(ard_cont, ard_cat)
  message(sprintf("合并后共 %d 行", nrow(merged)))

  # Step 6: 转 gtsummary
  message("\n[Step 6] 转换为 gtsummary 表格 ...")
  tbl <- ard_to_gtsummary(ard_cont, title = "各缸数连续变量汇总")
  print(tbl)

  # Step 7: 导出
  message("\n[Step 7] 导出 ARD ...")
  outdir <- tempdir()
  ard_export(merged, file.path(outdir, "ard_merged.csv"))
  message(sprintf("导出路径: %s", file.path(outdir, "ard_merged.csv")))

  message("\n=== 工作流完成 ===")
  invisible(list(
    continuous   = ard_cont,
    categorical  = ard_cat,
    comparison   = ard_comp,
    regression   = ard_reg,
    merged       = merged
  ))
}

# 如果直接运行此脚本则执行演示
if (sys.nframe() == 0 && grepl("ard_output_template", sys.frame(1)$ofile %||% "")) {
  full_ard_workflow()
}
