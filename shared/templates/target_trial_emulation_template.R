# 目标试验模拟 (Target Trial Emulation) 模板
# =============================================================
# 核心方法: 克隆-删失-加权 (Clone-Censor-Weight) 框架
# 适用场景: 利用观察性数据模拟随机对照试验, 估计因果治疗效果
#
# 依赖:
#   install.packages(c("survival", "WeightIt", "survey", "broom",
#                       "ggplot2", "dplyr", "sandwich"))
#
# 作者: MSRA Team | 版本: 0.1.0

# --- 依赖安装与加载 ---
for (pkg in c("survival", "WeightIt", "survey", "broom", "ggplot2", "dplyr", "sandwich")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}
library(survival); library(WeightIt); library(survey)
library(broom); library(ggplot2); library(dplyr)


# ==============================================================================
# 1. 定义目标试验方案 (Specify the Target Trial)
# ==============================================================================

#' 定义目标试验方案
#'
#' 将临床问题转化为结构化的试验方案, 包括纳入标准、治疗策略、
#' 结局指标、随访时间和因果对比类型。
#'
#' @param eligibility 命名列表, 纳入/排除标准 (如 list(age_min = 18, age_max = 75))
#' @param treatment_strategies 字符向量, 治疗策略名称 (如 c("DrugA", "DrugB"))
#' @param outcome 字符, 主要结局变量名
#' @param time_to_event 字符, 生存时间变量名 (可为 NULL, 用于非生存结局)
#' @param follow_up_months 数值, 最大随访时间 (月)
#' @param causal_contrast 字符, 因果对比类型: "ATE" (平均治疗效应) 或 "ATT" (治疗组平均效应)
#' @param grace_period_days 数值, 恩惠期 (grace period) 天数 (默认 0)
#' @return list, 结构化的试验方案
#' @examples
#' protocol <- tte_specify_trial(
#'   eligibility    = list(age_min = 40, sex = "all"),
#'   treatment_strategies = c("SGLT2i", "SU"),
#'   outcome        = "cv_event",
#'   time_to_event  = "follow_up_days",
#'   follow_up_months = 36,
#'   causal_contrast = "ATE"
#' )
tte_specify_trial <- function(eligibility,
                              treatment_strategies,
                              outcome,
                              time_to_event = NULL,
                              follow_up_months,
                              causal_contrast = c("ATE", "ATT"),
                              grace_period_days = 0) {

  causal_contrast <- match.arg(causal_contrast)

  stopifnot(
    "treatment_strategies 至少需要 2 种" = length(treatment_strategies) >= 2,
    "follow_up_months 必须为正数"       = follow_up_months > 0,
    "outcome 不能为空"                  = nchar(outcome) > 0
  )

  protocol <- list(
    eligibility           = eligibility,
    treatment_strategies  = treatment_strategies,
    outcome               = outcome,
    time_to_event         = time_to_event,
    follow_up_months      = follow_up_months,
    follow_up_days        = follow_up_months * 30.44,
    causal_contrast       = causal_contrast,
    grace_period_days     = grace_period_days,
    created_at            = Sys.time()
  )

  message("[TTE] 目标试验方案已定义:")
  message("  治疗策略: ", paste(treatment_strategies, collapse = " vs "))
  message("  结局: ", outcome, " | 随访: ", follow_up_months, " 个月")
  message("  因果对比: ", causal_contrast, " | 恩惠期: ", grace_period_days, " 天")
  return(protocol)
}


# ==============================================================================
# 2. 克隆-删失 (Clone-Censor) 创建虚拟试验数据
# ==============================================================================

