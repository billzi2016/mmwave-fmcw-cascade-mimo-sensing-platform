import math

import numpy as np

from .antenna_map import ANTENNA_86
from .config import CascadeProcessingConfig


def normalize_minmax(data: np.ndarray) -> np.ndarray:
    data_min = np.min(data)
    data_max = np.max(data)
    if data_max == data_min:
        return np.zeros_like(data, dtype=np.float32)
    return ((data - data_min) / (data_max - data_min)).astype(np.float32)


def build_speed_heatmap(doppler_fft_out: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """生成单帧 speed heatmap。"""
    collapsed = doppler_fft_out.reshape(
        doppler_fft_out.shape[0],
        doppler_fft_out.shape[1],
        -1,
    )
    signal = 10 * np.log10(np.sum(np.abs(collapsed) ** 2, axis=2) + 1)
    range_limit_bins = math.ceil(config.range_limit_m / config.range_bin_size_m)
    signal = signal[:range_limit_bins, :]
    return normalize_minmax(signal)


def build_angle_heatmap(doppler_fft_out: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """生成单帧 angle heatmap。"""
    antenna_cube = np.zeros(
        (
            doppler_fft_out.shape[0],
            doppler_fft_out.shape[1],
            len(ANTENNA_86),
        ),
        dtype=np.complex64,
    )
    for antenna_index, (tx_index, rx_index) in enumerate(ANTENNA_86):
        antenna_cube[..., antenna_index] = doppler_fft_out[..., rx_index, tx_index]

    angle_fft = np.fft.fftshift(
        np.fft.fft(antenna_cube, axis=2, n=config.angle_fft_size),
        axes=2,
    )
    angle_fft = np.abs(angle_fft)
    max_values = np.max(angle_fft, axis=1)

    range_limit_bins = math.ceil(config.range_limit_m / config.range_bin_size_m)
    return max_values[:range_limit_bins, :].astype(np.float32)
