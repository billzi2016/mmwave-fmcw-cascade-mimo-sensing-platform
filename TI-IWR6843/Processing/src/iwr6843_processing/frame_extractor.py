import numpy as np


def extract_frame(
    frame_data: np.ndarray,
    n_samples: int,
    n_chirps: int,
    n_tx: int,
    n_rx: int,
) -> tuple[np.ndarray, np.ndarray]:
    """从单帧 LVDS 数据中重建虚拟天线矩阵。"""
    file_size = frame_data.shape[0]
    lvds_data = np.zeros((n_tx, file_size // 2 // n_tx), dtype=np.complex64)

    for chirp in range(n_chirps):
        for lvds in range(n_tx):
            counter = 0
            start_index = (chirp * file_size // n_chirps) + lvds * file_size // n_tx // n_chirps
            end_index = (chirp * file_size // n_chirps) + (lvds + 1) * file_size // n_tx // n_chirps - 2
            for index in range(start_index, end_index, 4):
                lvds_data[lvds, (chirp * n_samples * n_rx) + counter] = frame_data[index] + 1j * frame_data[index + 2]
                lvds_data[lvds, (chirp * n_samples * n_rx) + counter + 1] = frame_data[index + 1] + 1j * frame_data[index + 3]
                counter += 2

    lvds_data = lvds_data.reshape(lvds_data.shape[0], n_samples * n_rx, n_chirps, order="F")
    lvds_data = np.transpose(lvds_data, (0, 2, 1))

    radar_data = np.zeros((n_rx * n_tx, n_chirps * n_samples), dtype=np.complex64)
    for tx in range(n_tx):
        for rx in range(n_rx):
            for chirp in range(n_chirps):
                radar_data[tx * n_rx + rx, chirp * n_samples : (chirp + 1) * n_samples] = (
                    lvds_data[tx, chirp, rx * n_samples : (rx + 1) * n_samples]
                )

    # 按原始脚本的极性修正规则处理反向通道。
    inverse_index = [1, 2, 5, 6, 9, 10]
    radar_data[inverse_index, :] = -radar_data[inverse_index, :]

    radar_data = radar_data.reshape(radar_data.shape[0], n_samples, n_chirps, order="F")
    radar_data = np.transpose(radar_data, (1, 2, 0))

    radar_matrix = np.array(
        [
            [0, 3, 4, 7],
            [1, 2, 5, 6],
            [4, 5, 8, 9],
            [7, 6, 11, 10],
        ]
    )

    return radar_data, radar_matrix
