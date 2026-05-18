from pathlib import Path

import numpy as np

from .config import CascadeProcessingConfig
from .file_index import CaptureGroup


def read_valid_frame_count(idx_file: Path) -> int:
    """读取 TDA2 idx 文件中的有效帧数。"""
    header = np.fromfile(idx_file, dtype=np.uint32, count=4)
    if len(header) < 4:
        raise ValueError(f"idx 文件头部不完整：{idx_file}")
    return int(header[3])


def _read_device_frame(
    file_path: Path,
    frame_index: int,
    config: CascadeProcessingConfig,
) -> np.ndarray:
    expected_uint16_per_frame = (
        config.num_adc_samples
        * config.num_chirps_in_loop
        * config.nchirp_loops
        * config.num_rx_per_device
        * 2
    )
    offset_bytes = frame_index * expected_uint16_per_frame * 2

    with file_path.open("rb") as fp:
        fp.seek(offset_bytes)
        adc_uint16 = np.fromfile(fp, dtype=np.uint16, count=expected_uint16_per_frame)

    if adc_uint16.size != expected_uint16_per_frame:
        raise EOFError(f"文件 {file_path.name} 在第 {frame_index} 帧数据不足。")

    adc_iq = adc_uint16.view(np.int16).astype(np.float32)
    adc_complex = adc_iq[0::2] + 1j * adc_iq[1::2]

    adc_complex = adc_complex.reshape(
        (
            config.num_rx_per_device,
            config.num_adc_samples,
            config.num_chirps_in_loop,
            config.nchirp_loops,
        ),
        order="F",
    )
    adc_complex = np.transpose(adc_complex, (1, 3, 0, 2))
    return adc_complex.astype(np.complex64)


def read_cascade_frame(
    group: CaptureGroup,
    frame_index: int,
    config: CascadeProcessingConfig,
) -> np.ndarray:
    """读取四片雷达的一帧并拼接成 16 路接收通道。"""
    frames = [
        _read_device_frame(group.data_files["master"], frame_index, config),
        _read_device_frame(group.data_files["slave1"], frame_index, config),
        _read_device_frame(group.data_files["slave2"], frame_index, config),
        _read_device_frame(group.data_files["slave3"], frame_index, config),
    ]
    return np.concatenate(frames, axis=2)
