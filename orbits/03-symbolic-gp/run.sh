#!/bin/bash
# Reproduce orbit 03-symbolic-gp experiments
set -e
cd "$(dirname "$0")/../.."

echo "=== Evaluating solution ==="
for SEED in 42 123 7; do
    python3 research/eval/evaluator.py --solution orbits/03-symbolic-gp/solution.py --seed $SEED
done

echo ""
echo "=== Generating figure ==="
python3 orbits/03-symbolic-gp/plot.py

echo ""
echo "Done."
