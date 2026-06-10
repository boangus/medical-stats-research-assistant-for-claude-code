# =============================================================================
# 统一数据导入模板 — Medical Statistics Research Assistant
# =============================================================================
# 基于 rio R 包设计理念 (https://gesistsa.github.io/rio/)
# 自动根据文件扩展名选择合适的读取器
# 实现 "一个函数搞定所有格式"
#
# 参考: rio 的 import() / export() / convert() 三核心函数
#
# 依赖:
#   install.packages("rio")           # 核心（已包含所有依赖）
#   或按需安装:
#   install.packages("readr")         # CSV/TSV
#   install.packages("readxl")        # Excel
#   install.packages("haven")         # SPSS/SAS/Stata
#   install.packages("jsonlite")      # JSON
#   install.packages("arrow")         # Parquet
# =============================================================================

library(dplyr)
library(tools)

# =============================================================================
# 1. 核心导入函数
# =============================================================================

#' 自动识别文件格式并导入数据
#'
#' 根据文件扩展名自动选择适当的读取函数
#' 支持格式：csv, tsv, xlsx, xls, sav, dta, sas7bdat, rda, rds, json, parquet
#'
#' @param file_path 文件路径（字符串）
#' @param sheet    Excel 工作表名或编号（默认为第1个）
#' @param na       缺失值标记（默认 c("", "NA", "N/A", "NULL"))
#' @param ...      传递给底层读取函数的额外参数
#' @return data.frame
import_data <- function(file_path, sheet = NULL,
                        na = c("", "NA", "N/A", "NULL", "Missing", "missing"),
                        ...) {
  
  if (!file.exists(file_path)) {
    stop("文件不存在: ", file_path)
  }
  
  ext <- tolower(file_ext(file_path))
  
  cat("📂 正在导入:", basename(file_path), "\n")
  cat("   格式:", ext, "\n")
  
  data <- switch(ext,
    # --- 分隔文本 ---
    csv  = import_csv(file_path, na, ...),
    tsv  = import_tsv(file_path, na, ...),
    txt  = import_csv(file_path, na, sep = "\t", ...),
    
    # --- Excel ---
    xlsx = import_excel(file_path, sheet, na, ...),
    xls  = import_excel(file_path, sheet, na, ...),
    
    # --- 统计软件 ---
    sav  = import_spss(file_path, na, ...),
    zsav = import_spss(file_path, na, ...),
    dta  = import_stata(file_path, na, ...),
    sas7bdat = import_sas(file_path, na, ...),
    por  = import_spss(file_path, na, ...),
    
    # --- R 对象 ---
    rda  = import_rda(file_path, ...),
    rds  = import_rds(file_path, ...),
    
    # --- JSON ---
    json = import_json(file_path, na, ...),
    
    # --- Parquet ---
    parquet = import_parquet(file_path, ...),
    
    # --- 不支持 ---
    stop("不支持的格式: .", ext, "\n",
         "支持的格式: csv, tsv, txt, xlsx, xls, ",
         "sav, zsav, dta, sas7bdat, por, rda, rds, json, parquet")
  )
  
  # 标准化
  data <- standardize_imported_data(data, file_path)
  
  cat("✔ 导入完成: ", nrow(data), "行 × ", ncol(data), "列\n", sep = "")
  
  return(data)
}

#' 批量导入（处理多个文件或 Excel 多工作表）
import_data_list <- function(file_path, ...) {
  ext <- tolower(file_ext(file_path))
  
  if (ext %in% c("xlsx", "xls")) {
    # Excel 多工作表
    sheets <- readxl::excel_sheets(file_path)
    cat("📂 检测到", length(sheets), "个工作表\n")
    
    data_list <- list()
    for (s in sheets) {
      cat("  导入工作表:", s, "\n")
      data_list[[s]] <- import_data(file_path, sheet = s, ...)
    }
  } else if (ext == "rda") {
    # RData 多对象
    data_list <- import_rda_list(file_path)
  } else {
    # 单文件，返回单元素列表
    cat("  单文件导入\n")
    data_list <- list(data = import_data(file_path, ...))
  }
  
  return(data_list)
}

# =============================================================================
# 2. 格式专用导入函数
# =============================================================================

#' 导入 CSV
import_csv <- function(file_path, na = c("", "NA"),
                       sep = ",", ...) {
  readr::read_csv(file_path, na = na, show_col_types = FALSE, ...)
}

#' 导入 TSV
import_tsv <- function(file_path, na = c("", "NA"), ...) {
  readr::read_tsv(file_path, na = na, show_col_types = FALSE, ...)
}

#' 导入 Excel
import_excel <- function(file_path, sheet = NULL,
                         na = c("", "NA"), ...) {
  if (is.null(sheet)) {
    sheet <- 1  # 默认第一个工作表
  }
  readxl::read_excel(file_path, sheet = sheet, na = na, ...)
}

#' 导入 SPSS
import_spss <- function(file_path, na = c("", "NA"), ...) {
  haven::read_sav(file_path, ...) %>%
    haven::zap_labels() %>%        # 去掉值标签
    haven::zap_missing()           # 去掉用户定义缺失
}

#' 导入 Stata
import_stata <- function(file_path, na = c("", "NA"), ...) {
  haven::read_dta(file_path, ...) %>%
    haven::zap_labels()
}

