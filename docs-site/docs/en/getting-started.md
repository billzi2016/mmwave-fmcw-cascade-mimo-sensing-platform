# Getting Started

This page gives the shortest useful path through the repository.

It is not a command reference for every script. Instead, it explains how the folders fit together, what output to expect, and which part of the repository to open next.

## Repository Shape

The code is organized around two radar systems:

```text
mmwave-fmcw-cascade-mimo-sensing-platform/
├── DEMO/
├── TI-IWR2243-Cascade/
│   ├── Processing/
│   └── Visualization/
├── TI-IWR6843/
│   ├── Processing/
│   └── Visualization/
└── docs-site/
```

The `Processing` folders transform raw radar captures into structured arrays, heatmaps, and point-cloud data. The `Visualization` folders turn processed arrays into images, videos, and normalized assets.

The top-level split is intentional:

- `DEMO/` shows what good output looks like.
- `TI-IWR2243-Cascade/` contains the four-chip cascade path.
- `TI-IWR6843/` contains the single-chip path.
- `docs-site/` contains this MkDocs documentation site.

Inside each radar folder, `Processing` and `Visualization` are separated because they answer different questions. Processing asks: how do raw samples become structured arrays? Visualization asks: how do structured arrays become readable outputs?

## Suggested Reading Order

If you are new to the project, use this order:

1. Look at the `DEMO/` folder to see expected outputs.
2. Read the top-level README to understand the two radar paths.
3. Open the processing README for the radar you care about.
4. Read the visualization README for the output format you need.
5. Use this documentation site when you want a slower explanation of the pipeline.

If you already know which radar you are using, you can skip directly to that path. If you are comparing the two paths, read **System Overview** before opening the code.

## Minimal Mental Model

The project takes raw radar samples and gradually turns them into easier-to-read forms:

```text
raw samples
-> frame reconstruction
-> calibration
-> Range FFT
-> Doppler FFT
-> Angle FFT / AoA
-> heatmaps and point clouds
-> images, videos, H5, NPZ
```

You do not need to understand all signal-processing details before using the repository. Start with the input folder, output folder, and expected result type. Then move deeper as needed.

## Choosing The Right Path

Use **TI-IWR2243 Cascade** when your data comes from a four-chip cascade capture. You should expect multiple device files and a calibration file. This path is more complex because the code must keep several devices aligned and coherent.

Use **TI-IWR6843** when your data comes from a single-chip capture with XML parameters and BIN samples. This path is easier to follow and is a good starting point for understanding frame extraction, FFT processing, and point-cloud generation.

## Input And Output Checklist

Before running a processing script, check the input files:

- For IWR2243 Cascade, confirm that `master`, `slave1`, `slave2`, and `slave3` data and idx files are all present.
- For IWR2243 Cascade, confirm whether a calibration `.mat` file should be supplied.
- For IWR6843, confirm that the input directory contains both XML parameters and BIN raw samples.
- For visualization, confirm that the expected H5, NPZ, or MAT file already exists.

After running a script, check the output folder:

- If you requested data only, expect H5 or NPZ files.
- If image rendering is enabled, expect frame folders or PNG files.
- If video rendering is enabled, expect MP4 files after frame rendering.

## Where To Run Commands

Each processing or visualization subproject has its own `main.py`.

- Run processing commands inside a `Processing/` directory.
- Run visualization commands inside a `Visualization/` directory.
- Use `TI-IWR2243-Cascade/main.py` when you want both cascade processing and point-cloud visualization from one command.

## First Debug Checks

If output looks wrong, start with simple checks:

1. Confirm the input path points to the expected capture.
2. Confirm the frame count is reasonable.
3. Confirm output files were created before judging image quality.
4. For heatmaps, check whether the range limit hides useful bins.
5. For point clouds, check whether spatial limits or fixed-point sampling removed too many points.

These checks are faster than changing signal-processing parameters immediately.
