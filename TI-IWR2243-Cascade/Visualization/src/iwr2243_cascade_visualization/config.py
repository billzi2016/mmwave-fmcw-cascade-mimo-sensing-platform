"""TI IWR2243 Cascade 点云可视化配置。

本文件只保存点云导出和渲染阶段需要的参数，例如每帧固定点数、
空间裁剪范围、并发进程数和是否合成视频。
"""

from dataclasses import dataclass
from multiprocessing import cpu_count


@dataclass(slots=True)
class CascadeVisualizationConfig:
    """级联雷达点云可视化配置。"""

    target_points: int = 2048
    xyz_limits: tuple[tuple[float, float], tuple[float, float], tuple[float, float]] = (
        (-1.5, 1.5),
        (0.0, 1.5),
        (-1.0, 1.0),
    )
    workers: int | None = None
    render_video: bool = False
    export_data_only: bool = False
    point_size: float = 5.0

    def resolve_workers(self) -> int:
        """确定绘图进程数。

        视频合成时使用单进程，避免逐帧图片写入顺序和 ffmpeg 输入顺序不一致。
        """
        if self.render_video:
            return 1
        if self.workers is not None and self.workers > 0:
            return self.workers
        return max(1, cpu_count() // 2)
