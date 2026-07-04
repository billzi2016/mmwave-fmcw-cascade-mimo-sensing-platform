"""从速度谱中选取高能量候选点。"""

import numpy as np


def cut_speed_fft(
    speed_antenna: np.ndarray,
    radar_matrix: np.ndarray,
    n_points: int,
    point_gap: int,
) -> np.ndarray:
    """为每个虚拟天线组选取速度谱中的高亮点索引。

    输出数组中偶数行保存 range bin，奇数行保存 doppler bin。后续 AOV
    计算会根据这些候选点去角度谱中查找方位/俯仰峰值。
    """
    del point_gap

    speed_antenna_index = np.zeros(
        (radar_matrix.shape[0], speed_antenna.shape[-1] * 2, n_points),
        dtype=int,
    )

    abs_speed = np.abs(speed_antenna)

    for radar_index in range(radar_matrix.shape[0]):
        for rx in range(speed_antenna.shape[-1]):
            current_antenna_matrix = abs_speed[radar_index, :, :, rx]
            # argpartition 只取最大的 n_points 个位置，比完整排序更轻。
            flat_indices = np.argpartition(current_antenna_matrix.flatten(), -n_points)[-n_points:]
            row, col = np.unravel_index(flat_indices, current_antenna_matrix.shape)
            speed_antenna_index[radar_index, rx * 2, :] = row
            speed_antenna_index[radar_index, rx * 2 + 1, :] = col

    return speed_antenna_index
