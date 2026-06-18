"""
自动化报告合规检查器
====================
检查生成的报告是否符合指定的报告规范 (CONSORT/STROBE/PRISMA/STARD/TRIPOD+AI/PRISMA-NMA)

用法:
    python compliance_checker.py --report final_report.md --guideline CONSORT_2025
    python compliance_checker.py --report final_report.md --guideline STROBE --verbose

输出:
    JSON 格式的合规检查结果，包含覆盖率、缺失条目、改进建议
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


# 报告规范检查清单定义
CHECKLISTS = {
    "CONSORT_2025": {
        "name": "CONSORT 2025",
        "items": {
            "1_title": {"keywords": ["随机", "randomized", "randomised"], "section": "title"},
            "2_background": {"keywords": ["背景", "rationale", "background", "目的", "objective"], "section": "introduction"},
            "3_design": {"keywords": ["平行", "交叉", "析因", "parallel", "crossover", "factorial", "设计"], "section": "methods"},
            "3a_adaptive": {"keywords": ["自适应", "adaptive", "适应规则"], "section": "methods"},
            "4_participants": {"keywords": ["纳入标准", "排除标准", "inclusion", "exclusion", "合格标准"], "section": "methods"},
            "4a_diversity": {"keywords": ["多样性", "diversity", "种族", "ethnicity", "公平"], "section": "methods"},
            "5_interventions": {"keywords": ["干预", "intervention", "治疗方案"], "section": "methods"},
            "6_outcomes": {"keywords": ["主要结局", "次要结局", "primary outcome", "secondary outcome"], "section": "methods"},
            "7_sample_size": {"keywords": ["样本量", "sample size", "power", "检验效能"], "section": "methods"},
            "8_randomization": {"keywords": ["随机化", "randomization", "分配隐藏", "allocation concealment"], "section": "methods"},
            "8a_blinding": {"keywords": ["盲法", "blinding", "双盲", "单盲", "安慰剂"], "section": "methods"},
            "9_statistics": {"keywords": ["统计方法", "statistical", "ITT", "意向性治疗"], "section": "methods"},
            "9a_sap": {"keywords": ["统计分析计划", "SAP", "analysis plan"], "section": "methods"},
            "9b_data_sharing": {"keywords": ["数据共享", "data sharing", "数据可用", "data availability"], "section": "methods"},
            "10_flow": {"keywords": ["流程图", "CONSORT", "flow diagram", "参与者流程"], "section": "results"},
            "12_baseline": {"keywords": ["基线", "baseline", "人口学", "demographic"], "section": "results"},
            "13_outcomes": {"keywords": ["效应量", "effect size", "95% CI", "置信区间", "p值", "p-value"], "section": "results"},
            "14_harms": {"keywords": ["不良事件", "不良反应", "adverse", "安全性", "safety"], "section": "results"},
            "15_limitations": {"keywords": ["局限性", "limitation", "偏倚", "bias"], "section": "discussion"},
            "18_registration": {"keywords": ["注册", "registration", "临床试验注册", "ClinicalTrials"], "section": "other"},
            "20_funding": {"keywords": ["资金", "funding", "资助"], "section": "other"},
            "22_ai_disclosure": {"keywords": ["AI", "人工智能", "LLM", "大语言模型", "机器学习"], "section": "other"},
        },
        "min_coverage": 0.82,
    },
    "STROBE": {
        "name": "STROBE",
        "items": {
            "1_title": {"keywords": ["队列", "病例对照", "横断面", "cohort", "case-control", "cross-sectional"], "section": "title"},
            "2_background": {"keywords": ["背景", "rationale", "background", "目的"], "section": "introduction"},
            "3_design": {"keywords": ["设计", "design", "回顾性", "前瞻性", "retrospective", "prospective"], "section": "methods"},
            "4_participants": {"keywords": ["纳入标准", "排除标准", "inclusion", "exclusion"], "section": "methods"},
            "5_variables": {"keywords": ["变量", "variable", "暴露", "exposure", "结局", "outcome"], "section": "methods"},
            "6_data_sources": {"keywords": ["数据来源", "data source", "数据收集"], "section": "methods"},
            "7_bias": {"keywords": ["偏倚", "bias", "混杂", "confounding"], "section": "methods"},
            "8_sample_size": {"keywords": ["样本量", "sample size"], "section": "methods"},
            "9_quantitative": {"keywords": ["统计方法", "statistical", "回归", "regression"], "section": "methods"},
            "10_participants": {"keywords": ["参与者", "participant", "应答率", "response rate"], "section": "results"},
            "11_descriptive": {"keywords": ["描述性", "descriptive", "基线", "baseline"], "section": "results"},
            "12_outcomes": {"keywords": ["效应量", "effect size", "95% CI", "置信区间"], "section": "results"},
            "14_missing": {"keywords": ["缺失数据", "missing data", "多重插补", "multiple imputation"], "section": "results"},
            "16_main_results": {"keywords": ["主要结果", "main result", "调整", "adjusted"], "section": "results"},
            "17_sensitivity": {"keywords": ["敏感性分析", "sensitivity analysis", "E-value"], "section": "results"},
            "18_limitations": {"keywords": ["局限性", "limitation"], "section": "discussion"},
            "19_generalizability": {"keywords": ["可推广性", "generalizability", "外推"], "section": "discussion"},
            "20_funding": {"keywords": ["资金", "funding"], "section": "other"},
        },
        "min_coverage": 0.83,
    },
    "TRIPOD_AI": {
        "name": "TRIPOD+AI",
        "items": {
            "1_title": {"keywords": ["预测模型", "prediction model", "机器学习", "machine learning"], "section": "title"},
            "2_background": {"keywords": ["背景", "background", "现有模型"], "section": "introduction"},
            "3_sources": {"keywords": ["数据来源", "data source", "训练集", "验证集"], "section": "methods"},
            "4_participants": {"keywords": ["参与者", "participant", "纳入标准"], "section": "methods"},
            "5_outcome": {"keywords": ["结局", "outcome", "预测目标"], "section": "methods"},
            "6_predictors": {"keywords": ["预测因子", "predictor", "特征", "feature"], "section": "methods"},
            "7_sample_size": {"keywords": ["样本量", "sample size", "EPV", "事件数"], "section": "methods"},
            "8_missing": {"keywords": ["缺失数据", "missing data"], "section": "methods"},
            "9_model_selection": {"keywords": ["模型选择", "model selection", "特征工程", "feature engineering"], "section": "methods"},
            "10_model_spec": {"keywords": ["模型规格", "model specification", "算法描述", "超参数"], "section": "methods"},
            "11_evaluation": {"keywords": ["评估", "evaluation", "区分度", "calibration", "AUC", "Brier"], "section": "results"},
            "12_validation": {"keywords": ["验证", "validation", "内部验证", "外部验证", "bootstrap"], "section": "results"},
            "13_performance": {"keywords": ["性能", "performance", "C-index", "校准曲线"], "section": "results"},
            "14_fairness": {"keywords": ["公平性", "fairness", "偏倚", "bias", "亚组"], "section": "results"},
            "15_explainability": {"keywords": ["可解释性", "explainability", "SHAP", "特征重要性"], "section": "results"},
            "16_limitations": {"keywords": ["局限性", "limitation"], "section": "discussion"},
            "17_implications": {"keywords": ["临床意义", "clinical implication", "实用性"], "section": "discussion"},
        },
        "min_coverage": 0.81,
    },
}


def load_report(filepath: str) -> str:
    """加载报告文件"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"报告文件不存在: {filepath}")
    return path.read_text(encoding="utf-8")


