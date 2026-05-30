# MSRA SAP到方法学描述转换器 (R版本)
#
# 解析SAP中的方法选择，生成符合报告规范的方法学描述。
# 用于 Report Generation 的 Phase 5 方法学描述生成。

#' SAP到方法学描述转换器
#'
#' @description 解析SAP中的方法选择，生成符合报告规范的方法学描述
#' @param sap_path SAP文件路径
#' @param template_path 模板文件路径
#' @return 转换器对象
SAPToMethods <- function(sap_path = NULL, template_path = NULL) {
  # 初始化SAP数据
  sap_data <- list()
  
  #' 加载SAP文件
  #'
  #' @param sap_path SAP文件路径
  #' @return SAP数据列表
  load_sap <- function(sap_path) {
    tryCatch({
      if (grepl("\\.json$", sap_path)) {
        sap_data <<- jsonlite::fromJSON(sap_path)
      } else {
        # 假设是Markdown格式
        content <- readLines(sap_path, warn = FALSE)
        sap_data <<- parse_markdown_sap(paste(content, collapse = "\n"))
      }
      
      return(sap_data)
    }, error = function(e) {
      message(paste("加载SAP文件失败:", e$message))
      return(list())
    })
  }
  
  #' 解析Markdown格式的SAP
  #'
  #' @param content Markdown内容
  #' @return SAP数据列表
  parse_markdown_sap <- function(content) {
    sap_data <- list(
      study_design = "",
      population = "",
      sample_size = "",
      primary_analysis = "",
      secondary_analyses = list(),
      sensitivity_analyses = list(),
      subgroup_analyses = list(),
      software = ""
    )
    
    # 简单解析逻辑（实际应用中需要更复杂的解析）
    lines <- strsplit(content, "\n")[[1]]
    current_section <- ""
    
    for (line in lines) {
      line <- trimws(line)
      if (nchar(line) == 0) next
      
      # 检测章节标题
      if (grepl("^#+", line)) {
        current_section <- tolower(gsub("^#+\\s*", "", line))
      } else if (nchar(current_section) > 0 && nchar(line) > 0) {
        if (grepl("study design", current_section)) {
          sap_data$study_design <- paste(sap_data$study_design, line)
        } else if (grepl("population", current_section)) {
          sap_data$population <- paste(sap_data$population, line)
        } else if (grepl("sample size", current_section)) {
          sap_data$sample_size <- paste(sap_data$sample_size, line)
        } else if (grepl("primary", current_section)) {
          sap_data$primary_analysis <- paste(sap_data$primary_analysis, line)
        } else if (grepl("secondary", current_section)) {
          sap_data$secondary_analyses <- c(sap_data$secondary_analyses, list(line))
        } else if (grepl("sensitivity", current_section)) {
          sap_data$sensitivity_analyses <- c(sap_data$sensitivity_analyses, list(line))
        } else if (grepl("subgroup", current_section)) {
          sap_data$subgroup_analyses <- c(sap_data$subgroup_analyses, list(line))
        } else if (grepl("software", current_section)) {
          sap_data$software <- paste(sap_data$software, line)
        }
      }
    }
    
    return(sap_data)
  }
  
  #' 加载模板
  #'
  #' @param template_path 模板文件路径
  #' @return 模板列表
  load_templates <- function(template_path = NULL) {
    default_templates <- list(
      study_design = "本研究采用{design}设计。",
      population = "研究人群包括{population_description}。",
      sample_size = "样本量计算基于{sample_size_justification}。",
      primary_analysis = "主要分析采用{method}，效应量以{effect_measure}及其95%置信区间表示。",
      secondary_analyses = "次要分析包括{analyses}。",
      sensitivity_analyses = "敏感性分析包括{analyses}。",
      subgroup_analyses = "亚组分析包括{analyses}。",
      software = "统计分析使用{software}（版本{version}）进行。"
    )
    
    if (!is.null(template_path) && file.exists(template_path)) {
      tryCatch({
        templates <- jsonlite::fromJSON(template_path)
        # 合并模板
        for (name in names(templates)) {
          if (name %in% names(default_templates)) {
            default_templates[[name]] <- templates[[name]]
          }
        }
      }, error = function(e) {
        message(paste("加载模板文件失败:", e$message))
      })
    }
    
    return(default_templates)
  }
  
  # 加载模板
  templates <- load_templates(template_path)
  
  #' 生成方法学描述
  #'
  #' @param output_format 输出格式（"markdown" 或 "text"）
  #' @return 方法学描述字符串
  generate_methods_description <- function(output_format = "markdown") {
    if (length(sap_data) == 0) {
      return("未加载SAP数据，无法生成方法学描述。")
    }
    
    sections <- list()
    
    # 研究设计
    if (nchar(sap_data$study_design) > 0) {
      sections <- c(sections, list(generate_study_design_section()))
    }
    
    # 研究人群
    if (nchar(sap_data$population) > 0) {
      sections <- c(sections, list(generate_population_section()))
    }
    
    # 样本量
    if (nchar(sap_data$sample_size) > 0) {
      sections <- c(sections, list(generate_sample_size_section()))
    }
    
    # 主要分析
    if (nchar(sap_data$primary_analysis) > 0) {
      sections <- c(sections, list(generate_primary_analysis_section()))
    }
    
    # 次要分析
    if (length(sap_data$secondary_analyses) > 0) {
      sections <- c(sections, list(generate_secondary_analyses_section()))
    }
    
    # 敏感性分析
    if (length(sap_data$sensitivity_analyses) > 0) {
      sections <- c(sections, list(generate_sensitivity_analyses_section()))
    }
    
    # 亚组分析
    if (length(sap_data$subgroup_analyses) > 0) {
      sections <- c(sections, list(generate_subgroup_analyses_section()))
    }
    
    # 软件
    if (nchar(sap_data$software) > 0) {
      sections <- c(sections, list(generate_software_section()))
    }
    
    # 组装完整描述
    full_description <- paste(sections, collapse = "\n\n")
    
    if (output_format == "markdown") {
      return(paste("## 统计分析方法\n\n", full_description, sep = ""))
    } else {
      return(full_description)
    }
  }
  
  #' 生成研究设计部分
  #'
  #' @return 研究设计描述
  generate_study_design_section <- function() {
    design <- sap_data$study_design
    template <- templates$study_design
    
    gsub("\\{design\\}", design, template)
  }
  
  #' 生成研究人群部分
  #'
  #' @return 研究人群描述
  generate_population_section <- function() {
    population <- sap_data$population
    template <- templates$population
    
    gsub("\\{population_description\\}", population, template)
  }
  
  #' 生成样本量部分
  #'
  #' @return 样本量描述
  generate_sample_size_section <- function() {
    sample_size <- sap_data$sample_size
    template <- templates$sample_size
    
    gsub("\\{sample_size_justification\\}", sample_size, template)
  }
  
  #' 生成主要分析部分
  #'
  #' @return 主要分析描述
  generate_primary_analysis_section <- function() {
    primary_analysis <- sap_data$primary_analysis
    template <- templates$primary_analysis
    
    # 解析主要分析方法
    method <- extract_method(primary_analysis)
    effect_measure <- extract_effect_measure(primary_analysis)
    
    template <- gsub("\\{method\\}", method, template)
    template <- gsub("\\{effect_measure\\}", effect_measure, template)
    
    return(template)
  }
  
  #' 生成次要分析部分
  #'
  #' @return 次要分析描述
  generate_secondary_analyses_section <- function() {
    secondary_analyses <- sap_data$secondary_analyses
    template <- templates$secondary_analyses
    
    if (length(secondary_analyses) > 0) {
      # 最多列出3个
      analyses_list <- secondary_analyses[1:min(3, length(secondary_analyses))]
      analyses_text <- paste(analyses_list, collapse = "、")
      
      if (length(secondary_analyses) > 3) {
        analyses_text <- paste(analyses_text, paste0("等", length(secondary_analyses), "项分析"))
      }
    } else {
      analyses_text <- "无"
    }
    
    gsub("\\{analyses\\}", analyses_text, template)
  }
  
  #' 生成敏感性分析部分
  #'
  #' @return 敏感性分析描述
  generate_sensitivity_analyses_section <- function() {
    sensitivity_analyses <- sap_data$sensitivity_analyses
    template <- templates$sensitivity_analyses
    
    if (length(sensitivity_analyses) > 0) {
      # 最多列出3个
      analyses_list <- sensitivity_analyses[1:min(3, length(sensitivity_analyses))]
      analyses_text <- paste(analyses_list, collapse = "、")
      
      if (length(sensitivity_analyses) > 3) {
        analyses_text <- paste(analyses_text, paste0("等", length(sensitivity_analyses), "项分析"))
      }
    } else {
      analyses_text <- "无"
    }
    
    gsub("\\{analyses\\}", analyses_text, template)
  }
  
  #' 生成亚组分析部分
  #'
  #' @return 亚组分析描述
  generate_subgroup_analyses_section <- function() {
    subgroup_analyses <- sap_data$subgroup_analyses
    template <- templates$subgroup_analyses
    
    if (length(subgroup_analyses) > 0) {
      # 最多列出3个
      analyses_list <- subgroup_analyses[1:min(3, length(subgroup_analyses))]
      analyses_text <- paste(analyses_list, collapse = "、")
      
      if (length(subgroup_analyses) > 3) {
        analyses_text <- paste(analyses_text, paste0("等", length(subgroup_analyses), "项分析"))
      }
    } else {
      analyses_text <- "无"
    }
    
    gsub("\\{analyses\\}", analyses_text, template)
  }
  
  #' 生成软件部分
  #'
  #' @return 软件描述
  generate_software_section <- function() {
    software <- sap_data$software
    template <- templates$software
    
    # 尝试提取软件名称和版本
    software_name <- software
    version <- ""
    
    version_match <- regmatches(software, regexpr("\\d+\\.\\d+(\\.\\d+)?", software))
    if (length(version_match) > 0) {
      version <- version_match[1]
      software_name <- gsub(version, "", software)
      software_name <- trimws(software_name)
    }
    
    template <- gsub("\\{software\\}", software_name, template)
    template <- gsub("\\{version\\}", version, template)
    
    return(template)
  }
  
  #' 从分析文本中提取方法
  #'
  #' @param analysis_text 分析文本
  #' @return 方法名称
  extract_method <- function(analysis_text) {
    method_keywords <- list(
      "t检验" = "独立样本t检验",
      "t-test" = "独立样本t检验",
      "ANOVA" = "单因素方差分析",
      "anova" = "单因素方差分析",
      "卡方" = "χ²检验",
      "chi-square" = "χ²检验",
      "Fisher" = "Fisher精确检验",
      "Mann-Whitney" = "Mann-Whitney U检验",
      "Kruskal-Wallis" = "Kruskal-Wallis检验",
      "线性回归" = "线性回归",
      "linear regression" = "线性回归",
      "Logistic回归" = "Logistic回归",
      "logistic regression" = "Logistic回归",
      "Cox" = "Cox比例风险回归",
      "cox" = "Cox比例风险回归"
    )
    
    for (keyword in names(method_keywords)) {
      if (grepl(keyword, analysis_text, ignore.case = TRUE)) {
        return(method_keywords[[keyword]])
      }
    }
    
    return("适当的统计方法")
  }
  
  #' 从分析文本中提取效应量
  #'
  #' @param analysis_text 分析文本
  #' @return 效应量名称
  extract_effect_measure <- function(analysis_text) {
    effect_keywords <- list(
      "均数差" = "均数差",
      "mean difference" = "均数差",
      "MD" = "均数差",
      "标准化均数差" = "标准化均数差",
      "SMD" = "标准化均数差",
      "Cohen's d" = "Cohen's d",
      "优势比" = "优势比",
      "OR" = "优势比",
      "odds ratio" = "优势比",
      "风险比" = "风险比",
      "HR" = "风险比",
      "hazard ratio" = "风险比",
      "相对风险" = "相对风险",
      "RR" = "相对风险",
      "relative risk" = "相对风险"
    )
    
    for (keyword in names(effect_keywords)) {
      if (grepl(keyword, analysis_text, ignore.case = TRUE)) {
        return(effect_keywords[[keyword]])
      }
    }
    
    return("效应量")
  }
  
  #' 为特定报告规范生成方法学描述
  #'
  #' @param report_type 报告类型（CONSORT/STROBE/STARD等）
  #' @return 各部分的方法学描述列表
  generate_methods_for_report <- function(report_type = "CONSORT") {
    sections <- list()
    
    # 根据报告类型调整描述
    if (report_type == "CONSORT") {
      sections$randomization <- "采用随机数字表法进行随机分组。"
      sections$blinding <- "采用双盲设计，患者和研究者均不知分组情况。"
      sections$allocation_concealment <- "采用中央随机化系统进行分配隐藏。"
    } else if (report_type == "STROBE") {
      sections$design <- "本研究采用队列/病例对照设计。"
      sections$setting <- "研究在[研究机构]进行，招募时间为[时间范围]。"
      sections$participants <- "纳入标准：[标准1]、[标准2]；排除标准：[标准1]、[标准2]。"
    } else if (report_type == "STARD") {
      sections$study_design <- "本研究采用诊断准确性研究设计。"
      sections$index_test <- "索引试验：[试验名称]。"
      sections$reference_standard <- "金标准：[金标准名称]。"
    }
    
    # 生成通用方法学描述
    sections$statistical_analysis <- generate_methods_description()
    
    return(sections)
  }
  
  # 返回转换器对象
  list(
    load_sap = load_sap,
    generate_methods_description = generate_methods_description,
    generate_methods_for_report = generate_methods_for_report
  )
}

