"""从级联雷达频域结果生成速度和角度热力图。

本模块接收 `run_processing_chain` 输出的复数 range-doppler-rx-tx 张量，
把高维频谱压缩成便于保存和展示的二维图像。
"""

import math

import numpy as np

from .antenna_map import ANTENNA_86
from .config import CascadeProcessingConfig


def normalize_minmax(data: np.ndarray) -> np.ndarray:
    """将输入矩阵归一化到 0 到 1。"""
    data_min = np.min(data)
    data_max = np.max(data)
    if data_max == data_min:
        # 常量图没有动态范围，直接返回全零，避免除零产生 NaN。
        return np.zeros_like(data, dtype=np.float32)
    return ((data - data_min) / (data_max - data_min)).astype(np.float32)


def build_speed_heatmap(doppler_fft_out: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """生成单帧速度热力图。

    先把 RX/TX 天线维度压平，再对所有天线通道做能量累加，得到
    range-doppler 平面上的总回波强度。
    """
    collapsed = doppler_fft_out.reshape(
        doppler_fft_out.shape[0],
        doppler_fft_out.shape[1],
        -1,
    )
    # 使用 dB 压缩动态范围，`+ 1` 避免空响应位置出现 log(0)。
    signal = 10 * np.log10(np.sum(np.abs(collapsed) ** 2, axis=2) + 1)
    range_limit_bins = math.ceil(config.range_limit_m / config.range_bin_size_m)
    signal = signal[:range_limit_bins, :]
    return normalize_minmax(signal)


def build_angle_heatmap(doppler_fft_out: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """生成单帧角度热力图。

    该函数按照 `ANTENNA_86` 的虚拟阵列顺序抽取 RX/TX 通道，然后沿
    虚拟天线维做角度 FFT，最后在速度维取最大值，形成 range-angle 图。
    """
    antenna_cube = np.zeros(
        (
            doppler_fft_out.shape[0],
            doppler_fft_out.shape[1],
            len(ANTENNA_86),
        ),
        dtype=np.complex64,
    )
    for antenna_index, (tx_index, rx_index) in enumerate(ANTENNA_86):
        # ANTENNA_86 保存的是虚拟天线到原始 tx/rx 频谱位置的映射。
        antenna_cube[..., antenna_index] = doppler_fft_out[..., rx_index, tx_index]

    # 角度 FFT 后做 fftshift，使 0 度附近响应位于图像中心。
    angle_fft = np.fft.fftshift(
        np.fft.fft(antenna_cube, axis=2, n=config.angle_fft_size),
        axes=2,
    )
    angle_fft = np.abs(angle_fft)
    max_values = np.max(angle_fft, axis=1)

    range_limit_bins = math.ceil(config.range_limit_m / config.range_bin_size_m)
    return max_values[:range_limit_bins, :].astype(np.float32)
