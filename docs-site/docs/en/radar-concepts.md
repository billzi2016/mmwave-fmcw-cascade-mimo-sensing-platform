# Radar Concepts

This page introduces the main radar concepts used by the code.

If **Radar Basics** is the starting point, this page is the bridge to the actual configuration values and code modules in the repository.

## FMCW

FMCW radar transmits chirps whose frequency changes over time. Reflected signals are mixed with the transmitted signal. The resulting beat frequency is related to target distance.

In code, this becomes a sequence of ADC samples. The Range FFT turns those samples into distance bins.

## Range

Range is target distance. In the repository, range appears as:

- `range_profiles`,
- range heatmaps,
- distance axes in speed and angle plots,
- range-related conversion factors in H5 metadata.

## Doppler

Doppler describes target motion relative to the radar. Repeated chirps allow the system to observe phase changes over time. The Doppler FFT converts those changes into speed bins.

Speed heatmaps show how energy is distributed over distance and velocity.

## AoA And Angle

Angle of Arrival estimates where a signal comes from. The code uses virtual antenna groups to build angle spectra.

Angle heatmaps show response strength over range and angle. In the point-cloud path, angle estimates are combined with distance to compute x, y, and z coordinates.

## Virtual Array

A virtual array is formed from TX/RX combinations. It gives the signal-processing chain more spatial samples than a single physical receive row would provide.

This is especially important in the IWR2243 Cascade path, where multiple chips are stitched into a larger sensing aperture.

## Point Clouds

A radar point cloud is a set of estimated target points. In this repository, point-cloud rows commonly include:

- x,
- y,
- z,
- intensity or SNR,
- sometimes speed or additional diagnostic fields.

Point clouds are easier to inspect visually, but they are built from several earlier steps: frame reconstruction, FFT, candidate selection, angle estimation, and coordinate conversion.

## Configuration Parameters In Plain Language

Radar code contains many parameters. They can look intimidating at first, but most of them answer a small set of questions.

### Sampling parameters

These define how raw signals are captured:

- `num_adc_samples` or `n_samples`: how many ADC samples are collected in one chirp.
- `adc_sample_rate` or `sample_rate`: how fast ADC samples are collected.
- `start_frequency_hz` or `start_freq`: the radar carrier frequency.
- `chirp_slope_hz_per_s` or `freq_slope`: how quickly chirp frequency changes over time.
- `chirp_ramp_end_time_s` or `ramp_end_time`: how long the chirp ramp lasts.

These parameters affect range calculation. For example, sampling rate and chirp slope are used to convert beat frequency into distance.

### Chirp and frame parameters

These define how repeated measurements are grouped:

- `nchirp_loops` or `n_chirps`: how many chirps are repeated in a frame.
- `num_chirps_in_loop`: how many TX slots are used inside a loop.
- `frame_periodicity_s` or `periodicity`: time interval between frames.

Repeated chirps are necessary for Doppler processing. Without repeated chirps, the code cannot estimate target velocity in the same way.

### Antenna parameters

These define the spatial sensing layout:

- `num_tx` or `n_tx`: number of transmit channels.
- `num_rx` or `n_rx`: number of receive channels.
- `rx_for_mimo`: receive-channel reorder list for cascade MIMO processing.
- `ANTENNA_86`: virtual antenna mapping used by the IWR2243 cascade angle heatmap.
- `radar_matrix`: virtual antenna grouping used by the IWR6843 angle and point-cloud path.

These parameters affect angle estimation. Wrong channel order can still produce non-empty plots, but the spatial meaning will be wrong.

### FFT parameters

These define output resolution and processing shape:

- `range_fft_size` or `range_fft_n`: FFT size along ADC samples.
- `doppler_fft_size` or `speed_fft_n`: FFT size along chirps.
- `angle_fft_size` or `angle_fft_n`: FFT size along virtual antennas.

Larger FFT sizes can create finer bins, but they do not automatically create new physical information. They change the sampled frequency grid and the output shape.

### Display and filtering parameters

These control output readability:

- `range_limit_m`: maximum range shown in heatmaps.
- `target_points`: fixed number of points per point-cloud frame.
- `threshold_percentile`: point-cloud strength threshold.
- `speed_cut`: displayed fraction around the zero-speed region.
- `render_video`: whether to export MP4 videos.
- `export_data_only` or `export_assets_only`: whether to skip image/video rendering.

These parameters do not change the raw capture. They mainly affect what is saved or displayed.

## How IWR2243 Cascade Configuration Differs

The IWR2243 Cascade path has more multi-device configuration because four radar chips must be treated as one larger sensing system.

Important configuration ideas:

- `num_devices = 4`: four chips are expected.
- `num_rx_per_device = 4`: each device contributes four receive channels.
- total RX channels become `num_devices * num_rx_per_device`.
- `tx_to_enable` defines the TX order used by the processing chain.
- `rx_for_mimo` reorders channels into the expected MIMO layout.
- calibration parameters control frequency and phase correction.

The cascade path therefore spends more code on file grouping, channel reordering, and calibration before FFT results are trusted.

## How IWR6843 Configuration Differs

The IWR6843 path starts from one XML file and one or more BIN files. Many important capture parameters come from XML rather than a large static cascade config.

Important configuration ideas:

- XML provides frequency slope, sample rate, start frequency, sample count, frame count, and chirp count.
- `ProcessingConfig` provides FFT sizes, point count, angle search settings, and window functions.
- `frame_extractor.py` defines how raw LVDS samples become virtual antenna data.
- `radar_matrix` defines which virtual antennas are grouped for angle processing.

This path is easier to trace because the input is single-device, but the frame reconstruction still needs exact layout assumptions.

## Why Parameters Should Not Be Changed Blindly

Many parameters are tied to hardware capture settings. If a value describes how the radar was configured during collection, changing it after capture can make the parser or physical conversion wrong.

Good candidates for experimentation:

- output directory,
- frame limit,
- video rendering switch,
- range display limit,
- point-cloud target count,
- visualization thresholds.

Parameters that require more care:

- sample rate,
- chirp slope,
- number of ADC samples,
- number of chirps,
- TX/RX mapping,
- calibration matrices.

When in doubt, first verify array shapes and output files before tuning physical parameters.
