"""读取 TI IWR2243 Cascade 的原始 TDA2 二进制数据。

级联雷达每帧数据分散在 master/slave1/slave2/slave3 四个文件中。
本模块负责按帧读取每个设备的 interleaved I/Q 数据，并拼接成后续
校准和 FFT 所需的复数 ADC 张量。
"""

from pathlib import Path

import numpy as np

from .config import CascadeProcessingConfig
from .file_index import CaptureGroup


def read_valid_frame_count(idx_file: Path) -> int:
    """读取 TDA2 idx 文件中的有效帧数。

    idx 文件头部第 4 个 uint32 记录可用帧数，处理阶段用它避免读到
    data 文件末尾之外的数据。
    """
    header = np.fromfile(idx_file, dtype=np.uint32, count=4)
    if len(header) < 4:
        raise ValueError(f"idx 文件头部不完整：{idx_file}")
    return int(header[3])


def _read_device_frame(
    file_path: Path,
    frame_index: int,
    config: CascadeProcessingConfig,
) -> np.ndarray:
    """读取单个雷达设备的一帧 ADC 数据。

    返回维度为 `(num_adc_samples, nchirp_loops, num_rx_per_device, num_chirps_in_loop)`。
    这里仍然只处理单个设备，四设备拼接由 `read_cascade_frame` 完成。
    """
    expected_uint16_per_frame = (
        config.num_adc_samples
        * config.num_chirps_in_loop
        * config.nchirp_loops
        * config.num_rx_per_device
        * 2
    )
    # data.bin 中每帧是固定长度块，按帧号直接计算 byte offset。
    offset_bytes = frame_index * expected_uint16_per_frame * 2

    with file_path.open("rb") as fp:
        fp.seek(offset_bytes)
        adc_uint16 = np.fromfile(fp, dtype=np.uint16, count=expected_uint16_per_frame)

    if adc_uint16.size != expected_uint16_per_frame:
        raise EOFError(f"文件 {file_path.name} 在第 {frame_index} 帧数据不足。")

    # 原始 I/Q 以 int16 交织保存，偶数位为 I，奇数位为 Q。
    adc_iq = adc_uint16.view(np.int16).astype(np.float32)
    adc_complex = adc_iq[0::2] + 1j * adc_iq[1::2]

    # 使用 Fortran 顺序匹配原始采集脚本的列优先展开方式。
    adc_complex = adc_complex.reshape(
        (
            config.num_rx_per_device,
            config.num_adc_samples,
            config.num_chirps_in_loop,
            config.nchirp_loops,
        ),
        order="F",
    )
    # 调整为后续 FFT 更自然的维度顺序：sample、loop、rx、tx-slot。
    adc_complex = np.transpose(adc_complex, (1, 3, 0, 2))
    return adc_complex.astype(np.complex64)


def read_cascade_frame(
    group: CaptureGroup,
    frame_index: int,
    config: CascadeProcessingConfig,
) -> np.ndarray:
    """读取四片雷达的一帧并拼接成 16 路接收通道。

    四个设备必须使用同一个 `frame_index`，否则级联虚拟阵列的时间对齐会被破坏。
    """
    frames = [
        _read_device_frame(group.data_files["master"], frame_index, config),
        _read_device_frame(group.data_files["slave1"], frame_index, config),
        _read_device_frame(group.data_files["slave2"], frame_index, config),
        _read_device_frame(group.data_files["slave3"], frame_index, config),
    ]
    # axis=2 是 RX 维度，四个设备各 4 路 RX，拼接后得到 16 路 RX。
    return np.concatenate(frames, axis=2)
