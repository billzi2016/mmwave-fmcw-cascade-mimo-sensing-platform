"""TI IWR2243 Cascade 处理结果渲染工具。

本模块只负责把已经生成的 speed/angle 热力图保存为图片，或调用
ffmpeg 把逐帧图片合成为视频；不参与雷达信号处理本身。
"""

from pathlib import Path
import subprocess

import matplotlib.pyplot as plt
import numpy as np

from .config import CascadeProcessingConfig


def save_speed_image(image: np.ndarray, frame_index: int, output_dir: Path, config: CascadeProcessingConfig) -> None:
    """保存单帧速度热力图。

    横轴是速度，纵轴是距离；坐标轴尺度由配置中的 bin size 派生。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 8), dpi=200)
    plt.imshow(
        image,
        extent=(
            -config.doppler_fft_size // 2 * config.velocity_bin_size_m_per_s,
            config.doppler_fft_size // 2 * config.velocity_bin_size_m_per_s,
            0,
            image.shape[0] * config.range_bin_size_m,
        ),
        cmap="viridis",
        aspect="auto",
        origin="lower",
    )
    plt.colorbar()
    plt.xlabel("Speed (m/s)")
    plt.ylabel("Range (m)")
    plt.title(f"Speed Heatmap, Frame = {frame_index}")
    plt.tight_layout()
    plt.savefig(output_dir / f"{frame_index:06d}.png", dpi=200)
    plt.close()


def save_angle_image(image: np.ndarray, frame_index: int, output_dir: Path, config: CascadeProcessingConfig) -> None:
    """保存单帧角度热力图。

    横轴固定为 -90 到 90 度，纵轴为距离，用于观察目标在角度域的分布。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 8), dpi=200)
    plt.imshow(
        image,
        extent=(-90, 90, 0, image.shape[0] * config.range_bin_size_m),
        cmap="viridis",
        aspect="auto",
        origin="lower",
    )
    plt.colorbar()
    plt.xlabel("Angle (degree)")
    plt.ylabel("Range (m)")
    plt.title(f"Angle Heatmap, Frame = {frame_index}")
    plt.tight_layout()
    plt.savefig(output_dir / f"{frame_index:06d}.png", dpi=200)
    plt.close()


def render_video_from_frames(frame_dir: Path, output_path: Path, frame_rate: int = 10) -> None:
    """使用 ffmpeg 将逐帧图片合成为视频。

    输入帧按 `%06d.png` 命名；函数只负责调用外部 ffmpeg，不检查编码器是否可用。
    """
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
