import numpy as np
from tqdm import tqdm

from .point_cloud_processing import normalize_points, subspace


def build_point_cloud_frames(
    xyz_all: np.ndarray,
    target_points: int,
    xyz_limits: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
) -> np.ndarray:
    """从 xyz_all 提取固定点数点云序列。"""
    point_cloud_frames = np.zeros((len(xyz_all), target_points, 4), dtype=np.float32)

    for frame_index in tqdm(range(len(xyz_all)), desc="xyz_all", ncols=100):
        frame_points = np.asarray(xyz_all[frame_index], dtype=np.float32)
        frame_points = subspace(frame_points, xyz_limits)
        point_cloud_frames[frame_index] = normalize_points(frame_points, target_points)

    return point_cloud_frames
