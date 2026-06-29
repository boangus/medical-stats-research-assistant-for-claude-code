# 网络 Meta 分析 (Network Meta-Analysis) 模板
# =============================================================
# 核心方法: 频率学 (netmeta), 贝叶斯 (gemtc), 一致性检验, 排名
# 适用场景: 多种干预措施的间接比较与综合排名
#
# 依赖:
#   install.packages(c("netmeta", "meta", "ggplot2", "dplyr"))
#   # 可选 (贝叶斯): install.packages(c("gemtc", "rjags")) 并安装 JAGS
#
# 作者: MSRA Team | 版本: 0.1.0

# --- 依赖安装与加载 ---
for (pkg in c("netmeta", "meta", "ggplot2", "dplyr")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}
library(netmeta); library(meta); library(ggplot2); library(dplyr)
gemtc_available <- requireNamespace("gemtc", quietly = TRUE)
if (gemtc_available) library(gemtc)


# ==============================================================================
# 1. 准备网络数据
# ==============================================================================

#' 准备网络 Meta 分析数据
#'
#' 将成对比较数据转换为 netmeta 所需的格式 (对比水平, pairwise 格式)。
#'
#' @param data 数据框, 需包含:
#'   - treat1: 干预 1 名称
#'   - treat2: 干预 2 名称
#'   - TE: 效应量 (如 log OR, log HR, MD)
#'   - seTE: 效应量标准误
#'   - studlab: 研究标签 (可选)
#' @param sm 字符, 效应量指标: "OR" (比值比), "HR" (风险比), "MD" (均数差), "SMD" (标准化均数差)
#' @return list: pw (pairwise 格式), treat_list (干预列表), n_studies, n_treats, n_comparisons
#' @examples
#' net_data <- nma_prepare_network(df, sm = "OR")
nma_prepare_network <- function(data, sm = c("OR", "HR", "MD", "SMD")) {

  sm <- match.arg(sm)

  # 确保必需列存在
  required_cols <- c("treat1", "treat2", "TE", "seTE")
  missing_cols <- setdiff(required_cols, names(data))
  if (length(missing_cols) > 0) {
    stop("[NMA] 缺失必需列: ", paste(missing_cols, collapse = ", "))
  }

  # 补充 study label
  if (!"studlab" %in% names(data)) {
    data$studlab <- paste0("Study_", seq_len(nrow(data)))
  }

  # 转换为 pairwise 格式
  pw <- pairwise(
    treat = list(treat1, treat2),
    TE    = TE,
    seTE  = seTE,
    studlab = studlab,
    data  = data,
    sm    = sm
  )

  treats <- sort(unique(c(data$treat1, data$treat2)))
  n_comparisons <- nrow(data)

  message("[NMA] 网络数据准备完成:")
  message("  干预措施: ", length(treats), " (", paste(treats, collapse = ", "), ")")
  message("  研究数: ", length(unique(data$studlab)), " | 比较数: ", n_comparisons)
  message("  效应量: ", sm)

  return(list(
    pw           = pw,
    treat_list   = treats,
    n_studies    = length(unique(data$studlab)),
    n_treats     = length(treats),
    n_comparisons = n_comparisons,
    sm           = sm
  ))
}


# ==============================================================================
# 2. 频率学 NMA (netmeta)
# ==============================================================================

#' 拟合频率学网络 Meta 分析 (一致性模型)
#'
#' @param net_data list, 由 nma_prepare_network() 生成
#' @param reference 字符, 参照组干预名称 (默认取第一个)
#' @param common logical, 是否拟合固定效应模型 (默认 TRUE)
#' @param random logical, 是否拟合随机效应模型 (默认 TRUE)
#' @return netmeta 对象
#' @examples
#' nma_fit <- nma_fit_freq(net_data, reference = "Placebo")
nma_fit_freq <- function(net_data, reference = NULL,
                         common = TRUE, random = TRUE) {

  pw <- net_data$pw
  if (is.null(reference)) reference <- net_data$treat_list[1]

  message("[NMA] 拟合频率学一致性模型 (参考: ", reference, ")...")

  nma <- netmeta(
    TE     = TE,
    seTE   = seTE,
    treat1 = treat1,
    treat2 = treat2,
    studlab = studlab,
    data   = pw,
    sm     = net_data$sm,
    reference = reference,
    common = common,
    random = random
  )

  message("[NMA] 模型拟合完成:")
  message("  全局一致性: Q = ", round(nma$Q, 2), " (df=", nma$df.Q, ")",
          " | p = ", formatC(nma$pval.Q, format = "e", digits = 2))

  return(nma)
}


