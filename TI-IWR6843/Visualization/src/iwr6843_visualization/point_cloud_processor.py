"""IWR6843 点云可视化前的数据整理工具。"""

import numpy as np


def merge_frame(points_frames: np.ndarray, frames: int) -> np.ndarray:
    """将连续多帧点云合并为一个时间窗口。

    合并后每帧包含更多点，轨迹显示更连续；代价是时间分辨率会降低。
    """
    num_frames, num_points_per_frame, num_dims = points_frames.shape
    new_frames = num_frames // frames
    merged_frames = np.zeros((new_frames, num_points_per_frame * frames, num_dims))

    for frame in range(new_frames):
        # 连续 frames 帧直接拉平成一个点集。
        merged_frames[frame, :, :] = points_frames[frame * frames : (frame + 1) * frames, :, :].reshape(-1, num_dims)

    return merged_frames


def threshold_segment(points_frames: np.ndarray, percentile: float) -> np.ndarray:
    """按强度百分位筛选点云。

    第 4 列被视为强度/SNR，只保留高于指定百分位的点，减少低强度噪声。
    """
    num_frames, num_points_per_frame, num_dims = points_frames.shape
    keep_count = int(num_points_per_frame * (1 - percentile / 100))
    segmented_frames = np.zeros((num_frames, keep_count, num_dims))

    for frame in range(num_frames):
        amplify = points_frames[frame, :, 3]
        threshold = np.percentile(amplify, percentile)
        mask = amplify >= threshold
        segmented_frames[frame, :, :] = points_frames[frame, mask, :][:keep_count, :]

    return segmented_frames
