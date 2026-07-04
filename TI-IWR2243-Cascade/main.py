"""TI IWR2243 Cascade 的统一运行入口。

该入口同时串联 Processing 和 Visualization 两条链路：先处理原始 4-chip
bin 数据得到 speed/angle 结果，再读取 Cascade.mat 导出标准化点云结果。
如果只需要其中一个阶段，也可以分别运行子目录下的 main.py。
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parent
PROCESSING_SRC = PROJECT_DIR / "Processing" / "src"
VISUALIZATION_SRC = PROJECT_DIR / "Visualization" / "src"

# 统一入口需要同时导入 Processing 和 Visualization 两套 src 包。
for path in (PROCESSING_SRC, VISUALIZATION_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from iwr2243_cascade_processing.config import CascadeProcessingConfig
from iwr2243_cascade_processing.pipeline import run_processing
from iwr2243_cascade_visualization.config import CascadeVisualizationConfig
from iwr2243_cascade_visualization.pipeline import run_visualization


def build_argument_parser() -> argparse.ArgumentParser:
    """构建统一入口的命令行参数解析器。"""
    parser = argparse.ArgumentParser(description="TI IWR2243 Cascade 统一处理入口")
    parser.add_argument("--raw-input-dir", required=True, type=Path, help="4-chip cascade 原始 bin 输入目录")
    parser.add_argument("--processing-output-dir", required=True, type=Path, help="speed / angle 输出目录")
    parser.add_argument("--point-cloud-mat", required=True, type=Path, help="Cascade.mat 输入路径")
    parser.add_argument("--point-output-dir", required=True, type=Path, help="点云输出目录")
    parser.add_argument("--calibration-file", type=Path, default=None, help="校准矩阵 mat 文件")
    parser.add_argument("--workers", type=int, default=None, help="默认进程数，未单独指定时使用该值")
    parser.add_argument("--processing-workers", type=int, default=None, help="处理链进程数")
    parser.add_argument("--visualization-workers", type=int, default=None, help="点云可视化进程数")
    parser.add_argument("--frame-limit", type=int, default=None, help="限制处理帧数")
    parser.add_argument("--range-limit", type=float, default=2.5, help="热力图显示的最大距离，单位米")
    parser.add_argument("--target-points", type=int, default=2048, help="每帧点云点数")
    parser.add_argument("--disable-speed", action="store_true", help="关闭 speed 输出，angle 与 point 仍然会输出")
    parser.add_argument("--processing-data-only", action="store_true", help="处理链只导出聚合数据，不生成逐帧图片")
    parser.add_argument("--point-data-only", action="store_true", help="点云链只导出 npz，不生成逐帧图片")
    parser.add_argument("--processing-video", action="store_true", help="将 speed / angle 图片合成为视频")
    parser.add_argument("--point-video", action="store_true", help="将点云图片合成为视频")
    return parser


def main() -> None:
    """按顺序运行级联雷达处理链和点云可视化链。"""
    args = build_argument_parser().parse_args()

    # 单独指定 worker 时优先使用阶段参数，否则共用 --workers。
    processing_workers = args.processing_workers if args.processing_workers is not None else args.workers
    visualization_workers = args.visualization_workers if args.visualization_workers is not None else args.workers

    processing_config = CascadeProcessingConfig(
        workers=processing_workers,
        frame_limit=args.frame_limit,
        range_limit_m=args.range_limit,
        enable_speed_output=not args.disable_speed,
        export_data_only=args.processing_data_only,
        render_video=args.processing_video,
    )
    # 第一阶段：从四芯片原始数据生成 speed/angle 热力图及聚合数据。
    run_processing(
        args.raw_input_dir,
        args.processing_output_dir,
        args.calibration_file,
        processing_config,
    )

    visualization_config = CascadeVisualizationConfig(
        workers=visualization_workers,
        target_points=args.target_points,
        render_video=args.point_video,
        export_data_only=args.point_data_only,
    )
    # 第二阶段：从 Cascade.mat 生成固定点数点云、图片和可选视频。
    run_visualization(
        args.point_cloud_mat,
        args.point_output_dir,
        visualization_config,
    )


if __name__ == "__main__":
    main()
