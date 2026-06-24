# MSRA 综合测试数据集生成器
# 覆盖所有 SKILL 中提及的数据质量"坑"
# 输出: tests/msra_test_data.csv

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

N = 600
OUT = "tests/msra_test_data.csv"

FEMALE_NAMES = ["li xia","wang fang","zhang li","chen yu","lin mei",
                "Liu Na","Huang Jing","Zhou Yu","Wu Fang","Xu Lan"]
MALE_NAMES = ["wang wei","li ming","zhang qiang","liu bo","chen gang",
              "Yang Lei","Zhao Peng","Sun Hao","Ma Long","Zhu Feng"]

TCM_VARIANTS = [
    "心脾两虚","心脾两虚证","心脾两虚证型",
    "肝郁气滞","肝郁气滞证","肝气郁结",
    "肾阳虚","肾阳虚证","肾阳不足",
    "痰湿阻络","痰湿内阻","痰湿阻滞证",
    "气血两虚","气血两虚证","气血不足",
    "湿热下注",
]

BLOOD_TYPES = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
CONDITIONS = ["Cancer","Diabetes","Hypertension","Arthritis","Asthma","Obesity",
              "冠心病","糖尿病","高血压病"]
INSURANCE = ["Medicare","Blue Cross","Aetna","Cigna","UnitedHealthcare"]
ADMISSION = ["Emergency","Elective","Urgent"]
MEDS = ["Aspirin","Ibuprofen","Paracetamol","Lipitor","Penicillin",
         "桂枝茯苓丸","六味地黄丸","补中益气汤"]
GENDERS = ["Male","Female"]
EDUCATION = ["小学","初中","高中/中专","大学/大专","研究生及以上","文盲"]
SMOKING = ["从不","已戒烟","当前吸烟","偶尔","pipe"]
AE_TYPES = ["No","Yes","Severe"]

BASE = datetime(2020,1,1)
END = datetime(2024,12,31)
SPAN = (END - BASE).days

def rand_date():
    return BASE + timedelta(days=random.randint(0, SPAN))

def rand_name():
    raw = random.choice(FEMALE_NAMES + MALE_NAMES)
    return "".join(c.upper() if random.random() < 0.3 else c.lower() for c in raw)

rows = []
seen_ids = set()