# ==============================================================================
# 3. 贝叶斯 NMA (gemtc, 可选)
# ==============================================================================

#' 拟合贝叶斯网络 Meta 分析 (gemtc)
#'
#' @param data 数据框, 原始数据 (含 treat1, treat2, TE, seTE, studlab)
#' @param sm 字符, 效应量指标
#' @param reference 字符, 参照组
#' @param n_iter 整数, MCMC 迭代次数 (默认 50000)
#' @param n_burnin 整数, 预热次数 (默认 10000)
#' @param n_thin 整数, 稀释间隔 (默认 10)
#' @return list: model, results, summary (或 NULL 如 gemtc 不可用)
#' @examples
#' bayes_res <- nma_fit_bayes(data, sm = "OR", reference = "Placebo")
nma_fit_bayes <- function(data, sm = "OR", reference = NULL,
                          n_iter = 50000, n_burnin = 10000, n_thin = 10) {

  if (!gemtc_available) {
    message("[NMA] gemtc 不可用, 跳过贝叶斯分析。")
    message("  请安装: install.packages(c('gemtc', 'rjags')) + JAGS 软件")
    return(NULL)
  }

  if (is.null(reference)) reference <- unique(c(data$treat1, data$treat2))[1]

  message("[NMA] 拟合贝叶斯 NMA (参考: ", reference, ")...")

  # 构建 gemtc 网络
  mtc_data <- mtc.data.study(
    data.frame(
      study   = data$studlab,
      treatment = data$treat1,
      responder = round(exp(data$TE) * 100),  # 简化: 将效应转为近似事件数
      sampleSize = rep(100, nrow(data)),
      stringsAsFactors = FALSE
    )
  )

  # 使用对比水平数据
  contrasts <- data.frame(
    study = data$studlab,
    treatment = data$treat2,
    diff = data$TE,
    std.err = data$seTE,
    stringsAsFactors = FALSE
  )
  # 补充基线
  baselines <- data.frame(
    study = data$studlab,
    treatment = data$treat1,
    diff = NA_real_,
    std.err = NA_real_,
    stringsAsFactors = FALSE
  )
  combined <- rbind(baselines, contrasts)
  combined <- combined[order(combined$study, is.na(combined$diff)), ]

  network <- mtc.network(combined)

  model <- mtc.model(network, likelihood = "normal", link = "identity",
                     linearModel = "random")

  results <- mtc.run(model, n.adapt = n_burnin, n.iter = n_iter, thin = n_thin)

  # 提取排名
  ranks <- rank.probability(results, preferredDirection = -1)

  message("[NMA] 贝叶斯 NMA 完成")
  summary_res <- summary(results)
  print(summary_res)

  return(list(
    model    = model,
    results  = results,
    summary  = summary_res,
    ranks    = ranks,
    network  = network
  ))
}


# ==============================================================================
# 4. 一致性检验
# ==============================================================================

#' 全局和局部一致性检验
#'
#' @param nma netmeta 对象, 由 nma_fit_freq() 返回
#' @return list: global (全局 Q 统计量), local (设计-治疗交互), node_split (节点分裂, 如可用)
#' @examples
#' consist <- nma_consistency_test(nma_fit)
nma_consistency_test <- function(nma) {

  results <- list()

  # --- 全局一致性 (netmeta 内建) ---
  Q_total   <- nma$Q
  Q_het     <- nma$Q.heterogeneity
  Q_inc     <- nma$Q.inconsistency
  df_inc    <- nma$df.Q.inconsistency
  p_inc     <- nma$pval.Q.inconsistency

  results$global <- list(
    Q_inconsistency = Q_inc,
    df              = df_inc,
    p_value         = p_inc,
    Q_heterogeneity = Q_het
  )

  message("[NMA] 全局一致性检验:")
  message("  Q 不一致性 = ", round(Q_inc, 2), " (df=", df_inc, ")",
          " | p = ", formatC(p_inc, format = "e", digits = 2))
  message("  Q 异质性   = ", round(Q_het, 2))

  # --- 设计-治疗交互模型 (design-by-treatment interaction) ---
  tryCatch({
    dbt <- netsplit(nma)
    results$netsplit <- dbt

    message("[NMA] 设计-治疗交互 (netsplit):")
    if (!is.null(dbt$compare)) {
      # 显示直接 vs 间接比较不一致的部分
      inconsistent <- dbt$compare[dbt$compare$p.value < 0.05, ]
      if (nrow(inconsistent) > 0) {
        message("  发现 ", nrow(inconsistent), " 个不一致比较:")
        for (i in seq_len(min(5, nrow(inconsistent)))) {
          message("    ", inconsistent$comparison[i], " p = ",
                  formatC(inconsistent$p.value[i], format = "e", digits = 2))
        }
      } else {
        message("  未发现显著不一致 (所有 p > 0.05)")
      }
    }
  }, error = function(e) {
    message("[NMA] netsplit 失败: ", e$message)
    results$netsplit <- NULL
  })

  # --- 节点分裂检验 (node-splitting, 如 netsplit 提供) ---
  if (!is.null(results$netsplit)) {
    results$node_split <- results$netsplit
  }

  return(results)
}


