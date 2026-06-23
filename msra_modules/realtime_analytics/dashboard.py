"""
Real-time Dashboard - 实时仪表盘

RT-008: 实时仪表盘
"""

import numpy as np
from typing import Optional, Dict, List, Callable
from collections import deque
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RealtimeDashboard:
    """实时仪表盘 (基于Dash/Streamlit)"""

    def __init__(self,
                 max_points: int = 1000,
                 update_interval: float = 1.0):
        """初始化仪表盘

        Args:
            max_points: 最大数据点数
            update_interval: 更新间隔(秒)
        """
        self.max_points = max_points
        self.update_interval = update_interval
        self._data: Dict[str, deque] = {}
        self._alerts: deque = deque(maxlen=100)
        self._stats: Dict[str, Dict] = {}

    def add_metric(self, name: str,
                   display_name: Optional[str] = None,
                   unit: str = "",
                   warning_range: Optional[tuple] = None,
                   critical_range: Optional[tuple] = None):
        """添加监控指标

        Args:
            name: 指标名
            display_name: 显示名
            unit: 单位
            warning_range: 警告范围
            critical_range: 危险范围
        """
        self._data[name] = deque(maxlen=self.max_points)
        self._stats[name] = {
            "display_name": display_name or name,
            "unit": unit,
            "warning_range": warning_range,
            "critical_range": critical_range,
            "current": 0.0,
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
        }

    def update(self, metric: str, value: float,
               timestamp: Optional[float] = None):
        """更新指标值

        Args:
            metric: 指标名
            value: 值
            timestamp: 时间戳
        """
        if metric not in self._data:
            self.add_metric(metric)

        if timestamp is None:
            timestamp = time.time()

        self._data[metric].append((timestamp, value))

        # 更新统计
        values = [v for _, v in self._data[metric]]
        stats = self._stats[metric]
        stats["current"] = value
        stats["mean"] = float(np.mean(values))
        stats["std"] = float(np.std(values))
        stats["min"] = float(np.min(values))
        stats["max"] = float(np.max(values))

    def add_alert(self, alert: Dict):
        """添加警报

        Args:
            alert: 警报字典
        """
        self._alerts.append(alert)

    def get_dashboard_data(self) -> Dict:
        """获取仪表盘数据

        Returns:
            仪表盘数据字典
        """
        return {
            "metrics": {
                name: {
                    "data": list(self._data[name]),
                    "stats": self._stats[name],
                }
                for name in self._data
            },
            "alerts": list(self._alerts),
            "timestamp": time.time(),
        }

    def get_metric_status(self, metric: str) -> str:
        """获取指标状态

        Args:
            metric: 指标名

        Returns:
            状态 ("normal", "warning", "critical")
        """
        if metric not in self._stats:
            return "unknown"

        stats = self._stats[metric]
        value = stats["current"]

        if stats["critical_range"]:
            low, high = stats["critical_range"]
            if value < low or value > high:
                return "critical"

        if stats["warning_range"]:
            low, high = stats["warning_range"]
            if value < low or value > high:
                return "warning"

        return "normal"

    def export_snapshot(self, filepath: str):
        """导出快照

        Args:
            filepath: 文件路径
        """
        import json

        data = self.get_dashboard_data()

        # 转换tuple为list以便JSON序列化
        for metric_data in data["metrics"].values():
            metric_data["data"] = [
                [ts, val] for ts, val in metric_data["data"]
            ]

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported dashboard snapshot to: {filepath}")

    def create_streamlit_app(self):
        """创建Streamlit应用

        Returns:
            Streamlit应用对象 (需要streamlit安装)
        """
        try:
            import streamlit as st
            import pandas as pd
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError as e:
            raise ImportError(
                f"Streamlit and plotly required: {e}. "
                "Install with: pip install streamlit plotly"
            )

        st.set_page_config(
            page_title="MSRA Real-time Monitor",
            page_icon=":hospital:",
            layout="wide"
        )

        st.title("MSRA 实时监测仪表盘")

        # 自动刷新
        st_autorefresh = st.experimental_rerun

        # 显示指标卡片
        cols = st.columns(len(self._stats))
        for i, (name, stats) in enumerate(self._stats.items()):
            with cols[i]:
                status = self.get_metric_status(name)
                color = {
                    "normal": "green",
                    "warning": "orange",
                    "critical": "red",
                    "unknown": "gray"
                }.get(status, "gray")

                st.metric(
                    label=stats["display_name"],
                    value=f"{stats['current']:.1f} {stats['unit']}",
                    delta=f"μ={stats['mean']:.1f} σ={stats['std']:.1f}"
                )

        # 显示趋势图
        st.subheader("趋势图")
        for name, data in self._data.items():
            if len(data) > 0:
                timestamps, values = zip(*list(data))
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines',
                    name=name
                ))
                st.plotly_chart(fig, use_container_width=True)

        # 显示警报
        st.subheader("最近警报")
        if self._alerts:
            alerts_df = pd.DataFrame(list(self._alerts))
            st.dataframe(alerts_df)
        else:
            st.info("暂无警报")

        return st


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        """初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_imaging_report(self,
                                patient_info: Dict,
                                imaging_findings: Dict,
                                radiomics_features: Dict,
                                output_format: str = "html") -> str:
        """生成影像分析报告

        Args:
            patient_info: 患者信息
            imaging_findings: 影像发现
            radiomics_features: 影像组学特征
            output_format: 输出格式 ("html", "markdown")

        Returns:
            报告文件路径
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"imaging_report_{timestamp}.{output_format}"
        filepath = self.output_dir / filename

        if output_format == "html":
            content = self._generate_html_report(
                patient_info, imaging_findings, radiomics_features
            )
        else:
            content = self._generate_markdown_report(
                patient_info, imaging_findings, radiomics_features
            )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Generated imaging report: {filepath}")
        return str(filepath)

    def generate_bio_report(self,
                            sample_info: Dict,
                            qc_summary: Dict,
                            analysis_results: Dict,
                            output_format: str = "html") -> str:
        """生成生物信息报告

        Args:
            sample_info: 样本信息
            qc_summary: QC摘要
            analysis_results: 分析结果

        Returns:
            报告文件路径
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"bio_report_{timestamp}.{output_format}"
        filepath = self.output_dir / filename

        if output_format == "html":
            content = self._generate_bio_html_report(
                sample_info, qc_summary, analysis_results
            )
        else:
            content = self._generate_bio_markdown_report(
                sample_info, qc_summary, analysis_results
            )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Generated bio report: {filepath}")
        return str(filepath)

    def generate_monitoring_report(self,
                                   duration: str,
                                   stats: Dict,
                                   alerts: List[Dict],
                                   output_format: str = "html") -> str:
        """生成实时监测报告

        Args:
            duration: 监测时长
            stats: 统计数据
            alerts: 警报列表

        Returns:
            报告文件路径
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"monitoring_report_{timestamp}.{output_format}"
        filepath = self.output_dir / filename

        if output_format == "html":
            content = self._generate_monitoring_html_report(
                duration, stats, alerts
            )
        else:
            content = self._generate_monitoring_markdown_report(
                duration, stats, alerts
            )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Generated monitoring report: {filepath}")
        return str(filepath)

    def _generate_html_report(self, patient_info, findings, features):
        """生成HTML影像报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>医学影像分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        .section {{ margin-bottom: 30px; }}
        .finding {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>医学影像分析报告</h1>

    <div class="section">
        <h2>患者信息</h2>
        <table>
            <tr><th>项目</th><th>内容</th></tr>
            <tr><td>患者ID</td><td>{patient_info.get('patient_id', 'N/A')}</td></tr>
            <tr><td>姓名</td><td>{patient_info.get('patient_name', 'N/A')}</td></tr>
            <tr><td>性别</td><td>{patient_info.get('patient_sex', 'N/A')}</td></tr>
            <tr><td>检查日期</td><td>{patient_info.get('study_date', 'N/A')}</td></tr>
            <tr><td>检查类型</td><td>{patient_info.get('modality', 'N/A')}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>影像发现</h2>
"""
        for finding, value in findings.items():
            html += f'        <div class="finding"><strong>{finding}:</strong> {value}</div>\n'

        html += """
    </div>

    <div class="section">
        <h2>影像组学特征</h2>
"""
        for feature_class, feature_dict in features.items():
            html += f'        <h3>{feature_class}</h3>\n'
            html += '        <table>\n'
            html += '            <tr><th>特征名</th><th>值</th></tr>\n'
            for name, value in feature_dict.items():
                if isinstance(value, (int, float)):
                    html += f'            <tr><td>{name}</td><td>{value:.4f}</td></tr>\n'
                else:
                    html += f'            <tr><td>{name}</td><td>{value}</td></tr>\n'
            html += '        </table>\n'

        html += """
    </div>

    <div class="section">
        <p><em>报告生成时间: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """</em></p>
        <p><em>本报告由MSRA系统自动生成</em></p>
    </div>