# 使用示例
if (FALSE) {
  # 创建转换器
  converter <- SAPToMethods()
  
  # 示例SAP数据
  converter$sap_data <- list(
    study_design = "随机对照试验",
    population = "年龄18-65岁、确诊为[疾病]的患者",
    sample_size = "基于主要结局指标的效应量0.5，检验效能80%，双侧α=0.05，计算需要每组至少80例患者",
    primary_analysis = "主要分析采用独立样本t检验比较两组主要结局指标的差异，效应量以均数差及其95%置信区间表示",
    secondary_analyses = list("次要结局指标的组间比较", "亚组分析", "相关性分析"),
    sensitivity_analyses = list("缺失数据敏感性分析", "不同统计方法敏感性分析"),
    subgroup_analyses = list("年龄亚组分析", "性别亚组分析", "疾病严重程度亚组分析"),
    software = "R 4.3.1"
  )
  
  # 生成方法学描述
  methods_description <- converter$generate_methods_description()
  
  cat("生成的方法学描述：\n")
  cat(methods_description, "\n")
  
  # 为CONSORT报告生成方法学描述
  consort_methods <- converter$generate_methods_for_report("CONSORT")
  
  cat("\nCONSORT报告方法学描述：\n")
  for (section in names(consort_methods)) {
    cat("\n", section, ":\n", sep = "")
    cat(consort_methods[[section]], "\n")
  }
}