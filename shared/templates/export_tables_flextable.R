# export_tables_flextable.R — 三线表 Word 导出器 (R flextable 版)
# ================================================================
# 将分析结果表格输出为符合医学期刊三线表格式的 .docx 文件。
#
# 三线表格式:
#   ───────────── 顶线粗
#   表序 + 表题
#   ───────────── 表头下线中
#   表头 | 数据
#   ───────────── 底线粗 (无竖线, 无左右端线)
#   表注 (可选)
#
# 依赖: flextable, officer, dplyr
# 安装: install.packages(c("flextable", "officer", "dplyr"))
#
# 用法:
#   source("export_tables_flextable.R")
#   export_three_line_table(data, title = "表1 基线特征", output = "table1.docx")
#
# 作者: MSRA Team
# 版本: 0.1.0

library(flextable)
library(officer)
library(dplyr)

# ============================================================================
# 三线表格式常量
# ============================================================================

# 边框
BORDER_TOP <- fp_border(width = 2)      # 顶线粗
BORDER_MID <- fp_border(width = 1)      # 表头下线中
BORDER_BOTTOM <- fp_border(width = 2)   # 底线粗
BORDER_NONE <- fp_border(width = 0)     # 无线

# 字体
FONT_NAME <- "宋体"
FONT_NAME_HEADER <- "黑体"
FONT_SIZE <- 10    # pt
FONT_SIZE_TITLE <- 10.5

# ============================================================================
# 核心函数: 输出三线表
# ============================================================================

#' 将数据框导出为三线表格式的 Word 文档
#'
#' @param data 数据框 (第一行将作为表头)
#' @param title 表序 + 表题 (例如 "表1 基线特征")
#' @param note 表注 (可选)
#' @param output 输出文件路径 (必须为 .docx)
#' @param font_size 正文字号 (默认 10)
#' @param header_font_size 表头字号 (默认 10)
#' @param header_bold 表头是否加粗 (默认 TRUE)
#' @param col_align 各列对齐方式向量 ("left"/"center"/"right")
#'       默认第一列左对齐, 其余居中
#'
#' @return 无 (写文件)
export_three_line_table <- function(data,
                                     title = "",
                                     note = "",
                                     output = "table.docx",
                                     font_size = FONT_SIZE,
                                     header_font_size = FONT_SIZE,
                                     header_bold = TRUE,
                                     col_align = NULL) {

  # --- 参数校验 ---
  if (!grepl("\\.docx$", output, ignore.case = TRUE)) {
    stop("output 必须以 .docx 结尾")
  }

  n_cols <- ncol(data)

  # 默认对齐: 第一列左对齐, 其余居中
  if (is.null(col_align)) {
    col_align <- c("left", rep("center", n_cols - 1))
  }
  col_align <- rep(col_align, length.out = n_cols)

  # --- 构建 flextable ---
  ft <- flextable(data) %>%

    # 主题: 三线表
    border_remove() %>%
    hline_top(border = BORDER_TOP) %>%
    hline(i = 1, part = "header", border = BORDER_MID) %>%
    hline_bottom(border = BORDER_BOTTOM) %>%

    # 列宽自适应
    autofit() %>%

    # 字体
    font(fontname = FONT_NAME, part = "all") %>%
    fontsize(size = font_size, part = "body") %>%
    fontsize(size = header_font_size, part = "header") %>%
    bold(part = "header") %>%

    # 对齐
    align(j = 1, align = col_align[1], part = "all")

  for (j in 2:n_cols) {
    ft <- ft %>%
      align(j = j, align = col_align[j], part = "all")
  }

  # --- 添加表题 ---
  doc <- read_docx() %>%
    body_add_flextable(
      ft %>% set_caption(
        caption = block_list(
          as_paragraph(
            as_chunk(title, bold = FALSE,
                     fontname = FONT_NAME_HEADER,
                     fontsize = FONT_SIZE_TITLE)
          )
        )
      )
    )

  # --- 添加表注 ---
  if (nchar(note) > 0) {
    doc <- doc %>%
      body_add_par("", style = "Normal") %>%
      body_add_flextable(
        flextable(data.frame(Note = note)) %>%
          border_remove() %>%
          font(fontname = FONT_NAME, part = "all") %>%
          fontsize(size = 9, part = "all") %>%
          align(j = 1, align = "left", part = "all") %>%
          italic()
      )
  }

  # --- 写文件 ---
  dir.create(dirname(output), showWarnings = FALSE, recursive = TRUE)
  print(doc, target = output)
  message(sprintf("✅ 三线表已导出: %s", normalizePath(output)))
}


# ============================================================================
# 便捷函数: 从回归结果创建三线表
# ============================================================================

#' 从回归结果创建三线表
#'
#' @param results_df 数据框 (变量/OR/95%CI/p值)
#' @param title 表题
#' @param output 输出路径
create_regression_table <- function(results_df,
                                     title = "表2 Logistic回归结果",
                                     output = "reports/tables/table2_regression.docx") {
  ft <- flextable(results_df) %>%
    border_remove() %>%
    hline_top(border = BORDER_TOP) %>%
    hline(i = 1, part = "header", border = BORDER_MID) %>%
    hline_bottom(border = BORDER_BOTTOM) %>%
    autofit() %>%
    font(fontname = FONT_NAME, part = "all") %>%
    fontsize(size = FONT_SIZE, part = "all") %>%
    bold(part = "header") %>%
    align(j = 1, align = "left", part = "all") %>%
    align(j = 2:ncol(results_df), align = "center", part = "all")

  doc <- read_docx() %>%
    body_add_flextable(ft)

  dir.create(dirname(output), showWarnings = FALSE, recursive = TRUE)
  print(doc, target = output)
  message(sprintf("✅ 回归结果三线表已导出: %s", normalizePath(output)))
}
