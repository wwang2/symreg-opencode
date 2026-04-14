#!/usr/bin/env python3
"""Generate figures for orbit/02-fourier-fit."""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "medium",
        "axes.labelsize": 11,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.grid": True,
        "grid.alpha": 0.15,
        "grid.linewidth": 0.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlepad": 10.0,
        "axes.labelpad": 6.0,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "legend.frameon": False,
        "legend.borderpad": 0.3,
        "legend.handletextpad": 0.5,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "figure.constrained_layout.use": True,
    }
)

# Load training data
train = np.loadtxt("research/eval/train_data.csv", delimiter=",", skiprows=1)
x_train = train[:, 0]
y_train = train[:, 1]

# Import solution to get coefficients and term count
import sys

sys.path.insert(0, "orbits/02-fourier-fit")
from solution import (
    f,
    _N_TERMS,
    _COEFFS,
    _build_design,
    _x_train as _xt,
    _y_train as _yt,
)

L = 5.0

# Prediction on dense grid
x_dense = np.linspace(-5, 5, 500)
y_pred = f(x_dense)

# Training residuals
y_train_pred = f(x_train)
residuals = y_train - y_train_pred

# Sweep MSE vs number of terms
term_range = range(1, 25)
train_mses = []
for n in term_range:
    A = _build_design(_xt, n)
    coeffs, _, _, _ = np.linalg.lstsq(A, _yt, rcond=None)
    y_hat = A @ coeffs
    train_mses.append(np.mean((_yt - y_hat) ** 2))

# Residuals on dense grid (interpolated from training fit quality)
y_dense_residuals_approx = y_train_pred - f(x_train)  # just for reference

fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)

# Panel (a): Data + Fit
ax = axes[0, 0]
ax.scatter(
    x_train, y_train, s=25, color="#4C72B0", alpha=0.7, label="Training data", zorder=3
)
ax.plot(
    x_dense, y_pred, color="#DD8452", linewidth=2, label=f"Fourier fit (N={_N_TERMS})"
)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("(a) Fourier basis fit")
ax.legend(loc="upper left")
ax.text(-0.12, 1.05, "", transform=ax.transAxes, fontsize=14, fontweight="bold")

# Panel (b): Residuals
ax = axes[0, 1]
ax.stem(x_train, residuals, linefmt="#55A868", markerfmt="o", basefmt="k-")
ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
ax.set_xlabel("x")
ax.set_ylabel("Residual (y - ŷ)")
ax.set_title("(b) Training residuals")
ax.set_ylim(-0.25, 0.25)

# Panel (c): MSE vs number of Fourier terms
ax = axes[1, 0]
ax.plot(
    list(term_range), train_mses, "o-", color="#4C72B0", markersize=4, linewidth=1.5
)
ax.axhline(0.01, color="#888888", linestyle="--", linewidth=1, label="Target (0.01)")
ax.set_xlabel("Number of Fourier terms")
ax.set_ylabel("Training MSE")
ax.set_title("(c) Model selection")
ax.legend()

# Panel (d): Fourier coefficient magnitudes
ax = axes[1, 1]
n_bars = _N_TERMS
cos_mags = np.abs(_COEFFS[1::2][:n_bars])
sin_mags = np.abs(_COEFFS[2::2][:n_bars])
x_pos = np.arange(1, n_bars + 1)
width = 0.35
ax.bar(
    x_pos - width / 2, cos_mags, width, color="#4C72B0", alpha=0.8, label="|cos coeff|"
)
ax.bar(
    x_pos + width / 2, sin_mags, width, color="#DD8452", alpha=0.8, label="|sin coeff|"
)
ax.set_xlabel("Harmonic n")
ax.set_ylabel("|coefficient|")
ax.set_title("(d) Fourier coefficients")
ax.legend()

plt.savefig(
    "orbits/02-fourier-fit/figures/results.png",
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
)
plt.close(fig)
print("Figure saved to orbits/02-fourier-fit/figures/results.png")
