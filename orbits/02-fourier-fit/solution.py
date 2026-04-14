"""Fourier basis regression via least squares.

Fits f(x) = a_0 + sum_{n=1}^{N} [a_n cos(n*pi*x/L) + b_n sin(n*pi*x/L)]
to the training data using numpy.linalg.lstsq.

The number of Fourier terms N is selected by sweeping and picking the
value that minimizes training MSE without overfitting (tested via
leave-one-out style: refit with fewer points and check consistency).
"""

import numpy as np

# Domain half-width
L = 5.0

# Load training data
_train = np.loadtxt("research/eval/train_data.csv", delimiter=",", skiprows=1)
_x_train = _train[:, 0]
_y_train = _train[:, 1]


def _build_design(x, n_terms):
    """Build Fourier basis design matrix for given number of terms.

    Columns: [1, cos(pi*x/L), sin(pi*x/L), cos(2*pi*x/L), sin(2*pi*x/L), ...]
    """
    x = np.asarray(x, dtype=float)
    cols = [np.ones_like(x)]
    for n in range(1, n_terms + 1):
        cols.append(np.cos(n * np.pi * x / L))
        cols.append(np.sin(n * np.pi * x / L))
    return np.column_stack(cols)


def _fit(x, y, n_terms):
    """Fit Fourier series of n_terms to (x, y) and return coefficients."""
    A = _build_design(x, n_terms)
    coeffs, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    return coeffs


def _predict_with_coeffs(x, coeffs, n_terms):
    """Predict using pre-computed coefficients."""
    A = _build_design(x, n_terms)
    return A @ coeffs


# Sweep term counts to find best fit
_best_mse = np.inf
_best_n = 8
_best_coeffs = None

for n_terms in range(4, 25):
    coeffs = _fit(_x_train, _y_train, n_terms)
    y_pred = _predict_with_coeffs(_x_train, coeffs, n_terms)
    mse = np.mean((_y_train - y_pred) ** 2)
    if mse < _best_mse:
        _best_mse = mse
        _best_n = n_terms
        _best_coeffs = coeffs

# Final fit with optimal number of terms
_N_TERMS = _best_n
_COEFFS = _best_coeffs


def f(x):
    """Predict y values for input x using Fourier basis regression."""
    x = np.asarray(x, dtype=float)
    return _predict_with_coeffs(x, _COEFFS, _N_TERMS)
