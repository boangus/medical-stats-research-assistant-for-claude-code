"""
Vital Signs Simulator - 生命体征数据模拟器

RT-003: 数据源模拟器
"""

import numpy as np
import time
import json
from typing import Optional, Dict, Callable, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class VitalSigns:
    """生命体征数据"""
    timestamp: float
    heart_rate: float
    systolic_bp: float
    diastolic_bp: float
    spo2: float
    temperature: float
    respiratory_rate: float

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class VitalSignsSimulator:
    """生命体征模拟器"""

    def __init__(self,
                 baseline_hr: float = 75,
                 baseline_sbp: float = 120,
                 baseline_dbp: float = 80,
                 baseline_spo2: float = 98,
                 baseline_temp: float = 37.0,
                 baseline_rr: float = 16):
        """初始化模拟器

        Args:
            baseline_hr: 基线心率
            baseline_sbp: 基线收缩压
            baseline_dbp: 基线舒张压
            baseline_spo2: 基线血氧
            baseline_temp: 基线体温
            baseline_rr: 基线呼吸率
        """
        self.baselines = {
            "heart_rate": baseline_hr,
            "systolic_bp": baseline_sbp,
            "diastolic_bp": baseline_dbp,
            "spo2": baseline_spo2,
            "temperature": baseline_temp,
            "respiratory_rate": baseline_rr,
        }

        self.noise_levels = {
            "heart_rate": 3.0,
            "systolic_bp": 5.0,
            "diastolic_bp": 3.0,
            "spo2": 0.5,
            "temperature": 0.1,
            "respiratory_rate": 1.0,
        }

        self._anomaly_active = False
        self._anomaly_type = None
        self._anomaly_start = None
        self._anomaly_duration = 0

    def generate_sample(self, timestamp: Optional[float] = None) -> VitalSigns:
        """生成单个样本

        Args:
            timestamp: 时间戳

        Returns:
            生命体征数据
        """
        if timestamp is None:
            timestamp = time.time()

        values = {}

        for metric, baseline in self.baselines.items():
            noise = np.random.normal(0, self.noise_levels[metric])

            # 应用异常
            if self._anomaly_active:
                values[metric] = self._apply_anomaly(metric, baseline, noise)
            else:
                values[metric] = baseline + noise

            # 确保在合理范围内
            values[metric] = self._clamp(metric, values[metric])

        return VitalSigns(
            timestamp=timestamp,
            heart_rate=values["heart_rate"],
            systolic_bp=values["systolic_bp"],
            diastolic_bp=values["diastolic_bp"],
            spo2=values["spo2"],
            temperature=values["temperature"],
            respiratory_rate=values["respiratory_rate"]
        )

    def _apply_anomaly(self, metric: str, baseline: float, noise: float) -> float:
        """应用异常

        Args:
            metric: 指标名
            baseline: 基线值
            noise: 噪声

        Returns:
            异常值
        """
        if self._anomaly_type == "tachycardia" and metric == "heart_rate":
            return 160 + noise
        elif self._anomaly_type == "bradycardia" and metric == "heart_rate":
            return 35 + noise
        elif self._anomaly_type == "hypoxemia" and metric == "spo2":
            return 85 + noise
        elif self._anomaly_type == "hypertension" and metric == "systolic_bp":
            return 190 + noise
        elif self._anomaly_type == "hypotension" and metric == "systolic_bp":
            return 80 + noise
        elif self._anomaly_type == "hyperthermia" and metric == "temperature":
            return 39.5 + noise
        else:
            return baseline + noise

    def _clamp(self, metric: str, value: float) -> float:
        """限制值在合理范围

        Args:
            metric: 指标名
            value: 值

        Returns:
            限制后的值
        """
        ranges = {
            "heart_rate": (20, 250),
            "systolic_bp": (50, 250),
            "diastolic_bp": (30, 150),
            "spo2": (70, 100),
            "temperature": (30, 42),
            "respiratory_rate": (5, 40),
        }

        if metric in ranges:
            low, high = ranges[metric]
            return max(low, min(high, value))
        return value

    def trigger_anomaly(self, anomaly_type: str, duration: int = 60):
        """触发异常

        Args:
            anomaly_type: 异常类型
            duration: 持续时间 (秒)
        """
        self._anomaly_active = True
        self._anomaly_type = anomaly_type
        self._anomaly_start = time.time()
        self._anomaly_duration = duration
        logger.info(f"Triggered anomaly: {anomaly_type} for {duration}s")

    def stop_anomaly(self):
        """停止异常"""
        self._anomaly_active = False
        self._anomaly_type = None
        logger.info("Anomaly stopped")

    def generate_stream(self, duration: int = 3600,
                       interval: float = 1.0,
                       callback: Optional[Callable[[VitalSigns], None]] = None
                       ) -> List[VitalSigns]:
        """生成数据流

        Args:
            duration: 持续时间 (秒)
            interval: 采样间隔 (秒)
            callback: 回调函数

        Returns:
            生命体征列表
        """
        samples = []
        n_samples = int(duration / interval)

        for i in range(n_samples):
            timestamp = time.time() + i * interval
            sample = self.generate_sample(timestamp)
            samples.append(sample)

            if callback:
                callback(sample)

            # 检查异常是否应该停止
            if self._anomaly_active and self._anomaly_start:
                if time.time() - self._anomaly_start > self._anomaly_duration:
                    self.stop_anomaly()

            time.sleep(interval)

        return samples

    def generate_to_kafka(self, topic: str,
                          duration: int = 3600,
                          interval: float = 1.0,
                          kafka_servers: str = "localhost:9092"):
        """生成数据并发送到Kafka

        Args:
            topic: Kafka主题
            duration: 持续时间
            interval: 采样间隔
            kafka_servers: Kafka服务器
        """
        try:
            from kafka import KafkaProducer
            import json

            producer = KafkaProducer(
                bootstrap_servers=kafka_servers,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )

            logger.info(f"Starting Kafka stream to topic: {topic}")

            n_samples = int(duration / interval)
            for i in range(n_samples):
                sample = self.generate_sample()
                producer.send(topic, sample.to_dict())
                time.sleep(interval)

            producer.flush()
            producer.close()
            logger.info("Kafka stream complete")

        except ImportError:
            logger.warning(
                "kafka-python not installed. Install with: pip install kafka-python"
            )
        except Exception as e:
            logger.error(f"Kafka error: {e}")
