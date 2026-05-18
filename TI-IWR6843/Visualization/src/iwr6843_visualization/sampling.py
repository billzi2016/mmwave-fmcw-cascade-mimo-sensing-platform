import numpy as np


def uniform_points(points: np.ndarray, target_count: int) -> np.ndarray:
    """将点云采样为固定点数。"""
    current_count = len(points)
    if current_count == 0:
        return np.zeros((target_count, points.shape[1]), dtype=points.dtype)
    if current_count == target_count:
        return points
    if current_count < target_count:
        repeat_count = target_count - current_count
        replace = repeat_count > current_count
        extra_indices = np.random.choice(current_count, repeat_count, replace=replace)
        additional_points = points[extra_indices]
        return np.vstack([points, additional_points])

    indices = np.random.choice(current_count, target_count, replace=False)
    return points[indices]
