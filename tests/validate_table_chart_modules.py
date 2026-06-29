#!/usr/bin/env python3
"""
表格和图表理解模块验证脚本
==========================

使用示例数据验证新创建的模块功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def validate_table_understanding():
    """验证表格理解模块"""
    print("=" * 60)
    print("验证表格理解模块")
    print("=" * 60)

    try:
        # 使用绝对路径导入
        table_understanding_path = project_root / 'src' / 'shared' / 'table_understanding'
        sys.path.insert(0, str(table_understanding_path))
        from table_chain_verifier import TableChainVerifier
        from table_master_extractor import TableMasterExtractor
        from table_tree_analyzer import TableTreeAnalyzer

        # 示例医学表格数据
        medical_table = {
            'headers': ['指标', '治疗组(n=100)', '对照组(n=100)', '差异', '95% CI', 'P值'],
            'rows': [
                ['收缩压(mmHg)', '128.5±12.3', '135.2±13.1', '-6.7', '(-8.2, -5.2)', '<0.001'],
                ['舒张压(mmHg)', '82.1±8.5', '85.3±9.2', '-3.2', '(-4.5, -1.9)', '<0.001'],
                ['心率(次/分)', '72.3±10.2', '74.1±11.5', '-1.8', '(-3.1, -0.5)', '0.008'],
                ['BMI(kg/m²)', '24.5±3.2', '25.1±3.5', '-0.6', '(-1.1, -0.1)', '0.025'],
                ['总胆固醇(mmol/L)', '4.8±0.9', '5.1±1.0', '-0.3', '(-0.5, -0.1)', '0.012'],
            ]
        }

        print("\n1. Chain-of-Table 验证")
        print("-" * 40)
        verifier = TableChainVerifier(medical_table)
        chain_result = verifier.verify()
        print(f"验证分数: {chain_result['score']:.2f}")
        print(f"发现问题: {len(chain_result['issues'])}个")
        for issue in chain_result['issues'][:3]:  # 只显示前3个
            print(f"  - {issue}")

        print("\n2. Tree-of-Table 分析")
        print("-" * 40)
        analyzer = TableTreeAnalyzer(medical_table)
        tree_result = analyzer.analyze()
        print(f"层次结构: {len(tree_result.get('hierarchy', {}))}个层级")
        print(f"数据分布: {len(tree_result.get('data_distribution', {}))}个指标")

        print("\n3. TableMaster 提取")
        print("-" * 40)
        extractor = TableMasterExtractor(medical_table)
        extraction_result = extractor.extract()
        print(f"实体数量: {len(extraction_result.get('entities', []))}")
        print(f"关系数量: {len(extraction_result.get('relationships', []))}")
        print(f"统计指标: {len(extraction_result.get('statistics', {}))}")

        # 获取语义描述
        semantic_desc = extractor.get_semantic_description()
        print(f"\n语义描述:\n{semantic_desc[:200]}...")

        return True

    except Exception as e:
        print(f"表格理解模块验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_chart_understanding():
    """验证图表理解模块"""
    print("\n" + "=" * 60)
    print("验证图表理解模块")
    print("=" * 60)

    try:
        # 使用绝对路径导入
        chart_understanding_path = project_root / 'src' / 'shared' / 'chart_understanding'
        sys.path.insert(0, str(chart_understanding_path))
        from chart_fdv_generator import ChartFDVGenerator

        # 示例散点图数据
        scatter_chart = {
            'type': 'scatter',
            'title': 'BMI与收缩压的关系',
            'xlabel': 'BMI (kg/m²)',
            'ylabel': '收缩压 (mmHg)',
            'data_points': [
                {'x': 22.5, 'y': 120, 'label': '样本1'},
                {'x': 25.0, 'y': 135, 'label': '样本2'},
                {'x': 28.5, 'y': 145, 'label': '样本3'},
                {'x': 30.0, 'y': 150, 'label': '样本4'},
                {'x': 32.5, 'y': 158, 'label': '样本5'},
            ],
            'correlation': 0.85,
            'p_value': 0.001,
            'sample_size': 5,
            'confidence_interval': [0.72, 0.93]
        }

        print("\n1. FDV 描述生成")
        print("-" * 40)
        generator = ChartFDVGenerator(scatter_chart)
        fdv_description = generator.generate_description()

        print(f"图表类型: {fdv_description.get('chart_type', 'N/A')}")
        print(f"标题: {fdv_description.get('title', 'N/A')}")
        print(f"X轴: {fdv_description.get('x_axis', {}).get('label', 'N/A')}")
        print(f"Y轴: {fdv_description.get('y_axis', {}).get('label', 'N/A')}")
        print(f"数据点数量: {len(fdv_description.get('data_points', []))}")

        key_findings = fdv_description.get('key_findings', [])
        if key_findings:
            print("关键发现:")
            for finding in key_findings[:3]:
                print(f"  - {finding}")

        print("\n2. 质量评估")
        print("-" * 40)
        quality = generator.assess_quality()
        print(f"质量分数: {quality['score']:.2f}")

        # 安全地获取分数
        completeness_score = quality.get('completeness', {}).get('score', 'N/A')
        clarity_score = quality.get('clarity', {}).get('score', 'N/A')
        accuracy_score = quality.get('accuracy', {}).get('score', 'N/A')

        # 格式化输出
        if isinstance(completeness_score, (int, float)):
            print(f"完整性: {completeness_score:.2f}")
        else:
            print(f"完整性: {completeness_score}")

        if isinstance(clarity_score, (int, float)):
            print(f"清晰度: {clarity_score:.2f}")
        else:
            print(f"清晰度: {clarity_score}")

        if isinstance(accuracy_score, (int, float)):
            print(f"准确性: {accuracy_score:.2f}")
        else:
            print(f"准确性: {accuracy_score}")

        print("\n3. 一致性检查")
        print("-" * 40)
        consistency = generator.check_consistency()

        # 安全地获取分数
        consistency_score = consistency.get('score', 'N/A')
        if isinstance(consistency_score, (int, float)):
            print(f"一致性分数: {consistency_score:.2f}")
        else:
            print(f"一致性分数: {consistency_score}")

        print(f"发现问题: {len(consistency.get('issues', []))}个")

        return True

    except Exception as e:
        print(f"图表理解模块验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_compliance_checker():
    """验证合规性检查器增强功能"""
    print("\n" + "=" * 60)
    print("验证合规性检查器增强功能")
    print("=" * 60)

    try:
        # 使用绝对路径导入
        report_assembler_path = project_root / 'src' / 'shared' / 'report_assembler'
        sys.path.insert(0, str(report_assembler_path))
        from compliance_checker import (
            check_chart_quality_automated,
            check_table_data_consistency,
            check_table_structure_integrity,
        )

        # 测试表格结构完整性检查
        print("\n1. 表格结构完整性检查")
        print("-" * 40)
        table_data = {
            'headers': ['变量', '治疗组', '对照组', 'P值'],
            'rows': [
                ['年龄', '45.2±12.3', '46.1±11.8', '0.45'],
                ['性别(男)', '60(50%)', '55(45.8%)', '0.32'],
                ['BMI', '24.5±3.2', '25.1±3.5', '0.18'],
            ]
        }

        structure_result = check_table_structure_integrity(table_data)
        print(f"结构完整性分数: {structure_result['structure_score']:.2f}")
        print(f"发现问题: {len(structure_result['issues'])}个")

        # 测试表格数据一致性检查
        print("\n2. 表格数据一致性检查")
        print("-" * 40)
        consistency_result = check_table_data_consistency(table_data)
        print(f"数据一致性分数: {consistency_result['consistency_score']:.2f}")
        print(f"发现问题: {len(consistency_result['issues'])}个")

        # 测试图表质量自动化评估
        print("\n3. 图表质量自动化评估")
        print("-" * 40)
        chart_data = {
            'type': 'scatter',
            'title': 'BMI与心血管风险的关系',
            'xlabel': 'BMI (kg/m²)',
            'ylabel': '10年心血管风险 (%)',
            'data_points': [
                {'x': 22, 'y': 3.5},
                {'x': 25, 'y': 5.2},
                {'x': 28, 'y': 7.8},
                {'x': 32, 'y': 12.5},
            ],
            'legend': ['研究人群'],
            'sample_size': 1000
        }

        quality_result = check_chart_quality_automated(chart_data)
        print(f"图表质量分数: {quality_result['quality_score']:.2f}")
        print(f"发现问题: {len(quality_result['issues'])}个")

        return True

    except Exception as e:
        print(f"合规性检查器验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主验证函数"""
    print("开始验证表格和图表理解模块...")

    results = {
        'table_understanding': False,
        'chart_understanding': False,
        'compliance_checker': False
    }

    # 验证表格理解模块
    results['table_understanding'] = validate_table_understanding()

    # 验证图表理解模块
    results['chart_understanding'] = validate_chart_understanding()

    # 验证合规性检查器
    results['compliance_checker'] = validate_compliance_checker()

    # 汇总结果
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)

    all_passed = True
    for module, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{module}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有模块验证通过！")
    else:
        print("⚠️  部分模块验证失败，请检查错误信息")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