for i in range(N):
    row = {}
    # PatientID - 少量重复
    if i == 299:  pid = rows[200]["PatientID"]
    elif i == 449: pid = rows[350]["PatientID"]
    else: pid = "SUBJ-{:04d}".format(i+1)
    row["PatientID"] = pid

    # Name - 大小写不一致
    if i < 10:
        raw = random.choice(FEMALE_NAMES + MALE_NAMES)
        row["Name"] = raw.upper() if i % 2 == 0 else raw.lower()
    else:
        row["Name"] = rand_name()

    # Age - 负值/极高/缺失
    if i == 30: row["Age"] = -5
    elif i == 31: row["Age"] = 250
    elif i in range(32,38): row["Age"] = ""
    else: row["Age"] = random.randint(18,90)

    # Gender - 含逻辑错误
    if i == 70: row["Gender"] = "Male"      # 但接卵巢囊肿
    elif i == 71: row["Gender"] = "Female"  # 但接前列腺癌
    else: row["Gender"] = random.choice(GENDERS)

    # BloodType - 含无效值
    if i == 50: row["BloodType"] = "XX"
    elif i == 51: row["BloodType"] = "不明"
    else: row["BloodType"] = random.choice(BLOOD_TYPES)

    # TCM_Diagnosis - 术语变体
    if i < 30:
        row["TCM_Diagnosis"] = TCM_VARIANTS[i // 5]
    elif i == 90: row["TCM_Diagnosis"] = "心脾两虚"
    elif i == 91: row["TCM_Diagnosis"] = "心脾两虚证"
    elif i == 92: row["TCM_Diagnosis"] = "心脾两虚证型"
    elif i < 100: row["TCM_Diagnosis"] = random.choice(TCM_VARIANTS)
    else: row["TCM_Diagnosis"] = ""

    # MedicalCondition - 逻辑矛盾 + 稀少
    if i == 70: row["MedicalCondition"] = "卵巢囊肿"    # Male
    elif i == 71: row["MedicalCondition"] = "前列腺癌"   # Female
    elif i == 110: row["MedicalCondition"] = "rare_disease_999"
    else: row["MedicalCondition"] = random.choice(CONDITIONS)

    # Admission/Discharge - 日期逻辑错误
    ad = rand_date()
    dd = ad + timedelta(days=random.randint(1,30))
    if i == 120: ad, dd = dd, ad                  # 出院早于入院
    elif i == 121: dd = ad - timedelta(days=5)     # 同上
    elif i == 122: ad = datetime(2026,6,15)        # 未来日期
    row["AdmissionDate"] = ad.strftime("%Y-%m-%d")
    row["DischargeDate"] = dd.strftime("%Y-%m-%d")

    # PSA_Level - 数值截断标记
    if i == 140: row["PSA_Level"] = "<0.1"
    elif i == 141: row["PSA_Level"] = "<1.5"
    elif i == 142: row["PSA_Level"] = ">100.0"
    elif i == 143: row["PSA_Level"] = "小于0.5"
    elif i == 144: row["PSA_Level"] = "大于50"
    elif i == 145: row["PSA_Level"] = "<=4.0"
    elif i == 146: row["PSA_Level"] = ">=10.0"
    else: row["PSA_Level"] = round(random.uniform(0.1,50.0),2)

    # BillingAmount - 负值/极端异常/逗号多值/缺失
    if i == 160: row["BillingAmount"] = -2008
    elif i == 161: row["BillingAmount"] = -0.01
    elif i == 162: row["BillingAmount"] = 999999.99
    elif i == 163: row["BillingAmount"] = "1,2,3"
    elif i == 164: row["BillingAmount"] = "500,600"
    elif i == 165: row["BillingAmount"] = ""
    else: row["BillingAmount"] = round(random.uniform(100,50000),2)

    # HeartRate - 不可能值/极端异常/缺失/零方差
    if i == 180: row["HeartRate"] = 0
    elif i == 181: row["HeartRate"] = 350
    elif i in range(182,186): row["HeartRate"] = ""
    elif i in range(500,510): row["HeartRate"] = 72
    else: row["HeartRate"] = random.randint(50,110)

    # Temperature - 超高/中文数字/零方差
    if i == 200: row["Temperature"] = 42.5
    elif i == 201: row["Temperature"] = 34.0
    elif i == 202: row["Temperature"] = "五"
    elif i == 203: row["Temperature"] = "三十七"
    elif i in range(500,510): row["Temperature"] = 36.5
    else: row["Temperature"] = round(random.uniform(35.5,38.0),1)

    # LabResult_Multi - 逗号多值
    if i == 220: row["LabResult_Multi"] = "1.2, 2.3, 3.1"
    elif i == 221: row["LabResult_Multi"] = "5,10,15,20"
    elif i == 222: row["LabResult_Multi"] = "0.5, 1.0"
    else: row["LabResult_Multi"] = round(random.uniform(0.5,10.0),1)

    # SmokingStatus - 稀少/术语变体
    if i in range(240,245): row["SmokingStatus"] = "pipe"
    elif i == 245: row["SmokingStatus"] = "吸"
    elif i == 246: row["SmokingStatus"] = "不吸"
    elif i == 247: row["SmokingStatus"] = "每日1包"
    else: row["SmokingStatus"] = random.choice(SMOKING)

    # FollowUpMonths - 范围表示/缺失/非标
    if i == 260: row["FollowUpMonths"] = "3-6"
    elif i == 261: row["FollowUpMonths"] = "6-12"
    elif i in range(262,269): row["FollowUpMonths"] = ""
    elif i == 269: row["FollowUpMonths"] = "约3个月"
    else: row["FollowUpMonths"] = random.randint(1,48)

    # EducationLevel - 稀少类别
    if i in range(280,284): row["EducationLevel"] = "文盲"
    else: row["EducationLevel"] = random.choice(EDUCATION)

    # Insurance / AdmissionType
    row["InsuranceProvider"] = random.choice(INSURANCE)
    row["AdmissionType"] = random.choice(ADMISSION)

    # Medication - 中西药混合
    if i == 400: row["Medication"] = "阿司匹林"
    elif i == 401: row["Medication"] = "布洛芬"
    else: row["Medication"] = random.choice(MEDS)

    # TreatmentGroup - 极端不平衡
    if i < 540: row["TreatmentGroup"] = "Treatment"
    elif i < 560: row["TreatmentGroup"] = "Control"
    else: row["TreatmentGroup"] = random.choices(["Treatment","Control"],[90,10])[0]

    # Outcome - 主结局含缺失 (MAR 模式)
    # 先随机生成 Outcome（非空为主）
    row["Outcome"] = random.choice(["改善","稳定","进展"])

    # AdverseEvent - 严重不良事件
    if i in (580,581): row["AdverseEvent"] = "Severe"
    else: row["AdverseEvent"] = random.choice(AE_TYPES)

    # Notes - 中文数字
    if i == 420: row["Notes"] = "患者自述疼痛评分五级"
    elif i == 421: row["Notes"] = "术后第三日出现发热"
    elif i == 422: row["Notes"] = "血压一百四/九十"
    elif i == 423: row["Notes"] = ""
    elif i == 424: row["Notes"] = "不详"
    else: row["Notes"] = ""

    rows.append(row)

# MAR: Outcome 缺失集中在 Education=文盲 子集
# 策略：将大量文盲行的 Outcome 设为空，非文盲行几乎不缺失
# 1. 先把 rows 300-349 设为 Education=文盲
for i in range(300, 350):
    rows[i]["EducationLevel"] = "文盲"
    rows[i]["Outcome"] = ""  # 文盲行全部缺失

# 2. 非文盲行只保留极少量缺失（<3%）
for i in range(0, 300):
    if random.random() < 0.02:  # 2% 概率随机缺失
        rows[i]["Outcome"] = ""
    else:
        rows[i]["Outcome"] = random.choice(["改善","稳定","进展"])

# 重复行
for i in range(450,455):
    src = rows[i-50]  # 复制 400-404
    rows[i] = dict(src)
    rows[i]["PatientID"] = "SUBJ-{:04d}".format(i+1)

# 写入 CSV
columns = [
    "PatientID","Name","Age","Gender","BloodType",
    "TCM_Diagnosis","MedicalCondition",
    "AdmissionDate","DischargeDate",
    "PSA_Level","BillingAmount",
    "HeartRate","Temperature","LabResult_Multi",
    "SmokingStatus","FollowUpMonths",
    "EducationLevel","InsuranceProvider",
    "AdmissionType","Medication",
    "TreatmentGroup","Outcome","AdverseEvent","Notes",
]
with open(OUT,"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f,fieldnames=columns)
    w.writeheader()
    w.writerows(rows)

print("OK: {} rows -> {}".format(len(rows), OUT))

# 验证报告
print("\n=== Pitfall Checklist ===\n")
ok_list = []

neg = [r["PatientID"] for r in rows if isinstance(r["BillingAmount"],(int,float)) and r["BillingAmount"] < 0]
print("[1] Negative billing: {} rows".format(len(neg)))
ok_list.append(len(neg) > 0)

age_bad = [r["PatientID"] for r in rows if isinstance(r["Age"],(int,float)) and (r["Age"] < 0 or r["Age"] > 120)]
print("[2] Impossible age: {} rows -> {}".format(len(age_bad), age_bad))
ok_list.append(len(age_bad) > 0)

age_miss = [r["PatientID"] for r in rows if r["Age"] == ""]
print("[3] Missing age: {} rows".format(len(age_miss)))
ok_list.append(len(age_miss) > 0)

tcm_vals = sorted(set(r["TCM_Diagnosis"] for r in rows if r["TCM_Diagnosis"]))
print("[4] TCM variants: {} types -> {}".format(len(tcm_vals), tcm_vals[:6]))
ok_list.append(len(tcm_vals) > 10)

logic = [r["PatientID"] for r in rows if (r["Gender"]=="Male" and r["MedicalCondition"]=="卵巢囊肿") or (r["Gender"]=="Female" and r["MedicalCondition"]=="前列腺癌")]
print("[5] Gender-diagnosis contradiction: {} rows".format(len(logic)))
ok_list.append(len(logic) > 0)

date_bad = sum(1 for r in rows if r["AdmissionDate"] > r["DischargeDate"])
print("[6] Discharge before admission: {} rows".format(date_bad))
ok_list.append(date_bad > 0)

trunc = sum(1 for r in rows if any(c in str(r["PSA_Level"]) for c in "<>小于大于等于"))
print("[7] PSA truncation markers: {} rows".format(trunc))
ok_list.append(trunc > 0)

multi = sum(1 for r in rows if isinstance(r["BillingAmount"],str) and "," in r["BillingAmount"])
print("[8] Comma-multivalue billing: {} rows".format(multi))
ok_list.append(multi > 0)

extreme = sum(1 for r in rows if isinstance(r["BillingAmount"],(int,float)) and r["BillingAmount"] > 1e5)
print("[9] Extreme billing outlier: {} rows".format(extreme))
ok_list.append(extreme > 0)

hr_dead = [r["PatientID"] for r in rows if isinstance(r["HeartRate"],(int,float)) and (r["HeartRate"] < 20 or r["HeartRate"] > 250)]
print("[10] Impossible heart rate: {} rows".format(len(hr_dead)))
ok_list.append(len(hr_dead) > 0)

hr_miss = sum(1 for r in rows if r["HeartRate"] == "")
print("[11] Missing heart rate: {} rows".format(hr_miss))
ok_list.append(hr_miss > 0)

cn_num = sum(1 for r in rows if isinstance(r["Temperature"],str) and any(c in r["Temperature"] for c in "一二三四五六七八九十"))
cn_num += sum(1 for r in rows if any(c in r.get("Notes","") for c in "一二三四五六七八九十"))
print("[12] Chinese numerals: {} rows".format(cn_num))
ok_list.append(cn_num > 0)

cn_meds = set(r["Medication"] for r in rows if any('\u4e00' <= c <= '\u9fff' for c in r["Medication"]))
print("[13] Chinese medication names: {}".format(cn_meds))
ok_list.append(len(cn_meds) > 0)

bt_bad = sum(1 for r in rows if r["BloodType"] not in BLOOD_TYPES)
print("[14] Invalid blood type: {} rows".format(bt_bad))
ok_list.append(bt_bad > 0)

hr_const = sum(1 for r in rows[500:510] if r["HeartRate"] == 72)
print("[15] Zero-variance heart rate (rows 500-509): {}/10".format(hr_const))
ok_list.append(hr_const >= 9)

rare_smk = sum(1 for r in rows if r["SmokingStatus"] == "pipe")
print("[16] Rare smoking=pipe: {} rows".format(rare_smk))
ok_list.append(rare_smk > 0)

rare_edu = sum(1 for r in rows if r["EducationLevel"] == "文盲")
print("[17] Rare education=文盲: {} rows".format(rare_edu))
ok_list.append(rare_edu > 0)

fup_range = [r["PatientID"] for r in rows if isinstance(r["FollowUpMonths"],str) and "-" in r["FollowUpMonths"]]
print("[18] Range notation in FollowUp: {} rows -> {}".format(len(fup_range), fup_range))
ok_list.append(len(fup_range) > 0)

tc = sum(1 for r in rows if r["TreatmentGroup"] == "Treatment")
cc = sum(1 for r in rows if r["TreatmentGroup"] == "Control")
print("[19] Group imbalance: T={} C={} ratio={:.1f}:1".format(tc, cc, tc/max(cc,1)))
ok_list.append(tc > cc * 5)

ids_seen = set(); dups = set()
for r in rows:
    if r["PatientID"] in ids_seen: dups.add(r["PatientID"])
    ids_seen.add(r["PatientID"])
print("[20] Duplicate PatientIDs: {} IDs".format(len(dups)))
ok_list.append(len(dups) > 0)

mar_outcome = sum(1 for r in rows if r["Outcome"] == "" and r["EducationLevel"] == "文盲")
non_mar = sum(1 for r in rows if r["Outcome"] == "" and r["EducationLevel"] != "文盲")
print("[21] MAR: Outcome missing & Edu=文盲: {} rows (non-文盲 missing: {})".format(mar_outcome, non_mar))
ok_list.append(mar_outcome > non_mar * 2)  # 文盲缺失应显著多于非文盲

print("\n>>> {} of 21 pitfalls covered <<<".format(sum(ok_list)))