def check_item(text: str, keywords: List[str]) -> Tuple[bool, List[str]]:
    """检查单个条目是否在报告中体现"""
    found = []
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            found.append(kw)
    return len(found) > 0, found


def run_compliance_check(
    report_text: str,
    guideline: str,
    verbose: bool = False
) -> Dict:
    """执行合规检查"""
    if guideline not in CHECKLISTS:
        raise ValueError(f"不支持的报告规范: {guideline}. 可选: {list(CHECKLISTS.keys())}")

    checklist = CHECKLISTS[guideline]
    results = {
        "guideline": checklist["name"],
        "total_items": len(checklist["items"]),
        "passed": 0,
        "failed": 0,
        "coverage": 0.0,
        "status": "pending",
        "details": [],
        "missing_items": [],
        "suggestions": [],
    }

    for item_id, item_spec in checklist["items"].items():
        found, matched_kw = check_item(report_text, item_spec["keywords"])
        detail = {
            "item": item_id,
            "section": item_spec["section"],
            "status": "✅" if found else "❌",
            "matched_keywords": matched_kw,
        }
        results["details"].append(detail)

        if found:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["missing_items"].append(item_id)
            results["suggestions"].append(
                f"[{item_id}] 缺失 — 请在 {item_spec['section']} 部分补充相关内容"
            )

    results["coverage"] = results["passed"] / results["total_items"]

    # 判定状态
    min_cov = checklist["min_coverage"]
    if results["coverage"] >= min_cov:
        results["status"] = "✅ 通过"
    elif results["coverage"] >= min_cov * 0.85:
        results["status"] = "⚠️ 警告"
    else:
        results["status"] = "❌ 不通过"

    if verbose:
        print(f"\n{'='*50}")
        print(f"  {checklist['name']} 合规检查报告")
        print(f"{'='*50}")
        print(f"  总条目: {results['total_items']}")
        print(f"  通过: {results['passed']} | 未通过: {results['failed']}")
        print(f"  覆盖率: {results['coverage']:.1%}")
        print(f"  状态: {results['status']}")
        print(f"{'='*50}")

        if results["missing_items"]:
            print(f"\n  缺失条目:")
            for item in results["missing_items"]:
                print(f"    ❌ {item}")

        if results["suggestions"]:
            print(f"\n  改进建议:")
            for s in results["suggestions"]:
                print(f"    💡 {s}")

    return results