</body>
</html>
"""
        return html

    def _generate_markdown_report(self, patient_info, findings, features):
        """生成Markdown影像报告"""
        md = f"""# 医学影像分析报告

## 患者信息

| 项目 | 内容 |
|------|------|
| 患者ID | {patient_info.get('patient_id', 'N/A')} |
| 姓名 | {patient_info.get('patient_name', 'N/A')} |
| 性别 | {patient_info.get('patient_sex', 'N/A')} |
| 检查日期 | {patient_info.get('study_date', 'N/A')} |
| 检查类型 | {patient_info.get('modality', 'N/A')} |

## 影像发现

"""
        for finding, value in findings.items():
            md += f"- **{finding}**: {value}\n"

        md += "\n## 影像组学特征\n\n"
        for feature_class, feature_dict in features.items():
            md += f"### {feature_class}\n\n"
            md += "| 特征名 | 值 |\n|--------|----|\n"
            for name, value in feature_dict.items():
                if isinstance(value, (int, float)):
                    md += f"| {name} | {value:.4f} |\n"
                else:
                    md += f"| {name} | {value} |\n"
            md += "\n"

        md += f"\n---\n*报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*  \n"
        md += "*本报告由MSRA系统自动生成*\n"

        return md

    def _generate_bio_html_report(self, sample_info, qc_summary, results):
        """生成HTML生物信息报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>单细胞分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #27ae60; border-bottom: 2px solid #27ae60; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #27ae60; color: white; }}
    </style>
