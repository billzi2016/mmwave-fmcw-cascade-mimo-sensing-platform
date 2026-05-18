from __future__ import annotations

import argparse
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from .calibration import apply_calibration, load_calibration
from .config import CascadeProcessingConfig
from .fft import run_processing_chain
from .file_index import CaptureGroup, discover_capture_groups
from .heatmap import build_angle_heatmap, build_speed_heatmap
from .raw_reader import read_cascade_frame, read_valid_frame_count
from .rendering import render_video_from_frames, save_angle_image, save_speed_image
from .storage import save_speed_h5


_WORKER_CONFIG: CascadeProcessingConfig | None = None
_WORKER_CALIBRATION: dict[str, np.ndarray] | None = None


def _init_worker(config: CascadeProcessingConfig, calibration: dict[str, np.ndarray] | None) -> None:
    global _WORKER_CONFIG, _WORKER_CALIBRATION
    _WORKER_CONFIG = config
    _WORKER_CALIBRATION = calibration


def _process_frame(task: tuple[CaptureGroup, int, Path | None, Path, bool]) -> tuple[int, np.ndarray | None, np.ndarray]:
    group, frame_index, speed_dir, angle_dir, export_data_only = task
    assert _WORKER_CONFIG is not None

    adc_data = read_cascade_frame(group, frame_index, _WORKER_CONFIG)
    adc_data = apply_calibration(adc_data, _WORKER_CALIBRATION, _WORKER_CONFIG)
    doppler_fft_out = run_processing_chain(adc_data, _WORKER_CONFIG)

    angle_heatmap = build_angle_heatmap(doppler_fft_out, _WORKER_CONFIG)
    speed_heatmap = None
    if _WORKER_CONFIG.enable_speed_output:
        speed_heatmap = build_speed_heatmap(doppler_fft_out, _WORKER_CONFIG)

    if not export_data_only:
        if speed_heatmap is not None and speed_dir is not None:
            save_speed_image(speed_heatmap, frame_index + 1, speed_dir, _WORKER_CONFIG)
        save_angle_image(angle_heatmap, frame_index + 1, angle_dir, _WORKER_CONFIG)

    return frame_index, speed_heatmap, angle_heatmap


def _run_capture_group(
    group: CaptureGroup,
    output_dir: Path,
    config: CascadeProcessingConfig,
    calibration: dict[str, np.ndarray] | None,
) -> None:
    frame_count = read_valid_frame_count(group.idx_files["master"])
    if config.frame_limit is not None:
        frame_count = min(frame_count, config.frame_limit)

    capture_output_dir = output_dir / group.output_stem
    speed_dir = capture_output_dir / "speed_heatmap" if config.enable_speed_output else None
    angle_dir = capture_output_dir / "angle_heatmap"
    capture_output_dir.mkdir(parents=True, exist_ok=True)

    print()
    print(f'>> capture_id = "{group.capture_id}"')
    print(f">> frame_count = {frame_count}")
    print(f'>> output_dir = "{capture_output_dir}"')
    print()

    tasks = [
        (group, frame_index, speed_dir, angle_dir, config.export_data_only)
        for frame_index in range(frame_count)
    ]

    workers = config.resolve_workers()
    with Pool(processes=workers, initializer=_init_worker, initargs=(config, calibration)) as pool:
        results = pool.map(_process_frame, tasks)

    results.sort(key=lambda item: item[0])
    angle_frames = np.stack([item[2] for item in results], axis=0)
    speed_frames = None
    if config.enable_speed_output:
        speed_frames = np.stack([item[1] for item in results if item[1] is not None], axis=0)

    if speed_frames is not None:
        save_speed_h5(
            capture_output_dir / "speed.h5",
            speed_frames,
            config.range_bin_size_m,
            config.velocity_bin_size_m_per_s,
        )
    np.savez_compressed(
        capture_output_dir / "angle.npz",
        angle_frames=angle_frames,
        range_bin_size_m=config.range_bin_size_m,
    )

    if config.render_video and not config.export_data_only:
        if speed_dir is not None:
            render_video_from_frames(speed_dir, capture_output_dir / "speed_heatmap.mp4")
        render_video_from_frames(angle_dir, capture_output_dir / "angle_heatmap.mp4")


def run_processing(
    input_dir: Path,
    output_dir: Path,
    calibration_file: Path | None,
    config: CascadeProcessingConfig,
) -> None:
    capture_groups = discover_capture_groups(input_dir)
    if not capture_groups:
        raise FileNotFoundError(f"在 {input_dir} 中没有发现完整的 4-chip cascade 数据组。")

    calibration = load_calibration(calibration_file)

    print()
    print(f'>> input_dir = "{input_dir}"')
    print(f'>> output_dir = "{output_dir}"')
    print(f'>> calibration_file = "{calibration_file}"')
    print(f">> workers = {config.resolve_workers()}")
    print(f">> range_fft_size = {config.range_fft_size}")
    print(f">> doppler_fft_size = {config.doppler_fft_size}")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)

    for group in capture_groups:
        _run_capture_group(group, output_dir, config, calibration)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TI IWR2243 Cascade Python 处理链")
    parser.add_argument("--input-dir", required=True, type=Path, help="4-chip cascade 原始 bin 输入目录")
    parser.add_argument("--output-dir", required=True, type=Path, help="speed / angle 输出目录")
    parser.add_argument("--calibration-file", type=Path, default=None, help="校准矩阵 mat 文件")
    parser.add_argument("--workers", type=int, default=None, help="处理进程数，默认使用一半 CPU")
    parser.add_argument("--frame-limit", type=int, default=None, help="限制处理帧数")
    parser.add_argument("--range-limit", type=float, default=2.5, help="热力图显示的最大距离，单位米")
    parser.add_argument("--disable-speed", action="store_true", help="关闭 speed 输出，angle 仍然会输出")
    parser.add_argument("--export-data-only", action="store_true", help="只导出 npz，不生成图片")
    parser.add_argument("--render-video", action="store_true", help="将逐帧图片合成为视频")
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    config = CascadeProcessingConfig(
        workers=args.workers,
        frame_limit=args.frame_limit,
        range_limit_m=args.range_limit,
        enable_speed_output=not args.disable_speed,
        export_data_only=args.export_data_only,
        render_video=args.render_video,
    )
    run_processing(args.input_dir, args.output_dir, args.calibration_file, config)
