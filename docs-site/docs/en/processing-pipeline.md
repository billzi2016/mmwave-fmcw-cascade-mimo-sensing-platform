# Processing Pipeline

This page explains the data flow from raw samples to visual outputs.

## 1. Raw Input

Raw radar samples are not yet meaningful images or point clouds. They are encoded streams of ADC values. The first task is to recover the shape of the measurement:

- frame index,
- chirp index,
- ADC sample index,
- TX/RX channel,
- I/Q complex sample.

## 2. Frame Reconstruction

For IWR2243 Cascade, each frame is read from four device files and concatenated along the RX dimension. For IWR6843, the single BIN stream is split into frames and then reshaped into a virtual antenna matrix.

This stage is mostly about data layout. If the layout is wrong, every later FFT or angle estimate will look wrong even if the formulas are correct.

## 3. Calibration

The cascade path applies frequency and phase calibration before FFT. This matters because multiple chips must behave like one coherent array.

Calibration reduces channel-to-channel mismatch and makes angle-domain processing more reliable.

## 4. Range FFT

Range FFT converts fast-time ADC samples into distance bins. A target at a certain distance creates a beat frequency, and the FFT maps that frequency to a range bin.

The code applies a window before FFT when configured. Windowing reduces spectral leakage and makes the result easier to interpret.

## 5. Doppler FFT

Doppler FFT operates along the chirp dimension. It detects phase changes across chirps and maps them to velocity bins.

After `fftshift`, zero velocity is centered, negative and positive motion appear on opposite sides, and speed heatmaps become easier to read.

## 6. Angle Processing

Angle processing uses the virtual antenna dimension. The code arranges TX/RX channels into array groups and performs an angle FFT or related AoA mapping.

The output is a spatial response: where a target appears in angle or in 3D point-cloud coordinates.

## 7. Outputs

The final outputs serve different tasks:

- **H5** keeps full processing results for later analysis.
- **NPZ** stores compact arrays for visualization or downstream scripts.
- **PNG** is good for quick inspection.
- **MP4** is useful for motion review and presentation.

Processing and visualization are separated so expensive signal processing does not need to be repeated just to change the display format.
