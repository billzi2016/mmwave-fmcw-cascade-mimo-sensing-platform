from pathlib import Path

import numpy as np


def read_bin(bin_path: str | Path) -> np.ndarray:
    """读取原始雷达二进制采样数据。"""
    with Path(bin_path).open("rb") as file:
        return np.fromfile(file, dtype=np.int16)
