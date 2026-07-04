"""TI IWR2243 Cascade 离线处理配置。

本文件集中保存四芯片级联雷达的采样参数、阵列映射、校准开关、
FFT 设置和输出控制。处理链路中的距离、速度和角度换算都依赖这里的
派生属性，因此配置集中放在这里，避免各个模块重复写硬编码常量。
"""

from dataclasses import dataclass, field
from multiprocessing import cpu_count

import numpy as np


# TX/RX 的方位向物理位置，用于把硬件通道组织为虚拟阵列。
TX_POSITIONS_AZI = (11, 10, 9, 32, 28, 24, 20, 16, 12, 8, 4, 0)
RX_POSITIONS_AZI = tuple(list(range(11, 15)) + list(range(50, 54)) + list(range(46, 50)) + list(range(0, 4)))

# 原始 RX 通道重排顺序，匹配级联 MIMO 阵列处理时需要的虚拟接收通道排列。
RX_FOR_MIMO = (13, 14, 15, 16, 1, 2, 3, 4, 9, 10, 11, 12, 5, 6, 7, 8)


@dataclass(slots=True)
class CascadeProcessingConfig:
    """四芯片级联雷达处理配置。

    字段分为几类：ADC/Chirp 采样参数、设备与通道数量、TX/RX 阵列映射、
    校准控制、FFT/显示设置，以及批处理输出控制。
    """

    num_adc_samples: int = 256
    adc_sample_rate: float = 8_000_000.0
    start_frequency_hz: float = 77_000_000_000.0
    chirp_slope_hz_per_s: float = 78_986_000_000_000.0
    chirp_idle_time_s: float = 5e-6
    adc_start_time_s: float = 6e-6
    chirp_ramp_end_time_s: float = 40e-6
    frame_periodicity_s: float = 0.08
    num_chirps_in_loop: int = 12
    nchirp_loops: int = 64
    num_devices: int = 4
    num_rx_per_device: int = 4
    tx_to_enable: tuple[int, ...] = (12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1)
    rx_for_mimo: tuple[int, ...] = RX_FOR_MIMO
    tx_positions_azi: tuple[int, ...] = TX_POSITIONS_AZI
    rx_positions_azi: tuple[int, ...] = RX_POSITIONS_AZI
    slope_calib: float = 78_986_000_000_000.0
    fs_calib: float = 8_000_000.0
    calibration_interp: int = 5
    phase_calibration_only: bool = True
    adc_calibration_on: bool = True
    range_window_enable: bool = True
    doppler_window_enable: bool = False
    clutter_remove: bool = False
    angle_fft_size: int = 180
    range_limit_m: float = 2.5
    workers: int | None = None
    frame_limit: int | None = None
    enable_speed_output: bool = True
    export_data_only: bool = False
    render_video: bool = False

    @property
    def num_tx(self) -> int:
        """实际启用的发射天线数量。"""
        return len(self.tx_to_enable)

    @property
    def num_rx(self) -> int:
        """四片设备拼接后的接收通道总数。"""
        return self.num_devices * self.num_rx_per_device

    @property
    def range_fft_size(self) -> int:
        """距离向 FFT 点数，取不小于 ADC 采样点数的 2 的幂。"""
        return int(2 ** np.ceil(np.log2(self.num_adc_samples)))

    @property
    def doppler_fft_size(self) -> int:
        """多普勒向 FFT 点数，取不小于 chirp loop 数的 2 的幂。"""
        return int(2 ** np.ceil(np.log2(self.nchirp_loops)))

    @property
    def num_chirps_per_frame(self) -> int:
        """单帧内的 chirp 总数。"""
        return self.nchirp_loops * self.num_chirps_in_loop

    @property
    def chirp_ramp_time_s(self) -> float:
        """ADC 采样窗口对应的 ramp 时间。"""
        return self.num_adc_samples / self.adc_sample_rate

    @property
    def chirp_interval_s(self) -> float:
        """相邻 chirp 之间的时间间隔。"""
        return self.chirp_ramp_end_time_s + self.chirp_idle_time_s

    @property
    def carrier_frequency_hz(self) -> float:
        """ADC 采样窗口中心时刻对应的载频。"""
        return self.start_frequency_hz + (
            self.adc_start_time_s + self.chirp_ramp_time_s / 2
        ) * self.chirp_slope_hz_per_s

    @property
    def wavelength_m(self) -> float:
        """当前载频对应的波长。"""
        return 3e8 / self.carrier_frequency_hz

    @property
    def chirp_bandwidth_hz(self) -> float:
        """单个 chirp 在 ADC 采样期间覆盖的带宽。"""
        return self.chirp_slope_hz_per_s * self.chirp_ramp_time_s

    @property
    def range_resolution_m(self) -> float:
        """理论距离分辨率。"""
        return 3e8 / (2 * self.chirp_bandwidth_hz)

    @property
    def range_bin_size_m(self) -> float:
        """距离 FFT 输出中每个 bin 对应的实际距离。"""
        return self.range_resolution_m * self.num_adc_samples / self.range_fft_size

    @property
    def velocity_resolution_m_per_s(self) -> float:
        """理论速度分辨率。"""
        return self.wavelength_m / (2 * self.nchirp_loops * self.chirp_interval_s * self.num_tx)

    @property
    def velocity_bin_size_m_per_s(self) -> float:
        """多普勒 FFT 输出中每个 bin 对应的速度。"""
        return self.velocity_resolution_m_per_s * self.nchirp_loops / self.doppler_fft_size

    @property
    def range_window(self) -> np.ndarray:
        """距离向窗函数；关闭时返回全 1，等价于不加窗。"""
        if not self.range_window_enable:
            return np.ones(self.num_adc_samples, dtype=np.float32)
        return np.hanning(self.num_adc_samples).astype(np.float32)

    @property
    def doppler_window(self) -> np.ndarray:
        """多普勒向窗函数；关闭时返回全 1，等价于不加窗。"""
        if not self.doppler_window_enable:
            return np.ones(self.nchirp_loops, dtype=np.float32)
        return np.hanning(self.nchirp_loops).astype(np.float32)

    def resolve_workers(self) -> int:
        """确定实际使用的处理进程数。"""
        if self.workers is not None and self.workers > 0:
            return self.workers
        return max(1, cpu_count() // 2)