# ==============================================================================
# 5. 治疗排名
# ==============================================================================

#' 计算 SUCRA、P-score 和排名概率矩阵
#'
#' @param nma netmeta 对象, 由 nma_fit_freq() 返回
#' @param higher_better logical, 高值是否表示更好 (默认 FALSE, 如 OR<1 有利)
#' @return list: pscore (P-score 数据框), sucra (SUCRA), rank_matrix (排名概率矩阵)
#' @examples
#' ranking <- nma_ranking(nma_fit, higher_better = FALSE)
nma_ranking <- function(nma, higher_better = FALSE) {

  results <- list()

  # --- P-score (netmeta 内建) ---
  ps <- netrank(nma, small.values = ifelse(higher_better, "good", "desirable"))
  pscore_df <- data.frame(
    treatment = names(ps$Pscore.fixed),
    pscore_fixed  = round(ps$Pscore.fixed, 3),
    pscore_random = round(ps$Pscore.random, 3),
    stringsAsFactors = FALSE
  )
  pscore_df <- pscore_df[order(-pscore_df$pscore_random), ]
  rownames(pscore_df) <- NULL
  results$pscore <- pscore_df

  message("[NMA] P-score 排名 (随机效应):")
  for (i in seq_len(nrow(pscore_df))) {
    message("  ", i, ". ", pscore_df$treatment[i],
            " (P-score = ", pscore_df$pscore_random[i], ")")
  }

  # --- SUCRA 近似 (基于 P-score) ---
  # SUCRA = (排名累积概率的平均 - 1/n) / (1 - 1/n)
  n_treats <- nma$n

  # 计算排名概率矩阵
  # 使用 pairwise 比较结果推导排名概率
  trt_effects <- nma$TE.random
  trt_se      <- nma$seTE.random

  treat_names <- nma$trts
  rank_mat <- matrix(NA, nrow = n_treats, ncol = n_treats,
                     dimnames = list(treat_names, paste0("Rank", 1:n_treats)))

  # 基于效应量的 Monte Carlo 排名概率
  set.seed(42)
  n_sim <- 10000
  # 从各治疗的效应分布中抽样
  # 获取相对于参考的效应量
  effects_matrix <- matrix(0, nrow = n_sim, ncol = n_treats,
                           dimnames = list(NULL, treat_names))
  ref_idx <- 1
  for (j in 2:n_treats) {
    effects_matrix[, j] <- rnorm(n_sim, trt_effects[ref_idx, j],
                                  trt_se[ref_idx, j])
  }

  # 排名
  if (higher_better) {
    rank_sim <- t(apply(-effects_matrix, 1, rank))
  } else {
    rank_sim <- t(apply(effects_matrix, 1, rank))
  }

  for (j in 1:n_treats) {
    for (r in 1:n_treats) {
      rank_mat[j, r] <- mean(rank_sim[, j] == r)
    }
  }
  results$rank_matrix <- round(rank_mat, 3)

  # SUCRA
  sucra_vals <- sapply(1:n_treats, function(j) {
    cum_probs <- cumsum(rank_mat[j, ])
    (mean(cum_probs[-n_treats]) - 1 / n_treats) / (1 - 1 / n_treats)
  })
  results$sucra <- data.frame(
    treatment = treat_names,
    sucra = round(sucra_vals, 3),
    stringsAsFactors = FALSE
  )
  results$sucra <- results$sucra[order(-results$sucra$sucra), ]

  message("[NMA] SUCRA 排名:")
  for (i in seq_len(nrow(results$sucra))) {
    message("  ", i, ". ", results$sucra$treatment[i],
            " (SUCRA = ", results$sucra$sucra[i], ")")
  }

  return(results)
}


# ==============================================================================
# 6. 森林图
# ==============================================================================

