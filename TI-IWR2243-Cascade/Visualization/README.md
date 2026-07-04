# TI-IWR2243-Cascade Visualization

This directory contains point-cloud visualization and standardized engineering code for TI IWR2243 Cascade.

## Scope

1. Read `Cascade.mat`
2. Extract the point-cloud subspace
3. Perform SNR-weighted sampling and DBSCAN cleanup
4. Export fixed-size point clouds as `npz`
5. Export per-frame point-cloud images and optional videos

## Usage

```bash
python main.py   --input-mat /path/to/Cascade.mat   --output-dir /path/to/output
```

If you want unified control over `speed / angle / point`, prefer using `../main.py` from the project root.

Optional arguments:

- `--workers`: number of plotting workers; defaults to half of the CPU cores
- `--target-points`: number of points retained per frame; default is `2048`
- `--render-video`: pass point-cloud images to `ffmpeg` and compose a video
- `--export-data-only`: export only `npz` files without generating images
