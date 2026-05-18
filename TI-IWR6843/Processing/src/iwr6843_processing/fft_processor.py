import numpy as np
import scipy.signal.windows as win
from scipy.fft import fft, fftshift

from .aov import speed_to_angle_aov
from .fft_cutter import cut_speed_fft


def process_fft(
    radar_data: np.ndarray,
    radar_matrix: np.ndarray,
    n_samples: int,
    n_chirps: int,
    window: str,
    range_fft_n: int,
    speed_fft_n: int,
    angle_fft_n: int,
    start_bins: int,
    target_bins: int,
    bias_list: tuple[int, ...],
    n_points: int,
    point_gap: int,
    speed_index: int,
    mm_lambda: float,
    sample_rate: float,
    chirp_period: float,
    light_speed: float,
    freq_slope: float,
    n_tx: int,
    obj_h_up: float,
    obj_h_down: float,
    az_angle: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """执行距离、多普勒、角度处理并生成点云。"""
    del speed_index

    if window == "flattop":
        range_window = win.flattop(n_samples)
        doppler_window = win.flattop(n_chirps)
    elif window == "blackmanharris":
        range_window = win.blackmanharris(n_samples)
        doppler_window = win.blackmanharris(n_chirps)
    else:
        raise ValueError(f"不支持的窗函数：{window}")

    range_profile = np.zeros((range_fft_n, n_chirps, radar_data.shape[-1]), dtype=np.complex64)
    for rx in range(radar_data.shape[-1]):
        for chirp in range(n_chirps):
            range_profile[:, chirp, rx] = fft(radar_data[:, chirp, rx] * range_window, range_fft_n)

    speed_profile = np.zeros((target_bins, speed_fft_n, radar_data.shape[-1]), dtype=np.complex64)
    for rx in range(radar_data.shape[-1]):
        for target_bin in range(target_bins):
            speed_profile[target_bin, :, rx] = fftshift(
                fft(range_profile[start_bins + target_bin - 1, :, rx] * doppler_window.T, speed_fft_n)
            )

    speed_antenna = np.zeros(
        (radar_matrix.shape[0], target_bins, speed_fft_n, radar_matrix.shape[1]),
        dtype=np.complex64,
    )
    for i in range(radar_matrix.shape[0]):
        for j in range(radar_matrix.shape[1]):
            speed_antenna[i, :, :, j] = speed_profile[:, :, radar_matrix[i, j]]

    speed_antenna_index = cut_speed_fft(speed_antenna, radar_matrix, n_points, point_gap)

    angle_antenna = np.zeros(
        (radar_matrix.shape[0], target_bins, speed_fft_n, angle_fft_n),
        dtype=np.complex64,
    )
    for antenna in range(radar_matrix.shape[0]):
        for target_bin in range(target_bins):
            for speed_bin in range(speed_fft_n):
                angle_antenna[antenna, target_bin, speed_bin, :] = np.fft.fftshift(
                    np.fft.fft(speed_antenna[antenna, target_bin, speed_bin, :], angle_fft_n)
                )

    seq_list = np.array([[0, 2], [1, 2], [1, 3], [0, 3]])
    points_rx = np.zeros((seq_list.shape[0] * 4, len(bias_list) * n_points, 16))

    for i in range(seq_list.shape[0]):
        for antenna_seq in range(4):
            points_rx[i * 4 + antenna_seq, :, :] = speed_to_angle_aov(
                angle_antenna[seq_list[i, 0]],
                angle_antenna[seq_list[i, 1]],
                speed_antenna_index[seq_list[i, 0]],
                antenna_seq,
                range_fft_n,
                speed_fft_n,
                angle_fft_n,
                bias_list,
                n_points,
                mm_lambda,
                sample_rate,
                chirp_period,
                light_speed,
                freq_slope,
                n_tx,
                start_bins,
                obj_h_up,
                obj_h_down,
                az_angle,
            )

    points_frame = np.vstack([points_rx[i, :, :5] for i in range(16)])
    dynamic_range_angle_image = np.abs(angle_antenna[...])

    return range_profile, speed_profile, dynamic_range_angle_image, points_frame
