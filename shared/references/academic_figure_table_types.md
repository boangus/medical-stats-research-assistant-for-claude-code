# 学术图表类型完整清单

> 基于PubMed文献检索和医学统计研究标准实践整理
> 版本: 1.0
> 更新日期: 2026-06-22

---

## 一、数据可视化图表 (Data Visualization)

### 1.1 分布可视化

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 直方图 | Histogram | 展示连续变量分布 | 频数/频率、分组区间、正态曲线叠加 | X轴标签、Y轴标签、标题、样本量标注 | data_profile_template.py |
| 箱线图 | Box Plot | 展示数据分布和异常值 | 中位数、四分位数、异常值点 | 分组比较、添加原始数据点(jitter) | publication_figure_template.py |
| 小提琴图 | Violin Plot | 展示数据分布形态 | 核密度估计、中位数线、四分位数 | 结合箱线图使用、分组比较 | enhanced_chart_template.py |
| 密度图 | Density Plot | 展示连续变量概率密度 | 核密度曲线、分组叠加 | 透明度设置、分组颜色区分 | data_profile_template.py |

### 1.2 关系可视化

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 散点图 | Scatter Plot | 展示两个连续变量关系 | X/Y轴变量、回归线、置信区间 | 相关系数r和P值标注、样本量 | publication_figure_template.py |
| 气泡图 | Bubble Chart | 展示三个变量关系 | X/Y轴变量、气泡大小(第三变量) | 气泡大小图例、颜色分组 | publication_figure_template.py |
| 热图 | Heatmap | 展示矩阵数据模式 | 相关矩阵/表达矩阵、颜色标尺 | 聚类分析、数值标注、颜色标尺 | publication_figure_template.py |
| 等高线图 | Contour Plot | 展示三维数据表面 | X/Y/Z轴变量、等高线 | 颜色填充、数值标注 | enhanced_chart_template.py |

### 1.3 比较可视化

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 柱状图 | Bar Chart | 展示分类数据比较 | 分类变量、频数/比例、误差棒 | 误差棒(标准误/置信区间)、P值标注 | publication_figure_template.py |
| 堆叠柱状图 | Stacked Bar Chart | 展示分类数据组成 | 分类变量、各组分比例 | 百分比标注、颜色区分 | enhanced_chart_template.py |
| 分组柱状图 | Grouped Bar Chart | 展示多组比较 | 分组变量、分类变量、均值 | 误差棒、P值标注、图例 | publication_figure_template.py |

---

## 二、统计分析图表 (Statistical Analysis)

### 2.1 生存分析

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| Kaplan-Meier曲线 | KM Curve | 展示生存概率随时间变化 | 生存曲线、置信区间带、风险表 | 中位生存时间、Log-rank P值、风险表 | survival_ggsurvfit.R, cox_template.py |
| 竞争风险曲线 | Cumulative Incidence Curve | 展示竞争风险下事件累积发生率 | 累积发生率曲线、置信区间 | Gray检验P值、风险表 | competing_risks_template.R |
| 生存森林图 | Survival Forest Plot | 展示亚组生存分析结果 | HR、95%CI、亚组标签 | 交互作用P值、样本量 | forest_plot_template.py |

### 2.2 诊断试验

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| ROC曲线 | ROC Curve | 展示诊断试验性能 | ROC曲线、AUC值、置信区间 | AUC值、敏感度/特异度、最佳切点 | roc_template.py, roc_visualization_template.R |
| PR曲线 | Precision-Recall Curve | 展示不平衡数据诊断性能 | PR曲线、AUC值 | AUC值、样本量标注 | roc_template.py |
| 校准曲线 | Calibration Curve | 展示预测模型校准度 | 预测概率vs实际概率、对角线 | Hosmer-Lemeshow P值、样本量 | calibration_plot_template.R |
| 决策曲线 | Decision Curve | 展示临床决策收益 | 净收益曲线、阈值范围 | 治疗全员/无人线、样本量 | prediction_model_template.py |

### 2.3 回归分析

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 森林图 | Forest Plot | 展示回归系数/OR/HR及CI | 效应量、95%CI、变量标签 | 参考线(1或0)、异质性检验 | forest_plot_template.py |
| 残差图 | Residual Plot | 展示回归模型拟合质量 | 残差vs拟合值、参考线 | 正态性检验、异常值标注 | logistic_template.py |
| QQ图 | Q-Q Plot | 展示数据正态性 | 理论分位数vs样本分位数 | 参考线、Shapiro-Wilk P值 | data_profile_template.py |
| 影响力图 | Influence Plot | 展示回归影响点 | Cook's D、杠杆值、残差 | 影响力阈值线、异常值标注 | logistic_template.py |

