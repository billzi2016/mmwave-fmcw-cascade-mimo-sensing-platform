from pathlib import Path
import subprocess

import matplotlib.pyplot as plt
import numpy as np

from .config import CascadeProcessingConfig


def save_speed_image(image: np.ndarray, frame_index: int, output_dir: Path, config: CascadeProcessingConfig) -> None:
    """保存单帧 speed 热力图。"""
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
    """保存单帧 angle 热力图。"""
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
    """使用 ffmpeg 将逐帧图片合成为视频。"""
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
