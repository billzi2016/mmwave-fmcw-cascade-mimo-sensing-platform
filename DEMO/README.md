# Demo Overview

This directory collects representative demo results for the `FMCW` millimeter-wave radar project. It shows the array structure, motion observation outputs, and point-cloud and signal-to-noise-ratio visualization results. The contents correspond to the cascaded-radar and single-chip-radar processing pipelines in this repository, and provide a quick entry point for understanding the overall output formats.

From the result perspective, these demos correspond to typical outputs in `4D` millimeter-wave sensing: range, velocity, azimuth, and elevation information around targets, further organized as heatmaps, point clouds, and auxiliary analysis results.

## Content Overview

The current demo results are divided into two parts:

- `cascade 2243` array antenna layout diagrams
- Heatmap and point-cloud visualization videos for motion scenarios

## Array Layout

The two `png` images show the antenna position layout of the `TI IWR2243 Cascade` array. This cascaded solution uses four radar chips working together, forming higher-dimensional observation capability after array organization. The summarized array configuration is:

- 86 antennas in the horizontal direction
- 11 antennas in the vertical direction

This array structure provides the foundation for angle estimation, spatial resolution, and point-cloud generation, and is an important prerequisite for `4D` imaging capability.

Related files:

- `cascade_2243_antenna_layout_86h_11v_drawio.png`
  - A drawn version of the array layout, used to inspect antenna position relationships and the overall arrangement.
- `cascade_2243_antenna_layout_86h_11v_signal.png`
  - A signal-oriented array layout diagram, used to help understand channel organization and array configuration.

## Motion Observation Results

### Human Lateral Motion Scenario

The following two videos correspond to a human lateral-motion scenario and can be used to observe how angle-domain and velocity-domain responses change during motion:

- `human_lateral_motion_angle_heatmap.mp4`
  - Shows angle heatmap changes during human lateral motion.
- `human_lateral_motion_speed_heatmap.mp4`
  - Shows speed heatmap changes during human lateral motion.

### Multi-Position Static Capture Scenario

The following two videos correspond to static captures at multiple positions. They show the angle-domain and velocity-domain distribution characteristics of targets at different spatial locations:

- `multi_position_static_capture_angle_heatmap.mp4`
  - Shows the angle heatmap under multi-position static capture conditions.
- `multi_position_static_capture_speed_heatmap.mp4`
  - Shows the speed heatmap under multi-position static capture conditions.

## Point Cloud and SNR Visualization

The following two videos show point-cloud results and the corresponding signal-to-noise-ratio information:

- `point_cloud_back_and_forth_motion.mp4`
  - Shows point-cloud changes during back-and-forth target motion.
- `point_cloud_snr_visualization.mp4`
  - Shows the `SNR` visualization corresponding to the point-cloud results.

Combining point-cloud and `SNR` results makes it easier to observe target trajectories, spatial distributions, and echo-strength changes.

In the context of this repository's processing pipeline, these results are usually built on joint range-domain, velocity-domain, and angle-domain processing, and can further connect to key steps such as target detection, angle estimation, and spatial spectrum analysis.

## How to Use This Directory

- Inspect the two antenna layout diagrams first if you want to quickly understand the `2243 cascade` array structure.
- Inspect the heatmap and point-cloud videos first if you want to view motion-sensing results.
- Use this directory as a direct example of system output formats if the results are needed for project presentations or interviews.
