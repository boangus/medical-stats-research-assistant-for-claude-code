# MSRA 综合测试数据集

## 概况

| 属性 | 值 |
|------|-----|
| 文件 | `tests/msra_test_data.csv` |
| 行数 | 600 |
| 变量 | 24 |
| 编码 | UTF-8 |
| 生成 | `tests/generate_test_data.py` |

## 变量清单

| # | 变量 | 类型 | 描述 | 注 |
|---|------|------|------|----|
| 1 | PatientID | 字符 | 受试者编号 | 含 2 个重复 ID |
| 2 | Name | 字符 | 姓名 | 大小写不一致 |
| 3 | Age | 数值/空 | 年龄 | 含负值(-5)、超高(250)、6行缺失 |
| 4 | Gender | 分类 | 性别 | 含逻辑错误（男+卵巢囊肿、女+前列腺癌） |
| 5 | BloodType | 分类 | 血型 | 含无效值(XX、不明) |
| 6 | TCM_Diagnosis | 字符 | 中医辨证分型 | 16种变体（心脾两虚/心脾两虚证/心脾两虚证型等）|
| 7 | MedicalCondition | 分类 | 西医诊断 | 含中英文混合、稀少类别 |
| 8 | AdmissionDate | 日期 | 入院日期 | 含逻辑错误（出院早于入院、未来日期）|
| 9 | DischargeDate | 日期 | 出院日期 | 同上 |
| 10 | PSA_Level | 数值/字符 | PSA水平 | 含截断标记(<0.1、<1.5、>100、小于0.5、大于50、<=4.0、>=10.0) |
| 11 | BillingAmount | 数值/字符/空 | 计费金额 | 含负值(-2008)、极端异常(999999)、逗号多值、缺失 |
| 12 | HeartRate | 数值/空 | 心率 | 含不可能值(0、350)、缺失、rows500-509零方差块 |
| 13 | Temperature | 数值/字符 | 体温 | 含超高(42.5)、中文数字(五、三十七)、零方差块 |
| 14 | LabResult_Multi | 数值/字符 | 检验结果 | 含逗号多值("1.2, 2.3, 3.1") |
| 15 | SmokingStatus | 分类 | 吸烟状态 | 含稀少类别(pipe)、术语变体(吸/不吸)、非标表述(每日1包) |
| 16 | FollowUpMonths | 数值/字符/空 | 随访月数 | 含范围表示(3-6, 6-12)、非标表述(约3个月)、缺失 |
| 17 | EducationLevel | 分类 | 教育程度 | 含稀少类别(文盲) |
| 18 | InsuranceProvider | 分类 | 保险 | 标准5种 |
| 19 | AdmissionType | 分类 | 入院类型 | 标准3种 |
| 20 | Medication | 分类 | 用药 | 中英文混合（桂枝茯苓丸、六味地黄丸、阿司匹林等）|
| 21 | TreatmentGroup | 分类 | 治疗组 | 极端不平衡(T:579, C:21, 27.6:1) |
| 22 | Outcome | 字符/空 | 结局 | 含缺失(MAR模式, 与EducationLevel=文盲相关) |
| 23 | AdverseEvent | 分类 | 不良事件 | 含Severe类别 |
| 24 | Notes | 字符 | 备注 | 含中文数字("疼痛评分五级")、空值、"不详" |

## 覆盖的 21 个数据质量"坑"

| # | 坑 | 来源 SKILL | 所在行/列 |
|---|------|-----------|----------|
| 1 | 负值金额 | data-prep | BillingAmount: SUBJ-0161,0162 |
| 2 | 异常年龄 | data-prep | Age: SUBJ-0031(-5), 0032(250) |
| 3 | 年龄缺失 | data-prep | Age: SUBJ-0033~0038 |
| 4 | TCM术语变体 | data-prep(值规范化) | TCM_Diagnosis: 16种变体 |
| 5 | 性别-诊断矛盾 | data-prep(逻辑一致性) | Gender+MedicalCondition: SUBJ-0071,0072 |
| 6 | 日期逻辑错误 | data-prep(逻辑一致性) | AdmissionDate/DischargeDate: SUBJ-0121~0123 |
| 7 | 数值截断标记 | data-prep(值规范化) | PSA_Level: 7种标记 |
| 8 | 逗号多值 | data-prep(值规范化) | BillingAmount: SUBJ-0164,0165 |
| 9 | 极端异常值 | data-prep | BillingAmount: SUBJ-0163(999999) |
| 10 | 不可能生理值 | data-prep | HeartRate: SUBJ-0181(0), 0182(350) |
| 11 | 缺失值块 | data-prep/analysis-exec | HeartRate: SUBJ-0183~0186 |
| 12 | 中文数字 | data-prep(值规范化) | Temperature(五), Notes(五级/第三日) |
| 13 | 中英文药名混用 | data-prep | Medication: 阿司匹林/桂枝茯苓丸等 |
| 14 | 无效分类值 | data-prep | BloodType: XX, 不明 |
| 15 | 零方差变量 | report | HeartRate/Temperature: rows500-509 |
| 16 | 稀少类别 | data-prep/analysis-plan | SmokingStatus=pipe, Education=文盲 |
| 17 | 非标数值表示 | data-prep(值规范化) | FollowUpMonths: 3-6, 约3个月 |
| 18 | 组间极端不平衡 | analysis-exec(样本量验证) | TreatmentGroup: 579:21 |
| 19 | 重复记录 | data-prep | PatientID: SUBJ-0300,0450 |
| 20 | 缺失模式(MAR) | analysis-plan/exec | Outcome缺失集中在Education=文盲 |
| 21 | 严重不良事件 | analysis-exec | AdverseEvent: SUBJ-0581,0582(Severe) |

## 适用测试场景

| MSRA 阶段 | 可用数据坑 |
|-----------|----------|
| Stage 1 Data Prep | #1~#21 (全部) |
| Stage 1.5 质量门闸 | #1~#7 (门闸检查项) |
| Stage 2 Analysis Plan | #18(组不平衡)、#20(MAR) |
| Stage 3 Analysis Exec | #15(零方差)、#19(重复)、#20(缺失) |
| Stage 4 Report | #15(零方差表)、#16(稀少类别报告) |



