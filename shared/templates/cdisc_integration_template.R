# CDISC 数据集成模板 (CDISC Data Integration)
# =================================================
# 实现 SDTM/ADaM 格式检测、转换、验证与导出
# 适用于：临床试验数据的 CDISC 标准化处理与监管递交准备
#
# 核心功能:
#   - 自动检测数据是否符合 SDTM/ADaM 结构
#   - SDTM 域转换为分析就绪数据
#   - ADaM 数据集结构验证
#   - XPT 传输文件导出（FDA 递交格式）
#   - ADaM 规范文档生成
#
# 参考:
#   - CDISC SDTM v3.4: https://www.cdisc.org/standards/foundational/sdtm
#   - CDISC ADaM v2.1: https://www.cdisc.org/standards/foundational/adam
#
# 依赖:
#   install.packages("haven")    # XPT I/O
#   install.packages("dplyr")
#   install.packages("tidyr")
#   install.packages("lubridate")

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
})

.has_haven <- requireNamespace("haven", quietly = TRUE)
if (.has_haven) library(haven)

# CDISC 标准域前缀定义
.sdtm_domains <- c(
  "DM", "AE", "CM", "EX", "LB", "MH", "SV", "VS", "EG", "PE",
  "QS", "SC", "DS", "FA", "IS", "MB", "MS", "PP", "RELREC", "SUPP"
)

.adam_structures <- list(
  ADSL = c(
    "STUDYID", "USUBJID", "SUBJID", "SITEID", "TRT01P", "TRT01A",
    "AGE", "AGEGR1", "SEX", "RACE", "ETHNIC", "SAFFL", "ITTFL",
    "RANDFL", "TRTSDT", "TRTEDT", "DTHDT", "LSTALVDT"
  ),
  ADAE = c(
    "STUDYID", "USUBJID", "AESEQ", "AETERM", "AEDECOD", "AESOC",
    "AESTDTC", "AEENDTC", "AESEV", "AESER", "AEREL", "AEACN",
    "AOCCFL", "TRTA", "TRTAN"
  ),
  ADLB = c(
    "STUDYID", "USUBJID", "LBSEQ", "PARAMCD", "PARAM", "AVAL",
    "BASE", "CHG", "PCHG", "ANRIND", "BNRIND", "ADT", "ATM",
    "AVISIT", "AVISITN", "TRTP", "TRTA"
  ),
  ADTTE = c(
    "STUDYID", "USUBJID", "PARAMCD", "PARAM", "AVAL", "AVALU",
    "CNSR", "STARTDT", "ADT", "SRCDRV", "PARCAT1"
  )
)

# ==============================================================================
# 1. detect_cdisc_format() — 自动检测 CDISC 格式
# ==============================================================================

