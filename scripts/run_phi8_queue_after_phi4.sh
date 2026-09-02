#!/usr/bin/env bash
set -euo pipefail

repo_root="${1:-/Users/gbanyan/Project/novelty-seeking-agent}"
frozen_root="${2:-/tmp/nmi-phi8-frozen-4ebc679b}"
base_url="http://127.0.0.1:18002"
results_root="$repo_root/experiments/nmi_extension_v1/results"
last_phi4="$results_root/phi_repair/heldout_control/summary.json"
remote_script="/tmp/nmi_phi4_transformers_openai_server_frozen.py"
phi_snapshot="/root/.cache/huggingface/hub/models--microsoft--phi-4/snapshots/2db69c1c3e91a05d2c64a3185acfbaf36f744e25"

cd "$repo_root"

cleanup() {
  rtk mkdir -p "$results_root"
  rtk ssh gblinux 'docker logs nmi-phi8-server' \
    > "$results_root/phi8_server.log" 2>&1 || true
  rtk ssh gblinux 'docker stop nmi-phi8-server' >/dev/null 2>&1 || true
  rtk ssh gblinux "rm -f $remote_script" >/dev/null 2>&1 || true
  rtk tmux kill-session -t nmi_phi8_tunnel >/dev/null 2>&1 || true
}
trap cleanup EXIT

while ! rtk proxy test -f "$last_phi4"; do
  if ! rtk tmux has-session -t nmi_phi4_queue 2>/dev/null; then
    rtk proxy echo "Phi 4-bit queue ended without the final verified shard" >&2
    exit 1
  fi
  rtk proxy sleep 60
done

rtk ssh gblinux 'docker logs nmi-phi4-vllm' \
  > "$results_root/phi4_server_final.log" 2>&1
rtk ssh gblinux 'docker stop nmi-phi4-vllm'
rtk scp "$frozen_root/scripts/phi4_transformers_openai_server.py" \
  "gblinux:$remote_script"
rtk ssh gblinux "docker run -d --rm --name nmi-phi8-server --gpus all \
  -p 127.0.0.1:8000:8000 \
  -v /home/gbanyan/abductive-model-cache:/root/.cache/huggingface \
  -v $remote_script:/opt/server.py:ro \
  --entrypoint python3 vllm/vllm-openai:v0.10.2 \
  /opt/server.py --model-path $phi_snapshot --served-model-name microsoft/phi-4 \
  --host 0.0.0.0 --port 8000 --max-model-len 4096"
rtk tmux new-session -d -s nmi_phi8_tunnel \
  'rtk ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -L 18002:127.0.0.1:8000 gblinux'

ready=0
for _ in $(rtk proxy seq 1 60); do
  if rtk curl --max-time 5 -s "$base_url/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  rtk proxy sleep 5
done
if [[ "$ready" -ne 1 ]]; then
  rtk proxy echo "Phi 8-bit server did not become ready" >&2
  exit 1
fi

validate_shard() {
  local treatment="$1"
  local shard="$2"
  rtk proxy "$repo_root/.venv/bin/python" "$repo_root/scripts/finalize_nmi_extension_v1.py" \
    --config "$repo_root/experiments/nmi_extension_v1/configs/${treatment}/${shard}.json" \
    --run-dir "$results_root/${treatment}/${shard}" \
    > "$results_root/${treatment}/${shard}/validation.json"
}

run_shard() {
  local shard="$1"
  local output="$results_root/phi8_precision/${shard}"
  local module="abductive_jump.compositional_experiment"
  if [[ "$shard" == factorial_* ]]; then
    module="abductive_jump.factorial_experiment"
  fi
  rtk mkdir -p "$output"
  rtk proxy env PYTHONPATH="$frozen_root/src" "$repo_root/.venv/bin/python" -m "$module" \
    --config "$frozen_root/experiments/nmi_extension_v1/configs/phi8_precision/${shard}.json" \
    --output-dir "$output" \
    --base-url "$base_url" \
    > "$output/run.stdout.log" \
    2> "$output/run.stderr.log"
  validate_shard phi8_precision "$shard"
}

run_shard known_jump
run_shard heldout_jump
run_shard factorial_jump
run_shard known_control
run_shard heldout_control
run_shard factorial_control
