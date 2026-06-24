"""Generate mock vital signs time series for realtime analytics E2E tests.

Creates 60-120 seconds of simulated vital signs data (heart rate,
blood pressure, SpO2, temperature, respiratory rate).
All data uses seed=42 for reproducibility.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_mock_vitals(
    duration: int = 60,
    interval: float = 1.0,
    seed: int = 42,
    inject_anomaly: bool = False,
    output_path: str = None,
) -> dict:
    """Generate mock vital signs time series.

    Args:
        duration: Duration in seconds
        interval: Sampling interval in seconds
        seed: Random seed
        inject_anomaly: If True, inject anomalous values
        output_path: Optional path to save CSV

    Returns:
        dict: {metric_name: [values]} for each vital sign
    """
    np.random.seed(seed)
    n_points = int(duration / interval)

    # Normal ranges
    heart_rate = np.random.normal(75, 8, n_points)
    systolic_bp = np.random.normal(120, 10, n_points)
    diastolic_bp = np.random.normal(80, 8, n_points)
    spo2 = np.random.normal(97, 2, n_points)
    temperature = np.random.normal(36.8, 0.3, n_points)
    respiratory_rate = np.random.normal(16, 2, n_points)

    # Clip to physiological ranges
    heart_rate = np.clip(heart_rate, 40, 180)
    systolic_bp = np.clip(systolic_bp, 70, 200)
    diastolic_bp = np.clip(diastolic_bp, 40, 120)
    spo2 = np.clip(spo2, 80, 100)
    temperature = np.clip(temperature, 35, 41)
    respiratory_rate = np.clip(respiratory_rate, 8, 35)

    if inject_anomaly:
        # Inject anomalies in the second half
        start_idx = n_points // 2
        # Tachycardia (high heart rate)
        heart_rate[start_idx:start_idx + 10] = np.random.uniform(140, 170, 10)
        # Hypertension
        systolic_bp[start_idx + 5:start_idx + 15] = np.random.uniform(170, 195, 10)
        # Desaturation
        spo2[start_idx + 10:start_idx + 20] = np.random.uniform(82, 88, 10)

    vitals = {
        "heart_rate": heart_rate.tolist(),
        "systolic_bp": systolic_bp.tolist(),
        "diastolic_bp": diastolic_bp.tolist(),
        "spo2": spo2.tolist(),
        "temperature": temperature.tolist(),
        "respiratory_rate": respiratory_rate.tolist(),
    }

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(vitals)
        df.to_csv(output_path, index=False)

    return vitals


def generate_mock_vitals_dataframe(
    duration: int = 60,
    interval: float = 1.0,
    seed: int = 42,
    inject_anomaly: bool = False,
) -> pd.DataFrame:
    """Generate mock vital signs as a DataFrame.

    Args:
        duration: Duration in seconds
        interval: Sampling interval
        seed: Random seed
        inject_anomaly: If True, inject anomalous values

    Returns:
        pd.DataFrame: vital signs time series
    """
    vitals = generate_mock_vitals(
        duration=duration,
        interval=interval,
        seed=seed,
        inject_anomaly=inject_anomaly,
    )
    return pd.DataFrame(vitals)


if __name__ == "__main__":
    vitals = generate_mock_vitals(duration=60, output_path="mock_vitals.csv")
    print(f"Generated vitals: {len(vitals)} metrics, {len(vitals['heart_rate'])} points each")

    vitals_anomaly = generate_mock_vitals(duration=120, inject_anomaly=True)
    print(f"Generated anomalous vitals: {len(vitals_anomaly)} metrics")
