"""读取 TI IWR2243 Cascade 点云 MAT 文件。"""

from pathlib import Path

import numpy as np
from scipy.io import loadmat


def read_cascade_mat(mat_path: str | Path) -> np.ndarray:
    """读取 `Cascade.mat` 中的 `xyz_all`。

    `xyz_all` 通常按帧保存点云，每个点至少包含 x、y、z 和 SNR/强度字段。
    """
    mat_data = loadmat(Path(mat_path))
    xyz_all = np.squeeze(mat_data["xyz_all"])
    return xyz_all