### 2.4 Meta分析

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 森林图 | Forest Plot | 展示Meta分析结果 | 效应量、95%CI、权重 | 异质性(I², τ², Q检验)、亚组 | forest_plot_template.py |
| 漏斗图 | Funnel Plot | 展示发表偏倚 | 效应量vs标准误 | 对称性检验(Egger/Begg) | forest_plot_template.py |
| Galbraith图 | Galbraith Plot | 展示异质性来源 | 标准化效应量vs精度 | 参考线、异常研究标注 | forest_plot_template.py |

---

## 三、因果推断图表 (Causal Inference)

### 3.1 倾向性评分

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 倾向性评分分布图(PS分布图) | PS Distribution | 展示倾向性评分分布 | 处理组/对照组PS分布 | 重叠区域、SMD标注 | propensity_score_template.R |
| Love Plot | Love Plot | 展示协变量平衡 | 标准化均值差、平衡阈值 | 阈值线(0.1/0.2)、前后对比 | ps_diagnostics_template.R |
| 权重分布图 | Weight Distribution | 展示IPTW权重分布 | 权重直方图、极端值标注 | 截断阈值、权重统计量 | propensity_score_template.R |

### 3.2 DAG图

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| DAG图 | Directed Acyclic Graph | 展示因果关系结构 | 节点(变量)、边(因果关系) | 混杂/中介/碰撞变量标注 | dag_variable_selection_template.R |
| 调整集DAG | Adjustment Set DAG | 展示变量调整策略 | DAG + 调整变量高亮 | 调整路径标注 | dag_variable_selection_template.R |

---

## 四、机器学习图表 (Machine Learning)

### 4.1 模型解释

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| SHAP Summary | SHAP Summary Plot | 展示特征重要性 | 特征SHAP值、特征重要性排序 | 颜色表示特征值、样本量 | shap_plot_template.py |
| SHAP Dependence | SHAP Dependence Plot | 展示特征与预测关系 | 特征值vs SHAP值 | 交互效应、样本量 | shap_plot_template.py |
| 特征重要性 | Feature Importance | 展示模型特征重要性 | 特征名称、重要性分数 | 排序、置信区间 | ml_analysis_template.py |
| 部分依赖图 | Partial Dependence Plot | 展展特征边际效应 | 特征值、预测概率 | 置信区间、样本分布 | ml_analysis_template.py |

### 4.2 模型评估

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 学习曲线 | Learning Curve | 展示模型学习过程 | 训练/验证样本量、性能分数 | 过拟合/欠拟合诊断 | ml_analysis_template.py |
| 混淆矩阵 | Confusion Matrix | 展示分类模型性能 | 预测vs实际分类 | 准确率、敏感度、特异度 | ml_analysis_template.py |
| ROC对比 | ROC Comparison | 展示多模型ROC比较 | 多条ROC曲线、AUC值 | DeLong检验P值 | roc_template.py |

---

## 五、流程图和示意图 (Flowcharts & Diagrams)

### 5.1 研究流程图

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| CONSORT流程图 | CONSORT Flow Diagram | 展示RCT受试者流程 | 筛选、随机化、随访、分析人数 | CONSORT标准格式、样本量 | publication_figure_template.py |
| STROBE流程图 | STROBE Flow Diagram | 展示观察性研究流程 | 纳入排除、最终分析人群 | STROBE标准格式 | publication_figure_template.py |
| PRISMA流程图 | PRISMA Flow Diagram | 展示系统综述检索流程 | 检索、筛选、纳入研究 | PRISMA标准格式 | publication_figure_template.py |

### 5.2 技术路线图

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 研究设计图 | Study Design Diagram | 展示研究设计方案 | 时间线、干预、测量点 | 清晰标注、颜色区分 | enhanced_chart_template.py |
| 技术路线图 | Technical Roadmap | 展示研究技术路线 | 步骤、决策点、输出 | 流程清晰、标注完整 | enhanced_chart_template.py |
| 分析流程图 | Analysis Flow Chart | 展示统计分析流程 | 分析步骤、决策树 | 方法名称、假设检验 | enhanced_chart_template.py |

---

## 六、专业图表 (Specialized Figures)