#' 自动检测数据是否为 SDTM 或 ADaM 格式
#'
#' @param data 数据框
#' @param domain_hint 域名提示（如 "DM", "ADSL"），可选
#'
#' @return 列表：format (sdtm/adam/unknown), domain, confidence, details
#'
#' @examples
#' # 创建模拟 SDTM DM 域
#' dm <- data.frame(
#'   STUDYID = "STUDY01", USUBJID = paste0("STUDY01-00", 1:10),
#'   SUBJID  = paste0("00", 1:10), SITEID = "001",
#'   SEX     = sample(c("M", "F"), 10, replace = TRUE),
#'   AGE     = rnorm(10, 55, 10),
#'   ARM     = sample(c("Treatment", "Control"), 10, replace = TRUE)
#' )
#' detect_cdisc_format(dm)
detect_cdisc_format <- function(data, domain_hint = NULL) {
  col_names <- toupper(names(data))
  n_rows    <- nrow(data)
  n_cols    <- ncol(data)

  # 匹配 SDTM 特征列
  sdtm_core   <- c("STUDYID", "USUBJID", "DOMAIN")
  sdtm_common <- c("STUDYID", "USUBJID", "SUBJID", "SITEID",
                    "SEX", "AGE", "RACE", "ARM", "TRT", "VISIT")
  sdtm_score  <- sum(sdtm_core %in% col_names) * 2 +
                 sum(sdtm_common %in% col_names)

  # 匹配 ADaM 特征列
  adam_core   <- c("STUDYID", "USUBJID")
  adam_common <- c("STUDYID", "USUBJID", "PARAMCD", "PARAM", "AVAL",
                   "BASE", "CHG", "AVISIT", "TRT01P", "TRT01A",
                   "SAFFL", "ITTFL", "TRTP", "TRTA", "ADT")
  adam_score  <- sum(adam_core %in% col_names) * 2 +
                 sum(adam_common %in% col_names)

  # SDTM 特有标识
  has_domain_col <- "DOMAIN" %in% col_names
  has_seq_col    <- any(grepl("SEQ$", col_names)) && has_domain_col
  has_dtc_col    <- any(grepl("DTC$", col_names))

  # ADaM 特有标识
  has_paramcd    <- "PARAMCD" %in% col_names
  has_aval       <- "AVAL" %in% col_names
  has_flag       <- any(col_names %in% c("SAFFL", "ITTFL", "RANDFL", "EFFFL"))
  has_visitn     <- "AVISITN" %in% col_names

  # 域名推断
  domain <- domain_hint
  if (is.null(domain) && has_domain_col) {
    domain <- unique(data$DOMAIN)[1]
  }

  # 综合评分
  sdtm_indicators <- sum(has_domain_col, has_seq_col, has_dtc_col)
  adam_indicators <- sum(has_paramcd, has_aval, has_flag, has_visitn)

  if (adam_score > sdtm_score && adam_indicators >= 2) {
    fmt        <- "adam"
    confidence <- min(0.5 + adam_indicators * 0.15, 0.95)
    detected_domain <- if (!is.null(domain)) domain else {
      # 推断 ADaM 数据集名
      if (has_paramcd) {
        if ("CNSR" %in% col_names) "ADTTE" else "ADLB"
      } else {
        "ADSL"
      }
    }
  } else if (sdtm_score >= adam_score && sdtm_indicators >= 1) {
    fmt        <- "sdtm"
    confidence <- min(0.5 + sdtm_indicators * 0.15, 0.95)
    detected_domain <- domain %||% "DM"
  } else {
    fmt        <- "unknown"
    confidence <- 0
    detected_domain <- NA_character_
  }

  # 验证域名是否在标准列表中
  domain_valid <- if (fmt == "sdtm") {
    detected_domain %in% .sdtm_domains
  } else if (fmt == "adam") {
    detected_domain %in% names(.adam_structures)
  } else {
    FALSE
  }

  list(
    format      = fmt,
    domain      = detected_domain,
    confidence  = round(confidence, 2),
    domain_valid = domain_valid,
    details     = list(
      n_rows           = n_rows,
      n_cols           = n_cols,
      sdtm_score       = sdtm_score,
      adam_score       = adam_score,
      has_domain_col   = has_domain_col,
      has_seq_col      = has_seq_col,
      has_dtc_col      = has_dtc_col,
      has_paramcd      = has_paramcd,
      has_aval         = has_aval,
      has_flag         = has_flag,
      sdtm_indicators  = sdtm_indicators,
      adam_indicators   = adam_indicators
    )
  )
}

# ==============================================================================
# 2. sdtm_to_analysis() — SDTM 转分析数据
# ==============================================================================

