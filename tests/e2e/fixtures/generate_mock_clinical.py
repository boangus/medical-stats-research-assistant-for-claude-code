"""Generate mock clinical data for E2E tests.

Creates a clinical data DataFrame with patient demographics and lab values.
All data uses seed=42 for reproducibility.
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_mock_clinical(
    n_samples: int = 50,
    seed: int = 42,
    output_path: str = None,
) -> pd.DataFrame:
    """Generate mock clinical data.

    Args:
        n_samples: Number of patient samples
        seed: Random seed
        output_path: Optional path to save CSV

    Returns:
        pd.DataFrame: clinical data (n_samples × variables)
    """
    np.random.seed(seed)

    data = {
        "age": np.random.randint(30, 80, n_samples),
        "sex": np.random.choice(["M", "F"], n_samples),
        "bmi": np.random.normal(25, 4, n_samples),
        "glucose": np.random.normal(100, 20, n_samples),
        "cholesterol": np.random.normal(180, 30, n_samples),
        "hemoglobin": np.random.normal(13.5, 1.5, n_samples),
        "creatinine": np.random.normal(1.0, 0.3, n_samples),
        "wbc": np.random.normal(7.0, 2.0, n_samples),
        "platelet": np.random.normal(250, 50, n_samples),
        "tumor_stage": np.random.choice(["I", "II", "III", "IV"], n_samples),
    }

    index = [f"S{i:04d}" for i in range(n_samples)]
    df = pd.DataFrame(data, index=index)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path)

    return df


if __name__ == "__main__":
    clinical = generate_mock_clinical(output_path="mock_clinical.csv")
    print(f"Generated clinical data: {clinical.shape}")