#' 导入 SAS
import_sas <- function(file_path, na = c("", "NA"), ...) {
  haven::read_sas(file_path, ...)
}

#' 导入 RData
import_rda <- function(file_path, ...) {
  env <- new.env()
  load(file_path, envir = env)
  # 返回第一个数据框
  objs <- ls(env)
  for (obj in objs) {
    if (is.data.frame(get(obj, envir = env))) {
      return(get(obj, envir = env))
    }
  }
  stop("RData 文件中未找到数据框")
}

#' 批量导入 RData
import_rda_list <- function(file_path) {
  env <- new.env()
  load(file_path, envir = env)
  objs <- ls(env)
  data_list <- list()
  for (obj in objs) {
    if (is.data.frame(get(obj, envir = env))) {
      data_list[[obj]] <- get(obj, envir = env)
    }
  }
  if (length(data_list) == 0) {
    stop("RData 文件中未找到数据框")
  }
  cat("  找到", length(data_list), "个数据框\n")
  return(data_list)
}

#' 导入 RDS
import_rds <- function(file_path, ...) {
  readRDS(file_path)
}

#' 导入 JSON
import_json <- function(file_path, na = c("", "NA"), ...) {
  jsonlite::fromJSON(file_path, flatten = TRUE, ...)
}

#' 导入 Parquet
import_parquet <- function(file_path, ...) {
  arrow::read_parquet(file_path, ...)
}

# =============================================================================
# 3. 数据导出
# =============================================================================

#' 自动识别格式导出
#' @param data 数据框
#' @param file_path 导出文件路径
export_data <- function(data, file_path, ...) {
  ext <- tolower(file_ext(file_path))
  dir.create(dirname(file_path), showWarnings = FALSE, recursive = TRUE)
  
  cat("📤 正在导出:", basename(file_path), "\n")
  
  switch(ext,
    csv  = readr::write_csv(data, file_path, na = "", ...),
    tsv  = readr::write_tsv(data, file_path, na = "", ...),
    xlsx = writexl::write_xlsx(data, file_path, ...),
    sav  = haven::write_sav(data, file_path, ...),
    dta  = haven::write_dta(data, file_path, ...),
    rds  = saveRDS(data, file_path, ...),
    rda  = { assign("data", data); save(list = "data", file = file_path) },
    json = jsonlite::write_json(data, file_path, ...),
    parquet = arrow::write_parquet(data, file_path, ...),
    stop("不支持的导出格式: .", ext)
  )
  
  cat("✔ 导出完成:", file_path, "\n")
}

# =============================================================================
# 4. 格式转换
# =============================================================================

#' 格式转换（import + export）
#' @param input_file 输入文件
#' @param output_file 输出文件
convert_data <- function(input_file, output_file, ...) {
  cat("🔄 格式转换:", basename(input_file), "→", basename(output_file), "\n")
  data <- import_data(input_file, ...)
  export_data(data, output_file)
  cat("✔ 转换完成\n")
}

# =============================================================================
# 5. 标准化处理
# =============================================================================

#' 标准化导入后的数据
standardize_imported_data <- function(data, file_path) {
  data <- data %>%
    
    # 列名清洗（类似 janitor::clean_names）
    janitor::clean_names() %>%
    
    # 去掉全空列
    janitor::remove_empty("cols") %>%
    
    # 所有字符列去除前后空格
    mutate(across(where(is.character), ~trimws(.))) %>%
    
    # 空字符串转 NA
    mutate(across(where(is.character), ~na_if(., ""))) %>%
    
    # 添加来源标记
    mutate(.import_source = basename(file_path), .before = 1)
  
  return(data)
}

# =============================================================================
# 6. 批量处理
# =============================================================================

#' 批量导入目录下所有指定格式文件
#' @param dir_path 目录路径
#' @param pattern 文件模式（如 "*.csv"）
import_data_dir <- function(dir_path, pattern = "*.csv") {
  files <- list.files(dir_path, pattern = pattern, full.names = TRUE)
  
  if (length(files) == 0) {
    stop("未找到匹配文件: ", dir_path, " / ", pattern)
  }
  
  cat("📂 找到", length(files), "个文件\n")
  
  data_list <- list()
  for (f in files) {
    name <- tools::file_path_sans_ext(basename(f))
    cat("  读取:", basename(f), "\n")
    data_list[[name]] <- import_data(f)
  }
  
  return(data_list)
}

# =============================================================================
# 使用示例
# =============================================================================

if (FALSE) {
  # 1. 自动识别格式
  df1 <- import_data("data/raw_data.csv")
  df2 <- import_data("data/raw_data.xlsx")
  df3 <- import_data("data/raw_data.sav")
  
  # 2. 指定工作表
  df4 <- import_data("data/multi_sheet.xlsx", sheet = "Demographics")
  
  # 3. 批量导入所有 CSV
  dfs <- import_data_dir("data/raw/", "*.csv")
  
  # 4. Excel 多工作表
  sheets <- import_data_list("data/multi_sheet.xlsx")
  
  # 5. 导出
  export_data(df1, "data/cleaned_data.xlsx")
  
  # 6. 格式转换
  convert_data("data/raw_data.sav", "data/raw_data.csv")
}
