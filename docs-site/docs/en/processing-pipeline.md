# Processing Pipeline

This page explains the data flow from raw samples to visual outputs.

The pipeline is easiest to read as a sequence of shape changes. At first the data is a raw one-dimensional or multi-file sample stream. Later it becomes a complex-valued tensor. After FFT stages, it becomes range, velocity, and angle spectra. Finally it is compressed into heatmaps or converted into point-cloud coordinates.

## 1. Raw Input

Raw radar samples are not yet meaningful images or point clouds. They are encoded streams of ADC values. The first task is to recover the shape of the measurement:

- frame index,
- chirp index,
- ADC sample index,
- TX/RX channel,
- I/Q complex sample.

The raw input stage is also where file assumptions matter. A capture can fail before any radar math happens if the expected files are missing, if frame counts do not match, or if the XML parameters do not describe the BIN file.

For that reason, the processing code starts with file discovery and parameter parsing instead of jumping directly to FFT.

## 2. Frame Reconstruction

For IWR2243 Cascade, each frame is read from four device files and concatenated along the RX dimension. For IWR6843, the single BIN stream is split into frames and then reshaped into a virtual antenna matrix.

This stage is mostly about data layout. If the layout is wrong, every later FFT or angle estimate will look wrong even if the formulas are correct.

Common layout operations include:

- converting interleaved I/Q integers into complex samples,
- reshaping one-dimensional samples into frame/chirp/sample dimensions,
- transposing axes into the order expected by FFT code,
- mapping physical channels into virtual antenna indices.

These operations are simple individually, but the exact axis order matters. The code comments around reshape and transpose are intentionally detailed because those are high-risk locations.

## 3. Calibration

The cascade path applies frequency and phase calibration before FFT. This matters because multiple chips must behave like one coherent array.

Calibration reduces channel-to-channel mismatch and makes angle-domain processing more reliable.

In this repository, calibration appears most clearly in the IWR2243 Cascade path. The code uses calibration matrices to correct frequency and phase differences across TX/RX channels.

If calibration is disabled or mismatched, range and speed heatmaps may still show energy, but angle estimates can become unstable because the virtual array no longer has a coherent phase reference.

## 4. Range FFT

Range FFT converts fast-time ADC samples into distance bins. A target at a certain distance creates a beat frequency, and the FFT maps that frequency to a range bin.

The code applies a window before FFT when configured. Windowing reduces spectral leakage and makes the result easier to interpret.

The output of Range FFT is still not a final image. It is an intermediate spectrum. Later stages either run Doppler FFT over repeated chirps or select distance bins for visualization.

When reading code, check the FFT axis:

- Range FFT should operate along the ADC sample dimension.
- Doppler FFT should operate along the chirp or slow-time dimension.
- Angle FFT should operate along the antenna or virtual-array dimension.

## 5. Doppler FFT

Doppler FFT operates along the chirp dimension. It detects phase changes across chirps and maps them to velocity bins.

After `fftshift`, zero velocity is centered, negative and positive motion appear on opposite sides, and speed heatmaps become easier to read.

The Doppler output can be interpreted as a range-speed response. For visualization, the code often collapses antenna channels by summing energy, then converts the magnitude to a display-friendly scale.

This step is useful for motion inspection, but it also hides per-antenna detail. If angle estimation is the goal, the channel structure must be preserved until angle processing.

## 6. Angle Processing

Angle processing uses the virtual antenna dimension. The code arranges TX/RX channels into array groups and performs an angle FFT or related AoA mapping.

The output is a spatial response: where a target appears in angle or in 3D point-cloud coordinates.

Angle processing depends strongly on correct channel ordering. A wrong antenna map can produce plausible-looking energy but incorrect spatial interpretation.

For the cascade path, `ANTENNA_86` defines how virtual antenna entries are pulled from the TX/RX frequency-domain tensor. For the IWR6843 path, `radar_matrix` groups virtual antennas for later AoA processing.

## 7. Outputs

The final outputs serve different tasks:

- **H5** keeps full processing results for later analysis.
- **NPZ** stores compact arrays for visualization or downstream scripts.
- **PNG** is good for quick inspection.
- **MP4** is useful for motion review and presentation.

Processing and visualization are separated so expensive signal processing does not need to be repeated just to change the display format.

## Failure Signals

Different failures show up in different places:

- Missing or mismatched input files usually fail during discovery or frame splitting.
- Wrong reshape or channel order often produces strange but non-empty heatmaps.
- Bad calibration often affects angle stability more than raw range energy.
- Overly strict point-cloud filtering can produce sparse or repeated point clouds.
- Incorrect output paths can make processing look like it failed even when arrays were created.

## Practical Debug Flow

When a new capture does not look right, use this order:

1. Confirm the input files and frame count.
2. Confirm that structured outputs were written.
3. Inspect NPZ/H5 array shapes.
4. Check one static PNG before rendering a full video.
5. Only then tune FFT sizes, range limits, clustering thresholds, or point counts.

This order keeps debugging grounded in observable outputs.
