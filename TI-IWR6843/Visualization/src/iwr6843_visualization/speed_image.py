"""IWR6843 速度热力图导出。"""

from pathlib import Path

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

from .normalization import norm


def render_speed(
    speed_profiles: np.ndarray,
    start_bins: int,
    reasonable_bins: int,
    range_factor: float,
    speed_factor: float,
    speed_cut: float,
    antenna: int,
    output_dir: Path,
    stem: str,
    render_video: bool,
    export_assets_only: bool,
) -> None:
    """导出速度热力图。

    输出包括归一化 NPZ，以及静态 PNG 或逐帧 MP4。横轴为速度，纵轴为距离。
    """
    # 先把所有天线通道能量累加到指定 antenna 通道，得到单通道速度图。
    speed_profiles[:, :, :, antenna] = np.sum(speed_profiles, axis=-1)

    speed_fft_n = speed_profiles.shape[2]
    # 只保留零速度附近的一段速度范围，减少无关高速区域对显示的干扰。
    start_speed = int(speed_fft_n // 2 * (1 - speed_cut))
    end_speed = int(speed_fft_n // 2 * (1 + speed_cut))
    speed_profiles = speed_profiles[:, :, start_speed : end_speed + 1, antenna]

    speed_shape = speed_profiles.shape
    # 每帧独立归一化，方便保存为统一范围的图像资产。
    speed_profiles_01 = np.apply_along_axis(norm, axis=1, arr=speed_profiles.reshape(speed_shape[0], -1))
    speed_profiles_01 = speed_profiles_01.reshape(speed_shape)
    np.savez_compressed(output_dir / f"speed_heatmap_{stem}.npz", speed_profiles=speed_profiles_01)

    if export_assets_only:
        return

    fig, ax = plt.subplots(figsize=(12, 9))
    img = ax.imshow(
        speed_profiles[0, :, :],
        extent=(-speed_factor * speed_cut, speed_factor * speed_cut, start_bins * range_factor, reasonable_bins * range_factor),
        origin="lower",
        aspect="auto",
        cmap="jet",
    )
    plt.colorbar(img, ax=ax)
    ax.set_xlabel("Speed (m/s)")
    ax.set_ylabel("Range (m)")

    def update(frame: int) -> None:
        """更新动画中的单帧速度热力图。"""
        img.set_array(speed_profiles[frame, :, :])
        ax.set_title(f"Heatmap of Speed Profiles, Frame: {frame}\n{stem}")
        fig.canvas.draw_idle()

    if render_video:
        animation = FuncAnimation(fig, update, frames=len(speed_profiles), interval=10, repeat=False)
        animation.save(
            output_dir / f"speed_heatmap_{stem}.mp4",
            writer="ffmpeg",
            fps=10,
            dpi=300,
            extra_args=["-vcodec", "h264_nvenc"],
        )
    else:
        update(0)
        plt.savefig(output_dir / f"speed_heatmap_{stem}.png", dpi=300)

    plt.close()
