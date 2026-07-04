"""TI IWR6843 可视化阶段配置。

本文件保存热力图、点云和视频导出相关参数，避免可视化流水线中散落
显示阈值、采样点数、帧合并数量等硬编码常量。
"""

from dataclasses import dataclass
from multiprocessing import cpu_count


@dataclass(slots=True)
class VisualizationConfig:
    """IWR6843 可视化阶段配置。"""

    speed_cut: float = 0.4
    merge_frames: int = 3
    threshold_percentile: float = 60.0
    target_count: int = 2048
    workers: int | None = None
    render_video: bool = False
    export_assets_only: bool = False
    point_alpha: float = 0.5
    point_size: float = 5.0

    def resolve_workers(self) -> int:
        """确定实际使用的可视化进程数。

        视频渲染时固定为单进程，普通图片/数据导出默认使用一半 CPU。
        """
        if self.render_video:
            return 1
        if self.workers is not None and self.workers > 0:
            return self.workers
        return max(1, cpu_count() // 2)
