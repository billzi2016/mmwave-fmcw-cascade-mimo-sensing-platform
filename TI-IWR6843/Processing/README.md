# TI-IWR6843 Processing

This directory contains the offline processing code for the TI IWR6843 millimeter-wave radar.

## Directory Description

- `main.py`: processing entry point
- `src/iwr6843_processing/`: processing modules
- `requirements.txt`: runtime dependencies

## Processing Pipeline

1. Read the `xml` parameter file in the input directory
2. Read the raw `bin` sample file in the input directory
3. Split frames and reconstruct virtual antenna data
4. Run range FFT, Doppler FFT, and AoA angle FFT
5. Directly generate point clouds and export `h5` / `npz`

## Usage

```bash
python main.py --input-dir /path/to/raw_data --output-dir /path/to/output
```

Optional arguments:

- `--workers`: specify the number of processes; defaults to half of the CPU cores
- `--windows`: specify the window function; default is `blackmanharris`

## Outputs

Each `bin` file is exported as one `h5` file according to the selected window function. The file contains:

- `range_profiles`
- `speed_profiles`
- `angle_profiles`
- `points_frames`
- `param`

An additional point-cloud result file is also exported:

- `*_points.npz`