</head>
<body>
    <h1>单细胞RNA-seq分析报告</h1>

    <h2>样本信息</h2>
    <table>
        <tr><th>项目</th><th>内容</th></tr>
        <tr><td>样本名称</td><td>{sample_info.get('sample_name', 'N/A')}</td></tr>
        <tr><td>数据来源</td><td>{sample_info.get('source', 'N/A')}</td></tr>
        <tr><td>细胞数</td><td>{qc_summary.get('n_cells', 'N/A')}</td></tr>
        <tr><td>基因数</td><td>{qc_summary.get('n_genes', 'N/A')}</td></tr>
    </table>

    <h2>QC摘要</h2>
    <table>
        <tr><th>指标</th><th>值</th></tr>
"""
        for key, value in qc_summary.items():
            if isinstance(value, float):
                html += f"        <tr><td>{key}</td><td>{value:.2f}</td></tr>\n"
            else:
                html += f"        <tr><td>{key}</td><td>{value}</td></tr>\n"

        html += """
    </table>

    <h2>分析结果</h2>
"""
        for analysis, result in results.items():
            html += f"    <h3>{analysis}</h3>\n"
            if isinstance(result, dict):
                html += '    <table>\n'
                for k, v in result.items():
                    html += f'        <tr><td>{k}</td><td>{v}</td></tr>\n'
                html += '    </table>\n'
            else:
                html += f'    <p>{result}</p>\n'

        html += f"""
    <p><em>报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    <p><em>本报告由MSRA系统自动生成</em></p>
</body>
</html>
"""
        return html

    def _generate_bio_markdown_report(self, sample_info, qc_summary, results):
        """生成Markdown生物信息报告"""
        md = f"""# 单细胞RNA-seq分析报告

