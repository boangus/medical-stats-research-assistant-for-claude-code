"""Generate mock NIfTI image and mask for medical imaging E2E tests.

Creates a 3D NIfTI image (64×64×32) with a simulated tumor region
and a corresponding binary mask.
Uses nibabel for NIfTI output; falls back to numpy arrays if nibabel unavailable.
All data uses seed=42 for reproducibility.
"""

from pathlib import Path

import numpy as np


def generate_mock_nifti(
    shape: tuple = (64, 64, 32),
    seed: int = 42,
    output_dir: str = None,
) -> tuple:
    """Generate a mock NIfTI image and mask.

    Args:
        shape: 3D shape of the image
        seed: Random seed for reproducibility
        output_dir: Optional directory to save NIfTI files

    Returns:
        tuple: (image_array, mask_array) as numpy arrays
    """
    np.random.seed(seed)

    # Create base image with brain-like intensity
    image = np.random.normal(loc=100, scale=20, size=shape).astype(np.float32)

    # Add a simulated tumor region (ellipsoid in the center)
    z, y, x = np.indices(shape)
    center = tuple(s // 2 for s in shape)
    # Ellipsoid radii
    rz, ry, rx = shape[0] // 6, shape[1] // 6, shape[2] // 4

    # Create ellipsoid mask
    ellipsoid = (
        ((z - center[0]) / rz) ** 2
        + ((y - center[1]) / ry) ** 2
        + ((x - center[2]) / rx) ** 2
    ) <= 1.0

    # Enhance intensity in tumor region
    image[ellipsoid] += 50

    # Create binary mask (tumor region)
    mask = ellipsoid.astype(np.float32)

    # Save as NIfTI if nibabel is available and output_dir is provided
    if output_dir:
        try:
            import nibabel as nib

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Create affine matrix (identity with 1mm voxel spacing)
            affine = np.eye(4)

            img_nii = nib.Nifti1Image(image, affine)
            mask_nii = nib.Nifti1Image(mask, affine)

            nib.save(img_nii, str(output_path / "mock_image.nii.gz"))
            nib.save(mask_nii, str(output_path / "mock_mask.nii.gz"))

        except ImportError:
            # nibabel not available, return numpy arrays only
            pass

    return image, mask


def generate_mock_image_array(
    shape: tuple = (64, 64, 32),
    seed: int = 42,
) -> np.ndarray:
    """Generate a mock 3D image array (numpy only, no NIfTI).

    Args:
        shape: 3D shape
        seed: Random seed

    Returns:
        np.ndarray: 3D image array
    """
    image, _ = generate_mock_nifti(shape=shape, seed=seed)
    return image


if __name__ == "__main__":
    image, mask = generate_mock_nifti(output_dir=".")
    print(f"Image shape: {image.shape}, dtype: {image.dtype}")
    print(f"Mask shape: {mask.shape}, dtype: {mask.dtype}")
    print(f"Mask nonzero voxels: {int(mask.sum())}")
