# TI-IWR2243-Cascade Processing

This directory contains the offline processing code for the TI IWR2243 Cascade millimeter-wave radar.

## Scope

1. Read raw `bin` data from a 4-chip cascade capture
2. Merge four-chip data and perform frequency and phase calibration
3. Compute Range FFT and Doppler FFT
4. Generate `speed` and `angle` heatmap data
5. Export per-frame images, aggregated `npz` files, and optional videos

## Directory Description

- `main.py`: processing entry point
- `src/iwr2243_cascade_processing/`: processing modules
- `requirements.txt`: runtime dependencies

## Usage

```bash
python main.py   --input-dir /path/to/raw_capture   --output-dir /path/to/output   --calibration-file /path/to/calibration.mat
```

If you want unified control over `speed / angle / point`, prefer using `../main.py` from the project root.

Optional arguments:

- `--workers`: number of processing workers; defaults to half of the CPU cores
- `--frame-limit`: limit the number of frames to process
- `--range-limit`: upper range limit for heatmap display; default is `2.5`
- `--disable-speed`: disable `speed` output and keep only `angle`
- `--export-data-only`: export only `npz` files without generating images
- `--render-video`: pass per-frame images to `ffmpeg` and compose videos

## Outputs

Each capture batch is exported to a separate directory containing:

- Optional `speed.h5`
- `angle.npz`
- `speed_heatmap/`
- `angle_heatmap/`
- Optional `speed_heatmap.mp4`
- Optional `angle_heatmap.mp4`
