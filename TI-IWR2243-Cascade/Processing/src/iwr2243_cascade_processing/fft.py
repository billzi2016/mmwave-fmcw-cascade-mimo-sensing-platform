import numpy as np

from .config import CascadeProcessingConfig


def run_range_fft(adc_data_tx: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """对单个 TX 槽位执行距离向 FFT。"""
    input_data = adc_data_tx.astype(np.complex64, copy=True)
    input_data = input_data - np.mean(input_data, axis=0, keepdims=True)
    input_data = input_data * config.range_window[:, None, None]
    return np.fft.fft(input_data, n=config.range_fft_size, axis=0).astype(np.complex64)


def run_doppler_fft(range_fft_tx: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """对单个 TX 槽位执行多普勒向 FFT。"""
    input_data = range_fft_tx * config.doppler_window[None, :, None]
    if config.clutter_remove:
        input_data = input_data - np.mean(input_data, axis=1, keepdims=True)
    doppler_fft = np.fft.fft(input_data, n=config.doppler_fft_size, axis=1)
    doppler_fft = np.fft.fftshift(doppler_fft, axes=1)
    return doppler_fft.astype(np.complex64)


def run_processing_chain(adc_data: np.ndarray, config: CascadeProcessingConfig) -> np.ndarray:
    """对整帧 12 个 TX 槽位依次执行 Range / Doppler FFT。"""
    doppler_fft = np.zeros(
        (config.range_fft_size, config.doppler_fft_size, config.num_rx, config.num_tx),
        dtype=np.complex64,
    )
    for tx_slot in range(config.num_tx):
        range_fft_tx = run_range_fft(adc_data[:, :, :, tx_slot], config)
        doppler_fft[:, :, :, tx_slot] = run_doppler_fft(range_fft_tx, config)
    return doppler_fft
