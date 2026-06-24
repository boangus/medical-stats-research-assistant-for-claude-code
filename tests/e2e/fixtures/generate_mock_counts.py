"""Generate mock count matrix for bioinformatics E2E tests.

Creates a 50-sample × 2000-gene count matrix with two condition groups
(control and treatment) and injected differential expression.
All data uses seed=42 for reproducibility.
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_mock_counts(
    n_samples: int = 50,
    n_genes: int = 2000,
    seed: int = 42,
    output_path: str = None,
) -> pd.DataFrame:
    """Generate a mock count matrix with differential expression.

    Args:
        n_samples: Number of samples (cells or bulk samples)
        n_genes: Number of genes
        seed: Random seed for reproducibility
        output_path: Optional path to save CSV

    Returns:
        pd.DataFrame: count matrix (samples × genes)
    """
    np.random.seed(seed)

    # Split samples into control and treatment groups
    n_ctrl = n_samples // 2
    n_treat = n_samples - n_ctrl

    # Base expression: Poisson distribution
    base_counts = np.random.poisson(lam=10, size=(n_samples, n_genes)).astype(float)

    # Inject differential expression in first 100 genes
    n_de = 100
    log2fc = np.zeros(n_genes)
    log2fc[:n_de] = np.random.choice([2.0, -2.0, 1.5, -1.5], n_de)

    # Apply fold change to treatment group
    for j in range(n_de):
        if log2fc[j] > 0:
            base_counts[n_ctrl:, j] *= (2 ** log2fc[j])
        else:
            base_counts[:n_ctrl, j] *= (2 ** abs(log2fc[j]))

    # Add some noise
    base_counts += np.random.normal(0, 1, base_counts.shape)

    # Ensure non-negative
    base_counts = np.maximum(base_counts, 0)

    # Create sample and gene names
    sample_names = [f"S{i:04d}" for i in range(n_samples)]
    gene_names = [f"GENE{i:04d}" for i in range(n_genes)]

    df = pd.DataFrame(base_counts, index=sample_names, columns=gene_names)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path)

    return df


def generate_sample_info(
    n_samples: int = 50,
    seed: int = 42,
    output_path: str = None,
) -> pd.DataFrame:
    """Generate sample information with condition labels.

    Args:
        n_samples: Number of samples
        seed: Random seed
        output_path: Optional path to save CSV

    Returns:
        pd.DataFrame: sample info with 'condition' column
    """
    np.random.seed(seed)
    n_ctrl = n_samples // 2
    conditions = ["control"] * n_ctrl + ["treatment"] * (n_samples - n_ctrl)
    batches = [f"batch_{i % 3}" for i in range(n_samples)]

    df = pd.DataFrame({
        "condition": conditions,
        "batch": batches,
    }, index=[f"S{i:04d}" for i in range(n_samples)])

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path)

    return df


if __name__ == "__main__":
    counts = generate_mock_counts(output_path="mock_counts.csv")
    sample_info = generate_sample_info(output_path="mock_sample_info.csv")
    print(f"Generated count matrix: {counts.shape}")
    print(f"Generated sample info: {sample_info.shape}")
