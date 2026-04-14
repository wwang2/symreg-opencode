#!/usr/bin/env python3
"""
Generate multi-panel figure for orbit 03-symbolic-gp.
Panel (a): Discovered expression vs training data
Panel (b): GP fitness across random seeds
Panel (c): Residuals analysis
"""

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

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "../..")

# Load training data
data = np.loadtxt(
    os.path.join(REPO_ROOT, "research/eval/train_data.csv"), delimiter=",", skiprows=1
)
x_train = data[:, 0]
y_train = data[:, 1]


def f_final(x):
    return (
        0.49761828 * np.sin(2.0 * x) * np.exp(-0.10289586 * x**2)
        + 0.30192147 * x * np.cos(0.99647836 * x)
        - 0.2112737
    )


def f_gp2(x):
    return np.sin(np.cos(x) * (np.sin(np.sin(np.sin(np.sin(x)))) + 0.435 * x)) - np.exp(
        -1.567
    )


x_dense = np.linspace(-5, 5, 500)
y_final = f_final(x_dense)
y_gp2 = f_gp2(x_dense)

y_pred_train = f_final(x_train)
residuals = y_train - y_pred_train

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

ax = axes[0]
ax.scatter(
    x_train,
    y_train,
    c="#4C72B0",
    s=30,
    alpha=0.7,
    zorder=3,
    label="Training data (noisy)",
)
ax.plot(
    x_dense,
    y_final,
    color="#DD8452",
    linewidth=2,
    label="Discovered expression",
    zorder=2,
)
ax.plot(
    x_dense,
    y_gp2,
    color="#55A868",
    linewidth=1.5,
    linestyle="--",
    alpha=0.7,
    label="GP raw output",
    zorder=1,
)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Symbolic Regression: Discovered Expression")
ax.legend(loc="lower left")
ax.text(-0.12, 1.05, "(a)", transform=ax.transAxes, fontsize=14, fontweight="bold")

ax = axes[1]
seeds = [7, 13, 21, 37, 53, 42]
fitness_vals = [0.0616, 0.0756, 0.0709, 0.0740, 0.0782, 0.0720]
colors = ["#4C72B0" if f == min(fitness_vals) else "#888888" for f in fitness_vals]
ax.bar(
    range(len(seeds)),
    fitness_vals,
    color=colors,
    width=0.6,
    edgecolor="white",
    linewidth=0.5,
)
ax.set_xticks(range(len(seeds)))
ax.set_xticklabels([f"S{s}" for s in seeds])
ax.set_xlabel("GP Run (seed)")
ax.set_ylabel("Fitness (lower is better)")
ax.set_title("GP Fitness Across Random Seeds")
ax.axhline(y=min(fitness_vals), color="#DD8452", linestyle="--", alpha=0.5, linewidth=1)
ax.text(-0.12, 1.05, "(b)", transform=ax.transAxes, fontsize=14, fontweight="bold")

ax = axes[2]
ax.scatter(x_train, residuals, c="#C44E52", s=30, alpha=0.7, zorder=3)
ax.axhline(y=0, color="#888888", linestyle="-", linewidth=0.8, alpha=0.5)
ax.fill_between(
    x_train, -0.05, 0.05, alpha=0.08, color="#888888", label="Noise band (±σ)"
)
ax.set_xlabel("x")
ax.set_ylabel("Residual (y − ŷ)")
ax.set_title("Residuals Analysis")
ax.legend(loc="upper right")
ax.text(-0.12, 1.05, "(c)", transform=ax.transAxes, fontsize=14, fontweight="bold")

out_path = os.path.join(SCRIPT_DIR, "figures", "results.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Figure saved to {out_path}")