#' 克隆-删失方法: 为每种治疗策略创建克隆
#'
#' @param data 数据框, 观察性数据 (宽格式)
#' @param protocol list, 由 tte_specify_trial() 生成的方案
#' @param treatment_var 字符, 实际治疗变量名
#' @param confounders 字符向量, 需要调整的混杂因素
#' @return 数据框, 长格式 (每行 = 一个克隆)
#' @examples
#' clones <- tte_clone_data(df, protocol, "treatment", c("age", "sex", "bmi"))
tte_clone_data <- function(data, protocol, treatment_var, confounders) {

  strategies <- protocol$treatment_strategies
  outcome    <- protocol$outcome
  time_var   <- protocol$time_to_event
  follow_up  <- protocol$follow_up_days

  # 应用纳入标准
  eligible <- data
  for (nm in names(protocol$eligibility)) {
    val <- protocol$eligibility[[nm]]
    if (is.numeric(val) && length(val) == 2) {
      eligible <- eligible[eligible[[nm]] >= val[1] & eligible[[nm]] <= val[2], ]
    } else if (is.character(val)) {
      eligible <- eligible[eligible[[nm]] %in% val, ]
    }
  }

  message("[TTE] 纳入标准筛选: ", nrow(data), " -> ", nrow(eligible), " 例")

  # 为每种治疗策略创建克隆
  clones_list <- lapply(seq_along(strategies), function(i) {
    clone <- eligible
    clone$clone_id      <- seq_len(nrow(clone))
    clone$assigned_trt  <- strategies[i]

    # 治疗策略一致性删失: 如果实际治疗与分配不同, 在治疗切换时删失
    actual <- clone[[treatment_var]]
    if (is.numeric(actual)) {
      consistent <- (actual == (i - 1))  # 假设 0/1 编码
    } else {
      consistent <- (actual == strategies[i])
    }
    clone$censor_at_switch <- as.integer(!consistent)

    # 限制随访时间
    time_col <- clone[[time_var]]
    clone$event <- ifelse(time_col > follow_up, 0, clone[[outcome]])
    clone$time  <- pmin(time_col, follow_up)

    # 若在恩惠期内未开始治疗, 标记
    clone <- clone %>%
      mutate(
        time  = ifelse(.data$censor_at_switch == 1, .data$time, .data$time),
        event = ifelse(.data$censor_at_switch == 1, 0, .data$event)
      )

    return(clone)
  })

  clones_df <- bind_rows(clones_list)
  message("[TTE] 克隆数据集: ", nrow(clones_df), " 行 (", length(strategies), " 策略)")
  return(clones_df)
}


# ==============================================================================
# 3. 逆概率删失加权 (IPCW)
# ==============================================================================

#' 计算逆概率删失加权 (IPCW)
#'
#' 对克隆-删失数据拟合删失模型, 生成稳定化 IPCW 权重。
#'
#' @param clones 数据框, 由 tte_clone_data() 生成的长格式克隆数据
#' @param confounders 字符向量, 混杂因素变量名
#' @param treatment_var 字符, 分配治疗变量名
#' @param method 字符, 权重估计方法: "ps" (倾向评分) 或 "gbm" (广义增强模型)
#' @return 数据框, 添加 weight 列
#' @examples
#' weighted <- tte_censor_weights(clones, c("age", "sex", "bmi"), "assigned_trt")
tte_censor_weights <- function(clones, confounders, treatment_var, method = c("ps", "gbm")) {

  method <- match.arg(method)

  # 构建删失指示: censor_at_switch == 1 表示被删失
  clones$is_censored <- clones$censor_at_switch

  # 仅对未删失 + 目标治疗策略的观测估计权重
  # 使用 WeightIt 包拟合倾向评分
  form <- as.formula(paste(treatment_var, "~", paste(confounders, collapse = " + ")))

  if (method == "ps") {
    W <- weightit(form, data = clones, method = "ps",
                  estimand = "ATE", stabilize = TRUE)
  } else {
    W <- weightit(form, data = clones, method = "gbm",
                  estimand = "ATE", stabilize = TRUE)
  }

  clones$ipcw_weight <- W$weights

  # 截断极端权重 (99 百分位)
  q99 <- quantile(clones$ipcw_weight, 0.99, na.rm = TRUE)
  clones$ipcw_weight <- pmin(clones$ipcw_weight, q99)

  message("[TTE] IPCW 权重: 均值 = ", round(mean(clones$ipcw_weight, na.rm = TRUE), 3),
          " | 范围 = [", round(min(clones$ipcw_weight, na.rm = TRUE), 3), ", ",
          round(max(clones$ipcw_weight, na.rm = TRUE), 3), "]")
  message("  极端权重已截断于 99 百分位 (", round(q99, 3), ")")

  return(clones)
}


