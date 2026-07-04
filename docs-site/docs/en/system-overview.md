# System Overview

The repository supports two radar paths with similar goals and different hardware assumptions.

## TI IWR2243 Cascade

The cascade path handles a four-chip radar setup. The main challenge is that raw data arrives from multiple synchronized devices. Before signal processing can be trusted, the code must organize files, read matching frames, map channels, and apply calibration.

Main stages:

1. Discover complete `master`, `slave1`, `slave2`, and `slave3` file groups.
2. Read the same frame from all four devices.
3. Reorder RX channels for MIMO processing.
4. Apply frequency and phase calibration.
5. Run Range FFT and Doppler FFT.
6. Generate speed and angle heatmaps.
7. Render images or videos.

The cascade path is useful when spatial resolution matters and a larger virtual array is available.

## TI IWR6843

The IWR6843 path handles a single-chip radar setup. The input is simpler than the cascade path, but the code still needs to reconstruct frames, virtual antennas, and point clouds.

Main stages:

1. Parse the XML capture configuration.
2. Read raw BIN samples.
3. Split the sample stream into frames.
4. Reconstruct the virtual antenna matrix.
5. Run Range FFT, Doppler FFT, and Angle FFT.
6. Generate point clouds.
7. Save H5 and NPZ outputs.
8. Render range, speed, angle, and point-cloud visuals.

## How The Paths Match

Both paths recover target distance, motion, and spatial information from FMCW radar samples.

They differ mostly in input structure:

- IWR2243 Cascade starts with four synchronized device streams.
- IWR6843 starts with a single raw sample stream plus XML parameters.

They converge again at the output level: heatmaps, point clouds, structured files, and visual assets.
