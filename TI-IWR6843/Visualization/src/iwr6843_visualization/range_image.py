from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .normalization import norm


def render_range(
    range_profiles: np.ndarray,
    start_bins: int,
    reasonable_bins: int,
    range_factor: float,
    periodicity: float,
    n_chirps: int,
    antenna: int,
    output_dir: Path,
    stem: str,
    export_assets_only: bool,
) -> None:
    """导出距离热力图。"""
    range_profiles = np.reshape(range_profiles, (range_profiles.shape[0], -1, range_profiles.shape[-1]))
    range_profiles = np.transpose(range_profiles, (1, 0, 2))
    range_profiles[:, :, antenna] = np.sum(range_profiles, axis=-1)
    range_profiles = range_profiles[start_bins * n_chirps : reasonable_bins * n_chirps, :, antenna]

    range_profiles_01 = norm(range_profiles)
    np.savez_compressed(output_dir / f"range_heatmap_{stem}.npz", range_profiles=range_profiles_01)

    if export_assets_only:
        return

    plt.figure(figsize=(12, 9))
    plt.imshow(
        range_profiles,
        extent=(0, periodicity * range_profiles.shape[1], start_bins * range_factor, reasonable_bins * range_factor),
        origin="lower",
        aspect="auto",
        cmap="jet",
    )
    plt.colorbar()
    plt.title(f"Heatmap of Range Profiles\n{stem}")
    plt.xlabel("Time (s)")
    plt.ylabel("Range (m)")
    plt.savefig(output_dir / f"range_heatmap_{stem}.png", dpi=300)
    plt.close()
