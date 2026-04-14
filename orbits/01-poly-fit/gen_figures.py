#!/usr/bin/env python3
"""Generate figures for orbit/01-poly-fit."""

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

# Training data
train_x = np.array(
    [
        -5.0000,
        -4.7959,
        -4.5918,
        -4.3878,
        -4.1837,
        -3.9796,
        -3.7755,
        -3.5714,
        -3.3673,
        -3.1633,
        -2.9592,
        -2.7551,
        -2.5510,
        -2.3469,
        -2.1429,
        -1.9388,
        -1.7347,
        -1.5306,
        -1.3265,
        -1.1224,
        -0.9184,
        -0.7143,
        -0.5102,
        -0.3061,
        -0.1020,
        0.1020,
        0.3061,
        0.5102,
        0.7143,
        0.9184,
        1.1224,
        1.3265,
        1.5306,
        1.7347,
        1.9388,
        2.1429,
        2.3469,
        2.5510,
        2.7551,
        2.9592,
        3.1633,
        3.3673,
        3.5714,
        3.7755,
        3.9796,
        4.1837,
        4.3878,
        4.5918,
        4.7959,
        5.0000,
    ]
)
train_y = np.array(
    [
        -0.57833,
        -0.31862,
        -0.01645,
        0.25192,
        0.34573,
        0.4849,
        0.67683,
        0.70654,
        0.6909,
        0.76792,
        0.72417,
        0.70571,
        0.68905,
        0.48576,
        0.34935,
        0.2116,
        -0.04658,
        -0.23449,
        -0.53845,
        -0.76097,
        -0.73739,
        -0.84353,
        -0.7454,
        -0.64348,
        -0.3589,
        -0.06277,
        0.11469,
        0.36756,
        0.40221,
        0.39609,
        0.26027,
        0.18566,
        -0.15047,
        -0.45694,
        -0.59859,
        -0.89664,
        -0.97098,
        -1.1749,
        -1.1954,
        -1.1375,
        -1.1039,
        -1.1058,
        -1.1039,
        -1.0129,
        -0.97053,
        -0.79343,
        -0.5988,
        -0.29831,
        -0.07111,
        0.11501,
    ]
)

# Dense x for smooth curves
x_dense = np.linspace(-5, 5, 500)

# Fit polynomials of various degrees
degrees = [3, 5, 8, 10, 12, 15]
colors = ["#937860", "#8172B3", "#C44E52", "#DD8452", "#55A868", "#4C72B0"]
polys = {}
for d in degrees:
    c = np.polyfit(train_x, train_y, deg=d)
    polys[d] = np.poly1d(c)

# Training MSE for each degree
train_mses = {}
for d in degrees:
    y_pred = polys[d](train_x)
    train_mses[d] = np.mean((train_y - y_pred) ** 2)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)

# Panel (a): Data + fits
ax = axes[0]
ax.scatter(
    train_x,
    train_y,
    s=25,
    color="#888888",
    alpha=0.7,
    zorder=5,
    label="Training data",
    edgecolors="none",
)
for d, col in zip(degrees, colors):
    ax.plot(
        x_dense,
        polys[d](x_dense),
        color=col,
        linewidth=1.2,
        alpha=0.85,
        label=f"deg {d}",
        zorder=4,
    )
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Polynomial fits by degree")
ax.set_xlim(-5.5, 5.5)
ax.set_ylim(-2.5, 2.0)
ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9)
ax.text(-0.12, 1.05, "(a)", transform=ax.transAxes, fontsize=14, fontweight="bold")

# Panel (b): Training MSE by degree
ax = axes[1]
mse_vals = [train_mses[d] for d in degrees]
bars = ax.bar(
    range(len(degrees)),
    mse_vals,
    color=colors,
    alpha=0.85,
    edgecolor="white",
    linewidth=0.5,
)
ax.set_xticks(range(len(degrees)))
ax.set_xticklabels([str(d) for d in degrees])
ax.set_xlabel("Polynomial degree")
ax.set_ylabel("Training MSE")
ax.set_title("Training error by degree")
ax.set_yscale("log")

# Annotate best
best_idx = mse_vals.index(min(mse_vals))
ax.annotate(
    f"best fit",
    xy=(best_idx, mse_vals[best_idx]),
    xytext=(best_idx + 0.5, mse_vals[best_idx] * 3),
    fontsize=9,
    color=colors[best_idx],
    arrowprops=dict(arrowstyle="->", color=colors[best_idx], lw=0.8),
)

ax.text(-0.12, 1.05, "(b)", transform=ax.transAxes, fontsize=14, fontweight="bold")

fig.savefig(
    "orbits/01-poly-fit/figures/results.png",
    dpi=150,
    bbox_inches="tight",
    facecolor="white",
)
plt.close(fig)
print("Saved figures/results.png")
