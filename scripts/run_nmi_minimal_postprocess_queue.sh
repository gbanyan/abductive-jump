#!/usr/bin/env bash
set -euo pipefail

repo_root="${1:-/Users/gbanyan/Project/novelty-seeking-agent}"
results_root="$repo_root/experiments/nmi_minimal_sensitivity_v1/results"

cd "$repo_root"
while :; do
  validations="$(rtk proxy find "$results_root" -name validation.json -type f | rtk proxy wc -l | rtk proxy tr -d ' ')"
  if [[ "$validations" -ge 5 ]]; then
    break
  fi
  rtk proxy sleep 60
done

rtk proxy env PYTHONPATH=src .venv/bin/python scripts/run_nmi_minimal_postprocessing.py --root .