# ==============================================================================
# 4. 拟合加权结局模型
# ==============================================================================

#' 拟合加权结局模型 (Cox 或 Logistic)
#'
#' @param data 数据框, 包含 weight 列的加权数据
#' @param protocol list, 试验方案
#' @param treatment_var 字符, 分配治疗变量名
#' @param confounders 字符向量, 调整变量
#' @param model_type 字符: "cox" (Cox 比例风险) 或 "logistic" (Logistic 回归)
#' @return list: model (模型对象), summary_df (结果数据框), hr_or (风险比或比值比)
#' @examples
#' result <- tte_fit_model(weighted_df, protocol, "assigned_trt",
#'                         c("age", "sex"), model_type = "cox")
tte_fit_model <- function(data, protocol, treatment_var, confounders,
                          model_type = c("cox", "logistic")) {

  model_type <- match.arg(model_type)

  # 使用 survey 包处理加权估计
  design <- svydesign(ids = ~1, weights = ~ipcw_weight, data = data)

  form_str <- paste("Surv(time, event) ~", treatment_var,
                     "+", paste(confounders, collapse = " + "))
  if (model_type == "logistic") {
    form_str <- paste("event ~", treatment_var,
                       "+", paste(confounders, collapse = " + "))
  }

  form <- as.formula(form_str)

  if (model_type == "cox") {
    model <- svyglm(form, design = design, family = quasipoisson())
    # svycoxph 可用于更精确的 Cox 模型
    tryCatch({
      model <- svycoxph(form, design = design)
    }, error = function(e) {
      message("[TTE] svycoxph 失败, 退回到 svyglm: ", e$message)
      model <<- svyglm(update(form, . ~ .), design = design)
    })
  } else {
    model <- svyglm(form, design = design, family = quasibinomial())
  }

  # 提取治疗效果
  tidy_res <- tidy(model, conf.int = TRUE, exponentiate = (model_type == "cox"))
  trt_row  <- tidy_res[tidy_res$term == treatment_var, ]

  effect_label <- if (model_type == "cox") "HR" else "OR"
  message("[TTE] 加权模型 (", model_type, "):")
  message("  ", effect_label, " = ", round(trt_row$estimate, 3),
          " (95% CI: ", round(trt_row$conf.low, 3), "-",
          round(trt_row$conf.high, 3), ")")
  message("  p = ", formatC(trt_row$p.value, format = "e", digits = 2))

  return(list(
    model      = model,
    summary_df = tidy_res,
    hr_or      = trt_row$estimate,
    ci_low     = trt_row$conf.low,
    ci_high    = trt_row$conf.high,
    p_value    = trt_row$p.value,
    effect_label = effect_label
  ))
}


# ==============================================================================
# 5. 敏感性分析
# ==============================================================================

