from pathlib import Path

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np


def render_point_cloud(
    data: np.ndarray,
    output_dir: Path,
    stem: str,
    render_video: bool,
    export_assets_only: bool,
    point_alpha: float,
    point_size: float,
) -> None:
    """导出点云静态图或视频。"""
    if export_assets_only:
        return

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")
    ax.view_init(elev=12, azim=-125)

    scatter = ax.scatter(
        [],
        [],
        [],
        c=[],
        cmap="bwr",
        alpha=point_alpha,
        s=point_size,
        vmin=np.min(data[:, :, 3]),
        vmax=np.max(data[:, :, 3]),
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_xlim([np.min(data[:, :, 0]), np.max(data[:, :, 0])])
    ax.set_ylim([np.min(data[:, :, 1]), np.max(data[:, :, 1])])
    ax.set_zlim([np.min(data[:, :, 2]), np.max(data[:, :, 2])])

    cbar = plt.colorbar(scatter, ax=ax, pad=0.1)
    cbar.set_label("Amplify")

    def update(frame: int) -> None:
        disp_index = data[frame, :, 3] != -1
        scatter._offsets3d = (
            data[frame, disp_index, 0],
            data[frame, disp_index, 1],
            data[frame, disp_index, 2],
        )
        scatter.set_array(data[frame, disp_index, 3])
        ax.set_title(f"Point Cloud, Frame: {frame}\n{stem}")
        ax.figure.canvas.draw()

    if render_video:
        animation = FuncAnimation(fig, update, frames=len(data), interval=10, repeat=False)
        animation.save(
            output_dir / f"point_cloud_{stem}.mp4",
            writer="ffmpeg",
            fps=5,
            dpi=300,
            extra_args=["-vcodec", "h264_nvenc"],
        )
    else:
        update(0)
        plt.savefig(output_dir / f"point_cloud_{stem}.png", dpi=300)

    plt.close()
