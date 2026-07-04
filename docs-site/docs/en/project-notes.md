# Project Notes

This page explains how to maintain and extend the project without changing its basic shape.

## Keep Processing And Visualization Separate

Processing code should produce structured outputs. Visualization code should read those outputs and create images, videos, or normalized assets.

This separation makes experiments easier:

- You can rerender a result without recomputing FFTs.
- You can change visualization style without touching raw data parsing.
- You can compare multiple display formats from the same processed arrays.

## Keep Shapes Explicit

Most bugs in radar code come from misunderstood dimensions. When adding new code, make array shapes clear near the transformation.

Useful examples:

- `(frame, range, doppler, antenna)`
- `(sample, chirp, virtual_rx)`
- `(frame, points, fields)`

## Add Comments Near Layout Changes

Comments are most useful around:

- reshape,
- transpose,
- channel mapping,
- file grouping,
- calibration,
- FFT axis selection,
- coordinate conversion.

These are the places where a reader cannot infer intent from the code alone.

## Extend Documentation Gradually

When new outputs are added, update the documentation in the same order:

1. Add a short overview.
2. Add expected input and output files.
3. Explain the processing chain.
4. Add notes about shapes, units, and assumptions.

The goal is steady clarity, not a large rewrite every time the repository changes.
