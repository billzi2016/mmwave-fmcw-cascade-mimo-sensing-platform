"""读取 TI IWR6843 原始 BIN 采样文件。"""

from pathlib import Path

import numpy as np


def read_bin(bin_path: str | Path) -> np.ndarray:
    """读取原始雷达二进制采样数据。

    返回一维 int16 数组；后续 `frame_extractor` 会根据 LVDS/IQ 交织规则
    把它恢复为复数虚拟天线数据。
    """
    with Path(bin_path).open("rb") as file:
        return np.fromfile(file, dtype=np.int16)
