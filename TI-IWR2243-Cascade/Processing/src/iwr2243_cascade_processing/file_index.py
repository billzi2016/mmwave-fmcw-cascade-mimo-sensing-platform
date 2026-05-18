from dataclasses import dataclass
from pathlib import Path
import re


ROLE_NAMES = ("master", "slave1", "slave2", "slave3")
DATA_PATTERN = re.compile(r"(?P<prefix>.*?)(?P<role>master|slave1|slave2|slave3).*?_(?P<file_idx>[^_]+)_data\.bin$")
IDX_PATTERN = re.compile(r"(?P<prefix>.*?)(?P<role>master|slave1|slave2|slave3).*?_(?P<file_idx>[^_]+)_idx\.bin$")


@dataclass(slots=True)
class CaptureGroup:
    capture_id: str
    data_folder: Path
    data_files: dict[str, Path]
    idx_files: dict[str, Path]

    @property
    def output_stem(self) -> str:
        return f"capture_{self.capture_id}"


def _match_role(path: Path, pattern: re.Pattern[str]) -> tuple[str, str] | None:
    match = pattern.match(path.name)
    if match is None:
        return None
    return match.group("role"), match.group("file_idx")


def discover_capture_groups(input_dir: Path) -> list[CaptureGroup]:
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
