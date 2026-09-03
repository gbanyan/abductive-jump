#!/usr/bin/env bash
set -euo pipefail

repo_root="${1:-/Users/gbanyan/Project/novelty-seeking-agent}"
frozen_root="${2:?frozen worktree required}"
base_url="${3:-http://192.168.30.16:8888/v1}"
results_root="$repo_root/experiments/nmi_minimal_sensitivity_v1/results"

cd "$repo_root"

run_shard() {
  local treatment="$1"
  local module="$2"
  local kind="$3"
  local config="$frozen_root/experiments/nmi_minimal_sensitivity_v1/configs/${treatment}.json"
  local output="$results_root/$treatment"
  if [[ -e "$output" ]]; then
    rtk proxy echo "Refusing to reuse existing output directory: $output" >&2
    return 1
  fi
  rtk mkdir -p "$output"
  rtk proxy env PYTHONPATH="$frozen_root/src" "$repo_root/.venv/bin/python" -m "$module" \
    --config "$config" --output-dir "$output" --base-url "$base_url" \
    > "$output/run.stdout.log" 2> "$output/run.stderr.log"
  rtk proxy env PYTHONPATH="$frozen_root/src" "$repo_root/.venv/bin/python" \
    "$frozen_root/scripts/finalize_nmi_minimal_sensitivity_v1.py" \
    --config "$config" --run-dir "$output" --kind "$kind" \
    > "$output/validation.json"
}

run_shard deepseek_matched_cself abductive_jump.compositional_experiment cself
run_shard deepseek_native_cself abductive_jump.compositional_experiment cself
run_shard deepseek_p2 abductive_jump.supplied_representation_experiment p2
