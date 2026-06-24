#!/usr/bin/env python3
"""
MSRA 数据去标识化工具

识别和处理直接标识符和间接标识符，生成可共享的去标识化数据。
用于数据共享包生成。
"""

import hashlib
import logging
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataDeidentifier:
    """数据去标识化工具"""

    def __init__(self):
        """初始化去标识化工具"""
        # 直接标识符模式
        self.direct_identifiers = {
            "name": [
                r"姓名", r"name", r"patient.*name", r"subject.*id",
                r"患者.*姓名", r"受试者.*姓名"
            ],
            "id_card": [
                r"身份证", r"id.*card", r"身份证号", r"证件号",
                r"公民身份号码", r"身份号码"
            ],
            "phone": [
                r"电话", r"手机", r"phone", r"mobile", r"tel",
                r"联系电话", r"手机号码"
            ],
            "email": [
                r"邮箱", r"email", r"电子邮件", r"邮件地址"
            ],
            "address": [
                r"地址", r"address", r"住址", r"居住地",
                r"家庭住址", r"通讯地址"
            ],
            "social_security": [
                r"社保号", r"social.*security", r"医保号",
                r"社会保障号", r"医疗保险号"
            ],
            "medical_record": [
                r"病历号", r"medical.*record", r"住院号",
                r"门诊号", r"病案号"
            ]
        }

        # 间接标识符模式（HIPAA Safe Harbor 18 类）
        self.indirect_identifiers = {
            "birth_date": [
                r"出生日期", r"birth.*date", r"出生年月",
                r"出生年月日", r"生日"
            ],
            "admission_date": [
                r"入院日期", r"admission.*date", r"入院时间",
                r"住院日期"
            ],
            "discharge_date": [
                r"出院日期", r"discharge.*date", r"出院时间",
                r"出院日期"
            ],
            "death_date": [
                r"死亡日期", r"death.*date", r"死亡时间"
            ],
            "zip_code": [
                r"邮编", r"zip.*code", r"邮政编码",
                r"邮政编码号"
            ],
            "geographic": [
                r"地区", r"region", r"省市", r"城市",
                r"区县", r"乡镇"
            ],
            "account_number": [
                r"账号", r"account.*num", r"银行.*号",
                r"保险.*号", r"医保.*卡号", r"社保.*卡号"
            ],
            "certificate_number": [
                r"证书.*号", r"license.*num", r"执照.*号",
                r"资格证.*号", r"执业.*证号"
            ],
            "vehicle_identifier": [
                r"车牌", r"vehicle.*id", r"车架号", r"VIN"
            ],
            "device_identifier": [
                r"设备.*号", r"device.*id", r"器械.*号",
                r"UDI", r"序列号"
            ],
            "web_url": [
                r"网址", r"url", r"website", r"链接",
                r"http[s]?://", r"www\."
            ],
            "ip_address": [
                r"IP.*地址", r"ip.*addr", r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            ],
            "biometric_identifier": [
                r"指纹", r"fingerprint", r"虹膜", r"retina",
                r"声纹", r"voiceprint", r"面部.*识别"
            ],
            "photo": [
                r"照片", r"photo", r"picture", r"图像",
                r"面部", r"face.*image"
            ]
        }

        # 去标识化策略
        self.strategies = {
            "suppress": "删除标识符列",
            "generalize": "泛化标识符（如年龄分组）",
            "hash": "哈希替换（不可逆）",
            "noise": "添加随机噪声",
            "pseudonymize": "假名替换（可逆）"
        }

    def identify_identifiers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        识别数据中的标识符
        
        Args:
            df: 数据框
            
        Returns:
            识别结果字典
        """
        results = {
            "direct_identifiers": [],
            "indirect_identifiers": [],
            "potential_identifiers": []
        }

        # 检查列名
        for col in df.columns:
            col_lower = col.lower()

            # 检查直接标识符
            for id_type, patterns in self.direct_identifiers.items():
                for pattern in patterns:
                    if re.search(pattern, col_lower):
                        results["direct_identifiers"].append({
                            "column": col,
                            "type": id_type,
                            "pattern": pattern
                        })
                        break

            # 检查间接标识符
            for id_type, patterns in self.indirect_identifiers.items():
                for pattern in patterns:
                    if re.search(pattern, col_lower):
                        results["indirect_identifiers"].append({
                            "column": col,
                            "type": id_type,
                            "pattern": pattern
                        })
                        break

        # 检查可能的高基数列（如唯一ID）
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio > 0.9:  # 高基数
                    results["potential_identifiers"].append({
                        "column": col,
                        "unique_ratio": unique_ratio,
                        "unique_count": df[col].nunique()
                    })

        return results

    def deidentify_data(self, df: pd.DataFrame,
                        strategy: str = "suppress",
                        columns_to_process: List[str] = None,
                        **kwargs) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        去标识化数据
        
        Args:
            df: 原始数据框
            strategy: 去标识化策略
            columns_to_process: 要处理的列（可选）
            **kwargs: 策略参数
            
        Returns:
            去标识化后的数据框和处理报告
        """
        df_deidentified = df.copy()
        report = {
            "strategy": strategy,
            "columns_processed": [],
            "original_values": {},
            "deidentified_values": {}
        }

        # 识别标识符
        identifiers = self.identify_identifiers(df)

        # 确定要处理的列
        if columns_to_process is None:
            columns_to_process = [id_info["column"] for id_info in
                                identifiers["direct_identifiers"] +
                                identifiers["indirect_identifiers"]]

        # 对每列应用去标识化策略
        for col in columns_to_process:
            if col not in df.columns:
                continue

            if strategy == "suppress":
                df_deidentified, col_report = self._suppress_column(df_deidentified, col)
            elif strategy == "hash":
                df_deidentified, col_report = self._hash_column(df_deidentified, col, **kwargs)
            elif strategy == "generalize":
                df_deidentified, col_report = self._generalize_column(df_deidentified, col, **kwargs)
            elif strategy == "noise":
                df_deidentified, col_report = self._add_noise_column(df_deidentified, col, **kwargs)
            else:
                continue

            report["columns_processed"].append(col)
            report["original_values"][col] = col_report.get("original_summary", "")
            report["deidentified_values"][col] = col_report.get("deidentified_summary", "")

        return df_deidentified, report

    def _suppress_column(self, df: pd.DataFrame, col: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """删除列"""
        report = {
            "strategy": "suppress",
            "original_summary": f"列 '{col}' 包含 {df[col].nunique()} 个唯一值",
            "deidentified_summary": f"列 '{col}' 已删除"
        }

        df = df.drop(columns=[col])

        return df, report

    def _hash_column(self, df: pd.DataFrame, col: str,
                     salt: str = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """哈希替换列"""
        if salt is None:
            salt = secrets.token_hex(16)
            import warnings
            warnings.warn(
                "去标识化使用了随机生成的盐值，结果不可复现。"
                "如需可复现的哈希，请显式传入 salt 参数。",
                UserWarning, stacklevel=2
            )
        original_values = df[col].dropna().unique()[:5]  # 记录前5个原始值

        # 哈希替换
        df[col] = df[col].apply(
            lambda x: hashlib.sha256(f"{salt}{x}".encode()).hexdigest()[:16]
            if pd.notna(x) else x
        )

        report = {
            "strategy": "hash",
            "salt": salt,
            "original_summary": f"原始值示例: {list(original_values)}",
            "deidentified_summary": f"已哈希替换 {len(original_values)}+ 个值"
        }

        return df, report

    def _generalize_column(self, df: pd.DataFrame, col: str,
                          bins: List[int] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """泛化列（HIPAA Safe Harbor: 年龄 >89 聚合为 '90+'）"""
        if bins is None:
            # 默认年龄分组（HIPAA: >89 必须聚合）
            bins = [0, 18, 30, 40, 50, 60, 70, 80, 90]

        original_values = df[col].dropna().unique()[:5]

        if df[col].dtype in ['int64', 'float64']:
            # HIPAA Safe Harbor: 年龄 >89 聚合为 "90+"
            if col.lower() in ['age', '年龄'] and df[col].max() > 89:
                df[col] = df[col].apply(lambda x: "90+" if pd.notna(x) and x > 89 else x)
                # 对 <=89 的值进行分组
                mask = df[col] != "90+"
                if mask.any():
                    numeric_vals = pd.to_numeric(df[mask[col]], errors='coerce')
                    df.loc[mask, col] = pd.cut(numeric_vals, bins=bins, right=False)
            else:
                # 数值型泛化
                df[col] = pd.cut(df[col], bins=bins, right=False)

        report = {
            "strategy": "generalize",
            "bins": bins,
            "original_summary": f"原始值示例: {list(original_values)}",
            "deidentified_summary": f"已泛化为 {len(bins)-1} 个组"
        }

        return df, report

    def _add_noise_column(self, df: pd.DataFrame, col: str,
                         noise_level: float = 0.1) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """添加随机噪声"""
        original_values = df[col].dropna().unique()[:5]

        if df[col].dtype in ['int64', 'float64']:
            # 数值型添加噪声
            std = df[col].std()
            noise = np.random.normal(0, std * noise_level, len(df))
            df[col] = df[col] + noise

        report = {
            "strategy": "noise",
            "noise_level": noise_level,
            "original_summary": f"原始值示例: {list(original_values)}",
            "deidentified_summary": f"已添加 {noise_level*100}% 水平噪声"
        }

        return df, report

    def generate_deidentification_report(self,
                                        original_df: pd.DataFrame,
                                        deidentified_df: pd.DataFrame,
                                        report: Dict[str, Any]) -> str:
        """
        生成去标识化报告
        
        Args:
            original_df: 原始数据框
            deidentified_df: 去标识化后的数据框
            report: 处理报告
            
        Returns:
            报告文件路径
        """
        report_content = f"""# 数据去标识化报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. 去标识化策略

- **策略**: {report['strategy']}
- **处理列数**: {len(report['columns_processed'])}

## 2. 处理详情

### 处理的列
"""

        for col in report['columns_processed']:
            report_content += f"\n#### {col}\n"
            report_content += f"- **原始值摘要**: {report['original_values'].get(col, 'N/A')}\n"
            report_content += f"- **去标识化后**: {report['deidentified_values'].get(col, 'N/A')}\n"

        report_content += f"""
## 3. 数据对比

| 指标 | 原始数据 | 去标识化数据 |
|------|----------|--------------|
| 行数 | {len(original_df)} | {len(deidentified_df)} |
| 列数 | {len(original_df.columns)} | {len(deidentified_df.columns)} |
| 列名 | {', '.join(original_df.columns[:5])}... | {', '.join(deidentified_df.columns[:5])}... |

## 4. 建议

1. 在共享数据前，再次检查是否仍有标识符
2. 考虑数据使用协议（DUA）的制定
3. 确保符合相关隐私法规（如GDPR、HIPAA）

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return report_content

    def save_deidentified_data(self, df: pd.DataFrame,
                              output_path: str,
                              format: str = "csv") -> str:
        """
        保存去标识化后的数据
        
        Args:
            df: 去标识化后的数据框
            output_path: 输出路径
            format: 输出格式
            
        Returns:
            保存的文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "csv":
            file_path = output_path.with_suffix('.csv')
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
        elif format == "parquet":
            file_path = output_path.with_suffix('.parquet')
            df.to_parquet(file_path, index=False)
        elif format == "json":
            file_path = output_path.with_suffix('.json')
            df.to_json(file_path, orient='records', force_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的格式: {format}")

        return str(file_path)


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    # 创建去标识化工具
    deidentifier = DataDeidentifier()

    # 示例数据
    data = {
        "姓名": ["张三", "李四", "王五", "赵六", "钱七"],
        "身份证号": ["110101199001011234", "110101199001021234",
                   "110101199001031234", "110101199001041234",
                   "110101199001051234"],
        "年龄": [25, 30, 35, 40, 45],
        "性别": ["男", "女", "男", "女", "男"],
        "诊断": ["糖尿病", "高血压", "冠心病", "哮喘", "肺炎"]
    }

    df = pd.DataFrame(data)

    # 识别标识符
    identifiers = deidentifier.identify_identifiers(df)
    logger.info("识别到的标识符:")
    logger.info(f"  直接标识符: {len(identifiers['direct_identifiers'])} 个")
    logger.info(f"  间接标识符: {len(identifiers['indirect_identifiers'])} 个")
    logger.info(f"  潜在标识符: {len(identifiers['potential_identifiers'])} 个")

    # 去标识化（哈希策略）
    df_deidentified, report = deidentifier.deidentify_data(
        df,
        strategy="hash",
        columns_to_process=["姓名", "身份证号"]
    )

    logger.info("\n去标识化完成:")
    logger.info(f"  处理列数: {len(report['columns_processed'])}")
    logger.info(f"  处理列: {report['columns_processed']}")

    # 保存去标识化后的数据
    output_path = deidentifier.save_deidentified_data(
        df_deidentified,
        "deidentified_data.csv"
    )
    logger.info(f"\n去标识化数据已保存: {output_path}")

    # 生成报告
    report_content = deidentifier.generate_deidentification_report(
        df, df_deidentified, report
    )

    report_path = "deidentification_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.info(f"去标识化报告已保存: {report_path}")