## 样本信息

| 项目 | 内容 |
|------|------|
| 样本名称 | {sample_info.get('sample_name', 'N/A')} |
| 数据来源 | {sample_info.get('source', 'N/A')} |
| 细胞数 | {qc_summary.get('n_cells', 'N/A')} |
| 基因数 | {qc_summary.get('n_genes', 'N/A')} |

## QC摘要

| 指标 | 值 |
|------|----|
"""
        for key, value in qc_summary.items():
            if isinstance(value, float):
                md += f"| {key} | {value:.2f} |\n"
            else:
                md += f"| {key} | {value} |\n"

        md += "\n## 分析结果\n\n"
        for analysis, result in results.items():
            md += f"### {analysis}\n\n"
            if isinstance(result, dict):
                for k, v in result.items():
                    md += f"- **{k}**: {v}\n"
            else:
                md += f"{result}\n"
            md += "\n"

        md += f"\n---\n*报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return md

    def _generate_monitoring_html_report(self, duration, stats, alerts):
        """生成HTML监测报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>实时监测报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #e74c3c; border-bottom: 2px solid #e74c3c; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #e74c3c; color: white; }}
        .alert-critical {{ background-color: #ffebee; }}
        .alert-warning {{ background-color: #fff3e0; }}
    </style>
</head>
<body>
    <h1>实时监测报告</h1>
    <p>监测时长: {duration}</p>

    <h2>统计摘要</h2>
    <table>
        <tr><th>指标</th><th>均值</th><th>标准差</th><th>最小值</th><th>最大值</th></tr>
"""
        for metric, m_stats in stats.items():
            html += f"        <tr><td>{metric}</td>"
            html += f"<td>{m_stats.get('mean', 0):.2f}</td>"
            html += f"<td>{m_stats.get('std', 0):.2f}</td>"
            html += f"<td>{m_stats.get('min', 0):.2f}</td>"
            html += f"<td>{m_stats.get('max', 0):.2f}</td></tr>\n"

        html += """
    </table>

    <h2>警报记录</h2>
"""
        if alerts:
            html += '    <table>\n'
            html += '        <tr><th>时间</th><th>规则</th><th>指标</th><th>值</th><th>级别</th><th>消息</th></tr>\n'
            for alert in alerts:
                level_class = f"alert-{alert.get('level', 'info')}"
                html += f'        <tr class="{level_class}">'
                html += f'<td>{alert.get("timestamp", "")}</td>'
                html += f'<td>{alert.get("rule_name", "")}</td>'
                html += f'<td>{alert.get("metric", "")}</td>'
                html += f'<td>{alert.get("value", 0):.1f}</td>'
                html += f'<td>{alert.get("level", "")}</td>'
                html += f'<td>{alert.get("message", "")}</td>'
                html += '</tr>\n'
            html += '    </table>\n'
        else:
            html += '    <p>监测期间无警报</p>\n'

        html += f"""
    <p><em>报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</body>
</html>
"""
        return html

    def _generate_monitoring_markdown_report(self, duration, stats, alerts):
        """生成Markdown监测报告"""
        md = f"""# 实时监测报告

监测时长: {duration}

## 统计摘要

| 指标 | 均值 | 标准差 | 最小值 | 最大值 |
|------|------|--------|--------|--------|
"""
        for metric, m_stats in stats.items():
            md += f"| {metric} | {m_stats.get('mean', 0):.2f} | {m_stats.get('std', 0):.2f} | {m_stats.get('min', 0):.2f} | {m_stats.get('max', 0):.2f} |\n"

        md += "\n## 警报记录\n\n"
        if alerts:
            md += "| 时间 | 规则 | 指标 | 值 | 级别 | 消息 |\n"
            md += "|------|------|------|----|----|------|\n"
            for alert in alerts:
                md += f"| {alert.get('timestamp', '')} | {alert.get('rule_name', '')} | {alert.get('metric', '')} | {alert.get('value', 0):.1f} | {alert.get('level', '')} | {alert.get('message', '')} |\n"
        else:
            md += "监测期间无警报\n"

        md += f"\n---\n*报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return md
