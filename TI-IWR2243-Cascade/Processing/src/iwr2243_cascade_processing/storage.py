from pathlib import Path

import h5py
import numpy as np


def save_speed_h5(
    output_path: Path,
    speed_frames: np.ndarray,
    range_bin_size_m: float,
    velocity_bin_size_m_per_s: float,
) -> None:
    """将 speed 热力图保存为 H5，并使用轻量压缩。"""
    with h5py.File(output_path, "w") as h5_file:
        h5_file.create_dataset(
            "speed_frames",
            data=speed_frames,
            compression="gzip",
            compression_opts=1,
        )
        h5_file.create_dataset(
            "meta",
            data=np.array([range_bin_size_m, velocity_bin_size_m_per_s], dtype=np.float32),
        )