### 6.1 样本量计算

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 样本量曲线 | Sample Size Curve | 展示样本量与效能关系 | 样本量、检验效能 | 效应量标注、α水平 | sample_size_template.py |
| 效能曲线 | Power Curve | 展示检验效能与效应量关系 | 效应量、检验效能 | 样本量标注、α水平 | sample_size_template.py |

### 6.2 敏感性分析

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| Tipping Point图 | Tipping Point Plot | 展示缺失数据敏感性 | 缺失假设、效应量变化 | 阈值标注、结论稳健性 | multiple_imputation_template.R |
| E-value图 | E-value Plot | 展示未测量混杂敏感性 | E-value、效应量阈值 | 观察到的效应量、阈值线 | effect_size_template.py |
| 阴性对照图 | Negative Control Plot | 展示阴性对照结果 | 阴性对照效应量、置信区间 | 预期效应量、异常标注 | effect_size_template.py |

### 6.3 贝叶斯分析

| 图表类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 后验分布 | Posterior Distribution | 展示参数后验分布 | 后验密度、可信区间 | 先验叠加、MCMC诊断 | bayesian_analysis_template.py |
| 先验敏感性 | Prior Sensitivity Plot | 展示先验选择影响 | 多种先验下后验分布 | 敏感性分析结果 | bayesian_analysis_template.py |
| 轨迹图 | Trace Plot | 展示MCMC采样过程 | 迭代次数、参数值 | 收敛诊断、多链对比 | bayesian_analysis_template.py |

---

## 七、表格类型 (Table Types)

### 7.1 描述性统计

| 表格类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 基线特征表 | Table 1 | 展示研究人群基线特征 | 人口学、临床特征、分组比较 | 三线表、P值、SMD | baseline_table1_engine.py |
| 描述统计表 | Descriptive Table | 展示变量描述统计 | 均值/中位数、标准差/IQR | 分组展示、缺失率 | gtsummary_template.R |
| 频率表 | Frequency Table | 展示分类变量频率 | 频数、百分比 | 分组比较、P值 | janitor_tabyl_template.R |

### 7.2 推断统计

| 表格类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| 回归结果表 | Regression Table | 展示回归分析结果 | 效应量、95%CI、P值 | 多模型对比、调整变量 | gtsummary_template.R |
| 亚组分析表 | Subgroup Table | 展示亚组分析结果 | 亚组、效应量、交互作用P值 | 森林图对应、P-interaction | forest_plot_template.py |
| 敏感性分析表 | Sensitivity Table | 展示敏感性分析结果 | 分析方法、效应量、结论一致性 | 主分析对比、稳健性评估 | gtsummary_template.R |

### 7.3 安全性分析

| 表格类型 | 英文名称 | 用途 | 内容要求 | 呈现标准 | 模板文件 |
|---------|---------|------|---------|---------|---------|
| AE汇总表 | AE Summary Table | 展示不良事件汇总 | AE类型、发生率、严重程度 | 因果关系判断、分组比较 | gtsummary_template.R |
| SAE详情表 | SAE Detail Table | 展示严重不良事件详情 | 受试者、SAE类型、转归 | 时间线、因果关系 | gtsummary_template.R |
| 实验室异常表 | Lab Abnormality Table | 展示实验室检查异常 | 检查项目、异常类型、发生率 | 分级标准、分组比较 | gtsummary_template.R |

---

## 八、交付物清单汇总

### 8.1 表格交付物

| 序号 | 交付物名称 | 格式 | 文件名模板 | 说明 |
|-----|-----------|------|-----------|------|
| T1 | Table 1 基线特征表 | .docx三线表 | table1_baseline.docx | 按分组展示基线特征 |
| T2 | 主分析结果表 | .docx三线表 | table2_main_results.docx | 回归分析(OR/HR/β及95%CI) |
| T3 | 敏感性分析表 | .docx三线表 | table3_sensitivity.docx | 敏感性分析结果 |
| T4 | 亚组分析表 | .docx三线表 | table4_subgroup.docx | 亚组分析结果 |
| T5 | 不良事件汇总表 | .docx三线表 | table5_adverse_events.docx | AE/SAE汇总 |
| T6 | 实验室异常表 | .docx三线表 | table6_lab_abnormality.docx | 实验室检查异常 |
| T7 | 样本量计算表 | .docx三线表 | table7_sample_size.docx | 样本量计算依据 |
| T8 | 变量定义表 | .docx三线表 | table8_variable_definition.docx | 变量构造定义 |

### 8.2 图表交付物

