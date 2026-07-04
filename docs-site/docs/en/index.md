# mmWave FMCW Cascade MIMO Sensing Platform

This documentation explains a radar processing and visualization project for millimeter-wave FMCW sensing.

The repository contains two radar paths:

- **TI IWR2243 Cascade**: a four-chip cascaded radar path for higher-dimensional array sensing.
- **TI IWR6843**: a single-chip radar path for offline processing, heatmaps, and point-cloud visualization.

The project focuses on offline workflows. Raw captures are processed into range, velocity, angle, and point-cloud outputs that can be inspected as images, videos, H5 files, and NPZ assets.

## What You Can Learn Here

Start with the simple pages first:

1. **Getting Started** explains the repository layout and what each folder is for.
2. **System Overview** connects the two radar hardware paths with their outputs.
3. **Processing Pipeline** walks through the data flow from raw samples to visual results.
4. **Radar Concepts** introduces the core signal-processing ideas behind the code.
5. **Project Notes** explains how to maintain and extend the project.

The goal is to introduce the project gradually: first outputs and file layout, then FFT, virtual arrays, calibration, and point-cloud generation.

## Output Types

The repository produces several kinds of artifacts:

- **Range heatmaps** for observing distance-domain responses.
- **Speed heatmaps** for observing Doppler-domain motion.
- **Angle heatmaps** for observing spatial responses.
- **Point clouds** for visualizing 3D target structure and motion.
- **NPZ/H5 files** for structured downstream analysis.
- **MP4 videos** for presentations and visual inspection.

## Language Structure

The documentation is bilingual:

- English pages live under `docs/en/`.
- Chinese pages live under `docs/zh/`.

Both languages follow the same page structure, so readers can switch languages without losing context.
