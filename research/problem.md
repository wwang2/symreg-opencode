# Symbolic Regression: Fit f(x) to Noisy Data

## Problem Statement
50 noisy (x, y) data points are provided in `research/eval/train_data.csv`. Find the function f(x) that best fits the data. The evaluator at `research/eval/evaluator.py` scores solutions on a held-out test set using Mean Squared Error (MSE).

## Solution Interface
Solution must be a Python file with a function `f(x)` that takes a numpy array and returns predictions.

## Success Metric
MSE (minimize). Target: 0.01.
