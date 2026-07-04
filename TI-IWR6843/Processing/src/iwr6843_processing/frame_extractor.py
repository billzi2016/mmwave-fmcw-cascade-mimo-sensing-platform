"""从 IWR6843 单帧 LVDS 原始数据恢复虚拟天线矩阵。"""

import numpy as np


def extract_frame(
    frame_data: np.ndarray,
    n_samples: int,
    n_chirps: int,
    n_tx: int,
    n_rx: int,
) -> tuple[np.ndarray, np.ndarray]:
    """从单帧 LVDS 数据中重建虚拟天线矩阵。

    返回的 `radar_data` 形状为 `(n_samples, n_chirps, n_tx * n_rx)`，
    `radar_matrix` 描述后续角度处理使用的虚拟天线分组。
    """
    file_size = frame_data.shape[0]
    lvds_data = np.zeros((n_tx, file_size // 2 // n_tx), dtype=np.complex64)

    # 原始 int16 流中 I/Q 数据交织保存；这里按 chirp 和 TX 逐段还原复数采样。
    for chirp in range(n_chirps):
        for lvds in range(n_tx):
            counter = 0
            start_index = (chirp * file_size // n_chirps) + lvds * file_size // n_tx // n_chirps
            end_index = (chirp * file_size // n_chirps) + (lvds + 1) * file_size // n_tx // n_chirps - 2
            for index in range(start_index, end_index, 4):
                # 每 4 个 int16 还原为两个复数采样：I0/Q0、I1/Q1。
                lvds_data[lvds, (chirp * n_samples * n_rx) + counter] = frame_data[index] + 1j * frame_data[index + 2]
                lvds_data[lvds, (chirp * n_samples * n_rx) + counter + 1] = frame_data[index + 1] + 1j * frame_data[index + 3]
                counter += 2

    # 使用 Fortran 顺序匹配原始 MATLAB 风格内存布局，再把维度调整为 TX、chirp、sample/RX。
    lvds_data = lvds_data.reshape(lvds_data.shape[0], n_samples * n_rx, n_chirps, order="F")
    lvds_data = np.transpose(lvds_data, (0, 2, 1))

    radar_data = np.zeros((n_rx * n_tx, n_chirps * n_samples), dtype=np.complex64)
    for tx in range(n_tx):
        for rx in range(n_rx):
            for chirp in range(n_chirps):
                # 将每个 TX/RX 的 chirp 采样连续写入对应虚拟天线行。
                radar_data[tx * n_rx + rx, chirp * n_samples : (chirp + 1) * n_samples] = (
                    lvds_data[tx, chirp, rx * n_samples : (rx + 1) * n_samples]
                )

    # 按原始脚本的极性修正规则处理反向通道。
    inverse_index = [1, 2, 5, 6, 9, 10]
    radar_data[inverse_index, :] = -radar_data[inverse_index, :]

    radar_data = radar_data.reshape(radar_data.shape[0], n_samples, n_chirps, order="F")
    radar_data = np.transpose(radar_data, (1, 2, 0))

    # 每行是一组用于角度估计的虚拟天线索引组合。
    radar_matrix = np.array(
        [
            [0, 3, 4, 7],
            [1, 2, 5, 6],
            [4, 5, 8, 9],
            [7, 6, 11, 10],
        ]
    )

    return radar_data, radar_matrix
