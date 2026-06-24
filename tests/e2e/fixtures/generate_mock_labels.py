"""Generate mock binary labels for E2E tests.

Creates binary classification labels (0/1) for prediction model training.
All data uses seed=42 for reproducibility.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_mock_labels(
    n_samples: int = 50,
    seed: int = 42,
    output_path: str = None,
) -> np.ndarray:
    """Generate mock binary labels (0/1).

    Args:
        n_samples: Number of samples
        seed: Random seed
        output_path: Optional path to save CSV

    Returns:
        np.ndarray: binary labels (0/1)
    """
    np.random.seed(seed)

    # Create roughly balanced labels
    n_pos = n_samples // 2
    labels = np.array([1] * n_pos + [0] * (n_samples - n_pos))
    np.random.shuffle(labels)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        pd.Series(labels, name="label").to_csv(output_path, index=False)

    return labels


def generate_mock_labels_from_vitals(
    n_samples: int = 20,
    seed: int = 42,
) -> np.ndarray:
    """Generate labels for time-series based prediction.

    Creates labels that correlate with the presence of anomalies
    in vital signs data.

    Args:
        n_samples: Number of time windows
        seed: Random seed

    Returns:
        np.ndarray: binary labels
    """
    np.random.seed(seed)
    # Roughly 30% positive (anomaly) samples
    labels = np.zeros(n_samples, dtype=int)
    n_pos = max(3, n_samples // 3)
    pos_indices = np.random.choice(n_samples, n_pos, replace=False)
    labels[pos_indices] = 1
    return labels


if __name__ == "__main__":
    labels = generate_mock_labels(output_path="mock_labels.csv")
    print(f"Generated labels: {len(labels)} samples, {labels.sum()} positive")
