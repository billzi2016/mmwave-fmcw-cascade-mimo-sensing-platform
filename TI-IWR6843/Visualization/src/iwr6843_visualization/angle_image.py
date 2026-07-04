"""IWR6843 角度热力图导出。"""

from pathlib import Path

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

from .normalization import norm


def render_angle(
    angle_profiles: np.ndarray,
    start_bins: int,
    reasonable_bins: int,
    range_factor: float,
    antenna_array: int,
    output_dir: Path,
    stem: str,
    render_video: bool,
    export_assets_only: bool,
) -> None:
    """导出角度热力图。

    输出包括归一化 NPZ，以及静态 PNG 或逐帧 MP4。横轴为角度，纵轴为距离。
    """
    # 选择一个虚拟阵列组用于展示 AoA 角度响应。
    angle_profiles = angle_profiles[:, antenna_array, :, :]
    angle_shape = angle_profiles.shape
    # 每帧独立归一化，保证导出的资产数值范围一致。
    angle_profiles_01 = np.apply_along_axis(norm, axis=1, arr=angle_profiles.reshape(angle_shape[0], -1))
    angle_profiles_01 = angle_profiles_01.reshape(angle_shape)
    np.savez_compressed(output_dir / f"angle_heatmap_{stem}.npz", angle_profiles=angle_profiles_01)

    if export_assets_only:
        return

    fig, ax = plt.subplots(figsize=(12, 9))
    img = ax.imshow(
        angle_profiles[0, :, :],
        extent=(-90, 90, start_bins * range_factor, reasonable_bins * range_factor),
        origin="lower",
        aspect="auto",
        cmap="jet",
    )
    plt.colorbar(img, ax=ax)
    ax.set_title(f"Heatmap of Angle Profiles\n{stem}")
    ax.set_xlabel("Angle (degree)")
    ax.set_ylabel("Range (m)")

    def update(frame: int) -> None:
        """更新动画中的单帧角度热力图。"""
        img.set_array(angle_profiles[frame, :, :])
        ax.set_title(f"Heatmap of Angle Profiles, Frame: {frame}\n{stem}")
        fig.canvas.draw_idle()

    if render_video:
        animation = FuncAnimation(fig, update, frames=len(angle_profiles), interval=10, repeat=False)
        animation.save(
            output_dir / f"angle_heatmap_{stem}.mp4",
            writer="ffmpeg",
            fps=10,
            dpi=300,
            extra_args=["-vcodec", "h264_nvenc"],
        )
    else:
        update(0)
        plt.savefig(output_dir / f"angle_heatmap_{stem}.png", dpi=300)

    plt.close()