#' 绘制 NMA 森林图 (各干预 vs 参照)
#'
#' @param nma netmeta 对象
#' @param reference 字符, 参照组 (可选, 默认使用模型中的 reference)
#' @param common logical, 是否显示固定效应结果 (默认 TRUE)
#' @param random logical, 是否显示随机效应结果 (默认 TRUE)
#' @return ggplot 对象 (如可用), 或调用 netmeta 内建绘图
#' @examples
#' nma_forest_plot(nma_fit, reference = "Placebo")
nma_forest_plot <- function(nma, reference = NULL,
                            common = TRUE, random = TRUE) {

  if (is.null(reference)) reference <- nma$reference

  message("[NMA] 森林图: 各干预 vs ", reference)

  # 使用 netmeta 内建森林图
  forest(nma, reference = reference,
         common = common, random = random,
         fontsize = 10, spacing = 1.2,
         label.left = paste0("Favors ", reference),
         label.right = "Favors intervention",
         xlab = paste0("Network Meta-Analysis (", nma$sm, ")"))

  # 尝试 ggplot2 版本
  trt_names <- nma$trts[nma$trts != reference]
  if (length(trt_names) > 0) {
    te_vals   <- nma$TE.random[reference, trt_names]
    se_vals   <- nma$seTE.random[reference, trt_names]
    ci_low    <- te_vals - 1.96 * se_vals
    ci_high   <- te_vals + 1.96 * se_vals

    if (nma$sm %in% c("OR", "HR", "RR")) {
      te_vals <- exp(te_vals)
      ci_low  <- exp(ci_low)
      ci_high <- exp(ci_high)
    }

    df <- data.frame(
      treatment = trt_names,
      estimate  = te_vals,
      ci_low    = ci_low,
      ci_high   = ci_high,
      stringsAsFactors = FALSE
    )

    ref_line <- ifelse(nma$sm %in% c("OR", "HR", "RR"), 1, 0)

    p <- ggplot(df, aes(x = .data$estimate, y = reorder(.data$treatment, -.data$estimate))) +
      geom_point(size = 4, color = "#2166AC") +
      geom_errorbarh(aes(xmin = .data$ci_low, xmax = .data$ci_high),
                     height = 0.2, color = "#2166AC") +
      geom_vline(xintercept = ref_line, linetype = "dashed", color = "red") +
      labs(title = paste0("NMA: 各干预 vs ", reference),
           x = paste0(nma$sm, " (95% CrI)"), y = NULL) +
      theme_minimal(base_size = 12)
    print(p)
    return(p)
  }
  return(invisible(NULL))
}


# ==============================================================================
# 7. 网络几何图
# ==============================================================================

#' 绘制网络几何图
#'
#' @param nma netmeta 对象
#' @param title 字符, 图标题
#' @return 绘制网络图 (netgraph)
#' @examples
#' nma_network_plot(nma_fit)
nma_network_plot <- function(nma, title = "NMA 网络几何图") {

  message("[NMA] 绘制网络几何图...")

  # netmeta 内建网络图
  netgraph(nma,
           plastic    = FALSE,
           thickness  = "number.of.studies",
           col        = "darkblue",
           number.of.studies = TRUE,
           cex.points = 1.5,
           cex.labels = 1.2,
           main       = title)

  # 额外: 使用 igraph 绘制 (如可用)
  if (requireNamespace("igraph", quietly = TRUE)) {
    # 构建邻接矩阵
    n <- nma$n
    adj <- matrix(0, n, n, dimnames = list(nma$trts, nma$trts))
    for (i in seq_len(nrow(nma$pairwise))) {
      t1 <- nma$pairwise$treat1[i]
      t2 <- nma$pairwise$treat2[i]
      adj[t1, t2] <- adj[t1, t2] + 1
      adj[t2, t1] <- adj[t2, t1] + 1
    }

    g <- igraph::graph_from_adjacency_matrix(adj, mode = "undirected", weighted = TRUE)
    edge_colors <- grDevices::colorRampPalette(c("lightblue", "darkblue"))(max(adj))[igraph::E(g)$weight]
    igraph::plot.igraph(g,
         vertex.size = 25,
         vertex.color = "lightyellow",
         vertex.label.cex = 1.0,
         edge.width = igraph::E(g)$weight * 2,
         edge.color = edge_colors,
         main = paste(title, "(igraph)"))
  }
}


# ==============================================================================
# 8. 联盟表 (League Table)
# ==============================================================================

