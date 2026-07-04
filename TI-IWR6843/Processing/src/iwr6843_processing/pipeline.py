"""TI IWR6843 离线处理主流水线。

本文件负责把 XML/BIN 输入转换为 H5/NPZ 结果：先解析采集参数，再切分帧、
逐帧执行 FFT 和点云生成，最后把所有帧聚合保存。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
import time

import h5py
import numpy as np

from .bin_reader import read_bin
from .config import ProcessingConfig
from .fft_processor import process_fft
from .frame_extractor import extract_frame
from .xml_reader import parse_xml


@dataclass(slots=True)
class RuntimeParameters:
    """由 XML 参数和静态配置共同推导出的运行时参数。"""

    n_samples: int
    n_chirps: int
    frames: int
    periodicity: float
    freq_slope: float
    ramp_end_time: float
    sample_rate: float
    start_freq: float
    start_bins: int
    reasonable_bins: int
    target_bins: int
    range_factor: float
    speed_factor: float
    chirp_period: float
    mm_lambda: float


def _build_runtime_parameters(config: ProcessingConfig, xml_path: Path) -> RuntimeParameters:
    """根据 XML 和配置计算 FFT 后物理量换算参数。"""
    freq_slope, ramp_end_time, sample_rate, start_freq, n_samples, frames, periodicity, n_chirps = parse_xml(xml_path)
    chirp_period = (100 + ramp_end_time) * 1e-6
    mm_lambda = config.light_speed / start_freq

    # 只处理一段合理距离范围，减少后续速度/角度处理的计算量。
    start_bins = int(np.ceil(config.start_bin_ratio * config.range_fft_n))
    reasonable_bins = int(np.ceil(config.reasonable_bin_ratio * config.range_fft_n))
    target_bins = reasonable_bins - start_bins + 1

    range_factor = sample_rate * config.light_speed / (2 * freq_slope * config.range_fft_n)
    speed_factor = mm_lambda / chirp_period / config.n_tx

    return RuntimeParameters(
        n_samples=n_samples,
        n_chirps=n_chirps,
        frames=frames,
        periodicity=periodicity,
        freq_slope=freq_slope,
        ramp_end_time=ramp_end_time,
        sample_rate=sample_rate,
        start_freq=start_freq,
        start_bins=start_bins,
        reasonable_bins=reasonable_bins,
        target_bins=target_bins,
        range_factor=range_factor,
        speed_factor=speed_factor,
        chirp_period=chirp_period,
        mm_lambda=mm_lambda,
    )


def _split_frames(bin_data: np.ndarray, runtime: RuntimeParameters, config: ProcessingConfig) -> np.ndarray:
    """把一维 BIN 原始数据切分为逐帧数组。"""
    frame_length = runtime.n_samples * runtime.n_chirps * 4 * 1 * 2 * config.n_tx
    frames_data = np.zeros((runtime.frames, frame_length), dtype=np.int16)

    for frame in range(runtime.frames):
        # 每帧长度固定，因此可以用 frame index 直接计算切片范围。
        start_index = frame * frame_length
        end_index = (frame + 1) * frame_length
        frames_data[frame, :] = bin_data[start_index:end_index]

    return frames_data


def _process_frame(args: tuple[np.ndarray, ProcessingConfig, RuntimeParameters, str]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """处理单帧数据。

    先恢复虚拟天线矩阵，再执行 Range/Doppler/Angle FFT 和点云生成。
    """
    frame_data, config, runtime, window = args
    radar_data, radar_matrix = extract_frame(
        frame_data,
        runtime.n_samples,
        runtime.n_chirps,
        config.n_tx,
        config.n_rx,
    )
    return process_fft(
        radar_data,
        radar_matrix,
        runtime.n_samples,
        runtime.n_chirps,
        window,
        config.range_fft_n,
        config.speed_fft_n,
        config.angle_fft_n,
        runtime.start_bins,
        runtime.target_bins,
        config.bias_list,
        config.n_points,
        config.point_gap,
        config.speed_index,
        runtime.mm_lambda,
        runtime.sample_rate,
        runtime.chirp_period,
        config.light_speed,
        runtime.freq_slope,
        config.n_tx,
        config.obj_h_up,
        config.obj_h_down,
        config.azimuth_angle,
    )


def _save_h5(
    output_path: Path,
    range_profiles: np.ndarray,
    speed_profiles: np.ndarray,
    angle_profiles: np.ndarray,
    points_frames: np.ndarray,
    runtime: RuntimeParameters,
) -> None:
    """保存完整频谱和点云结果到 H5。"""
    compression_options = {"compression": "gzip", "compression_opts": 1}

    with h5py.File(output_path, "w") as fw:
        # 四类主结果按数据集保存，Visualization 阶段可以按需读取。
        fw.create_dataset("range_profiles", data=range_profiles, **compression_options)
        fw.create_dataset("speed_profiles", data=speed_profiles, **compression_options)
        fw.create_dataset("angle_profiles", data=angle_profiles, **compression_options)
        fw.create_dataset("points_frames", data=points_frames, **compression_options)
        fw.create_dataset(
            "param",
            # param 顺序由 h5_loader 依赖，修改时需要同步更新读取端。
            data=(
                runtime.start_bins,
                runtime.reasonable_bins,
                runtime.range_factor,
                runtime.periodicity,
                runtime.n_chirps,
                runtime.speed_factor,
            ),
        )


def _save_points_npz(output_path: Path, points_frames: np.ndarray) -> None:
    """额外导出点云结果，方便直接使用。"""
    np.savez_compressed(output_path, points_frames=points_frames)


def run_processing(input_dir: Path, output_dir: Path, config: ProcessingConfig) -> None:
    """运行 IWR6843 离线处理流程。"""
    xml_files = sorted(input_dir.glob("*.xml"))
    bin_files = sorted(input_dir.glob("*.bin"))

    if not xml_files:
        raise FileNotFoundError(f"在 {input_dir} 中没有找到 XML 参数文件。")
    if not bin_files:
        raise FileNotFoundError(f"在 {input_dir} 中没有找到 BIN 原始数据文件。")

    runtime = _build_runtime_parameters(config, xml_files[0])
    workers = config.resolve_workers()

    print()
    print(f'>> input_dir = "{input_dir}"')
    print(f'>> output_dir = "{output_dir}"')
    print(f">> workers = {workers}")
    print(f">> RANGE_FFT_N = {config.range_fft_n}")
    print(f">> range_factor = {runtime.range_factor}")
    print()
    print(f">> SPEED_FFT_N = {config.speed_fft_n}")
    print(f">> speed_factor = {runtime.speed_factor / config.speed_fft_n}")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)

    for bin_path in bin_files:
        # 每个 BIN 文件独立处理；同目录下多个 BIN 会逐个输出结果。
        bin_data = read_bin(bin_path)
        frames_data = _split_frames(bin_data, runtime, config)

        for window in config.windows:
            start_time = time.time()
            args_list = [(frame_data, config, runtime, window) for frame_data in frames_data]

            # 帧之间没有依赖，可以并行处理；结果顺序由 pool.map 保持。
            with Pool(workers) as pool:
                results = pool.map(_process_frame, args_list)

            # 预分配聚合数组，避免在循环中反复 append 大矩阵。
            range_profiles = np.zeros((runtime.frames, config.range_fft_n, runtime.n_chirps, config.n_tx * config.n_rx))
            speed_profiles = np.zeros((runtime.frames, runtime.target_bins, config.speed_fft_n, config.n_tx * config.n_rx))
            angle_profiles = np.zeros((runtime.frames, 4, runtime.target_bins, config.angle_fft_n))
            points_frames = np.zeros((runtime.frames, len(config.bias_list) * 4 * 4 * config.n_points, 5))

            for frame, (range_profile, speed_profile, angle_profile, points_frame) in enumerate(results):
                # 将单帧结果写回按帧组织的输出数组。
                range_profiles[frame, :, :, :] = range_profile
                speed_profiles[frame, :, :, :] = speed_profile
                angle_profiles[frame, :, :, :] = angle_profile
                points_frames[frame, :, :] = points_frame

            output_path = output_dir / f"{bin_path.stem}_{window}.h5"
            _save_h5(output_path, range_profiles, speed_profiles, angle_profiles, points_frames, runtime)
            _save_points_npz(output_dir / f"{bin_path.stem}_{window}_points.npz", points_frames)

            end_time = time.time()
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(
                f'>> timestamp = {time_now}, elapsed time = {end_time - start_time:.2f} s, '
                f'generated "{output_path.name}".'
            )


def build_argument_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="TI IWR6843 雷达处理流水线")
    parser.add_argument("--input-dir", required=True, type=Path, help="包含 XML 和 BIN 的输入目录")
    parser.add_argument("--output-dir", required=True, type=Path, help="H5 输出目录")
    parser.add_argument("--workers", type=int, default=None, help="处理进程数，默认使用一半 CPU")
    parser.add_argument(
        "--windows",
        nargs="+",
        default=("blackmanharris",),
        help="窗函数列表，支持 blackmanharris 和 flattop",
    )
    return parser


def main() -> None:
    """命令行入口。"""
    args = build_argument_parser().parse_args()
    config = ProcessingConfig(
        workers=args.workers,
        windows=tuple(args.windows),
    )
    run_processing(args.input_dir, args.output_dir, config)
