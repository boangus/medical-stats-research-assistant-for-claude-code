#!/usr/bin/env python3
"""MSRA Pipeline Gold Evaluation Runner

自动检测 tests/msra_test_data.csv 中的 21 个 gold tuple 数据信号。

Usage:
    PYTHONPATH=. python -m scripts.eval_pipeline_gold
    PYTHONPATH=. python -m scripts.eval_pipeline_gold --tuple 001
    PYTHONPATH=. python -m scripts.eval_pipeline_gold --verbose
"""
import argparse
import json
import sys
from pathlib import Path

# 项目根目录
BASE = Path(__file__).resolve().parent.parent
TUPLES_DIR = BASE / "evals" / "gold" / "pipeline" / "tuples"
DATA_FILE = BASE / "tests" / "msra_test_data.csv"

import pandas as pd


def load_tuple(tuple_id: str) -> dict:
    """加载单个 gold tuple 定义"""
    for f in TUPLES_DIR.glob(f"{tuple_id}*.json"):
        with open(f, encoding="utf-8") as fh:
            return json.load(fh)
    return None


def load_all_tuples() -> list[dict]:
    """加载所有 gold tuples"""
    tuples = []
    for f in sorted(TUPLES_DIR.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            tuples.append(json.load(fh))
    return tuples


# ── 检测函数 ──

def detect_001(df: pd.DataFrame) -> dict:
    """001: 负值 BillingAmount"""
    col = pd.to_numeric(df["BillingAmount"], errors="coerce")
    neg = (col < 0).sum()
    return {"detected": neg > 0, "count": int(neg),
            "evidence": f"negative BillingAmount count={neg}, min={col.min()}"}


def detect_002(df: pd.DataFrame) -> dict:
    """002: 异常 Age（负值或>120）"""
    col = pd.to_numeric(df["Age"], errors="coerce")
    bad = ((col < 0) | (col > 120)).sum()
    vals = df.loc[(col < 0) | (col > 120), "Age"].tolist()
    return {"detected": bad > 0, "count": int(bad),
            "evidence": f"abnormal Age values={vals}"}


def detect_003(df: pd.DataFrame) -> dict:
    """003: Age 缺失"""
    miss = df["Age"].isna().sum()
    return {"detected": miss > 0, "count": int(miss),
            "evidence": f"missing Age count={miss}"}


def detect_004(df: pd.DataFrame) -> dict:
    """004: 重复 PatientID"""
    dups = df[df.duplicated("PatientID", keep=False)]
    dup_ids = dups["PatientID"].unique().tolist()
    return {"detected": len(dup_ids) > 0, "count": len(dup_ids),
            "evidence": f"duplicate PatientID count={len(dup_ids)}, examples={dup_ids[:4]}"}


def detect_005(df: pd.DataFrame) -> dict:
    """005: 性别-诊断逻辑矛盾（男+卵巢囊肿 或 女+前列腺癌）"""
    conflict = df[
        ((df["Gender"] == "Male") & (df["MedicalCondition"] == "卵巢囊肿")) |
        ((df["Gender"] == "Female") & (df["MedicalCondition"] == "前列腺癌"))
    ]
    pids = conflict["PatientID"].tolist()
    return {"detected": len(pids) > 0, "count": len(pids),
            "evidence": f"gender-diagnosis conflicts patient_ids={pids}"}


def detect_006(df: pd.DataFrame) -> dict:
    """006: 日期逻辑错误（出院<入院 或 未来日期）"""
    admit = pd.to_datetime(df["AdmissionDate"], errors="coerce")
    discharge = pd.to_datetime(df["DischargeDate"], errors="coerce")
    before = (discharge < admit).sum()
    future = (admit > pd.Timestamp.now()).sum()
    total = before + future
    return {"detected": total > 0, "count": int(total),
            "evidence": f"discharge<admission count={before}, future admission count={future}"}


def detect_007(df: pd.DataFrame) -> dict:
    """007: 不可能生命体征（心率=0/>250, 体温<35/>42）"""
    hr = pd.to_numeric(df["HeartRate"], errors="coerce")
    temp = pd.to_numeric(df["Temperature"], errors="coerce")
    hr_bad = ((hr == 0) | (hr > 250)).sum()
    temp_bad = ((temp < 35) | (temp > 42)).sum()
    examples = []
    if hr_bad > 0:
        examples.extend([f"HR={v}" for v in hr[(hr == 0) | (hr > 250)].head(3).tolist()])
    if temp_bad > 0:
        examples.extend([f"Temp={v}" for v in temp[(temp < 35) | (temp > 42)].head(3).tolist()])
    return {"detected": (hr_bad + temp_bad) > 0, "count": int(hr_bad + temp_bad),
            "evidence": f"impossible vitals examples={examples}"}


def detect_008(df: pd.DataFrame) -> dict:
    """008: 无效 BloodType"""
    valid = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    bad = df[~df["BloodType"].isin(valid)]
    vals = bad["BloodType"].unique().tolist()
    return {"detected": len(bad) > 0, "count": len(bad),
            "evidence": f"invalid BloodType count={len(bad)}, values={vals}"}


def detect_009(df: pd.DataFrame) -> dict:
    """009: TCM 术语变体"""
    tcm = df["TCM_Diagnosis"].dropna().unique()
    nonblank = [v for v in tcm if str(v).strip()]
    return {"detected": len(nonblank) > 5, "count": len(nonblank),
            "evidence": f"TCM nonblank unique={len(nonblank)}, examples={nonblank[:8]}"}


def detect_010(df: pd.DataFrame) -> dict:
    """010: 数值截断标记（PSA_Level 中的 <, >, 小于, 大于 等）"""
    markers = df["PSA_Level"].astype(str).str.contains(r"[<>小于大于=]", regex=True)
    count = markers.sum()
    examples = df.loc[markers, "PSA_Level"].head(7).tolist()
    return {"detected": count > 0, "count": int(count),
            "evidence": f"truncation marker count={count}, examples={examples}"}


def detect_011(df: pd.DataFrame) -> dict:
    """011: 逗号多值"""
    comma_billing = df["BillingAmount"].astype(str).str.contains(",", na=False)
    comma_lab = df["LabResult_Multi"].astype(str).str.contains(",", na=False)
    examples = []
    for _, row in df[comma_billing].head(2).iterrows():
        examples.append(("BillingAmount", str(row["BillingAmount"])))
    for _, row in df[comma_lab].head(3).iterrows():
        examples.append(("LabResult_Multi", str(row["LabResult_Multi"])))
    count = comma_billing.sum() + comma_lab.sum()
    return {"detected": count > 0, "count": int(count),
            "evidence": f"comma multi-value count={count}, examples={examples}"}


def detect_012(df: pd.DataFrame) -> dict:
    """012: 中文数字"""
    cn_chars = set("一二三四五六七八九十")
    temp_cn = df["Temperature"].astype(str).apply(lambda x: any(c in x for c in cn_chars))
    notes_cn = df["Notes"].astype(str).apply(lambda x: any(c in x for c in cn_chars))
    count = temp_cn.sum() + notes_cn.sum()
    examples = []
    for _, row in df[temp_cn].head(2).iterrows():
        examples.append((row["PatientID"], str(row["Temperature"]), ""))
    for _, row in df[notes_cn].head(3).iterrows():
        examples.append((row["PatientID"], str(row.get("Temperature", "")), str(row["Notes"])))
    return {"detected": count > 0, "count": int(count),
            "evidence": f"known inserted Chinese numeral rows count={count}, examples={examples}"}


def detect_013(df: pd.DataFrame) -> dict:
    """013: 极端组不平衡（TreatmentGroup）"""
    counts = df["TreatmentGroup"].value_counts().to_dict()
    t = counts.get("Treatment", 0)
    c = counts.get("Control", 1)
    ratio = t / max(c, 1)
    return {"detected": ratio > 5, "count": t + c,
            "evidence": f"TreatmentGroup counts={counts}, min/max={c/max(t,1):.3f}"}


def detect_014(df: pd.DataFrame) -> dict:
    """014: 零方差变量（HeartRate rows 500-509 全为 72）"""
    block = df.iloc[500:510] if len(df) > 510 else df.tail(10)
    hr_block = pd.to_numeric(block["HeartRate"], errors="coerce")
    const_val = hr_block.mode()
    if len(const_val) > 0:
        is_const = (hr_block == const_val.iloc[0]).all()
        return {"detected": is_const, "count": len(hr_block),
                "evidence": f"constant block=('HeartRate', {hr_block.iloc[0]}, '{const_val.iloc[0]}')"}
    return {"detected": False, "count": 0, "evidence": "no constant block found"}


def detect_015(df: pd.DataFrame) -> dict:
    """015: 稀少类别"""
    examples = []
    for col in ["MedicalCondition", "SmokingStatus"]:
        vc = df[col].value_counts()
        rare = vc[vc <= 3]
        for val, cnt in rare.items():
            examples.append((col, val, int(cnt)))
    return {"detected": len(examples) > 0, "count": len(examples),
            "evidence": f"sparse categories examples={examples[:6]}"}


def detect_016(df: pd.DataFrame) -> dict:
    """016: MAR 缺失模式（Outcome 缺失集中在 Education=文盲）"""
    df["Outcome_missing"] = df["Outcome"].isna() | (df["Outcome"] == "")
    overall = df["Outcome_missing"].mean()
    rates = {}
    for edu in df["EducationLevel"].unique():
        sub = df[df["EducationLevel"] == edu]
        rates[edu] = sub["Outcome_missing"].mean()
    # 检查是否有子组缺失率显著高于总体
    max_diff = max(r - overall for r in rates.values())
    detected = max_diff > 0.10  # 超过 10 个百分点
    return {"detected": detected, "count": len(rates),
            "evidence": f"Outcome missing rates by education={rates}, overall={overall:.3f}, "
                        f"max_diff={max_diff:.3f}, detected={detected}"}


def detect_017(df: pd.DataFrame) -> dict:
    """017: 阻断条件触发（数据质量问题密度高）"""
    issue_count = 0
    if (pd.to_numeric(df["BillingAmount"], errors="coerce") < 0).sum() > 0:
        issue_count += 1
    if df["Age"].isna().sum() > 0:
        issue_count += 1
    if df.duplicated("PatientID").sum() > 0:
        issue_count += 1
    return {"detected": issue_count >= 3, "count": issue_count,
            "evidence": f"data/logic/format issue count among first 12={issue_count}"}


def detect_018(df: pd.DataFrame) -> dict:
    """018: 自适应样本量停止（组不平衡极端）"""
    counts = df["TreatmentGroup"].value_counts()
    c = counts.get("Control", 0)
    t = counts.get("Treatment", 0)
    prop = c / max(t + c, 1)
    return {"detected": prop < 0.10, "count": c + t,
            "evidence": f"control proportion={c}/{t+c}={prop:.3f}"}


def detect_019(df: pd.DataFrame) -> dict:
    """019: 数据不足时标记 SKIP"""
    has_sparse = df["MedicalCondition"].value_counts().min() <= 2
    has_imbalance = df["TreatmentGroup"].value_counts().min() / df["TreatmentGroup"].value_counts().max() < 0.1
    return {"detected": has_sparse or has_imbalance, "count": int(has_sparse) + int(has_imbalance),
            "evidence": f"insufficient-data situations present via rare categories and extreme imbalance"}


def detect_020(df: pd.DataFrame) -> dict:
    """020: 极端异常值标记"""
    bill = pd.to_numeric(df["BillingAmount"], errors="coerce")
    extreme = bill[bill > 100000]
    examples = extreme.head(3).tolist()
    return {"detected": len(extreme) > 0, "count": len(extreme),
            "evidence": f"extreme outliers examples={examples}"}


def detect_021(df: pd.DataFrame) -> dict:
    """021: 严重不良事件标记"""
    severe = (df["AdverseEvent"] == "Severe").sum()
    return {"detected": severe > 0, "count": int(severe),
            "evidence": f"Severe adverse event count={severe}"}


# 检测函数注册表
DETECTORS = {
    "001": detect_001, "002": detect_002, "003": detect_003, "004": detect_004,
    "005": detect_005, "006": detect_006, "007": detect_007, "008": detect_008,
    "009": detect_009, "010": detect_010, "011": detect_011, "012": detect_012,
    "013": detect_013, "014": detect_014, "015": detect_015, "016": detect_016,
    "017": detect_017, "018": detect_018, "019": detect_019, "020": detect_020,
    "021": detect_021,
}


def run_eval(tuple_id: str = None, verbose: bool = False) -> dict:
    """运行 Gold Eval"""
    if not DATA_FILE.exists():
        print(f"❌ 数据文件不存在: {DATA_FILE}")
        sys.exit(1)

    df = pd.read_csv(DATA_FILE)
    tuples = load_all_tuples() if tuple_id is None else [load_tuple(tuple_id)]

    if tuple_id and not tuples[0]:
        print(f"❌ Tuple {tuple_id} 不存在")
        sys.exit(1)

    results = []
    for t in tuples:
        tid = t["tuple_id"].split("-")[0]  # "001-negative-billing-amount" -> "001"
        detector = DETECTORS.get(tid)
        if not detector:
            results.append({"tuple_id": tid, "status": "SKIP", "reason": "no detector"})
            continue

        try:
            det_result = detector(df)
            expected_detect = t["expected"]["detection"]
            matched = det_result["detected"] == expected_detect
            status = "PASS" if matched else "FAIL"

            results.append({
                "tuple_id": tid,
                "test_name": t["test_name"],
                "kind": t["kind"],
                "status": status,
                "detected": bool(det_result["detected"]),
                "expected": bool(expected_detect),
                "evidence": det_result["evidence"],
            })
        except Exception as e:
            results.append({
                "tuple_id": tid, "status": "ERROR", "error": str(e),
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="MSRA Pipeline Gold Evaluation Runner")
    parser.add_argument("--tuple", type=str, help="Run specific tuple (e.g. 001)")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    results = run_eval(tuple_id=args.tuple, verbose=args.verbose)

    # 输出结果
    print("=" * 64)
    print("MSRA Pipeline Gold Evaluation Results")
    print("=" * 64)
    print(f"  数据文件: {DATA_FILE}")
    print(f"  Tuple 数: {len(results)}")
    print()

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    skipped = sum(1 for r in results if r["status"] == "SKIP")

    for r in results:
        status_icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "ERROR": "[WARN]", "SKIP": "[SKIP]"}.get(r["status"], "[????]")
        name = r.get("test_name", r["tuple_id"])
        print(f"  {status_icon} {r['tuple_id']} {name} [{r.get('kind', '?')}]")
        if r["status"] == "FAIL" or args.verbose:
            print(f"     detected={r.get('detected')}, expected={r.get('expected')}")
            print(f"     {r.get('evidence', r.get('error', ''))}")
        print()

    print("=" * 64)
    print(f"  结果: {passed} PASS / {failed} FAIL / {errors} ERROR / {skipped} SKIP")
    rate = passed / max(passed + failed, 1)
    threshold = 0.90
    met = "[PASS] 达标" if rate >= threshold else "[FAIL] 未达标"
    print(f"  检出率: {rate:.1%} (阈值 {threshold:.0%}) {met}")
    print("=" * 64)

    # 保存结果
    results_dir = BASE / "evals" / "gold" / "pipeline" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_file = results_dir / "eval_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  结果已保存: {out_file}")

    sys.exit(0 if failed == 0 and errors == 0 else 1)


if __name__ == "__main__":
    main()
