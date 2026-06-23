"""
Alert System - 警报系统

RT-009: 警报通知系统
"""

import time
import json
import smtplib
from email.mime.text import MIMEText
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AlertChannel(Enum):
    """警报渠道"""
    LOG = "log"
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    FILE = "file"


@dataclass
class Alert:
    """警报事件"""
    rule_name: str
    metric: str
    value: float
    level: str  # "info", "warning", "critical"
    message: str
    timestamp: float
    context: Dict = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AlertSystem:
    """警报系统"""

    def __init__(self, log_file: Optional[str] = None):
        """初始化警报系统

        Args:
            log_file: 日志文件路径
        """
        self.log_file = Path(log_file) if log_file else None
        self._handlers: Dict[AlertChannel, Callable] = {}
        self._alert_history: List[Alert] = []
        self._max_history = 1000

        # 注册默认处理器
        self._handlers[AlertChannel.LOG] = self._log_handler
        if self.log_file:
            self._handlers[AlertChannel.FILE] = self._file_handler

    def register_handler(self, channel: AlertChannel,
                         handler: Callable[[Alert], None]):
        """注册警报处理器

        Args:
            channel: 渠道
            handler: 处理函数
        """
        self._handlers[channel] = handler
        logger.info(f"Registered alert handler for channel: {channel}")

    def send_alert(self, alert: Alert,
                   channels: Optional[List[AlertChannel]] = None):
        """发送警报

        Args:
            alert: 警报事件
            channels: 发送渠道列表 (默认所有)
        """
        # 记录历史
        self._alert_history.append(alert)
        if len(self._alert_history) > self._max_history:
            self._alert_history.pop(0)

        # 确定渠道
        if channels is None:
            channels = list(self._handlers.keys())

        # 发送到各渠道
        for channel in channels:
            handler = self._handlers.get(channel)
            if handler:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler error ({channel}): {e}")

    def _log_handler(self, alert: Alert):
        """日志处理器"""
        level_map = {
            "info": logging.INFO,
            "warning": logging.WARNING,
            "critical": logging.CRITICAL,
        }
        level = level_map.get(alert.level, logging.WARNING)
        logger.log(level, f"[{alert.level.upper()}] {alert.message}")

    def _file_handler(self, alert: Alert):
        """文件处理器"""
        if not self.log_file:
            return

        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{alert.to_json()}\n")

    def webhook_handler(self, webhook_url: str):
        """创建webhook处理器

        Args:
            webhook_url: Webhook URL

        Returns:
            处理函数
        """
        def handler(alert: Alert):
            try:
                import urllib.request
                import ssl

                data = alert.to_json().encode('utf-8')
                req = urllib.request.Request(
                    webhook_url,
                    data=data,
                    headers={'Content-Type': 'application/json'}
                )

                context = ssl.create_default_context()
                with urllib.request.urlopen(req, context=context, timeout=5) as response:
                    if response.status != 200:
                        logger.warning(f"Webhook returned {response.status}")

            except Exception as e:
                logger.error(f"Webhook error: {e}")

        return handler

    def email_handler(self, smtp_server: str, smtp_port: int,
                      sender: str, password: str,
                      recipients: List[str]):
        """创建邮件处理器

        Args:
            smtp_server: SMTP服务器
            smtp_port: SMTP端口
            sender: 发件人
            password: 密码
            recipients: 收件人列表

        Returns:
            处理函数
        """
        def handler(alert: Alert):
            try:
                subject = f"[MSRA Alert] {alert.level.upper()}: {alert.rule_name}"
                body = f"""
Alert Details:
- Rule: {alert.rule_name}
- Metric: {alert.metric}
- Value: {alert.value}
- Level: {alert.level}
- Message: {alert.message}
- Timestamp: {alert.timestamp}
- Context: {alert.context}
"""
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = sender
                msg['To'] = ', '.join(recipients)

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender, password)
                    server.sendmail(sender, recipients, msg.as_string())

                logger.info(f"Alert email sent to {recipients}")

            except Exception as e:
                logger.error(f"Email alert error: {e}")

        return handler

    def slack_handler(self, webhook_url: str):
        """创建Slack处理器

        Args:
            webhook_url: Slack webhook URL

        Returns:
            处理函数
        """
        def handler(alert: Alert):
            try:
                import urllib.request
                import ssl

                color_map = {
                    "info": "#36a64f",      # green
                    "warning": "#ffcc00",    # yellow
                    "critical": "#ff0000",   # red
                }

                payload = {
                    "attachments": [{
                        "color": color_map.get(alert.level, "#cccccc"),
                        "title": f"MSRA Alert: {alert.rule_name}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Metric", "value": alert.metric, "short": True},
                            {"title": "Value", "value": str(alert.value), "short": True},
                            {"title": "Level", "value": alert.level, "short": True},
                        ],
                        "ts": int(alert.timestamp)
                    }]
                }

                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    webhook_url,
                    data=data,
                    headers={'Content-Type': 'application/json'}
                )

                context = ssl.create_default_context()
                with urllib.request.urlopen(req, context=context, timeout=5):
                    pass

            except Exception as e:
                logger.error(f"Slack alert error: {e}")

        return handler

    def get_history(self, level: Optional[str] = None,
                    limit: int = 100) -> List[Alert]:
        """获取警报历史

        Args:
            level: 警报级别筛选
            limit: 返回数量

        Returns:
            警报列表
        """
        if level:
            filtered = [a for a in self._alert_history if a.level == level]
        else:
            filtered = self._alert_history.copy()

        return filtered[-limit:]

    def get_statistics(self) -> Dict:
        """获取警报统计"""
        total = len(self._alert_history)
        by_level = {}
        by_rule = {}

        for alert in self._alert_history:
            by_level[alert.level] = by_level.get(alert.level, 0) + 1
            by_rule[alert.rule_name] = by_rule.get(alert.rule_name, 0) + 1

        return {
            "total_alerts": total,
            "by_level": by_level,
            "by_rule": by_rule,
        }
