#!/usr/bin/env python3
"""
Symbolic regression solution discovered via genetic programming (gplearn)
followed by scipy coefficient refinement.

GP discovered oscillatory structure: sin(cos(x) * (sin^4(x) + 0.435*x)) - 0.209
This suggested a damped oscillation + phase-shifted product family.
Scipy Nelder-Mead refined coefficients to minimize training MSE.

Discovered expression:
  f(x) = 0.498 * sin(2x) * exp(-0.103 * x^2) + 0.302 * x * cos(0.996 * x) - 0.211
"""

import numpy as np


def f(x):
    x = np.asarray(x, dtype=np.float64)
    return (
        0.49761828 * np.sin(2.0 * x) * np.exp(-0.10289586 * x**2)
        + 0.30192147 * x * np.cos(0.99647836 * x)
        - 0.2112737
    )
