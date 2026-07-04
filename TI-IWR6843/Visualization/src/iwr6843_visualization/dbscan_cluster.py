"""使用 DBSCAN 对点云做离群点清理。"""

import numpy as np
from sklearn.cluster import DBSCAN

from .sampling import uniform_points


def build_cluster(points_frames: np.ndarray, target_count: int, single_process: bool) -> np.ndarray:
    """按原始逻辑做 DBSCAN 聚类后再重采样。

    每帧先在 xyz 空间中过滤掉 DBSCAN 标记为噪声的点，再调用
    `uniform_points` 采样到固定数量。
    """
    num_frames, _, num_dims = points_frames.shape
    target_points = np.zeros((num_frames, target_count, num_dims))

    for frame in range(num_frames):
        frame_data = points_frames[frame, :, :3]
        # n_jobs 在外层已经并行时设为 1，避免嵌套并行占满 CPU。
        dbscan_cluster = DBSCAN(
            eps=0.5,
            min_samples=max(1, int(len(frame_data) * 0.01)),
            n_jobs=-1 if single_process else 1,
        )
        labels = dbscan_cluster.fit_predict(frame_data)
        valid_points = points_frames[frame, labels != -1, :]
        target_points[frame, :, :] = uniform_points(valid_points, target_count)

    return target_points
