# MSRA 增强图表生成模板 (R版本)
#
# 支持自动调整图表尺寸、中英文标签、高分辨率输出。
# 用于 Report Generation 的 Phase 4 图表生成。

#' 增强图表生成器
#'
#' @description 创建出版级图表，支持中英文标签和期刊规范
#' @param journal_config 期刊配置（可选）
#' @return 图表生成器对象
EnhancedChartGenerator <- function(journal_config = NULL) {
  # 加载配置
  config <- load_config(journal_config)
  
  #' 加载配置
  #'
  #' @param journal_config 期刊配置文件路径
  #' @return 配置列表
  load_config <- function(journal_config) {
    default_config <- list(
      font = list(
        family = c("Arial", "SimHei", "sans-serif"),
        sizes = list(
          title = 14,
          axis_labels = 12,
          tick_labels = 10,
          legend = 9,
          caption = 9
        )
      ),
      sizes = list(
        single_column = 85,
        double_column = 175,
        max_height = 230,
        dpi = 300
      ),
      colors = list(
        primary = "#1f77b4",
        secondary = "#aec7e8",
        accent = "#ff7f0e",
        background = "#ffffff",
        text = "#333333",
        grid = "#e0e0e0"
      )
    )
    
    if (!is.null(journal_config) && file.exists(journal_config)) {
      tryCatch({
        journal_data <- jsonlite::fromJSON(journal_config)
        # 合并配置
        for (key in names(journal_data)) {
          if (key %in% names(default_config)) {
            if (is.list(default_config[[key]])) {
              default_config[[key]] <- modifyList(default_config[[key]], journal_data[[key]])
            } else {
              default_config[[key]] <- journal_data[[key]]
            }
          }
        }
      }, error = function(e) {
        message(paste("加载配置文件失败:", e$message))
      })
    }
    
    return(default_config)
  }
  
  #' 设置中文字体
  #'
  #' @param font_family 字体族
  setup_chinese_font <- function(font_family = NULL) {
    if (is.null(font_family)) {
      font_family <- config$font$family[1]
    }
    
    # 设置字体
    if (font_family == "SimHei" || font_family == "SimSun") {
      theme_set(theme_gray(base_family = font_family))
    } else {
      theme_set(theme_gray(base_family = font_family))
    }
  }
  
  #' 创建图表
  #'
  #' @param figure_type 图表类型
  #' @param column_width 列宽（"single" 或 "double"）
  #' @return ggplot对象
  create_figure <- function(figure_type = "generic", column_width = "single") {
    # 计算尺寸
    width_mm <- config$sizes[[paste0(column_width, "_column")]] %||% 85
    height_mm <- config$sizes$max_height * 0.6  # 默认60%高度
    
    # 转换为厘米
    width_cm <- width_mm / 10
    height_cm <- height_mm / 10
    
    # 创建基础图表
    p <- ggplot() +
      theme_bw() +
      theme(
        plot.title = element_text(size = config$font$sizes$title, face = "bold"),
        axis.title = element_text(size = config$font$sizes$axis_labels),
        axis.text = element_text(size = config$font$sizes$tick_labels),
        legend.text = element_text(size = config$font$sizes$legend),
        panel.grid.major = element_line(color = config$colors$grid, linetype = "dotted"),
        panel.grid.minor = element_blank()
      )
    
    return(p)
  }
  
  #' 设置字体大小
  #'
  #' @param p ggplot对象
  #' @param title 标题
  #' @param xlabel X轴标签
  #' @param ylabel Y轴标签
  #' @return 更新后的ggplot对象
  set_font_sizes <- function(p, title = NULL, xlabel = NULL, ylabel = NULL) {
    if (!is.null(title)) {
      p <- p + ggtitle(title)
    }
    
    if (!is.null(xlabel)) {
      p <- p + xlab(xlabel)
    }
    
    if (!is.null(ylabel)) {
      p <- p + ylab(ylabel)
    }
    
    return(p)
  }
  
  #' 添加网格线
  #'
  #' @param p ggplot对象
  #' @param axis 网格线轴（"both", "x", "y"）
  #' @param linetype 线型
  #' @param alpha 透明度
  #' @return 更新后的ggplot对象
  add_grid <- function(p, axis = "both", linetype = "dotted", alpha = 0.7) {
    if (axis == "both") {
      p <- p + theme(
        panel.grid.major = element_line(color = config$colors$grid, linetype = linetype, alpha = alpha),
        panel.grid.minor = element_line(color = config$colors$grid, linetype = linetype, alpha = alpha * 0.5)
      )
    } else if (axis == "x") {
      p <- p + theme(
        panel.grid.major.x = element_line(color = config$colors$grid, linetype = linetype, alpha = alpha),
        panel.grid.minor.x = element_line(color = config$colors$grid, linetype = linetype, alpha = alpha * 0.5),
        panel.grid.major.y = element_blank(),
        panel.grid.minor.y = element_blank()
      )
    } else if (axis == "y") {
      p <- p + theme(
        panel.grid.major.y = element_line(color = config$colors$grid, linetype = linetype, alpha = alpha),
        panel.grid.minor.y = element_line(color = config$colors$grid, linetype = linetype, alpha = alpha * 0.5),
        panel.grid.major.x = element_blank(),
        panel.grid.minor.x = element_blank()
      )
    }
    
    return(p)
  }
  
  #' 添加图例
  #'
  #' @param p ggplot对象
  #' @param labels 标签列表
  #' @param location 图例位置
  #' @param fontsize 字体大小
  #' @return 更新后的ggplot对象
  add_legend <- function(p, labels = NULL, location = "right", fontsize = NULL) {
    if (is.null(fontsize)) {
      fontsize <- config$font$sizes$legend
    }
    
    p <- p + theme(legend.position = location)
    
    if (!is.null(labels)) {
      # 这里应该有实际的图例添加逻辑
      # 为简化，这里只返回基本图表
    }
    
    return(p)
  }
  
  #' 保存图表
  #'
  #' @param p ggplot对象
  #' @param filepath 文件路径
  #' @param format 文件格式
  #' @param dpi 分辨率
  #' @param width 宽度（厘米）
  #' @param height 高度（厘米）
  save_figure <- function(p, filepath, format = "png", dpi = NULL, width = NULL, height = NULL) {
    if (is.null(dpi)) {
      dpi <- config$sizes$dpi
    }
    
    if (is.null(width)) {
      width <- config$sizes$single_column / 10  # 转换为厘米
    }
    
    if (is.null(height)) {
      height <- config$sizes$max_height * 0.6 / 10  # 转换为厘米
    }
    
    # 确保目录存在
    dir.create(dirname(filepath), recursive = TRUE, showWarnings = FALSE)
    
    # 保存图表
    ggsave(filepath, plot = p, device = format, dpi = dpi, width = width, height = height)
    
    message(paste("图表已保存:", filepath, "(DPI:", dpi, ")"))
  }
  
  #' 创建Kaplan-Meier曲线
  #'
  #' @param survival_data 生存数据
  #' @param title 图表标题
  #' @return ggplot对象
  create_km_curve <- function(survival_data, title = "Kaplan-Meier Curve") {
    p <- create_figure("km_curve")
    
    # 这里应该有实际的KM曲线绘制逻辑
    # 为简化，这里只创建一个示例
    
    # 设置字体大小
    p <- set_font_sizes(p, title = title, xlabel = "Time", ylabel = "Survival Probability")
    
    # 添加网格
    p <- add_grid(p)
    
    return(p)
  }
  
  #' 创建森林图
  #'
  #' @param effect_sizes 效应量列表
  #' @param confidence_intervals 置信区间列表
  #' @param labels 标签列表
  #' @param title 图表标题
  #' @return ggplot对象
  create_forest_plot <- function(effect_sizes, confidence_intervals, labels, title = "Forest Plot") {
    p <- create_figure("forest_plot")
    
    # 这里应该有实际的森林图绘制逻辑
    # 为简化，这里只创建一个示例
    
    # 设置字体大小
    p <- set_font_sizes(p, title = title, xlabel = "Effect Size", ylabel = "Study")
    
    # 添加网格
    p <- add_grid(p, axis = "x")
    
    return(p)
  }
  
  #' 创建ROC曲线
  #'
  #' @param fpr 假阳性率
  #' @param tpr 真阳性率
  #' @param auc_value AUC值
  #' @param title 图表标题
  #' @return ggplot对象
  create_roc_curve <- function(fpr, tpr, auc_value, title = "ROC Curve") {
    p <- create_figure("roc_curve")
    
    # 绘制ROC曲线
    roc_data <- data.frame(FPR = fpr, TPR = tpr)
    
    p <- p + 
      geom_line(data = roc_data, aes(x = FPR, y = TPR), color = config$colors$primary, size = 1) +
      geom_abline(intercept = 0, slope = 1, color = "gray", linetype = "dashed") +
      annotate("text", x = 0.7, y = 0.3, label = paste("AUC =", round(auc_value, 3)), size = 4)
    
    # 设置字体大小
    p <- set_font_sizes(p, title = title, xlabel = "False Positive Rate", ylabel = "True Positive Rate")
    
    # 添加图例
    p <- add_legend(p, c("ROC curve", "Random guess"))
    
    # 添加网格
    p <- add_grid(p)
    
    return(p)
  }
  
  # 返回图表生成器对象
  list(
    create_figure = create_figure,
    set_font_sizes = set_font_sizes,
    add_grid = add_grid,
    add_legend = add_legend,
    save_figure = save_figure,
    create_km_curve = create_km_curve,
    create_forest_plot = create_forest_plot,
    create_roc_curve = create_roc_curve
  )
}

# 使用示例
if (FALSE) {
  # 创建图表生成器
  generator <- EnhancedChartGenerator()
  
  # 创建示例图表
  p <- generator$create_figure("km_curve")
  
  # 生成示例数据
  x <- seq(0, 10, length.out = 100)
  y <- exp(-x/5)
  
  # 绘制曲线
  plot_data <- data.frame(x = x, y = y)
  p <- p + geom_line(data = plot_data, aes(x = x, y = y), color = "#1f77b4")
  
  # 设置字体大小
  p <- generator$set_font_sizes(p, title = "示例Kaplan-Meier曲线", 
                               xlabel = "时间（月）", ylabel = "生存概率")
  
  # 添加网格
  p <- generator$add_grid(p)
  
  # 保存图表
  generator$save_figure(p, "example_km_curve.png")
  
  message("示例图表已生成")
}