"""TI IWR6843 离线处理配置。

本文件集中保存单芯片雷达处理链路的静态参数，包括 FFT 点数、虚拟阵列
通道数量、点云候选数量、角度搜索范围、窗函数列表和并发设置。
"""

from dataclasses import dataclass, field
from multiprocessing import cpu_count


@dataclass(slots=True)
class ProcessingConfig:
    """IWR6843 处理阶段静态配置。"""

    n_tx: int = 3
    n_rx: int = 4
    range_fft_n: int = 1024
    speed_fft_n: int = 128
    angle_fft_n: int = 180
    speed_index: int = 64
    speed_cut: float = 0.4
    light_speed: float = 299792458.0
    bias_list: tuple[int, ...] = (0,)
    start_bin_ratio: float = 0.005
    reasonable_bin_ratio: float = 0.04
    n_points: int = 250
    point_gap: int = 0
    obj_h_up: float = 1.0
    obj_h_down: float = 1.0
    azimuth_angle: int = 60
    windows: tuple[str, ...] = field(default_factory=lambda: ("blackmanharris",))
    workers: int | None = None

    def resolve_workers(self) -> int:
        """确定实际使用的处理进程数。

        用户显式指定 workers 时优先使用该值；否则默认使用一半 CPU，避免离线处理占满机器。
        """
        if self.workers is not None and self.workers > 0:
            return self.workers
        return max(1, cpu_count() // 2)
