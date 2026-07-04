"""级联雷达处理结果的结构化保存工具。"""

from pathlib import Path

import h5py
import numpy as np


def save_speed_h5(
    output_path: Path,
    speed_frames: np.ndarray,
    range_bin_size_m: float,
    velocity_bin_size_m_per_s: float,
) -> None:
    """将速度热力图序列保存为 H5。

    `speed_frames` 是按帧堆叠的二维速度热力图；`meta` 中保存距离 bin 和
    速度 bin 的物理尺度，方便后续可视化或分析时恢复坐标轴。
    """
    with h5py.File(output_path, "w") as h5_file:
        # gzip level 1 是轻量压缩，主要降低文件体积，同时避免明显拖慢写入。
        h5_file.create_dataset(
            "speed_frames",
            data=speed_frames,
            compression="gzip",
            compression_opts=1,
        )
        # meta 顺序固定为：距离 bin 大小、速度 bin 大小。
        h5_file.create_dataset(
            "meta",
            data=np.array([range_bin_size_m, velocity_bin_size_m_per_s], dtype=np.float32),
        )
