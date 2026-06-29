# reproducibility_check.R — 结果复现验证模板
# =============================================
# 自动重跑分析代码 N 次并检查关键结论一致性
#
# 作者: MSRA Team
# 版本: 0.1.0

#' 检查分析结果的可复现性
#'
#' @param script_path 分析脚本路径
#' @param output_dir 输出目录
#' @param n_runs 重跑次数（默认 3）
#' @param key_params 需要跟踪的关键参数名称向量
#' @param seed_start 起始种子值
#' @param timeout_sec 每次运行超时（秒）
#'
#' @return list(results, summary, verdict)
check_reproducibility <- function(script_path,
                                   output_dir = "reproducibility/",
                                   n_runs = 3,
                                   key_params = NULL,
                                   seed_start = 42,
                                   timeout_sec = 300) {

  if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

  # 确保脚本存在
  if (!file.exists(script_path)) {
    stop("Script not found: ", script_path)
  }

  # 创建临时运行目录
  run_dir <- file.path(output_dir, "runs")
  if (!dir.exists(run_dir)) dir.create(run_dir, recursive = TRUE)

  results <- list()

  for (i in seq_len(n_runs)) {
    seed <- seed_start + i - 1
    cat(sprintf("\n  Run %d/%d (seed=%d)...", i, n_runs, seed))

    # 创建临时脚本（注入种子）
    temp_script <- file.path(run_dir, sprintf("run_%d.R", i))

    script_lines <- readLines(script_path, warn = FALSE)

    # 在脚本开头注入 set.seed
    seed_line <- sprintf("set.seed(%d)", seed)
    temp_lines <- c(seed_line, "", script_lines)
    writeLines(temp_lines, temp_script)

    # 输出文件
    output_file <- file.path(run_dir, sprintf("output_%d.RData", i))
    log_file <- file.path(run_dir, sprintf("log_%d.txt", i))

    # 修改脚本，将关键结果保存到 RData
    temp_lines <- c(
      sprintf('.run_output_file <- "%s"', output_file),
      sprintf('.run_log_file <- "%s"', log_file),
      "",
      '# 捕获所有输出对象',
      '.run_objects <- ls()',
      temp_lines,
      '',
      '# 保存新创建的对象',
      '.run_new_objects <- setdiff(ls(), .run_objects)',
      sprintf('save(list = .run_new_objects, file = "%s")', output_file),
      '# 清空临时变量',
      'rm(.run_output_file, .run_log_file, .run_objects, .run_new_objects)'
    )
    writeLines(temp_lines, temp_script)

    # 执行
    start_time <- Sys.time()
    tryCatch({
      sink(log_file)
      source(temp_script, local = TRUE, echo = FALSE)
      sink()
      elapsed <- as.numeric(difftime(Sys.time(), start_time, units = "secs"))

      # 加载结果
      if (file.exists(output_file)) {
        env <- new.env()
        load(output_file, envir = env)
        results[[i]] <- as.list(env)
        cat(sprintf(" done (%.1fs)", elapsed))
      } else {
        results[[i]] <- list(`__error__` = "No output file generated")
        cat(" WARNING: No output")
      }
    }, error = function(e) {
      sink()
      results[[i]] <<- list(`__error__` = conditionMessage(e))
      cat(sprintf(" ERROR: %s", conditionMessage(e)))
    })
  }

  cat("\n\n")

  # 提取关键参数
  param_values <- list()
  if (!is.null(key_params)) {
    for (p in key_params) {
      values <- sapply(results, function(r) {
        if (p %in% names(r) && !grepl("__error__", p)) {
          val <- r[[p]]
          if (is.numeric(val) && length(val) == 1) val else NA
        } else {
          NA
        }
      })
      param_values[[p]] <- as.numeric(values)
    }
  }

  # 计算一致性
  consistency <- data.frame(
    Parameter = names(param_values),
    Run1 = sapply(param_values, `[`, 1),
    Run2 = sapply(param_values, `[`, 2),
    Run3 = sapply(param_values, `[`, 3),
    Range = sapply(param_values, function(v) diff(range(v, na.rm = TRUE))),
    stringsAsFactors = FALSE
  )

  consistency$Verdict <- sapply(consistency$Range, function(r) {
    if (is.na(r) || is.nan(r)) return("N/A")
    if (r < 0.005) return("✅ Consistent")
    if (r < 0.05) return("⚠️ Minor variation")
    return("❌ Inconsistent")
  })

  # 总体判定
  n_inconsistent <- sum(grepl("❌", consistency$Verdict))
  if (n_inconsistent == 0) {
    verdict <- "✅ PASS — All key parameters consistent across runs"
  } else if (n_inconsistent <= ceiling(nrow(consistency) / 3)) {
    verdict <- "⚠️ CONDITIONAL — Some parameters show variation"
  } else {
    verdict <- "❌ FAIL — Key results not reproducible"
  }

  return(list(
    results = results,
    consistency = consistency,
    summary = consistency[, c("Parameter", "Range", "Verdict")],
    verdict = verdict,
    n_runs = n_runs,
    script = script_path
  ))
}


#' 打印复现验证报告
#'
#' @param check_result check_reproducibility 的返回值
print_reproducibility_report <- function(check_result) {
  cat("\n")
  cat("=", strrep("=", 58), "\n")
  cat("  结果复现验证报告\n")
  cat("=", strrep("=", 58), "\n\n")

  cat("分析脚本:", check_result$script, "\n")
  cat("运行次数:", check_result$n_runs, "\n\n")

  cat("--- 关键参数一致性 ---\n")
  print(check_result$summary, row.names = FALSE)
  cat("\n")

  cat("--- 结论 ---\n")
  cat(check_result$verdict, "\n")
  cat("\n")
  cat(strrep("=", 60), "\n")
}


# ============================================================================
# 示例
# ============================================================================
if (FALSE) {
  # 假设你有一个分析脚本
  result <- check_reproducibility(
    script_path = "analysis/survival_analysis.R",
    n_runs = 3,
    key_params = c("hr_treatment", "p_treatment", "c_index"),
    seed_start = 2024
  )
  print_reproducibility_report(result)
}

cat("✅ reproducibility_check.R 已加载\n")
cat("可用函数:\n")
cat("  check_reproducibility()        - 执行复现验证\n")
cat("  print_reproducibility_report() - 打印报告\n")
