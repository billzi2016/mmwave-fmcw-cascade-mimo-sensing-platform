from pathlib import Path
import subprocess

import matplotlib.pyplot as plt
import numpy as np

from .point_cloud_processing import log_snr


def save_point_cloud_image(
    point_cloud: np.ndarray,
    frame_index: int,
    output_dir: Path,
    data_range: tuple[float, float, float, float, float, float, float, float],
    point_size: float,
) -> None:
    """保存单帧点云图片。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    x_min, x_max, y_min, y_max, z_min, z_max, snr_min, snr_max = data_range

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    x = point_cloud[:, 0]
    y = point_cloud[:, 1]
    z = point_cloud[:, 2]
    snr = log_snr(point_cloud[:, 3])

    scatter = ax.scatter(x, y, z, c=snr, cmap="viridis", s=point_size, vmin=snr_min, vmax=snr_max)
    fig.colorbar(scatter)

    ax.set_xlim([x_min, x_max])
    ax.set_ylim([y_min, y_max])
    ax.set_zlim([z_min, z_max])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(f"Cascade 2243 Point Cloud, Frame = {frame_index}")

    plt.savefig(output_dir / f"{frame_index:06d}.png", dpi=200)
    plt.close()


def compute_point_cloud_range(point_cloud_frames: np.ndarray) -> tuple[float, float, float, float, float, float, float, float]:
    """计算整段点云的统一显示范围。"""
    x_min, x_max = np.min(point_cloud_frames[..., 0]), np.max(point_cloud_frames[..., 0])
    y_min, y_max = np.min(point_cloud_frames[..., 1]), np.max(point_cloud_frames[..., 1])
    z_min, z_max = np.min(point_cloud_frames[..., 2]), np.max(point_cloud_frames[..., 2])
    snr_min = np.min(log_snr(point_cloud_frames[..., 3]))
    snr_max = np.max(log_snr(point_cloud_frames[..., 3]))
    return x_min, x_max, y_min, y_max, z_min, z_max, snr_min, snr_max


def render_video_from_frames(frame_dir: Path, output_path: Path, frame_rate: int = 10) -> None:
    """使用 ffmpeg 将点云图片合成为视频。"""
    command = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(frame_rate),
        "-i",
        str(frame_dir / "%06d.png"),
        "-c:v",
        "h264_nvenc",
        "-r",
        str(frame_rate),
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
