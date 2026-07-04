# mmWave FMCW Cascade MIMO Sensing Platform

This repository organizes an `FMCW` radar data processing and result visualization project for millimeter-wave sensing tasks. It covers two radar configurations: `TI IWR2243 Cascade` and `TI IWR6843`. The code is structured around offline data processing, result generation, and visualization, and is suitable for array sensing, motion observation, and point-cloud result analysis.

From the sensing perspective, this project corresponds to a typical `4D` millimeter-wave sensing problem: jointly recovering target `Range`, `Doppler`, `Azimuth`, and `Elevation` information from raw sampled data, then organizing the results as heatmaps, point clouds, and related visual outputs.

## Project Overview

The repository contains two core technical paths:

- `TI-IWR2243-Cascade`
  - Data processing and result generation for a four-chip cascaded millimeter-wave radar.
  - Compared with a single-chip solution, the cascaded pipeline first needs to merge multi-chip raw data, organize channels, and perform calibration before entering subsequent frequency-domain processing stages.
- `TI-IWR6843`
  - Offline processing and result visualization for a single-chip millimeter-wave radar.
  - The processing and visualization paths are clearly separated, making them easier to reuse across different capture batches and output formats.

From the engineering structure, both radar implementations are divided into `Processing` and `Visualization` stages:

- `Processing`
  - Handles raw sample loading, parameter parsing, data reshaping, calibration, and frequency-domain processing.
- `Visualization`
  - Organizes processed results into heatmaps, point clouds, videos, and other outputs that are easier to analyze and present.

This structure decouples raw data processing, result export, and visualization logic, making it easier to extend the project to different radar models, capture tasks, and output formats.

## Repository Structure

```text
mmwave-fmcw-cascade-mimo-sensing-platform/
├── DEMO/
├── TI-IWR2243-Cascade/
│   ├── Processing/
│   └── Visualization/
└── TI-IWR6843/
    ├── Processing/
    └── Visualization/
```

Directory responsibilities:

- `DEMO`
  - Demo assets and result descriptions, including array antenna layout diagrams, heatmap videos, point-cloud videos, and related visualization results.
- `TI-IWR2243-Cascade/Processing`
  - Handles raw data loading, merging, frequency calibration, phase calibration, `Range FFT`, `Doppler FFT`, and heatmap result export for the four-chip cascaded radar.
- `TI-IWR2243-Cascade/Visualization`
  - Provides display and visualization logic for cascaded radar processing results.
- `TI-IWR6843/Processing`
  - Handles raw sample loading, parameter parsing, virtual antenna reconstruction, range/speed/angle-domain processing, and point-cloud result export for the single-chip radar.
- `TI-IWR6843/Visualization`
  - Generates heatmaps, point clouds, videos, and other visual outputs from processing-stage results.

## Technical Features

### 1. Support for Different Radar Configurations

This repository covers both single-chip and four-chip cascaded `FMCW` radar configurations. Both serve the same sensing goal: extracting spatial and motion information. In implementation, the `2243 cascade` path is more complex because it requires synchronized multi-chip capture, array stitching, and stricter calibration.

### 2. Offline Processing-Oriented Project Structure

Both processing pipelines are designed mainly for offline batch processing. This makes it convenient to repeatedly process historical captures, tune parameters, and reproduce results. The entry points, dependencies, and module boundaries are clear, which also makes the project suitable for later extension into a standardized toolchain.

### 3. Clear Result Visualization Path

The repository separates processing and visualization into independent stages. This preserves intermediate signal-processing results while making it convenient to convert final outputs into intuitive heatmaps, point clouds, and videos for analysis, reporting, and project demonstrations.

### 4. Complete Radar Signal Processing Semantics

The core value of this project is not only obtaining outputs from existing hardware, but also building an interpretable processing pipeline from raw sampled data. Based on the current project structure, the key capabilities include:

- Range-domain and velocity-domain spectral processing based on `Range FFT` and `Doppler FFT`
- Target detection and candidate response filtering based on `CA-CFAR`
- `AoA` angle estimation and spatial information recovery based on virtual arrays
- Understanding and implementation of subspace spectral analysis methods such as `MUSIC` for high-resolution angle estimation
- Extension capability for array signal processing methods such as `beamforming`

The `beamforming` methods mentioned here are part of the array-processing capabilities that this project can support. They are included to clarify the understanding of millimeter-wave spatial spectrum processing. The current repository still focuses on offline processing, heatmap generation, point-cloud export, and result visualization.

## Processing Pipeline Overview

### TI-IWR2243-Cascade

The `TI IWR2243 Cascade` path focuses on organizing four-chip cascaded data into a unified representation before frequency-domain analysis:

1. Read `4-chip cascade` raw sampled data
2. Merge multi-chip data and map channels
3. Perform frequency calibration and phase calibration
4. Compute range-domain and velocity-domain spectra, then organize the input for subsequent angle estimation
5. Recover spatial information through array processing and export angle heatmaps, speed heatmaps, and related results

### TI-IWR6843

The `TI IWR6843` path is based on single-chip sampled data and focuses on standardized offline processing and visualization:

1. Read parameter files and raw sample files
2. Split frames and reconstruct virtual antenna data
3. Perform range, velocity, and angle-domain processing, then filter targets using detection results
4. Generate point clouds and intermediate result files
5. Export heatmaps, point-cloud images, or videos

## Technical Highlights

- Organizes the processing pipeline for `4D FMCW` radar sensing tasks, covering recovery of range, velocity, azimuth, and elevation information.
- Parses, merges, calibrates, and processes raw sampled data from `TI` millimeter-wave radar hardware instead of only consuming precomputed results.
- Includes implementation and result interpretation capabilities for key steps such as `CA-CFAR`, `AoA`, and `MUSIC`, with extension potential for array-processing methods such as `beamforming`.
- For the `TI IWR2243 Cascade` four-chip scenario, handles multi-chip data merging, channel mapping, and consistency calibration before entering high-dimensional array processing.

## DEMO Contents

The `DEMO` directory provides demonstration results corresponding to this repository's code, mainly including:

- `cascade 2243` array antenna position diagrams
- Heatmap results for human lateral motion
- Heatmap results for multi-position static captures
- Point-cloud motion visualization and corresponding `SNR` visualization results

This directory is intended for quickly understanding the array structure and output format. See [DEMO/README.md](DEMO/README.md) for detailed file descriptions.

## Reading Guide

- Start from this page if you want to understand the overall repository structure.
- Go directly to the `DEMO` directory if you want to inspect result examples first.
- Read `TI-IWR2243-Cascade/Processing` first if you are interested in the four-chip cascaded processing logic.
- Read `TI-IWR6843/Processing` and `TI-IWR6843/Visualization` first if you are interested in the single-chip offline processing and point-cloud visualization pipeline.
