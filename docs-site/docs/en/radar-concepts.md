# Radar Concepts

This page introduces the main radar concepts used by the code.

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
