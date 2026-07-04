# Getting Started

This page gives the shortest useful path through the repository.

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

## Suggested Reading Order

If you are new to the project, use this order:

1. Look at the `DEMO/` folder to see expected outputs.
2. Read the top-level README to understand the two radar paths.
3. Open the processing README for the radar you care about.
4. Read the visualization README for the output format you need.
5. Use this documentation site when you want a slower explanation of the pipeline.

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

## Where To Run Commands

Each processing or visualization subproject has its own `main.py`.

- Run processing commands inside a `Processing/` directory.
- Run visualization commands inside a `Visualization/` directory.
- Use `TI-IWR2243-Cascade/main.py` when you want both cascade processing and point-cloud visualization from one command.
