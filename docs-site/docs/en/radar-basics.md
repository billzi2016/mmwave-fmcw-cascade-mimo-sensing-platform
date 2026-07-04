# Radar Basics

This page starts before FMCW, FFT, and point clouds. It explains the ideas needed to read the rest of the documentation.

## What Is Radar?

Radar is a sensing method that uses radio waves to detect objects. A radar sends out an electromagnetic signal, waits for reflections, and studies the returned signal.

The returned signal can tell us several things:

- whether something is present,
- how far away it is,
- whether it is moving,
- roughly which direction it is in,
- how strong the reflection is.

A simple way to think about radar is this:

```text
send signal -> object reflects signal -> receive echo -> estimate object information
```

Unlike a camera, radar does not directly receive a picture. It receives signal measurements. The code in this repository turns those measurements into heatmaps and point clouds.

## What Does Millimeter-Wave Mean?

Millimeter-wave radar uses radio waves whose wavelength is on the millimeter scale. Automotive and sensing radar systems often use frequencies around 60 GHz or 77 GHz.

Shorter wavelengths help with compact antennas and spatial sensing. They also make it possible to build arrays with multiple transmit and receive channels in a small physical device.

In this repository, the radar hardware paths are based on TI millimeter-wave devices:

- `TI IWR2243 Cascade`
- `TI IWR6843`

## What Is FMCW?

FMCW means **Frequency-Modulated Continuous Wave**.

Instead of sending one short pulse and waiting, an FMCW radar continuously transmits a signal whose frequency changes over time. A single frequency sweep is called a **chirp**.

A chirp can be imagined like this:

```text
frequency
   ^
   |        /
   |      /
   |    /
   |  /
   +----------------> time
```

The radar sends this chirp out. When the signal reflects from an object and comes back, it is delayed. Because the transmit frequency is changing, the delayed echo has a slightly different frequency than the current transmitted signal.

That frequency difference is called the **beat frequency**. The beat frequency is related to distance.

## Why FFT Appears Everywhere

The radar does not directly say “the target is 1.2 meters away.” It records samples. FFT is used to find frequency patterns inside those samples.

In this project:

- **Range FFT** looks for beat-frequency patterns and turns them into distance bins.
- **Doppler FFT** looks for phase changes over repeated chirps and turns them into velocity bins.
- **Angle FFT** looks across antenna channels and turns spatial phase differences into angle bins.

FFT is not magic here. It is a way to convert sampled signals into interpretable frequency-domain structure.

## What Are TX And RX?

Radar hardware has transmitters and receivers:

- **TX** means transmit antenna.
- **RX** means receive antenna.

More TX/RX combinations can create more spatial observations. That is why array layout matters.

For example:

- A single-chip radar may have a smaller number of physical TX/RX channels.
- A cascaded radar combines multiple chips to form a larger virtual array.

The code often maps physical TX/RX channels into a **virtual antenna** order. This mapping is necessary before angle estimation.

## What Is A Frame?

A frame is one complete radar measurement block. It usually contains multiple chirps, and each chirp contains multiple ADC samples.

A simplified shape is:

```text
frame
└── chirps
    └── ADC samples
        └── RX/TX channels
```

Most processing scripts work frame by frame. Each frame can produce one heatmap or one point-cloud slice.

## What Is A Point Cloud?

A point cloud is a list of estimated target points in space. A point usually contains:

- x position,
- y position,
- z position,
- intensity or SNR,
- sometimes velocity.

Radar point clouds are not camera-like 3D scans. They are sparse estimates from signal processing. Their quality depends on range estimation, Doppler processing, angle estimation, filtering, and sampling.

## How This Helps With The Repository

When you read the code, keep this chain in mind:

```text
radar echo
-> sampled ADC data
-> frame reconstruction
-> Range FFT
-> Doppler FFT
-> Angle / AoA processing
-> heatmaps and point clouds
```

The rest of the documentation uses these terms repeatedly. This page is the base layer.