#' 将 SDTM 域转换为分析就绪数据
#'
#' @param sdtm_data SDTM 数据框
#' @param domain SDTM 域名（如 "DM", "LB"），可选（自动检测）
#' @param pivot_wide 是否将纵向数据宽化（如 LB → 每行一个受试者）
#' @param date_cols 需要转换的日期列名（字符向量）
#'
#' @return 分析就绪的数据框
#'
#' @examples
#' lb <- data.frame(
#'   STUDYID = "S01", USUBJID = "S01-001", DOMAIN = "LB",
#'   LBTESTCD = c("ALT", "AST", "BILI"),
#'   LBSTRESN  = c(25, 30, 0.8),
#'   VISITNUM  = c(1, 1, 1)
#' )
#' sdtm_to_analysis(lb, domain = "LB", pivot_wide = TRUE)
sdtm_to_analysis <- function(sdtm_data,
                              domain = NULL,
                              pivot_wide = FALSE,
                              date_cols = NULL) {
  # 自动检测域
  if (is.null(domain)) {
    detection <- detect_cdisc_format(sdtm_data, domain_hint = NULL)
    domain    <- detection$domain
    message(sprintf("[sdtm_to_analysis] 自动检测域: %s (置信度: %.0f%%)",
                    domain, detection$confidence * 100))
  }

  out <- sdtm_data

  # 日期转换
  dtc_cols <- grep("DTC$", names(out), value = TRUE)
  if (!is.null(date_cols)) dtc_cols <- unique(c(dtc_cols, date_cols))

  for (col in dtc_cols) {
    if (col %in% names(out) && is.character(out[[col]])) {
      out[[col]] <- tryCatch(
        as.Date(out[[col]], format = "%Y-%m-%d"),
        error = function(e) {
          message(sprintf("  [警告] 列 %s 日期转换失败，保持原格式", col))
          out[[col]]
        }
      )
    }
  }

  # 根据域进行特定转换
  if (domain == "DM") {
    # DM 域：通常已是宽格式，添加分析常用派生变量
    if ("RFSTDTC" %in% names(out)) {
      out$TRTSDT <- as.Date(out$RFSTDTC, format = "%Y-%m-%d")
    }
    if ("AGE" %in% names(out)) {
      out$AGEGR1 <- cut(out$AGE,
                        breaks = c(0, 45, 65, Inf),
                        labels = c("<45", "45-65", ">=65"),
                        right = FALSE)
    }
    if ("SEX" %in% names(out)) {
      out$SEX <- toupper(out$SEX)
    }
  } else if (domain == "LB" && pivot_wide) {
    # LB 域宽化：每个 TESTCD 一列
    key_cols <- intersect(
      names(out),
      c("STUDYID", "USUBJID", "VISITNUM", "VISIT", "LBDTC")
    )
    if ("LBTESTCD" %in% names(out) && "LBSTRESN" %in% names(out)) {
      out <- out %>%
        tidyr::pivot_wider(
          id_cols   = all_of(key_cols),
          names_from  = LBTESTCD,
          values_from = LBSTRESN,
          names_prefix = "LB_"
        )
    }
  } else if (domain == "AE") {
    # AE 域：确保必需列存在
    if (!"AESEQ" %in% names(out)) {
      out <- out %>% group_by(USUBJID) %>% mutate(AESEQ = row_number()) %>% ungroup()
    }
    if ("AESTDTC" %in% names(out)) {
      out$ASTDT <- as.Date(out$AESTDTC, format = "%Y-%m-%d")
    }
  }

  # 清理列名中的前缀（如 LBTESTCD → TESTCD）
  message(sprintf("[sdtm_to_analysis] 域=%s, 输出 %d 行 x %d 列",
                  domain, nrow(out), ncol(out)))
  out
}

# ==============================================================================
# 3. adam_validate() — 验证 ADaM 数据集结构
# ==============================================================================

