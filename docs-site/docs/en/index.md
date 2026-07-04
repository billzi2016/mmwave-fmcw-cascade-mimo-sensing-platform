# mmWave FMCW Cascade MIMO Sensing Platform

This documentation explains a radar processing and visualization project for millimeter-wave FMCW sensing.

The repository contains two radar paths:

- **TI IWR2243 Cascade**: a four-chip cascaded radar path for higher-dimensional array sensing.
- **TI IWR6843**: a single-chip radar path for offline processing, heatmaps, and point-cloud visualization.

The project focuses on offline workflows. Raw captures are processed into range, velocity, angle, and point-cloud outputs that can be inspected as images, videos, H5 files, and NPZ assets.

The code is useful when you want to understand the full path from raw radar samples to visual outputs. It does not treat the radar as a black box. The repository keeps the intermediate processing stages visible: file grouping, frame reconstruction, calibration, FFT processing, heatmap generation, point-cloud normalization, and final rendering.

## Project Links

- GitHub repository: <https://github.com/billzi2016/mmwave-fmcw-cascade-mimo-sensing-platform>
- Documentation site: <https://billzi2016.github.io/mmwave-fmcw-cascade-mimo-sensing-platform/>

Use the GitHub repository when you need source code, commits, issues, or the deployment workflow. Use this documentation site when you want a guided explanation of the radar workflow before opening implementation files.

## Who This Site Is For

This site is written for several kinds of readers:

- A reader who wants to quickly understand what this repository does.
- A developer who needs to run the processing code on new captures.
- A researcher who wants to inspect how range, Doppler, angle, and point-cloud results are produced.
- A maintainer who needs to extend the code without breaking the existing processing layout.

The pages start with the visible outputs and folder structure. Later pages move into signal-processing concepts and implementation details.

## How The GitHub Repository And This Site Work Together

The GitHub repository is the source of truth for code. It contains the radar processing modules, visualization scripts, README files, and the MkDocs source used to build this site.

The documentation site is the readable layer. It does not replace the code or README files. It gives a slower path through the project, especially for readers who are new to radar, FMCW, or the difference between processing and visualization.

When reading both together, a practical workflow is:

1. Open this site to understand the idea and terminology.
2. Open the GitHub repository to inspect the matching files.
3. Use the README files for concrete command examples.
4. Return to this site when a processing step or parameter needs context.

## What You Can Learn Here

Start with the simple pages first:

1. **Getting Started** explains the repository layout and what each folder is for.
2. **System Overview** connects the two radar hardware paths with their outputs.
3. **Processing Pipeline** walks through the data flow from raw samples to visual results.
4. **Radar Concepts** introduces the core signal-processing ideas behind the code.
5. **Project Notes** explains how to maintain and extend the project.

The goal is to introduce the project gradually: first outputs and file layout, then FFT, virtual arrays, calibration, and point-cloud generation.

## Main Workflows

The repository is easier to understand if you separate it into four workflows.

### 1. Inspect demo results

The `DEMO/` folder gives a quick view of what the project can produce. It contains antenna layout images, heatmap videos, and point-cloud visualization outputs. This is the best starting point if you want to see the expected result format before reading code.

### 2. Process raw radar captures

The `Processing/` folders read raw radar data and produce structured outputs. This stage handles the expensive and sensitive steps: parsing capture parameters, reshaping raw samples, applying calibration, and running FFTs.

### 3. Export visual assets

The `Visualization/` folders read processed arrays and export images, videos, or normalized assets. This separation means you can rerender results without rerunning the full radar signal-processing chain.

### 4. Maintain documentation

The `docs-site/` folder contains this bilingual documentation site. English files live in `docs/en/`; Chinese files live in `docs/zh/`.

## Output Types

The repository produces several kinds of artifacts:

- **Range heatmaps** for observing distance-domain responses.
- **Speed heatmaps** for observing Doppler-domain motion.
- **Angle heatmaps** for observing spatial responses.
- **Point clouds** for visualizing 3D target structure and motion.
- **NPZ/H5 files** for structured downstream analysis.
- **MP4 videos** for presentations and visual inspection.

These outputs serve different needs. Heatmaps are compact and easy to compare frame by frame. Point clouds are more spatial and intuitive. H5 and NPZ files are better for scripts, model training, or repeated visualization experiments.

## What This Site Does Not Assume

You do not need to start with a complete radar background. The documentation explains the necessary concepts in context. When a page mentions Range FFT, Doppler FFT, AoA, or virtual arrays, it connects those terms back to the files and outputs in this repository.

You also do not need to read every page before using the code. If you only need to run an existing command, start with **Getting Started**. If you need to modify processing internals, continue into **Processing Pipeline** and **Radar Concepts**.

## Language Structure

The documentation is bilingual:

- English pages live under `docs/en/`.
- Chinese pages live under `docs/zh/`.

Both languages follow the same page structure, so readers can switch languages without losing context.
