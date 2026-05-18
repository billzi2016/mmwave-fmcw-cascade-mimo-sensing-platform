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
    """导出速度热力图。"""
    speed_profiles[:, :, :, antenna] = np.sum(speed_profiles, axis=-1)

    speed_fft_n = speed_profiles.shape[2]
    start_speed = int(speed_fft_n // 2 * (1 - speed_cut))
    end_speed = int(speed_fft_n // 2 * (1 + speed_cut))
    speed_profiles = speed_profiles[:, :, start_speed : end_speed + 1, antenna]

    speed_shape = speed_profiles.shape
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