def check_table_understanding(table_data: Dict) -> Dict:
    """
    检查表格理解质量
    
    使用Chain-of-Table、Tree-of-Table、TableMaster方法分析表格
    
    Parameters
    ----------
    table_data : Dict
        表格数据，包含headers和rows
        
    Returns
    -------
    Dict
        表格理解分析结果
    """
    try:
        # 导入表格理解模块
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from table_understanding import TableChainVerifier, TableTreeAnalyzer, TableMasterExtractor
        
        results = {
            'chain_verification': {},
            'tree_analysis': {},
            'master_extraction': {},
            'overall_score': 0.0,
            'recommendations': []
        }
        
        # Chain-of-Table 验证
        try:
            verifier = TableChainVerifier(table_data)
            chain_results = verifier.verify()
            results['chain_verification'] = chain_results
        except Exception as e:
            results['chain_verification'] = {'error': str(e)}
            results['recommendations'].append(f"Chain-of-Table验证失败: {e}")
        
        # Tree-of-Table 分析
        try:
            analyzer = TableTreeAnalyzer(table_data)
            tree_analysis = analyzer.analyze()
            results['tree_analysis'] = tree_analysis
        except Exception as e:
            results['tree_analysis'] = {'error': str(e)}
            results['recommendations'].append(f"Tree-of-Table分析失败: {e}")
        
        # TableMaster 提取
        try:
            extractor = TableMasterExtractor(table_data)
            master_extraction = extractor.extract()
            results['master_extraction'] = master_extraction
        except Exception as e:
            results['master_extraction'] = {'error': str(e)}
            results['recommendations'].append(f"TableMaster提取失败: {e}")
        
        # 计算总体分数
        scores = []
        if 'score' in results['chain_verification']:
            scores.append(results['chain_verification']['score'])
        if 'score' in results['tree_analysis']:
            scores.append(results['tree_analysis']['score'])
        if 'score' in results['master_extraction']:
            scores.append(results['master_extraction']['score'])
        
        if scores:
            results['overall_score'] = sum(scores) / len(scores)
        
        return results
        
    except ImportError as e:
        return {
            'error': f"无法导入表格理解模块: {e}",
            'overall_score': 0.0,
            'recommendations': ["请确保表格理解模块已正确安装"]
        }


