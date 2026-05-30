# 02_var_define.R
# 变量定义脚本 - 统一定义变量标签、分组、协变量
# 输入: load/01_extracted.rda
# 输出: load/02_var_defined.rda

rm(list = ls())

# 1. 加载配置 -------------------------------------------------------
load("load/00_config.rda")
load("load/01_extracted.rda")

cat("[02_var_define] 开始变量定义\n")

# 2. 变量标签定义 ---------------------------------------------------
# 用于表格展示的规范化标签
var_labels <- list(
  # 人口学特征
  Age = "Age (years)",
  Age_group = "Age group",
  Sex = "Sex",
  BMI = "Body-mass index (kg/m²)",
  BMI_group = "BMI group",
  
  # 临床特征
  SBP = "Systolic blood pressure (mmHg)",
  DBP = "Diastolic blood pressure (mmHg)",
  Hypertension = "Hypertension",
  Diabetes = "Diabetes mellitus",
  CVD = "Cardiovascular disease",
  Smoking = "Smoking history",
  
  # 疾病特征
  Disease_stage = "Disease stage",
  Tumor_grade = "Tumor grade",
  Biomarker = "Biomarker level",
  
  # 治疗相关
  Treatment = "Treatment group",
  Treatment_duration = "Treatment duration (months)",
  
  # 结局变量
  Event = "Event occurrence",
  Time_to_event = "Time to event (months)",
  Death = "Death",
  Survival_time = "Overall survival (months)"
)

# 3. 分类变量值标签定义 ---------------------------------------------
# 定义分类变量的编码对应标签
value_list <- list(
  # 二分类变量 (0/1 编码)
  Sex = list("0" = "Female", "1" = "Male"),
  Hypertension = list("0" = "No", "1" = "Yes"),
  Diabetes = list("0" = "No", "1" = "Yes"),
  CVD = list("0" = "No", "1" = "Yes"),
  Smoking = list("0" = "No", "1" = "Yes"),
  Event = list("0" = "No event", "1" = "Event occurred"),
  Death = list("0" = "Alive", "1" = "Dead"),
  
  # 多分类变量
  Age_group = list(
    "1" = "< 50 years",
    "2" = "50-64 years", 
    "3" = "≥ 65 years"
  ),
  
  Disease_stage = list(
    "I" = "Stage I",
    "II" = "Stage II",
    "III" = "Stage III",
    "IV" = "Stage IV"
  ),
  
  Treatment = list(
    "A" = "Treatment A",
    "B" = "Treatment B",
    "C" = "Treatment C"
  )
)

# 4. 分析用变量列表定义 ---------------------------------------------

# 协变量列表（用于多变量调整）
covariates <- c(
  "Age", "Sex", "BMI",
  "Hypertension", "Diabetes", "CVD", "Smoking",
  "Disease_stage"
)

# 亚组分析变量列表
subgroup_vars <- c(
  "Age_group",
  "Sex", 
  "Disease_stage"
)

# 基线表展示变量
tbl_vars <- c(
  "Age", "Age_group", "Sex", "BMI", "BMI_group",
  "Hypertension", "Diabetes", "CVD", "Smoking",
  "Disease_stage", "Treatment"
)

# 连续变量列表
continuous_vars <- c(
  "Age", "BMI", "SBP", "DBP",
  "Treatment_duration", "Time_to_event", "Survival_time"
)

# 分类变量列表
categorical_vars <- c(
  "Sex", "Age_group", "BMI_group",
  "Hypertension", "Diabetes", "CVD", "Smoking",
  "Disease_stage", "Treatment", "Event", "Death"
)

# 结局变量定义
outcome_vars <- list(
  time = "Time_to_event",      # 时间变量
  event = "Event",              # 事件变量
  death_time = "Survival_time", # 死亡时间
  death_event = "Death"         # 死亡事件
)

# 暴露/处理变量
treatment_var <- "Treatment"

# 5. 保存变量定义 ---------------------------------------------------
save(
  var_labels, value_list, 
  covariates, subgroup_vars, tbl_vars,
  continuous_vars, categorical_vars,
  outcome_vars, treatment_var,
  file = file.path(load_dir, "02_var_defined.rda")
)

cat("[02_var_define] 变量定义完成，已保存到 load/02_var_defined.rda\n")
cat("[02_var_define] 定义了", length(var_labels), "个变量标签\n")
cat("[02_var_define] 协变量:", length(covariates), "个\n")
cat("[02_var_define] 亚组变量:", length(subgroup_vars), "个\n")
