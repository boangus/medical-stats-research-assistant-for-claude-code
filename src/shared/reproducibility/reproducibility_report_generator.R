# MSRA 可重复性验证报告生成器 (R版本)
#
# 自动生成可重复性验证报告，包括环境信息、数据指纹、代码版本、结果一致性检查。
# 用于 Stage 3.5 质量门闸和 Stage 4 报告生成。

#' 可重复性验证报告生成器
#'
#' @description 自动生成可重复性验证报告
#' @param project_root 项目根目录
#' @return 报告生成器对象
ReproducibilityReportGenerator <- function(project_root = NULL) {
  # 初始化项目根目录
  if (is.null(project_root)) {
    project_root <- getwd()
  }
  
  project_root <- normalizePath(project_root)
  
  #' 生成环境信息报告
  #'
  #' @return 环境信息列表
  generate_environment_report <- function() {
    env_info <- list(
      platform = paste(R.version$platform, R.version$arch, sep = " - "),
      r_version = R.version.string,
      r_path = Sys.which("R"),
      timestamp = format(Sys.time(), "%Y-%m-%d %H:%M:%S"),
      working_directory = getwd(),
      libraries = list()
    )
    
    # 检查关键包版本
    key_packages <- c("survival", "ggplot2", "dplyr", "tidyr", "readr", "jsonlite")
    
    for (pkg in key_packages) {
      if (requireNamespace(pkg, quietly = TRUE)) {
        env_info$libraries[[pkg]] <- packageVersion(pkg)
      } else {
        env_info$libraries[[pkg]] <- "未安装"
      }
    }
    
    return(env_info)
  }
  
  #' 计算数据指纹
  #'
  #' @param data_path 数据文件路径
  #' @return 数据指纹列表
  compute_data_fingerprint <- function(data_path) {
    if (!file.exists(data_path)) {
      return(list(error = paste("数据文件不存在:", data_path)))
    }
    
    # 计算文件哈希
    file_hash <- digest::digest(data_path, file = TRUE)
    
    # 读取数据并计算统计指纹
    tryCatch({
      if (grepl("\\.csv$", data_path)) {
        df <- read.csv(data_path, stringsAsFactors = FALSE)
      } else if (grepl("\\.(xlsx|xls)$", data_path)) {
        df <- readxl::read_excel(data_path)
      } else {
        return(list(error = paste("不支持的数据格式:", data_path)))
      }
      
      # 计算数据指纹
      fingerprint <- list(
        file_path = data_path,
        file_hash = file_hash,
        shape = list(rows = nrow(df), cols = ncol(df)),
        columns = colnames(df),
        dtypes = sapply(df, class),
        missing_counts = colSums(is.na(df)),
        numeric_stats = list()
      )
      
      # 计算数值列的统计指纹
      numeric_cols <- sapply(df, is.numeric)
      for (col in names(df)[numeric_cols]) {
        col_data <- df[[col]]
        if (!all(is.na(col_data))) {
          fingerprint$numeric_stats[[col]] <- list(
            mean = mean(col_data, na.rm = TRUE),
            sd = sd(col_data, na.rm = TRUE),
            min = min(col_data, na.rm = TRUE),
            max = max(col_data, na.rm = TRUE),
            median = median(col_data, na.rm = TRUE)
          )
        }
      }
      
      return(fingerprint)
      
    }, error = function(e) {
      return(list(error = paste("数据指纹计算失败:", e$message)))
    })
  }
  
  #' 生成可重复性验证报告
  #'
  #' @param analysis_results 分析结果列表
  #' @return 报告文件路径
  generate_verification_report <- function(analysis_results = list()) {
    # 生成报告内容
    report_content <- paste0(
      "# 可重复性验证报告\n\n",
      "> 生成时间: ", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n",
      "> 项目路径: ", project_root, "\n\n",
      "---\n\n",
      "## 1. 环境信息\n\n"
    )
    
    # 添加环境信息
    env_info <- generate_environment_report()
    for (key in names(env_info)) {
      if (key != "libraries") {
        report_content <- paste0(report_content, "- **", key, "**: ", env_info[[key]], "\n")
      }
    }
    
    # 添加库信息
    if (length(env_info$libraries) > 0) {
      report_content <- paste0(report_content, "\n### 已安装包版本\n\n")
      for (pkg in names(env_info$libraries)) {
        report_content <- paste0(report_content, "- **", pkg, "**: ", env_info$libraries[[pkg]], "\n")
      }
    }
    
    report_content <- paste0(report_content, "\n---\n\n## 2. 数据指纹\n\n")
    
    # 添加数据指纹（如果提供）
    if ("data_fingerprints" %in% names(analysis_results)) {
      for (data_name in names(analysis_results$data_fingerprints)) {
        fingerprint <- analysis_results$data_fingerprints[[data_name]]
        report_content <- paste0(report_content, "### ", data_name, "\n")
        
        if ("error" %in% names(fingerprint)) {
          report_content <- paste0(report_content, "- **错误**: ", fingerprint$error, "\n")
        } else {
          report_content <- paste0(report_content, "- **文件哈希**: ", substr(fingerprint$file_hash, 1, 16), "...\n")
          report_content <- paste0(report_content, "- **数据形状**: ", fingerprint$shape$rows, " 行 × ", fingerprint$shape$cols, " 列\n")
          report_content <- paste0(report_content, "- **列数**: ", length(fingerprint$columns), "\n")
        }
        report_content <- paste0(report_content, "\n")
      }
    }
    
    report_content <- paste0(report_content, "\n---\n\n## 3. 可重复性检查结果\n\n")
    
    # 添加检查结果
    if ("reproducibility_checks" %in% names(analysis_results)) {
      for (check_name in names(analysis_results$reproducibility_checks)) {
        check_result <- analysis_results$reproducibility_checks[[check_name]]
        report_content <- paste0(report_content, "### ", check_name, "\n")
        
        if ("error" %in% names(check_result)) {
          report_content <- paste0(report_content, "- **错误**: ", check_result$error, "\n")
        } else {
          report_content <- paste0(report_content, "- **脚本**: ", check_result$script %||% "N/A", "\n")
          report_content <- paste0(report_content, "- **运行次数**: ", check_result$n_runs %||% "N/A", "\n")
          report_content <- paste0(report_content, "- **时间戳**: ", check_result$timestamp %||% "N/A", "\n")
        }
        report_content <- paste0(report_content, "\n")
      }
    }
    
    report_content <- paste0(report_content, "\n---\n\n## 4. 总结\n\n")
    
    # 添加总结
    report_content <- paste0(report_content, "- **验证时间**: ", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
    report_content <- paste0(report_content, "- **项目路径**: ", project_root, "\n")
    report_content <- paste0(report_content, "- **状态**: 验证完成\n")
    
    # 保存报告
    report_filename <- paste0("reproducibility_report_", format(Sys.time(), "%Y%m%d_%H%M%S"), ".md")
    report_path <- file.path(project_root, "reproducibility_report", report_filename)
    
    # 确保目录存在
    dir.create(dirname(report_path), recursive = TRUE, showWarnings = FALSE)
    
    writeLines(report_content, report_path)
    
    return(report_path)
  }
  
  #' 创建存档包
  #'
  #' @param analysis_results 分析结果列表
  #' @return 存档包路径
  create_archive_package <- function(analysis_results = list()) {
    archive_dir <- file.path(project_root, "reproducibility_report", 
                            paste0("archive_", format(Sys.time(), "%Y%m%d_%H%M%S")))
    
    # 创建存档包结构
    dirs <- c("data", "code", "results", "figures", "tables", "docs")
    for (dir_name in dirs) {
      dir.create(file.path(archive_dir, dir_name), recursive = TRUE, showWarnings = FALSE)
    }
    
    # 生成存档清单
    manifest <- list(
      created_at = format(Sys.time(), "%Y-%m-%d %H:%M:%S"),
      project_root = project_root,
      files = list()
    )
    
    # 复制关键文件到存档包
    if ("analysis_script" %in% names(analysis_results)) {
      script_path <- analysis_results$analysis_script
      if (file.exists(script_path)) {
        dest_path <- file.path(archive_dir, "code", basename(script_path))
        file.copy(script_path, dest_path)
        manifest$files$analysis_script <- dest_path
      }
    }
    
    if ("data_path" %in% names(analysis_results)) {
      data_path <- analysis_results$data_path
      if (file.exists(data_path)) {
        dest_path <- file.path(archive_dir, "data", basename(data_path))
        file.copy(data_path, dest_path)
        manifest$files$data <- dest_path
      }
    }
    
    # 保存存档清单
    manifest_path <- file.path(archive_dir, "manifest.json")
    jsonlite::write_json(manifest, manifest_path, auto_unbox = TRUE, pretty = TRUE)
    
    # 生成README
    readme_content <- paste0(
      "# 存档包\n\n",
      "> 创建时间: ", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n",
      "> 项目路径: ", project_root, "\n\n",
      "## 目录结构\n\n",
      "- `data/`: 原始数据文件\n",
      "- `code/`: 分析代码\n",
      "- `results/`: 分析结果\n",
      "- `figures/`: 图表文件\n",
      "- `tables/`: 表格文件\n",
      "- `docs/`: 文档文件\n\n",
      "## 使用方法\n\n",
      "1. 确保已安装所有依赖（见 manifest.json）\n",
      "2. 运行分析代码\n",
      "3. 检查结果是否与原始结果一致\n\n",
      "## 验证\n\n",
      "使用 `reproducibility_check.R` 进行验证。\n"
    )
    
    readme_path <- file.path(archive_dir, "README.md")
    writeLines(readme_content, readme_path)
    
    return(archive_dir)
  }
  
  # 返回报告生成器对象
  list(
    generate_environment_report = generate_environment_report,
    compute_data_fingerprint = compute_data_fingerprint,
    generate_verification_report = generate_verification_report,
    create_archive_package = create_archive_package
  )
}

# 使用示例
if (FALSE) {
  # 创建报告生成器
  generator <- ReproducibilityReportGenerator()
  
  # 生成环境报告
  env_report <- generator$generate_environment_report()
  
  cat("环境报告:\n")
  for (key in names(env_report)) {
    if (key != "libraries") {
      cat("  ", key, ": ", env_report[[key]], "\n", sep = "")
    }
  }
  
  # 创建存档包
  analysis_results <- list(
    analysis_script = "analysis/main_analysis.R",
    data_path = "data/cleaned_data.csv"
  )
  
  archive_path <- generator$create_archive_package(analysis_results)
  cat("\n存档包已创建:", archive_path, "\n")
}