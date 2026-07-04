"""TI IWR2243 Cascade 的频率和相位校准。

四芯片级联雷达存在设备间频率偏差和通道相位不一致。校准发生在 FFT
之前，目标是让不同 TX/RX 通道在虚拟阵列中保持一致的相位参考。
"""

from pathlib import Path

import numpy as np
from scipy.io import loadmat

from .config import CascadeProcessingConfig


def _loadmat_simplified(path: Path) -> dict:
    """兼容不同 scipy 版本读取 MATLAB 文件。"""
    try:
        return loadmat(path, simplify_cells=True)
    except TypeError:
        return loadmat(path, squeeze_me=True, struct_as_record=False)


def load_calibration(calibration_file: Path | None) -> dict[str, np.ndarray] | None:
    """读取校准矩阵。

    返回字典包含 `range_mat` 和 `peak_val_mat`。前者用于频率校准，
    后者用于相位/幅度校准；未提供校准文件时返回 None。
    """
    if calibration_file is None:
        return None

    mat = _loadmat_simplified(calibration_file)
    calib_result = mat.get("calibResult")
    if calib_result is None:
        raise KeyError(f"校准文件中缺少 calibResult：{calibration_file}")

    if isinstance(calib_result, dict):
        range_mat = np.asarray(calib_result["RangeMat"])
        peak_val_mat = np.asarray(calib_result["PeakValMat"])
    else:
        range_mat = np.asarray(calib_result.RangeMat)
        peak_val_mat = np.asarray(calib_result.PeakValMat)

    return {
        "range_mat": range_mat,
        "peak_val_mat": peak_val_mat,
    }


def apply_calibration(
    adc_data: np.ndarray,
    calibration: dict[str, np.ndarray] | None,
    config: CascadeProcessingConfig,
) -> np.ndarray:
    """对 4-chip cascade 的 ADC 数据做频率与相位校准。

    输入 `adc_data` 维度为 sample、chirp loop、RX、TX slot。函数先按
    `rx_for_mimo` 重排接收通道，再逐 TX/RX 应用频率修正和相位修正。
    """
    # 先把原始 RX 顺序转换为 MIMO 阵列处理期望的接收通道顺序。
    reordered = adc_data[:, :, np.asarray(config.rx_for_mimo) - 1, :]
    if calibration is None or not config.adc_calibration_on:
        return reordered

    range_mat = calibration["range_mat"]
    peak_val_mat = calibration["peak_val_mat"]

    tx_reference = config.tx_to_enable[0] - 1
    out_data = np.empty_like(reordered)
    sample_index = np.arange(config.num_adc_samples, dtype=np.float32)

    for tx_slot, tx_enabled in enumerate(config.tx_to_enable):
        tx_index = tx_enabled - 1

        # range_mat 的差值对应通道间频率偏差，换算为每个 ADC sample 上的相位旋转。
        freq_calib = (
            (range_mat[tx_index, :] - range_mat[tx_reference, 0])
            * config.fs_calib
            / config.adc_sample_rate
            * config.chirp_slope_hz_per_s
            / config.slope_calib
        )
        freq_calib = 2 * np.pi * freq_calib / (config.num_adc_samples * config.calibration_interp)
        freq_correction = np.exp(1j * np.outer(sample_index, freq_calib)).astype(np.complex64)
        freq_correction = freq_correction[:, None, :]

        # peak_val_mat 用参考 TX/RX 与当前通道的复数比值进行相位补偿。
        phase_calib = peak_val_mat[tx_reference, 0] / peak_val_mat[tx_index, :]
        if config.phase_calibration_only:
            # 只保留单位相位，不改变幅度。
            phase_calib = phase_calib / np.abs(phase_calib)
        phase_correction = phase_calib[None, None, :]

        out_data[:, :, :, tx_slot] = reordered[:, :, :, tx_slot] * freq_correction * phase_correction

    return out_data
