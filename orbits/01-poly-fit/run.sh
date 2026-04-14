#!/bin/bash
# Reproduce orbit/01-poly-fit evaluation
set -e
cd "$(dirname "$0")/../.."

echo "=== orbit/01-poly-fit: Polynomial degree 15 regression ==="
for SEED in 42 123 7; do
    echo "--- Seed $SEED ---"
    python3 research/eval/evaluator.py --solution orbits/01-poly-fit/solution.py --seed $SEED
done

echo ""
echo "=== Generate figures ==="
python3 orbits/01-poly-fit/gen_figures.py
echo "Done."
