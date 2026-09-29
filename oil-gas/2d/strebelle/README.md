# Strebelle

<sub>OIL-GAS · 2D · CLASSIC</sub>

The 250 × 250 channel training image. Classic public dataset, kept as published.

![Strebelle](preview.png)

## About the data

250 × 250 cells of 1 × 1 m, cell centres `X, Y` from 0.5 to 249.5 (the grid starts at 0, 0). `FACIES` 0 = shale, 1 = sand (72 / 28 %). Sinuous sand channels run along `Y`. The spacing is nominal; the image has no physical scale.

Strebelle, S. (2002). Conditional simulation of complex geological structures using multiple-point statistics. *Mathematical Geology* 34(1), 1–21. [doi](https://doi.org/10.1023/A:1014009426274)

## Suggested exercises

- Use the image as the training image for multiple-point simulation, unconditional and conditioned to a few sand and shale points.
- Compare indicator variograms of the image with those of a sequential indicator simulation: close variograms, different connectivity.
- Measure channel connectivity along `Y` in the image and in the realizations.

<sub>Techniques: training image · MPS · indicator variograms · connectivity.</sub>

## Files

| File | Rows | Size |
|---|---|---|
| [`training_image.csv`](training_image.csv) | 62 500 | 820 kB |

## Columns

### `training_image.csv`

| Column | Unit | Range / values | Missing |
|---|---|---|---|
| `X` | m | 0.5 – 249.5 |  |
| `Y` | m | 0.5 – 249.5 |  |
| `FACIES` |  | `0`, `1` |  |

[← all datasets](../../../README.md)
