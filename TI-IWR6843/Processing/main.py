from pathlib import Path
import sys


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from iwr6843_processing.pipeline import main


if __name__ == "__main__":
    main()
