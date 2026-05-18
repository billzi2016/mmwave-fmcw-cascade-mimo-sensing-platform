from pathlib import Path

import numpy as np
from scipy.io import loadmat


def read_cascade_mat(mat_path: str | Path) -> np.ndarray:
    """读取 Cascade.mat 中的 xyz_all。"""
    mat_data = loadmat(Path(mat_path))
    xyz_all = np.squeeze(mat_data["xyz_all"])
    return xyz_all
