"""级联雷达点云的裁剪、采样和离群点清理。"""

from collections import Counter

import numpy as np
from sklearn.cluster import DBSCAN


def log_snr(snr: np.ndarray) -> np.ndarray:
    """对 SNR 做对数压缩并保证非负。

    点云强度动态范围通常很大，取 log10 后更适合作为采样权重和颜色值。
    """
    snr = np.asarray(snr, dtype=np.float32)
    snr = np.clip(snr, 1e-6, None)
    return np.log10(snr)


def subspace(points: np.ndarray, xyz_limits: tuple[tuple[float, float], tuple[float, float], tuple[float, float]]) -> np.ndarray:
    """裁剪感兴趣点云子空间。

    `xyz_limits` 分别对应 x、y、z 三个轴的最小/最大范围。
    """
    x_range, y_range, z_range = xyz_limits
    mask = (
        (points[:, 0] >= x_range[0]) & (points[:, 0] <= x_range[1]) &
        (points[:, 1] >= y_range[0]) & (points[:, 1] <= y_range[1]) &
        (points[:, 2] >= z_range[0]) & (points[:, 2] <= z_range[1])
    )
    return points[mask]


def weighted_resample(points: np.ndarray, target_points: int) -> np.ndarray:
    """按 SNR 权重重采样到固定点数。

    强回波点被选中的概率更高；使用带放回采样可以在原始点数不足时补齐。
    """
    if len(points) == 0:
        return np.zeros((target_points, 4), dtype=np.float32)
    if len(points) == target_points:
        return points

    weights = log_snr(points[:, 3])
    # 平移到正数区间，避免概率中出现 0 或负值。
    weights = weights - np.min(weights) + 1e-6
    probabilities = weights / np.sum(weights)
    chosen_indices = np.random.choice(len(points), size=target_points, replace=True, p=probabilities)
    return points[chosen_indices]


def dbscan_filter(points: np.ndarray, target_points: int) -> np.ndarray:
    """保留最大簇，尽量移除离群点。

    如果 DBSCAN 没有找到有效簇，则保留原始点云，避免整帧被清空。
    """
    if len(points) == 0:
        return np.zeros((target_points, 4), dtype=np.float32)

    xyz = points[:, :3]
    # min_samples 随目标点数变化，避免点数很小时聚类阈值过高。
    dbscan = DBSCAN(eps=0.5, min_samples=max(1, int(target_points * 0.1)), n_jobs=-1)
    labels = dbscan.fit_predict(xyz)

    try:
        cluster_counts = Counter(labels[labels != -1])
        max_cluster_label = max(cluster_counts, key=cluster_counts.get)
        return points[labels == max_cluster_label]
    except ValueError:
        return points


def normalize_points(points: np.ndarray, target_points: int) -> np.ndarray:
    """执行两轮采样与一轮聚类清理。

    第一轮把输入统一到目标点数，DBSCAN 去掉明显离群点，第二轮再补齐固定形状。
    """
    points = weighted_resample(points, target_points)
    points = dbscan_filter(points, target_points)
    points = weighted_resample(points, target_points)
    return points.astype(np.float32)
