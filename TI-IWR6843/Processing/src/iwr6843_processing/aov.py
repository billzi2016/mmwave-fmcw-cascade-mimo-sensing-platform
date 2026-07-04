"""把距离-速度候选峰值映射为三维点云。"""

import numpy as np


def speed_to_angle_aov(
    angle_antenna_a: np.ndarray,
    angle_antenna_b: np.ndarray,
    speed_antenna_index_a: np.ndarray,
    antenna_seq: int,
    range_fft_n: int,
    speed_fft_n: int,
    angle_fft_n: int,
    bias_list: tuple[int, ...],
    n_points: int,
    mm_lambda: float,
    sample_rate: float,
    chirp_period: float,
    light_speed: float,
    freq_slope: float,
    n_tx: int,
    start_bins: int,
    obj_h_up: float,
    obj_h_down: float,
    azimuth_angle: int,
) -> np.ndarray:
    """将速度峰值索引映射为三维点云。

    函数先把 range/doppler bin 转换为距离和速度，再从两组角度谱中取
    方位/俯仰峰值，最终把球坐标转换成 x/y/z 点云坐标。
    """

    angle_n_points_3d = np.zeros((len(bias_list) * n_points, 16))

    for point in range(n_points):
        row = speed_antenna_index_a[2 * antenna_seq, point]
        col = speed_antenna_index_a[2 * antenna_seq + 1, point]

        # range bin 对应拍频，doppler bin 对应多普勒频率；距离公式中扣除了多普勒项。
        beat_frequency = ((row + start_bins - 1) * sample_rate) / range_fft_n
        doppler_frequency = (col - speed_fft_n / 2) / (speed_fft_n * chirp_period * n_tx)
        distance = light_speed * (beat_frequency - doppler_frequency) / (2 * freq_slope)
        speed = mm_lambda * doppler_frequency / 2

        # 根据目标高度上下界限制俯仰角搜索范围，减少不合理角度峰值。
        elevation_positive = int(np.ceil(np.degrees(np.arcsin(np.clip(obj_h_up / distance, -1, 1))))) + 15
        elevation_negative = int(np.floor(np.degrees(np.arcsin(np.clip(obj_h_down / distance, -1, 1))))) + 15

        # A/B 两组角度谱分别用于估计方位角和俯仰角。
        current_angle_a = np.abs(angle_antenna_a[row, col, :])
        current_angle_b = np.abs(angle_antenna_b[row, col, :])

        peak_1 = np.max(current_angle_a[angle_fft_n // 2 - azimuth_angle : angle_fft_n // 2 + azimuth_angle])
        if distance > obj_h_up * 1.5 and distance > obj_h_down * 1.5:
            peak_2 = np.max(
                current_angle_b[angle_fft_n // 2 - elevation_negative : angle_fft_n // 2 + elevation_positive]
            )
        else:
            peak_2 = np.max(current_angle_b[angle_fft_n // 2 - azimuth_angle : angle_fft_n // 2 + azimuth_angle])

        page_1 = np.argmax(current_angle_a == peak_1)
        page_2 = np.argmax(current_angle_b == peak_2)

        for bias_index, bias in enumerate(bias_list):
            # bias 用于在角度 FFT 栅格附近做偏移补偿，生成更细的候选角度。
            fw_1 = (page_1 + bias - angle_fft_n / 2 - 1) / angle_fft_n
            fw_2 = (page_2 + bias - angle_fft_n / 2 - 1) / angle_fft_n

            angle_azimuth = np.degrees(np.arcsin(np.clip(fw_1 * 2, -1, 1)))
            angle_elevation = np.degrees(np.arcsin(np.clip(fw_2 * 2, -1, 1)))

            # 球坐标到笛卡尔坐标：距离 + 方位角 + 俯仰角 -> x/y/z。
            dist_z = distance * np.sin(np.radians(angle_elevation))
            dist_intermediate = distance * np.cos(np.radians(angle_elevation))
            dist_x = dist_intermediate * np.sin(np.radians(angle_azimuth))
            dist_y = dist_intermediate * np.cos(np.radians(angle_azimuth))

            angle_n_points_3d[len(bias_list) * point + bias_index, :] = np.array(
                [
                    dist_x,
                    dist_y,
                    dist_z,
                    peak_1 + peak_2,
                    speed,
                    distance,
                    row,
                    col,
                    page_1,
                    page_2,
                    peak_1,
                    peak_2,
                    angle_azimuth,
                    angle_elevation,
                    elevation_positive,
                    elevation_negative,
                ]
            )

    return angle_n_points_3d