#' 验证 ADaM 数据集是否符合标准结构
#'
#' @param data ADaM 数据框
#' @param dataset ADaM 数据集名（如 "ADSL", "ADLB"）
#' @param strict 严格模式：缺失必需列时是否报错
#'
#' @return 列表：valid (TRUE/FALSE), missing_required, missing_recommended,
#'         extra_columns, warnings
#'
#' @examples
#' adsl <- data.frame(
#'   STUDYID = "S01", USUBJID = "S01-001", SUBJID = "001",
#'   AGE = 55, SEX = "M", TRT01P = "Treatment",
#'   SAFFL = "Y", ITTFL = "Y"
#' )
#' adam_validate(adsl, dataset = "ADSL")
adam_validate <- function(data, dataset = NULL, strict = FALSE) {
  # 自动检测数据集
  if (is.null(dataset)) {
    detection <- detect_cdisc_format(data)
    if (detection$format != "adam") {
      return(list(
        valid = FALSE,
        missing_required = character(0),
        missing_recommended = character(0),
        extra_columns = character(0),
        warnings = sprintf("未检测到 ADaM 格式 (检测结果: %s)", detection$format)
      ))
    }
    dataset <- detection$domain
  }

  # 获取标准结构
  if (!dataset %in% names(.adam_structures)) {
    return(list(
      valid = FALSE,
      missing_required = character(0),
      missing_recommended = character(0),
      extra_columns = character(0),
      warnings = sprintf("未知的 ADaM 数据集: %s", dataset)
    ))
  }

  expected_cols <- .adam_structures[[dataset]]
  actual_cols   <- toupper(names(data))

  # 分类必需列与推荐列
  required_cols <- expected_cols[1:min(6, length(expected_cols))]
  recommended_cols <- setdiff(expected_cols, required_cols)

  missing_required    <- setdiff(required_cols, actual_cols)
  missing_recommended <- setdiff(recommended_cols, actual_cols)
  extra_columns       <- setdiff(actual_cols, expected_cols)

  # 验证
  is_valid <- length(missing_required) == 0

  # 额外检查
  warnings_list <- character(0)

  # 检查 USUBJID 唯一性（ADSL 特有）
  if (dataset == "ADSL" && "USUBJID" %in% actual_cols) {
    dupes <- sum(duplicated(data$USUBJID))
    if (dupes > 0) {
      warnings_list <- c(warnings_list,
                         sprintf("ADSL 中 USUBJID 有 %d 个重复值", dupes))
    }
  }

  # 检查 AVAL 是否为数值型
  if ("AVAL" %in% actual_cols && !is.numeric(data$AVAL)) {
    warnings_list <- c(warnings_list, "AVAL 列应为数值型")
  }

  # 检查标志变量值
  flag_cols <- intersect(actual_cols, c("SAFFL", "ITTFL", "RANDFL", "EFFFL"))
  for (fc in flag_cols) {
    vals <- unique(data[[fc]])
    if (!all(vals %in% c("Y", "N", NA))) {
      warnings_list <- c(warnings_list,
                         sprintf("%s 列含非标准值: %s",
                                 fc, paste(vals, collapse = ", ")))
    }
  }

  if (strict && !is_valid) {
    stop(sprintf("ADaM 验证失败 (数据集 %s): 缺失必需列 %s",
                 dataset, paste(missing_required, collapse = ", ")))
  }

  list(
    valid               = is_valid,
    dataset             = dataset,
    missing_required    = missing_required,
    missing_recommended = missing_recommended,
    extra_columns       = extra_columns,
    n_rows              = nrow(data),
    n_cols              = ncol(data),
    warnings            = warnings_list
  )
}

# ==============================================================================
# 4. export_xpt() — 导出 XPT 传输文件
# ==============================================================================

