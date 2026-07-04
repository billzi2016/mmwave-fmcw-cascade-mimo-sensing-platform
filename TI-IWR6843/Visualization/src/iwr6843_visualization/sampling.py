"""点云固定点数采样工具。"""

import numpy as np


def uniform_points(points: np.ndarray, target_count: int) -> np.ndarray:
    """将点云采样为固定点数。

    点数不足时随机重复补齐，点数过多时随机下采样，保证输出形状稳定。
    """
    current_count = len(points)
    if current_count == 0:
        return np.zeros((target_count, points.shape[1]), dtype=points.dtype)
    if current_count == target_count:
        return points
    if current_count < target_count:
        repeat_count = target_count - current_count
        # 缺口比当前点数还大时允许重复抽样，否则不放回即可补齐。
        replace = repeat_count > current_count
        extra_indices = np.random.choice(current_count, repeat_count, replace=replace)
        additional_points = points[extra_indices]
        return np.vstack([points, additional_points])

    indices = np.random.choice(current_count, target_count, replace=False)
    return points[indices]
