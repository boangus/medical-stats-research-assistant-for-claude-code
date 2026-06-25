# 校准报告模板

> 来源：从 `skills/calibration/SKILL.md` L463-513 抽取。保留原文完整性，语义等价。
> 本文件提供校准报告的标准 Markdown 模板和工具引用。

## 报告模板

```markdown
# MSRA 度量校准报告
- 日期: YYYY-MM-DD | 金标准条目: N | 累计条目: M

## 混淆矩阵
|  | Gold: Sig | Gold: Non-Sig |
|--|-----------|---------------|
| MSRA: Sig | TP=XX | FP=XX |
| MSRA: Non-Sig | FN=XX | TN=XX |

## 关键指标
| 指标 | 值 | 门闸 |
|------|-----|------|
| TPR (灵敏度) | XX.X% | ✅/⚠️/❌ |
| TNR (特异度) | XX.X% | ✅/⚠️/❌ |
| FPR (假阳性率) | X.X% | ✅/⚠️/❌ |
| FNR (假阴性率) | X.X% | ✅/⚠️/❌ |
| F1 | X.XX | ✅/⚠️/❌ |
| 准确率 | XX.X% | ✅/⚠️/❌ |

## 方法匹配率
- 一致: XX/N = XX.X% | 最常见错误: XXX → XXX

## 数值偏差
| 指标 | 值 | 门闸 |
|------|-----|------|
| MAE | X.XXXX | ✅/⚠️/❌ |
| RMSE | X.XXXX | ✅/⚠️/❌ |
| MAPE | XX.X% | ✅/⚠️/❌ |
| Pearson r | X.XXXX | ✅/⚠️/❌ |

## 改进建议
- [具体短板领域及建议]
```

## 工具引用

- 校准引擎 (Python): [calibration_runner.py](calibration_runner.py)
- 校准引擎 (R): [calibration_runner.R](calibration_runner.R)
- 金标准示例: [gold_standard_example.csv](gold_standard_example.csv)
- 框架文档: [calibration_framework.md](calibration_framework.md)
- 反模式目录: [../anti-patterns/medical_stats_anti_patterns.md](../anti-patterns/medical_stats_anti_patterns.md)
- 方法验证目录: [../statistics-methods/methods_catalog.md](../statistics-methods/methods_catalog.md) — 统计方法选择验证与映射
- 审计追踪工具: [../reproducibility/pipeline_auditor.py](../reproducibility/pipeline_auditor.py) — 校准全流程审计日志

## 附录：校准指标公式

> 来源：从 `skills/calibration/SKILL.md` L138-150 移入（主文件快速开始瘦身时迁出）。

| 指标 | 公式 | 用途 | 阈值 |
|------|------|------|------|
| Brier Score | BS = (1/N)Σ(p_i - o_i)² | 预测准确性 | <0.25为良好 |
| ECE (期望校准误差) | ECE = Σ(|B_m|/N)×|acc(B_m)-conf(B_m)| | 校准误差 | <0.05为良好 |
| HL统计量 | H = Σ(O_k-E_k)²/E_k | 拟合优度（10分组） | P>0.05为良好 |
| 方法匹配率 | MMR = 正确方法数/总分析数 | 方法选择准确性 | >0.90为良好 |
| 数值偏差 | Δ = |MSRA值-金标准值|/金标准值 | 数值准确性 | <0.05为良好 |
| FPR | FPR = FP/(FP+TN) | 假阳性率 | <0.05为良好 |
| FNR | FNR = FN/(FN+TP) | 假阴性率 | <0.10为良好 |
| MSF (模型分离度) | MSF = max(|AUC_s1-AUC_s2|) | 公平性-性能差异 | <0.05为公平 |
| ESF (误差分离度) | ESF = max(|FPR_s1-FPR_s2|) | 公平性-误差差异 | <0.10为公平 |
