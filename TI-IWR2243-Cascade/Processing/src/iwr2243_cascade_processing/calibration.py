from pathlib import Path

import numpy as np
from scipy.io import loadmat

from .config import CascadeProcessingConfig


def _loadmat_simplified(path: Path) -> dict:
    try:
        return loadmat(path, simplify_cells=True)
    except TypeError:
        return loadmat(path, squeeze_me=True, struct_as_record=False)


def load_calibration(calibration_file: Path | None) -> dict[str, np.ndarray] | None:
    """读取校准矩阵。"""
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
    """对 4-chip cascade 的 ADC 数据做频率与相位校准。"""
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

        phase_calib = peak_val_mat[tx_reference, 0] / peak_val_mat[tx_index, :]
        if config.phase_calibration_only:
            phase_calib = phase_calib / np.abs(phase_calib)
        phase_correction = phase_calib[None, None, :]

        out_data[:, :, :, tx_slot] = reordered[:, :, :, tx_slot] * freq_correction * phase_correction

    return out_data
