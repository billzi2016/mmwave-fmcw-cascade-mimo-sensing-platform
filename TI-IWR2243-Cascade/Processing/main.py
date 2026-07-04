"""TI IWR2243 Cascade 处理阶段的命令行入口。

该文件只负责定位当前目录下的 src 包，并把实际执行逻辑交给
``iwr2243_cascade_processing.pipeline.main``。这样用户可以直接运行本文件，
不需要先把 src 安装成 Python 包。
"""

from pathlib import Path
import sys


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

# 允许从当前工程目录直接导入 src 下的处理模块。
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from iwr2243_cascade_processing.pipeline import main


if __name__ == "__main__":
    # 保持入口文件足够薄，所有参数解析和处理流程都放在 pipeline 中。
    main()
