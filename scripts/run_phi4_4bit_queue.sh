#!/usr/bin/env bash
set -euo pipefail

first_runner_pid="${1:?first runner PID required}"
repo_root="${2:-/Users/gbanyan/Project/novelty-seeking-agent}"
base_url="${3:-http://127.0.0.1:18000}"

cd "$repo_root"

validate_shard() {
  local treatment="$1"
  local shard="$2"
  rtk proxy .venv/bin/python scripts/finalize_nmi_extension_v1.py \
    --config "experiments/nmi_extension_v1/configs/${treatment}/${shard}.json" \
    --run-dir "experiments/nmi_extension_v1/results/${treatment}/${shard}" \
    > "experiments/nmi_extension_v1/results/${treatment}/${shard}/validation.json"
}

run_shard() {
  local treatment="$1"
  local shard="$2"
  local output="experiments/nmi_extension_v1/results/${treatment}/${shard}"
  rtk mkdir -p "$output"
  rtk proxy .venv/bin/python -m abductive_jump.compositional_experiment \
    --config "experiments/nmi_extension_v1/configs/${treatment}/${shard}.json" \
    --output-dir "$output" \
    --base-url "$base_url" \
    > "${output}/run.stdout.log" \
    2> "${output}/run.stderr.log"
  validate_shard "$treatment" "$shard"
}

while rtk proxy kill -0 "$first_runner_pid" 2>/dev/null; do
  rtk proxy sleep 30
done
rtk proxy test -f experiments/nmi_extension_v1/results/phi_budget/known_jump/summary.json
validate_shard phi_budget known_jump

run_shard phi_budget heldout_jump
run_shard phi_constrained known_jump
run_shard phi_constrained heldout_jump
run_shard phi_repair known_jump
run_shard phi_repair heldout_jump
run_shard phi_budget known_control
run_shard phi_budget heldout_control
run_shard phi_constrained known_control
run_shard phi_constrained heldout_control
run_shard phi_repair known_control
run_shard phi_repair heldout_control
