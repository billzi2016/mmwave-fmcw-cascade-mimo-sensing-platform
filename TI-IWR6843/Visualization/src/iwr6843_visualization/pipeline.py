"""TI IWR6843 可视化主流水线。

本文件读取 Processing 阶段生成的 H5，导出 range/speed/angle 热力图资产，
并整理点云结果为 NPZ、PNG 或 MP4。
"""

from __future__ import annotations

import argparse
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from .angle_image import render_angle
from .config import VisualizationConfig
from .dbscan_cluster import build_cluster
from .h5_loader import load_h5
from .point_cloud_processor import merge_frame, threshold_segment
from .point_cloud_vis import render_point_cloud
from .range_image import render_range
from .speed_image import render_speed


def _process_h5(args: tuple[Path, Path, VisualizationConfig]) -> None:
    """处理单个 H5 结果文件。"""
    h5_path, output_dir, config = args
    stem = h5_path.stem

    (
        range_profiles,
        speed_profiles,
        angle_profiles,
        points_frames,
        start_bins,
        reasonable_bins,
        range_factor,
        periodicity,
        n_chirps,
        speed_factor,
    ) = load_h5(h5_path)

    file_output_dir = output_dir / stem
    file_output_dir.mkdir(parents=True, exist_ok=True)

    # range 图一定存在；speed 图兼容 Processing 阶段未导出的情况。
    render_range(
        range_profiles,
        start_bins,
        reasonable_bins,
        range_factor,
        periodicity,
        n_chirps,
        0,
        file_output_dir,
        stem,
        config.export_assets_only,
    )
    if speed_profiles is not None:
        render_speed(
            speed_profiles,
            start_bins,
            reasonable_bins,
            range_factor,
            speed_factor,
            config.speed_cut,
            0,
            file_output_dir,
            stem,
            config.render_video,
            config.export_assets_only,
        )
    render_angle(
        angle_profiles,
        start_bins,
        reasonable_bins,
        range_factor,
        0,
        file_output_dir,
        stem,
        config.render_video,
        config.export_assets_only,
    )

    # 点云显示前先合并短时间窗口，再按强度筛选并聚类清理，最后固定点数。
    points_frames = merge_frame(points_frames, config.merge_frames)
    points_frames = threshold_segment(points_frames, config.threshold_percentile)
    points_frames = build_cluster(points_frames, config.target_count, single_process=config.render_video)
    np.savez_compressed(file_output_dir / f"{stem}_points.npz", points_frames=points_frames)

    render_point_cloud(
        points_frames,
        file_output_dir,
        stem,
        config.render_video,
        config.export_assets_only,
        config.point_alpha,
        config.point_size,
    )


def run_visualization(input_dir: Path, output_dir: Path, config: VisualizationConfig) -> None:
    """运行 IWR6843 可视化流程。"""
    h5_files = sorted(input_dir.glob("*.h5"))
    if not h5_files:
        raise FileNotFoundError(f"在 {input_dir} 中没有找到 H5 文件。")

    workers = config.resolve_workers()

    print()
    print(f'>> input_dir = "{input_dir}"')
    print(f'>> output_dir = "{output_dir}"')
    print(f">> workers = {workers}")
    print(f">> render_video = {config.render_video}")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)

    if config.render_video:
        # 视频渲染涉及 ffmpeg 和逐帧写图，顺序执行更容易保证输出稳定。
        for h5_path in h5_files:
            _process_h5((h5_path, output_dir, config))
        return

    args_list = [(h5_path, output_dir, config) for h5_path in h5_files]
    # 多个 H5 文件之间互不依赖，可以并行导出图片和 NPZ。
    with Pool(workers) as pool:
        pool.map(_process_h5, args_list)


def build_argument_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="TI IWR6843 雷达可视化流水线")
    parser.add_argument("--input-dir", required=True, type=Path, help="H5 输入目录")
    parser.add_argument("--output-dir", required=True, type=Path, help="结果输出目录")
    parser.add_argument("--workers", type=int, default=None, help="进程数，默认使用一半 CPU")
    parser.add_argument("--render-video", action="store_true", help="启用视频导出，自动切换为单进程")
    parser.add_argument("--export-assets-only", action="store_true", help="只导出 npz，不生成图片或视频")
    return parser


def main() -> None:
    """命令行入口。"""
    args = build_argument_parser().parse_args()
    config = VisualizationConfig(
        workers=args.workers,
        render_video=args.render_video,
        export_assets_only=args.export_assets_only,
    )
    run_visualization(args.input_dir, args.output_dir, config)
