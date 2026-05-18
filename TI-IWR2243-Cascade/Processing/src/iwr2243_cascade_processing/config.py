from dataclasses import dataclass, field
from multiprocessing import cpu_count

import numpy as np


TX_POSITIONS_AZI = (11, 10, 9, 32, 28, 24, 20, 16, 12, 8, 4, 0)
RX_POSITIONS_AZI = tuple(list(range(11, 15)) + list(range(50, 54)) + list(range(46, 50)) + list(range(0, 4)))
RX_FOR_MIMO = (13, 14, 15, 16, 1, 2, 3, 4, 9, 10, 11, 12, 5, 6, 7, 8)


@dataclass(slots=True)
class CascadeProcessingConfig:
    """4-chip cascade 处理配置。"""

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
        return len(self.tx_to_enable)

    @property
    def num_rx(self) -> int:
        return self.num_devices * self.num_rx_per_device

    @property
    def range_fft_size(self) -> int:
        return int(2 ** np.ceil(np.log2(self.num_adc_samples)))

    @property
    def doppler_fft_size(self) -> int:
        return int(2 ** np.ceil(np.log2(self.nchirp_loops)))

    @property
    def num_chirps_per_frame(self) -> int:
        return self.nchirp_loops * self.num_chirps_in_loop

    @property
    def chirp_ramp_time_s(self) -> float:
        return self.num_adc_samples / self.adc_sample_rate

    @property
    def chirp_interval_s(self) -> float:
        return self.chirp_ramp_end_time_s + self.chirp_idle_time_s

    @property
    def carrier_frequency_hz(self) -> float:
        return self.start_frequency_hz + (
            self.adc_start_time_s + self.chirp_ramp_time_s / 2
        ) * self.chirp_slope_hz_per_s

    @property
    def wavelength_m(self) -> float:
        return 3e8 / self.carrier_frequency_hz

    @property
    def chirp_bandwidth_hz(self) -> float:
        return self.chirp_slope_hz_per_s * self.chirp_ramp_time_s

    @property
    def range_resolution_m(self) -> float:
        return 3e8 / (2 * self.chirp_bandwidth_hz)

    @property
    def range_bin_size_m(self) -> float:
        return self.range_resolution_m * self.num_adc_samples / self.range_fft_size

    @property
    def velocity_resolution_m_per_s(self) -> float:
        return self.wavelength_m / (2 * self.nchirp_loops * self.chirp_interval_s * self.num_tx)

    @property
    def velocity_bin_size_m_per_s(self) -> float:
        return self.velocity_resolution_m_per_s * self.nchirp_loops / self.doppler_fft_size

    @property
    def range_window(self) -> np.ndarray:
        if not self.range_window_enable:
            return np.ones(self.num_adc_samples, dtype=np.float32)
        return np.hanning(self.num_adc_samples).astype(np.float32)

    @property
    def doppler_window(self) -> np.ndarray:
        if not self.doppler_window_enable:
            return np.ones(self.nchirp_loops, dtype=np.float32)
        return np.hanning(self.nchirp_loops).astype(np.float32)

    def resolve_workers(self) -> int:
        if self.workers is not None and self.workers > 0:
            return self.workers
        return max(1, cpu_count() // 2)
