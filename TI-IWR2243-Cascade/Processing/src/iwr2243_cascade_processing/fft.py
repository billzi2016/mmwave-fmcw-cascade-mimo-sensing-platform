"""TI IWR2243 Cascade 的距离向和多普勒向 FFT。

输入数据已经完成四芯片拼接和可选校准，本文件只负责把时域 ADC 数据
转换到 range-doppler 频域。角度处理和热力图生成在后续模块中完成。
"""

import numpy as np

from .config import CascadeProcessingConfig


def run_range_fft(adc_data_tx: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """对单个 TX 槽位执行距离向 FFT。

    `adc_data_tx` 的维度约定为 `(num_adc_samples, nchirp_loops, num_rx)`。
    这里先去除每个 chirp/RX 上的直流分量，再沿 ADC 采样维加窗并做 FFT。
    """
    input_data = adc_data_tx.astype(np.complex64, copy=True)
    # 去均值用于抑制静态直流偏置，避免 0Hz 分量污染距离谱。
    input_data = input_data - np.mean(input_data, axis=0, keepdims=True)
    # range_window 的形状扩展到采样维，保持 chirp 和 RX 维不变。
    input_data = input_data * config.range_window[:, None, None]
    return np.fft.fft(input_data, n=config.range_fft_size, axis=0).astype(np.complex64)


def run_doppler_fft(range_fft_tx: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """对单个 TX 槽位执行多普勒向 FFT。

    输入是距离向 FFT 的输出，维度约定为 `(range_bin, chirp_loop, rx)`。
    函数沿 chirp_loop 维做 FFT，并通过 `fftshift` 把零速度移动到频谱中心。
    """
    input_data = range_fft_tx * config.doppler_window[None, :, None]
    if config.clutter_remove:
        # 静态杂波通常在慢时间维近似为均值，减均值可以削弱静止背景。
        input_data = input_data - np.mean(input_data, axis=1, keepdims=True)
    doppler_fft = np.fft.fft(input_data, n=config.doppler_fft_size, axis=1)
    doppler_fft = np.fft.fftshift(doppler_fft, axes=1)
    return doppler_fft.astype(np.complex64)


def run_processing_chain(adc_data: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """对整帧所有 TX 槽位依次执行 Range / Doppler FFT。

    `adc_data` 的最后一维是 TX 槽位。输出统一整理为
    `(range_bin, doppler_bin, rx, tx)`，供后续 speed/angle heatmap 使用。
    """
    doppler_fft = np.zeros(
        (config.range_fft_size, config.doppler_fft_size, config.num_rx, config.num_tx),
        dtype=np.complex64,
    )
    for tx_slot in range(config.num_tx):
        # 每个 TX 槽位独立完成距离向和速度向 FFT，最后写回统一频谱张量。
        range_fft_tx = run_range_fft(adc_data[:, :, :, tx_slot], config)
        doppler_fft[:, :, :, tx_slot] = run_doppler_fft(range_fft_tx, config)
    return doppler_fft
