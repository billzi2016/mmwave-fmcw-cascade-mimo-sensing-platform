# TI-IWR6843 Visualization

This directory contains result visualization code for the TI IWR6843 millimeter-wave radar.

## Directory Description

- `main.py`: visualization entry point
- `src/iwr6843_visualization/`: visualization modules
- `requirements.txt`: runtime dependencies

## Scope

1. Read `h5` files exported by the processing stage
2. Export range, speed, and AoA angle heatmaps
3. Read or generate point-cloud `npz` files
4. Generate static point-cloud images or videos

## Concurrency Strategy

- Image and `npz` generation uses multiprocessing by default with half of the CPU cores
- Video generation runs sequentially in a single process and delegates export to `ffmpeg`

## Output Rules

- `AoA / angle` is exported by default
- `point cloud` is exported by default
- If `speed_profiles` exists in the result, `speed` visualization is exported
- If `speed_profiles` does not exist in the result, `speed` visualization is skipped automatically

## Usage

Generate images and `npz` files:

```bash
python main.py --input-dir /path/to/h5 --output-dir /path/to/output
```

Generate videos:

```bash
python main.py --input-dir /path/to/h5 --output-dir /path/to/output --render-video
```
