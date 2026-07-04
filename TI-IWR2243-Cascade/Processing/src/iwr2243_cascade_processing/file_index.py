"""发现并组织 TI IWR2243 Cascade 的四芯片采集文件。

一次完整采集需要 master、slave1、slave2、slave3 四个角色的 data/idx
文件同时存在。本模块根据文件名中的角色和采集编号把它们配成一组。
"""

from dataclasses import dataclass
from pathlib import Path
import re


ROLE_NAMES = ("master", "slave1", "slave2", "slave3")
DATA_PATTERN = re.compile(r"(?P<prefix>.*?)(?P<role>master|slave1|slave2|slave3).*?_(?P<file_idx>[^_]+)_data\.bin$")
IDX_PATTERN = re.compile(r"(?P<prefix>.*?)(?P<role>master|slave1|slave2|slave3).*?_(?P<file_idx>[^_]+)_idx\.bin$")


@dataclass(slots=True)
class CaptureGroup:
    """同一采集编号下的四芯片文件组。"""

    capture_id: str
    data_folder: Path
    data_files: dict[str, Path]
    idx_files: dict[str, Path]

    @property
    def output_stem(self) -> str:
        """生成该采集组对应的输出目录名。"""
        return f"capture_{self.capture_id}"


def _match_role(path: Path, pattern: re.Pattern[str]) -> tuple[str, str] | None:
    """从文件名中解析设备角色和采集编号。"""
    match = pattern.match(path.name)
    if match is None:
        return None
    return match.group("role"), match.group("file_idx")


def discover_capture_groups(input_dir: Path) -> list[CaptureGroup]:
    """扫描输入目录，返回所有完整的四芯片采集组。"""
    data_groups: dict[str, dict[str, Path]] = {}
    idx_groups: dict[str, dict[str, Path]] = {}

    for path in sorted(input_dir.glob("*_data.bin")):
        matched = _match_role(path, DATA_PATTERN)
        if matched is None:
            continue
        role, capture_id = matched
        data_groups.setdefault(capture_id, {})[role] = path

    for path in sorted(input_dir.glob("*_idx.bin")):
        matched = _match_role(path, IDX_PATTERN)
        if matched is None:
            continue
        role, capture_id = matched
        idx_groups.setdefault(capture_id, {})[role] = path

    capture_groups: list[CaptureGroup] = []
    for capture_id, files in data_groups.items():
        # data 和 idx 都必须包含四个角色；缺任意一个设备就跳过，避免后续帧拼接错位。
        if not all(role in files for role in ROLE_NAMES):
            continue
        if capture_id not in idx_groups or not all(role in idx_groups[capture_id] for role in ROLE_NAMES):
            continue
        capture_groups.append(
            CaptureGroup(
                capture_id=capture_id,
                data_folder=input_dir,
                data_files=files,
                idx_files=idx_groups[capture_id],
            )
        )

    return capture_groups