#' 生成联盟表: 所有成对比较的效应量矩阵
#'
#' @param nma netmeta 对象
#' @param random logical, 使用随机效应 (默认 TRUE)
#' @param digits 整数, 小数位数 (默认 3)
#' @return 矩阵, 行列均为干预措施, 单元格为效应量 (95% CI)
#' @examples
#' league <- nma_comparison_table(nma_fit)
nma_comparison_table <- function(nma, random = TRUE, digits = 3) {

  te_mat <- if (random) nma$TE.random else nma$TE.common
  se_mat <- if (random) nma$seTE.random else nma$seTE.common

  trts <- nma$trts
  n <- nma$n

  # 构建可读联盟表
  league <- matrix("", nrow = n, ncol = n, dimnames = list(trts, trts))

  for (i in 1:n) {
    for (j in 1:n) {
      if (i == j) {
        league[i, j] <- "---"
      } else if (i < j) {
        # 上三角: 列 vs 行 (row 有利)
        te <- te_mat[i, j]
        se <- se_mat[i, j]
        ci_l <- te - 1.96 * se
        ci_u <- te + 1.96 * se
        if (nma$sm %in% c("OR", "HR", "RR")) {
          league[i, j] <- paste0(round(exp(te), digits), " [",
                                  round(exp(ci_l), digits), ", ",
                                  round(exp(ci_u), digits), "]")
        } else {
          league[i, j] <- paste0(round(te, digits), " [",
                                  round(ci_l, digits), ", ",
                                  round(ci_u, digits), "]")
        }
      } else {
        # 下三角: 对称标记
        league[i, j] <- league[j, i]
      }
    }
  }

  message("[NMA] 联盟表 (", n, "x", n, "):")
  print(league, quote = FALSE)

  return(league)
}


# ==============================================================================
# 9. 端到端演示
# ==============================================================================

#' NMA 完整工作流演示
#'
#' 使用模拟数据展示网络 Meta 分析的完整流程。
#'
#' @return list, 含各步骤结果
#' @examples
#' demo <- full_nma_workflow()
full_nma_workflow <- function() {

  set.seed(2024)
  message("=" %>% rep(60) %>% paste(collapse = ""))
  message("网络 Meta 分析 (NMA) 完整工作流演示")
  message("=" %>% rep(60) %>% paste(collapse = ""))

  # --- 模拟 NMA 数据: 5 种干预, 12 个 RCT ---
  treats <- c("Placebo", "DrugA", "DrugB", "DrugC", "DrugD")
  # 真实效应 (log OR, 相对于 Placebo)
  true_effects <- c(0, -0.3, -0.5, -0.2, -0.4)
  names(true_effects) <- treats

  studies <- data.frame(
    studlab = paste0("Study_", 1:12),
    treat1  = c("Placebo","Placebo","Placebo","DrugA","Placebo",
                "DrugB","Placebo","DrugA","DrugC","Placebo","DrugB","DrugD"),
    treat2  = c("DrugA","DrugB","DrugC","DrugB","DrugD",
                "DrugC","DrugA","DrugC","DrugD","DrugA","DrugD","DrugA"),
    stringsAsFactors = FALSE
  )

  studies$TE <- true_effects[studies$treat2] - true_effects[studies$treat1] +
    rnorm(nrow(studies), 0, 0.15)
  studies$seTE <- abs(rnorm(nrow(studies), 0.12, 0.03))

  message("\n模拟数据:")
  print(studies)

  # Step 1: 准备网络
  net_data <- nma_prepare_network(studies, sm = "OR")

  # Step 2: 频率学 NMA
  nma_fit <- nma_fit_freq(net_data, reference = "Placebo")

  # Step 3: 一致性检验
  consist <- nma_consistency_test(nma_fit)

  # Step 4: 排名
  ranking <- nma_ranking(nma_fit, higher_better = FALSE)

  # Step 5: 网络图
  nma_network_plot(nma_fit)

  # Step 6: 森林图
  nma_forest_plot(nma_fit, reference = "Placebo")

  # Step 7: 联盟表
  league <- nma_comparison_table(nma_fit)

  # Step 8: 贝叶斯 NMA (可选)
  bayes_res <- NULL
  if (gemtc_available) {
    bayes_res <- nma_fit_bayes(studies, sm = "OR", reference = "Placebo",
                                n_iter = 20000, n_burnin = 5000)
  }

  message("\n[NMA] 完整工作流结束")

  return(list(
    net_data    = net_data,
    nma_fit     = nma_fit,
    consistency = consist,
    ranking     = ranking,
    league      = league,
    bayes       = bayes_res
  ))
}

# 运行演示:
# demo <- full_nma_workflow()
