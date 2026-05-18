from dataclasses import dataclass
from multiprocessing import cpu_count


@dataclass(slots=True)
class CascadeVisualizationConfig:
    """点云可视化配置。"""

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
        if self.render_video:
            return 1
        if self.workers is not None and self.workers > 0:
            return self.workers
        return max(1, cpu_count() // 2)