#' 敏感性分析: 变化删失假设
#'
#' 通过修改 IPCW 截断阈值、纳入不同混杂集等方式评估结果稳健性。
#'
#' @param data 数据框, 克隆数据
#' @param protocol list, 试验方案
#' @param treatment_var 字符, 治疗变量名
#' @param confounder_sets list of character vectors, 不同混杂因素组合
#' @param truncation_levels 数值向量, 权重截断百分位 (如 c(0.95, 0.97, 0.99, 1.0))
#' @param model_type 字符, "cox" 或 "logistic"
#' @return 数据框, 各场景下的效应估计
#' @examples
#' sens <- tte_sensitivity(clones, protocol, "assigned_trt",
#'                         list(c("age"), c("age", "sex", "bmi")),
#'                         c(0.95, 0.99, 1.0))
tte_sensitivity <- function(data, protocol, treatment_var,
                            confounder_sets, truncation_levels = c(0.95, 0.97, 0.99, 1.0),
                            model_type = "cox") {

  results <- expand.grid(
    confounders_name = sapply(confounder_sets, paste, collapse = "+"),
    truncation       = truncation_levels,
    stringsAsFactors = FALSE
  )
  results$hr <- results$ci_low <- results$ci_high <- NA_real_

  row_idx <- 1
  for (cs in confounder_sets) {
    cs_name <- paste(cs, collapse = "+")
    for (trunc in truncation_levels) {

      # 拷贝数据, 调整截断
      d <- data
      if (trunc < 1.0) {
        q_val <- quantile(d$ipcw_weight, trunc, na.rm = TRUE)
        d$ipcw_weight <- pmin(d$ipcw_weight, q_val)
      }

      tryCatch({
        res <- tte_fit_model(d, protocol, treatment_var, cs, model_type)
        mask <- results$confounders_name == cs_name & results$truncation == trunc
        results$hr[mask]     <- res$hr_or
        results$ci_low[mask] <- res$ci_low
        results$ci_high[mask] <- res$ci_high
      }, error = function(e) {
        message("[TTE] 敏感性分析失败: ", cs_name, " trunc=", trunc, " - ", e$message)
      })
      row_idx <- row_idx + 1
    }
  }

  # 绘制森林图
  results$label <- paste0(results$confounders_name, " (Q", results$truncation, ")")
  p <- ggplot(results, aes(x = .data$hr, y = reorder(.data$label, -.data$hr))) +
    geom_point(size = 3) +
    geom_errorbarh(aes(xmin = .data$ci_low, xmax = .data$ci_high), height = 0.2) +
    geom_vline(xintercept = 1, linetype = "dashed", color = "red") +
    labs(title = "TTE 敏感性分析", x = protocol$treatment_strategies[1],
         y = NULL) +
    theme_minimal(base_size = 12)
  print(p)

  message("[TTE] 敏感性分析完成: ", nrow(results), " 个场景")
  return(results)
}


# ==============================================================================
# 6. 端到端演示
# ==============================================================================

#' TTE 完整工作流演示
#'
#' 使用模拟数据展示目标试验模拟的完整流程。
#'
#' @return list, 含各步骤结果
#' @examples
#' demo <- full_tte_workflow()
full_tte_workflow <- function() {

  set.seed(42)
  n <- 800
  demo_data <- data.frame(
    id       = 1:n,
    age      = rnorm(n, 60, 10),
    sex      = sample(c("M", "F"), n, replace = TRUE),
    bmi      = rnorm(n, 27, 4),
    diabetes = sample(0:1, n, replace = TRUE, prob = c(0.6, 0.4)),
    treatment = sample(c("DrugA", "DrugB"), n, replace = TRUE, prob = c(0.5, 0.5))
  )

  # 模拟生存时间 (治疗有微弱效应)
  lambda <- exp(-5 + 0.01 * demo_data$age - 0.1 * (demo_data$treatment == "DrugA"))
  demo_data$time   <- rexp(n, lambda)
  demo_data$event  <- rbinom(n, 1, 0.3)
  demo_data$cv_event <- demo_data$event

  message("=" %>% rep(60) %>% paste(collapse = ""))
  message("TTE 完整工作流演示")
  message("=" %>% rep(60) %>% paste(collapse = ""))

  # Step 1: 定义试验方案
  protocol <- tte_specify_trial(
    eligibility          = list(age_min = 40, age_max = 80),
    treatment_strategies = c("DrugA", "DrugB"),
    outcome              = "cv_event",
    time_to_event        = "time",
    follow_up_months     = 36,
    causal_contrast      = "ATE"
  )

  # Step 2: 克隆数据
  clones <- tte_clone_data(demo_data, protocol, "treatment", c("age", "sex", "bmi", "diabetes"))

  # Step 3: IPCW
  weighted <- tte_censor_weights(clones, c("age", "sex", "bmi"), "assigned_trt")

  # Step 4: 拟合模型
  model_res <- tte_fit_model(weighted, protocol, "assigned_trt",
                              c("age", "sex", "bmi"), model_type = "cox")

  # Step 5: 敏感性分析
  sens <- tte_sensitivity(
    clones, protocol, "assigned_trt",
    confounder_sets    = list(c("age"), c("age", "sex"), c("age", "sex", "bmi", "diabetes")),
    truncation_levels  = c(0.95, 0.99, 1.0)
  )

  return(list(
    protocol    = protocol,
    clones      = clones,
    weighted    = weighted,
    model       = model_res,
    sensitivity = sens
  ))
}

# 运行演示:
# demo <- full_tte_workflow()
