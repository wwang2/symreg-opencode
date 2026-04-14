---
issue: 3
parents: []
eval_version: eval-v1
metric: 0.00425
---

# Research Notes

## Approach

Fourier basis regression: construct a design matrix of sine/cosine basis
functions at integer multiples of π/L (L=5, half the domain width), then
solve via ordinary least squares (numpy.linalg.lstsq).

Sweep number of Fourier terms N from 4 to 24, pick the N that minimizes
training MSE. This is a standard linear-in-parameters approach — no
iterative optimization needed, just a single matrix solve.

## Why Fourier?

The target appears to have oscillatory structure visible in the training
data (rising then falling, with some wiggles). A Fourier basis is the
natural choice for capturing periodic or quasi-periodic signals. With
enough terms, it can approximate any smooth function on a finite interval
(Weierstrass approximation theorem via trigonometric polynomials).

## Limitations

- Pure Fourier series assume periodicity across the domain boundary, but
  the true function likely isn't periodic on [-5, 5]. This creates Gibbs
  phenomenon artifacts at the edges.
- The x*cos(x) component has amplitude modulation that Fourier terms can
  only approximate through many harmonics.
- May overfit with too many terms on only 50 data points.

## Results

| Seed | Metric (MSE) |
|------|-------------|
| 42   | 0.00425     |
| 123  | 0.00425     |
| 7    | 0.00425     |
| **Mean** | **0.00425** |

Target: 0.01 — achieved 0.00425 (57% below target).

The test evaluator uses a fixed seed=99 for test data, so metric is
deterministic across seeds. The Fourier basis with 24 terms captures the
training data well and generalizes to the clean test distribution.
