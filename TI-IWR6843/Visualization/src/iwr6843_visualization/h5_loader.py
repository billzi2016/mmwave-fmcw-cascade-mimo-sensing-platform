"""读取 IWR6843 Processing 阶段导出的 H5 文件。"""

from pathlib import Path

import h5py
import numpy as np


def load_h5(h5_path: str | Path, display: bool = False) -> list[np.ndarray | int | float]:
    """读取处理阶段导出的 H5 文件。

    返回 range、speed、angle、points 以及 param 中保存的物理换算参数。
    `speed_profiles` 兼容缺失情况，便于只导出 angle/point 的结果也能可视化。
    """
    with h5py.File(Path(h5_path), "r") as file:
        range_profiles = np.array(file["range_profiles"])
        speed_profiles = np.array(file["speed_profiles"]) if "speed_profiles" in file else None
        angle_profiles = np.array(file["angle_profiles"])
        points_frames = np.array(file["points_frames"])
        # param 顺序必须和 Processing 阶段 `_save_h5` 中写入顺序一致。
        start_bins, reasonable_bins, range_factor, periodicity, n_chirps, speed_factor = np.array(file["param"])

    start_bins = int(start_bins)
    reasonable_bins = int(reasonable_bins)
    n_chirps = int(n_chirps)

    if display:
        # 调试模式下打印关键数组形状和物理换算参数，方便检查处理输出是否完整。
        print()
        print(h5_path)
        print("=" * 30)
        print("range_profiles.shape =", range_profiles.shape)
        print("speed_profiles.shape =", None if speed_profiles is None else speed_profiles.shape)
        print("angle_profiles.shape =", angle_profiles.shape)
        print("points_frames.shape =", points_frames.shape)
        print()
        print("start_bins =", start_bins)
        print("reasonable_bins =", reasonable_bins)
        print()
        print("range_factor =", range_factor)
        print("periodicity =", periodicity)
        print("n_chirps =", n_chirps)
        print()
        print("speed_factor =", speed_factor)
        print("=" * 30)
        print()

    return [
        range_profiles,
        speed_profiles,
        angle_profiles,
        points_frames,
        start_bins,
        reasonable_bins,
        range_factor,
        periodicity,
        n_chirps,
        speed_factor,
    ]