def check_chart_understanding(chart_data: Dict) -> Dict:
    """
    检查图表理解质量
    
    使用FDV方法分析图表
    
    Parameters
    ----------
    chart_data : Dict
        图表数据，包含类型、数据点、坐标轴等信息
        
    Returns
    -------
    Dict
        图表理解分析结果
    """
    try:
        # 导入图表理解模块
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from chart_understanding import ChartFDVGenerator
        
        results = {
            'fdv_description': {},
            'quality_assessment': {},
            'consistency_check': {},
            'overall_score': 0.0,
            'recommendations': []
        }
        
        # FDV 描述生成
        try:
            generator = ChartFDVGenerator(chart_data)
            fdv_description = generator.generate_description()
            results['fdv_description'] = fdv_description
        except Exception as e:
            results['fdv_description'] = {'error': str(e)}
            results['recommendations'].append(f"FDV描述生成失败: {e}")
        
        # 质量评估
        try:
            generator = ChartFDVGenerator(chart_data)
            quality_assessment = generator.assess_quality()
            results['quality_assessment'] = quality_assessment
        except Exception as e:
            results['quality_assessment'] = {'error': str(e)}
            results['recommendations'].append(f"质量评估失败: {e}")
        
        # 一致性检查
        try:
            generator = ChartFDVGenerator(chart_data)
            consistency_check = generator.check_consistency()
            results['consistency_check'] = consistency_check
        except Exception as e:
            results['consistency_check'] = {'error': str(e)}
            results['recommendations'].append(f"一致性检查失败: {e}")
        
        # 计算总体分数
        scores = []
        if 'score' in results['quality_assessment']:
            scores.append(results['quality_assessment']['score'])
        if 'score' in results['consistency_check']:
            scores.append(results['consistency_check']['score'])
        
        if scores:
            results['overall_score'] = sum(scores) / len(scores)
        
        return results
        
    except ImportError as e:
        return {
            'error': f"无法导入图表理解模块: {e}",
            'overall_score': 0.0,
            'recommendations': ["请确保图表理解模块已正确安装"]
        }


def main():
    parser = argparse.ArgumentParser(description="MSRA 自动化报告合规检查器")
    parser.add_argument("--report", required=True, help="报告文件路径 (MD/HTML)")
    parser.add_argument("--guideline", required=True, choices=list(CHECKLISTS.keys()), help="报告规范")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--output", help="输出 JSON 文件路径")
    parser.add_argument("--check-table", help="检查表格数据 (JSON格式)")
    parser.add_argument("--check-chart", help="检查图表数据 (JSON格式)")
    args = parser.parse_args()

    report_text = load_report(args.report)
    results = run_compliance_check(report_text, args.guideline, args.verbose)

    # 添加表格理解检查
    if args.check_table:
        try:
            table_data = json.loads(args.check_table)
            table_results = check_table_understanding(table_data)
            results['table_understanding'] = table_results
        except json.JSONDecodeError as e:
            results['table_understanding'] = {'error': f"JSON解析失败: {e}"}

    # 添加图表理解检查
    if args.check_chart:
        try:
            chart_data = json.loads(args.check_chart)
            chart_results = check_chart_understanding(chart_data)
            results['chart_understanding'] = chart_results
        except json.JSONDecodeError as e:
            results['chart_understanding'] = {'error': f"JSON解析失败: {e}"}

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