| 序号 | 交付物名称 | 格式 | 文件名模板 | 说明 |
|-----|-----------|------|-----------|------|
| F1 | CONSORT流程图 | .svg/.pdf/.png | figure1_consort_flow.* | RCT受试者流程 |
| F2 | Kaplan-Meier曲线 | .svg/.pdf/.png | figure2_km_curve.* | 生存分析 |
| F3 | 森林图 | .svg/.pdf/.png | figure3_forest_plot.* | 亚组/回归分析 |
| F4 | ROC曲线 | .svg/.pdf/.png | figure4_roc_curve.* | 诊断试验 |
| F5 | 校准曲线 | .svg/.pdf/.png | figure5_calibration.* | 预测模型 |
| F6 | Bland-Altman图 | .svg/.pdf/.png | figure6_bland_altman.* | 一致性检验 |
| F7 | 相关性热图 | .svg/.pdf/.png | figure7_correlation_heatmap.* | 变量相关性 |
| F8 | DAG图 | .svg/.pdf/.png | figure8_dag.* | 因果关系 |
| F9 | Love Plot | .svg/.pdf/.png | figure9_love_plot.* | 协变量平衡 |
| F10 | SHAP图 | .svg/.pdf/.png | figure10_shap.* | 机器学习解释 |

### 8.3 报告交付物

| 序号 | 交付物名称 | 格式 | 文件名模板 | 说明 |
|-----|-----------|------|-----------|------|
| R1 | 统计报告 | .html/.md | final_report.* | 完整统计分析报告 |
| R2 | 方法学描述 | .md | methods_section.md | 统计方法学段落 |
| R3 | 结果解读 | .md | results_interpretation.md | 结果临床意义解读 |
| R4 | 局限性讨论 | .md | limitations.md | 研究局限性讨论 |

---

## 九、图表质量标准

### 9.1 通用标准

1. **分辨率**: PNG ≥ 300dpi，SVG矢量格式
2. **字体**: 坐标轴标签 ≥ 10pt，图例 ≥ 8pt
3. **颜色**: 语义化调色板或期刊配色
4. **标注**: 样本量、P值、效应量等关键信息完整
5. **格式**: SVG(首要) + PDF(投稿) + PNG(预览)

### 9.2 三线表标准

1. **边框**: 顶线粗(2pt) + 表头下线中(1pt) + 底线粗(2pt)
2. **对齐**: 第一列左对齐，其余居中
3. **字体**: 宋体(中文) + Times New Roman(英文)，10pt
4. **格式**: .docx格式，符合医学期刊要求

### 9.3 学术规范

1. **CONSORT**: RCT必须包含流程图
2. **STROBE**: 观察性研究必须包含流程图
3. **PRISMA**: 系统综述必须包含检索流程图
4. **ICMJE**: 图表格式符合国际医学期刊编辑委员会要求

---

## 十、模板文件索引

### 10.1 Python模板

| 模板文件 | 支持图表类型 |
|---------|-------------|
| publication_figure_template.py | 森林图、ROC曲线、KM曲线、散点图、热图、柱状图 |
| forest_plot_template.py | 森林图、Meta分析森林图 |
| roc_template.py | ROC曲线、PR曲线 |
| bland_altman_template.py | Bland-Altman图 |
| calibration_plot_template.R | 校准曲线 |
| shap_plot_template.py | SHAP图 |
| ml_analysis_template.py | 机器学习相关图表 |
| data_profile_template.py | 直方图、密度图、箱线图 |
| baseline_table1_engine.py | Table 1基线特征表 |

### 10.2 R模板

| 模板文件 | 支持图表类型 |
|---------|-------------|
| survival_ggsurvfit.R | Kaplan-Meier曲线 |
| forest_plot_template.R | 森林图 |
| roc_visualization_template.R | ROC曲线 |
| gtsummary_template.R | 统计表格 |
| dag_variable_selection_template.R | DAG图 |
| competing_risks_template.R | 竞争风险曲线 |
| calibration_plot_template.R | 校准曲线 |

---

## 参考文献

1. CONSORT 2010 Statement: updated guidelines for reporting parallel group randomised trials. BMJ 2010.
2. STROBE Statement: Strengthening the Reporting of Observational Studies in Epidemiology. Lancet 2007.
3. PRISMA 2020: An updated guideline for reporting systematic reviews. BMJ 2021.
4. ICMJE Recommendations for the Conduct, Reporting, Editing, and Publication of Scholarly Work in Medical Journals. 2023.
5. Lang, T. A. & Secic, M. (2006). How to Report Statistics in Medicine. American College of Physicians.