#' 将数据框导出为 SAS XPT 传输文件（FDA 递交格式）
#'
#' @param data 数据框
#' @param file 输出文件路径（.xpt）
#' @param dataset_name XPT 内部数据集名称（最多 8 字符，大写）
#' @param version XPT 版本（5 或 8，默认 8）
#'
#' @return 无（副作用：写入 .xpt 文件）
#'
#' @examples
#' \dontrun{
#' adsl <- data.frame(STUDYID = "S01", USUBJID = "S01-001")
#' export_xpt(adsl, "adsl.xpt", dataset_name = "ADSL")
#' }
export_xpt <- function(data, file, dataset_name = NULL, version = 8) {
  if (!.has_haven) {
    stop("导出 XPT 需要 haven 包: install.packages('haven')")
  }

  # 自动推断数据集名
  if (is.null(dataset_name)) {
    fname <- toupper(tools::file_path_sans_ext(basename(file)))
    dataset_name <- substr(fname, 1, 8)
  }

  # 验证数据集名
  dataset_name <- toupper(dataset_name)
  if (nchar(dataset_name) > 8) {
    warning(sprintf("数据集名 '%s' 超过 8 字符，已截断为 '%s'",
                    dataset_name, substr(dataset_name, 1, 8)))
    dataset_name <- substr(dataset_name, 1, 8)
  }

  # 列名规范：全部大写
  names(data) <- toupper(names(data))

  # 导出
  haven::write_xpt(data, path = file, version = version)
  message(sprintf("[export_xpt] 已导出 XPT v%d: %s (数据集: %s, %d 行 x %d 列)",
                  version, file, dataset_name, nrow(data), ncol(data)))
  invisible(NULL)
}

# ==============================================================================
# 5. generate_adam_spec() — 生成 ADaM 规范文档
# ==============================================================================

#' 基于数据集生成 ADaM 规范文档（数据字典）
#'
#' @param data ADaM 数据框
#' @param dataset ADaM 数据集名
#' @param output_format 输出格式: "data.frame" | "csv" | "list"
#' @param file CSV 输出路径（当 output_format = "csv" 时需要）
#'
#' @return 根据格式返回数据框、CSV 文件或列表
#'
#' @examples
#' adsl <- data.frame(
#'   STUDYID = "S01", USUBJID = "S01-001",
#'   AGE = 55, SEX = "M", TRT01P = "Treatment",
#'   SAFFL = "Y"
#' )
#' spec <- generate_adam_spec(adsl, dataset = "ADSL")
#' print(spec)
generate_adam_spec <- function(data,
                               dataset = NULL,
                               output_format = "data.frame",
                               file = NULL) {
  output_format <- match.arg(output_format, c("data.frame", "csv", "list"))

  # 自动检测
  if (is.null(dataset)) {
    detection <- detect_cdisc_format(data)
    dataset   <- detection$domain %||% "UNKNOWN"
  }

  # 构建规范表
  spec <- data.frame(
    dataset    = dataset,
    variable   = names(data),
    type       = sapply(data, function(x) {
      if (is.numeric(x)) {
        if (all(x == round(x), na.rm = TRUE)) "INTEGER" else "NUMERIC"
      } else if (is.Date(x)) {
        "DATE"
      } else if (is.factor(x)) {
        "CHARACTER (FACTOR)"
      } else {
        "CHARACTER"
      }
    }),
    length     = sapply(data, function(x) max(nchar(as.character(x)), na.rm = TRUE)),
    label      = sapply(names(data), function(n) {
      # 从 CDISC 标准标签推断
      label_map <- c(
        STUDYID = "Study Identifier",
        USUBJID = "Unique Subject Identifier",
        SUBJID  = "Subject Identifier for the Study",
        SITEID  = "Study Site Identifier",
        AGE     = "Age",
        SEX     = "Sex",
        RACE    = "Race",
        ARM     = "Description of Planned Arm",
        TRT01P  = "Planned Treatment for Period 01",
        TRT01A  = "Actual Treatment for Period 01",
        SAFFL   = "Safety Population Flag",
        ITTFL   = "Intent-To-Treat Population Flag",
        AVAL    = "Analysis Value",
        BASE    = "Baseline Value",
        CHG     = "Change from Baseline",
        PARAMCD = "Parameter Code",
        PARAM   = "Parameter",
        AVISIT  = "Analysis Visit",
        CNSR    = "Censor"
      )
      ifelse(n %in% names(label_map), label_map[n], "")
    }),
    n_unique   = sapply(data, function(x) length(unique(x[!is.na(x)]))),
    n_missing  = sapply(data, function(x) sum(is.na(x))),
    pct_missing = round(sapply(data, function(x) 100 * mean(is.na(x))), 1),
    stringsAsFactors = FALSE
  )
  rownames(spec) <- NULL

  # 添加 ADaM 标准结构对照
  if (dataset %in% names(.adam_structures)) {
    expected   <- .adam_structures[[dataset]]
    spec$required <- ifelse(spec$variable %in% expected[1:min(6, length(expected))],
                            "Y", "N")
    spec$adam_standard <- ifelse(spec$variable %in% expected, "Y", "N")
  }

  # 输出
  if (output_format == "csv") {
    if (is.null(file)) file <- paste0(tolower(dataset), "_spec.csv")
    write.csv(spec, file, row.names = FALSE)
    message(sprintf("[generate_adam_spec] 规范文档已导出: %s", file))
    invisible(spec)
  } else if (output_format == "list") {
    as.list(spec)
  } else {
    spec
  }
}

