# System Overview

The repository supports two radar paths with similar goals and different hardware assumptions.

At a high level, both paths try to answer the same questions:

- How far away is the target?
- Is the target moving, and in which velocity bin does it appear?
- From which direction does the signal arrive?
- Can the response be represented as a heatmap, point cloud, image, or video?

The difference is not the final sensing goal. The difference is how much work is needed before the data is ready for FFT and angle processing.

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

### Important folders

The cascade path is split into:

- `TI-IWR2243-Cascade/Processing/`
  - reads raw cascade captures,
  - groups master/slave files,
  - applies calibration,
  - exports speed and angle data.
- `TI-IWR2243-Cascade/Visualization/`
  - reads `Cascade.mat`,
  - normalizes point clouds,
  - exports point-cloud NPZ, images, and videos.

The unified `TI-IWR2243-Cascade/main.py` can run both stages from one command, but the two stages remain separate internally.

### What to check first

For cascade captures, check file completeness before looking at signal-processing parameters. A missing slave file or mismatched frame count can break the pipeline earlier than any FFT issue.

Useful checks:

- all four roles are present,
- data and idx files share the same capture id,
- the calibration file matches the capture setup,
- the requested frame limit does not exceed available frames.

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

### Important folders

The single-chip path is split into:

- `TI-IWR6843/Processing/`
  - parses XML configuration,
  - reads BIN raw samples,
  - reconstructs frames and virtual antennas,
  - exports H5 and point-cloud NPZ files.
- `TI-IWR6843/Visualization/`
  - reads H5 outputs,
  - renders range, speed, and angle heatmaps,
  - filters and resamples point clouds,
  - exports images, videos, and NPZ assets.

The IWR6843 path is a good place to understand the pipeline because there is less multi-device bookkeeping than the cascade path.

### What to check first

For IWR6843 captures, the XML file and BIN file must describe the same capture. If the XML frame count, sample count, or chirp count does not match the BIN length, frame splitting will be unreliable.

Useful checks:

- the XML file is present,
- the BIN file is present,
- the frame count is plausible,
- the chosen FFT sizes are large enough for the configured samples and chirps.

## How The Paths Match

Both paths recover target distance, motion, and spatial information from FMCW radar samples.

They differ mostly in input structure:

- IWR2243 Cascade starts with four synchronized device streams.
- IWR6843 starts with a single raw sample stream plus XML parameters.

They converge again at the output level: heatmaps, point clouds, structured files, and visual assets.

## Processing vs Visualization

The repository intentionally separates processing from visualization.

Processing modules should answer:

- how raw data is decoded,
- how arrays are shaped,
- which FFT is applied on which axis,
- which metadata is saved for later interpretation.

Visualization modules should answer:

- how arrays are normalized for display,
- which axes and ranges appear in a figure,
- whether output is saved as NPZ, PNG, or MP4,
- how point clouds are filtered and sampled.

This separation makes the project easier to debug. If an H5 file looks correct but the image looks wrong, the issue is likely in visualization. If the H5 arrays already look wrong, the issue is likely upstream in frame reconstruction, calibration, or FFT.

## Output Comparison

| Output | Usually Produced By | Main Use |
| --- | --- | --- |
| `speed.h5` | IWR2243 Processing | Store speed heatmap frames and physical scale metadata |
| `angle.npz` | IWR2243 Processing | Store angle heatmap frames |
| `point_cloud.npz` | IWR2243 Visualization | Store fixed-size cascade point-cloud frames |
| `*_blackmanharris.h5` | IWR6843 Processing | Store range, speed, angle, point cloud, and parameters |
| `*_points.npz` | IWR6843 Processing or Visualization | Store point-cloud frames for reuse |
| `*.png` / `*.mp4` | Visualization stages | Visual inspection and presentation |
