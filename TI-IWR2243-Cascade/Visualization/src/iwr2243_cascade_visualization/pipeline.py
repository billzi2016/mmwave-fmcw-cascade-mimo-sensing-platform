"""TI IWR2243 Cascade 点云可视化主流水线。"""

from __future__ import annotations

import argparse
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from .config import CascadeVisualizationConfig
from .mat_reader import read_cascade_mat
from .rendering import compute_point_cloud_range, render_video_from_frames, save_point_cloud_image
from .xyz_extractor import build_point_cloud_frames


_WORKER_RANGE: tuple[float, float, float, float, float, float, float, float] | None = None
_WORKER_OUTPUT_DIR: Path | None = None
_WORKER_POINT_SIZE: float = 5.0


def _init_render_worker(
    data_range: tuple[float, float, float, float, float, float, float, float],
    output_dir: Path,
    point_size: float,
) -> None:
    """初始化点云渲染 worker 的共享上下文。"""
    global _WORKER_RANGE, _WORKER_OUTPUT_DIR, _WORKER_POINT_SIZE
    _WORKER_RANGE = data_range
    _WORKER_OUTPUT_DIR = output_dir
    _WORKER_POINT_SIZE = point_size


def _render_frame(task: tuple[int, np.ndarray]) -> None:
    """多进程渲染单帧点云图片。"""
    frame_index, point_cloud = task
    assert _WORKER_RANGE is not None
    assert _WORKER_OUTPUT_DIR is not None
    save_point_cloud_image(point_cloud, frame_index + 1, _WORKER_OUTPUT_DIR, _WORKER_RANGE, _WORKER_POINT_SIZE)


def run_visualization(input_mat: Path, output_dir: Path, config: CascadeVisualizationConfig) -> None:
    """运行完整点云可视化流程。"""
    xyz_all = read_cascade_mat(input_mat)
    point_cloud_frames = build_point_cloud_frames(xyz_all, config.target_points, config.xyz_limits)

    output_dir.mkdir(parents=True, exist_ok=True)
    # 先保存标准化点云数据；即使不渲染图片，也能直接复用该 npz。
    np.savez_compressed(output_dir / "point_cloud.npz", point_cloud_frames=point_cloud_frames)

    if config.export_data_only:
        return

    frame_dir = output_dir / "point_cloud_frames"
    data_range = compute_point_cloud_range(point_cloud_frames)
    tasks = [(frame_index, point_cloud_frames[frame_index]) for frame_index in range(len(point_cloud_frames))]

    workers = config.resolve_workers()
    if config.render_video:
        # 视频模式顺序渲染图片，再调用 ffmpeg 合成，避免并发写图导致帧缺失。
        for task in tasks:
            save_point_cloud_image(task[1], task[0] + 1, frame_dir, data_range, config.point_size)
        render_video_from_frames(frame_dir, output_dir / "point_cloud.mp4")
        return

    with Pool(
        processes=workers,
        initializer=_init_render_worker,
        initargs=(data_range, frame_dir, config.point_size),
    ) as pool:
        pool.map(_render_frame, tasks)


def build_argument_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="TI IWR2243 Cascade 点云可视化")
    parser.add_argument("--input-mat", required=True, type=Path, help="Cascade.mat 输入路径")
    parser.add_argument("--output-dir", required=True, type=Path, help="点云输出目录")
    parser.add_argument("--workers", type=int, default=None, help="绘图进程数，默认使用一半 CPU")
    parser.add_argument("--target-points", type=int, default=2048, help="每帧点数，默认 2048")
    parser.add_argument("--render-video", action="store_true", help="将点云图片合成为视频")
    parser.add_argument("--export-data-only", action="store_true", help="只导出 npz，不生成图片")
    return parser


def main() -> None:
    """命令行入口。"""
    args = build_argument_parser().parse_args()
    config = CascadeVisualizationConfig(
        workers=args.workers,
        target_points=args.target_points,
        render_video=args.render_video,
        export_data_only=args.export_data_only,
    )
    run_visualization(args.input_mat, args.output_dir, config)