# ==============================================================================
# 完整工作流示例
# ==============================================================================

#' CDISC 数据集成完整工作流演示
full_cdisc_workflow <- function() {
  message("========================================")
  message(" CDISC 数据集成 — 完整工作流演示")
  message("========================================")

  # 模拟 SDTM DM 域
  dm_sdtm <- data.frame(
    STUDYID  = "STUDY01",
    USUBJID  = paste0("STUDY01-00", sprintf("%02d", 1:20)),
    SUBJID   = sprintf("%03d", 1:20),
    DOMAIN   = "DM",
    SITEID   = "001",
    SEX      = sample(c("M", "F"), 20, replace = TRUE),
    AGE      = round(rnorm(20, 55, 10)),
    RACE     = "WHITE",
    ARM      = sample(c("Treatment A", "Treatment B", "Placebo"), 20, replace = TRUE),
    RFSTDTC  = "2024-01-15",
    stringsAsFactors = FALSE
  )

  # Step 1: 格式检测
  message("\n[Step 1] 检测 CDISC 格式 ...")
  fmt <- detect_cdisc_format(dm_sdtm)
  message(sprintf("  格式: %s, 域: %s, 置信度: %.0f%%",
                  fmt$format, fmt$domain, fmt$confidence * 100))

  # Step 2: SDTM → 分析数据
  message("\n[Step 2] SDTM 转分析就绪数据 ...")
  dm_analysis <- sdtm_to_analysis(dm_sdtm, domain = "DM")
  message(sprintf("  年龄分组: %s", paste(levels(dm_analysis$AGEGR1), collapse = ", ")))

  # Step 3: ADaM 验证
  message("\n[Step 3] 验证 ADaM 结构 ...")
  adsl <- dm_analysis %>%
    rename(TRT01P = ARM) %>%
    mutate(
      STUDYID = "STUDY01",
      SAFFL   = "Y",
      ITTFL   = "Y"
    )
  val <- adam_validate(adsl, dataset = "ADSL")
  message(sprintf("  验证结果: %s", ifelse(val$valid, "通过", "失败")))
  if (length(val$warnings) > 0) {
    message(sprintf("  警告: %s", paste(val$warnings, collapse = "; ")))
  }

  # Step 4: 导出 XPT
  message("\n[Step 4] 导出 XPT 文件 ...")
  xpt_file <- file.path(tempdir(), "adsl.xpt")
  export_xpt(adsl, xpt_file, dataset_name = "ADSL")

  # Step 5: 生成规范文档
  message("\n[Step 5] 生成 ADaM 规范文档 ...")
  spec <- generate_adam_spec(adsl, dataset = "ADSL")
  print(spec[, c("variable", "type", "label", "required")])

  message("\n========================================")
  message(" 工作流完成")
  message("========================================")

  invisible(list(
    format_detection = fmt,
    analysis_data    = dm_analysis,
    validation       = val,
    xpt_file         = xpt_file,
    spec             = spec
  ))
}

# 如果直接运行此脚本则执行演示
if (sys.nframe() == 0 && grepl("cdisc_integration_template", sys.frame(1)$ofile %||% "")) {
  full_cdisc_workflow()
}
