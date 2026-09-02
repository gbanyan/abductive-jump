# Phi-4 runtime and extension setup audit

Status: Phase 2 setup audit, 2026-09-03 (Asia/Taipei). No extension
confirmatory world was opened or executed during this audit. The only model
requests were `PING`/toy requests.

## Scope and conclusion

The historical Phi-4 evidence remains unchanged. Its exact model identity is
`microsoft/phi-4` at revision
`2db69c1c3e91a05d2c64a3185acfbaf36f744e25`. The historical server was vLLM
0.10.2 with dynamic bitsandbytes 4-bit loading, a 4,096-token server context,
one RTX 4090, temperature 0.2, top-p 0.95 and a 700-token completion cap
(temperature 0.7 for the registered sampled-proposal condition).

Three setup conclusions follow.

1. `PHI-BUDGET-SENSITIVITY` is justified as a separate prospective
   sensitivity condition. Every archived C_self phase-one request (1,500 of
   1,500) used exactly 700 completion tokens, and representative outputs end
   in incomplete JSON. This is direct evidence that the historical generation
   cap bound this interface. It is not evidence that a larger cap will recover
   executable or validated plans.
2. Exact-revision BF16 can technically be served on gblinux only with CPU
   offload. Pure-GPU BF16 is impossible because the 29,319,014,400-byte weight
   set alone exceeds the GPU's 24,564 MiB. A 12 GiB CPU-offload toy server
   loaded successfully, but generated 34 completion tokens in 25.57 seconds
   (about 1.33 tokens/s). This is not operationally feasible for the full
   registered sensitivity scale.
3. The historical vLLM 0.10.2 dynamic bitsandbytes loader does not offer a
   command-line switch that dynamically converts this BF16 checkpoint to
   8-bit. Its dynamic path defaults to 4-bit; its 8-bit path expects a
   bitsandbytes-prequantized configuration/checkpoint. A feasible 8-bit study
   therefore needs either a prospectively created, hashed 8-bit derivative of
   the exact revision or a separately frozen Transformers/bitsandbytes serving
   runtime. That runtime difference must be disclosed and cannot be described
   as changing numerical precision only.

## Live host audit

| Field | Observed value |
|---|---|
| SSH target | `gblinux` |
| Hostname | `GBLinux` |
| Audit reachability | successful, batch-mode SSH |
| Kernel | Linux 7.0.0-30-generic, x86_64 |
| GPU | NVIDIA GeForce RTX 4090 |
| GPU memory | 24,564 MiB |
| Driver | 595.84 |
| CPU | AMD Ryzen 7 5800X, 8 cores / 16 threads |
| RAM / swap | 60 GiB / 8 GiB |
| Free root storage at audit | 123 GiB |

No model server was running when the audit began. The stopped historical
container was started only for toy API tests and stopped again. The temporary
BF16 audit container was removed after its toy measurement. No GPU process was
left running by this audit.

## Model identity and files

The cached Hugging Face reference `main` resolved to the required revision at
audit time. The server command historically used the repository name without
`--revision`; reproducibility therefore depends on the cached `refs/main`
mapping. All extension launch commands must pass both `--revision` and
`--tokenizer-revision` explicitly.

| Field | Observed value |
|---|---|
| Repository | `microsoft/phi-4` |
| Revision | `2db69c1c3e91a05d2c64a3185acfbaf36f744e25` |
| Snapshot path | `/home/gbanyan/abductive-model-cache/hub/models--microsoft--phi-4/snapshots/2db69c1c3e91a05d2c64a3185acfbaf36f744e25` |
| Cache footprint | 28 GiB |
| Weight format | six safetensors shards |
| Weight bytes from index | 29,319,014,400 |
| Architecture | `Phi3ForCausalLM` (`model_type=phi3`) |
| Layers / hidden size | 40 / 5,120 |
| Attention heads / KV heads | 40 / 10 |
| Native max positions | 16,384 |
| Stored dtype | bfloat16 |
| `config.json` SHA256 | `07eedad2c48798b6e3728e4a1b75e0e092019a375ba725a40e40c78d13664045` |
| `tokenizer.json` SHA256 | `9f38d05d9d25756bb2f181ab5a0cebcd59e638df10336fc7ed1010f7296d0298` |
| `tokenizer_config.json` SHA256 | `2b707658c7c2b41580155a45503d7d3b42dc2f530bef678f67a39bf5d10b0510` |

## Historical serving runtime

The preserved container `abductive-vllm` records this launch command:

```text
python3 -m vllm.entrypoints.openai.api_server
  --model microsoft/phi-4
  --quantization bitsandbytes
  --load-format bitsandbytes
  --max-model-len 4096
  --gpu-memory-utilization 0.90
  --served-model-name microsoft/phi-4
  --seed 0
```

| Field | Observed value |
|---|---|
| Engine | vLLM 0.10.2 |
| Container image | `vllm/vllm-openai:v0.10.2` |
| Image digest | `sha256:607442e407b0fea97f8a132a78b787c121a996dd4de181fa08e8da06e71ec2db` |
| PyTorch | 2.8.0+cu128 |
| bitsandbytes | 0.47.0 |
| CUDA image runtime | 12.8.1 |
| Tensor / pipeline / data parallel | 1 / 1 / 1 |
| Loaded model memory | 9.1035 GiB (historical log) |
| Server context | 4,096 tokens |
| KV cache capacity | 57,904 tokens in the historical run log; 59,456 in the audit restart |
| Reported max concurrency | 14.14x historically; 14.52x in the audit restart at 4,096 tokens |
| API binding | host `127.0.0.1:8000` to container port 8000 |

The model configuration reports bfloat16 activations, while linear weights are
dynamically quantized by the bitsandbytes loader. The historical evidence and
all historical result files remain labeled `bitsandbytes-4bit`.

## API and constrained-decoding probes

The audit's `/v1/models` response reported model `microsoft/phi-4` and
`max_model_len=4096`. Two deterministic toy requests with seed 4242 returned
exactly `PING`; one used `max_tokens=32` and one used `max_tokens=2048`. This
establishes that the larger request cap is accepted by the historical API. It
does not evaluate scientific performance.

vLLM 0.10.2 on this server accepted the OpenAI-compatible
`response_format.type=json_schema` field. A toy schema restricting the output
to `{"status":"PING"}` returned schema-valid JSON and `finish_reason=stop`.
Therefore grammar/schema-constrained decoding is supported by the historical
serving stack at least for the tested JSON Schema subset. It must remain a
separate explicit `PHI-CONSTRAINED` condition. It must not be silently enabled
in `PHI-BUDGET-SENSITIVITY`, because doing so would change more than the
generation budget.

The current repository client stores message content and aggregate token
usage, but not the raw API response, `finish_reason`, `stop_reason`, token IDs,
or server fingerprint. Before any extension run, its extension-only logging
path must retain those fields. Historical artifacts must not be rewritten.

## Precision feasibility

### BF16

A toy server pinned both model and tokenizer revision and used:

```text
--dtype bfloat16 --max-model-len 4096 --gpu-memory-utilization 0.85
--cpu-offload-gb 12 --enforce-eager
```

It loaded 15.2896 GiB on GPU, retained 3.65 GiB for a 19,120-token KV cache,
and advertised maximum concurrency 4.67x at 4,096 tokens. The server returned
a correct PING. A 34-completion-token toy took 25.57 seconds. Because this is
roughly sixty times slower than the approximately 80 tokens/s visible in the
historical 4-bit server logs, BF16 with CPU offload is a technical proof of
servability, not a feasible full-scale extension runtime. Pure-GPU BF16 cannot
fit even before KV cache and runtime overhead.

### 8-bit

The installed vLLM source recognizes `load_in_8bit` only for its
prequantized-bitsandbytes path. For an ordinary BF16 checkpoint, the dynamic
loader defaults to 4-bit, so the historical vLLM command cannot be converted
to 8-bit through a supported precision flag.

An exact-revision Transformers/BitsAndBytes path was therefore tested with
`BitsAndBytesConfig(load_in_8bit=True)`, `device_map={"": 0}`,
BF16 activation declaration and local-only loading. It uses the same pinned
source snapshot and the historical container image/digest, with Transformers
4.56.1, Accelerate 1.10.1, bitsandbytes 0.47.0 and PyTorch 2.8.0+cu128. Loading
took 22.8505 s; model footprint was 15,687,526,656 bytes and allocated GPU
memory was 15,696,128,512 bytes. A greedy two-token PING took 0.5214 s.
BitsAndBytes reported that its 8-bit matrix multiply casts BF16 inputs to FP16.

The extension freezes a minimal OpenAI-compatible wrapper at
`scripts/phi4_transformers_openai_server.py` (SHA256
`628313593c65632bc4a5360a709cd2310a925d3e985a2440527a8cbf70fd3398`).
A second PING through this wrapper returned `PING` with a normal stop reason.
No benchmark world was used. This makes an 8-bit sensitivity operationally
feasible, but precision and serving engine change together; the final paper
must report that confounding rather than attribute differences solely to
numerical precision.

## `PHI-BUDGET-SENSITIVITY` frozen design recommendation

This condition is not a precision experiment and does not use constrained
decoding or repair. It isolates the historical completion ceiling.

| Field | Historical C_self | PHI-BUDGET-SENSITIVITY |
|---|---:|---:|
| Model revision | exact revision above | unchanged |
| Quantization/runtime | vLLM 0.10.2 dynamic BnB 4-bit | unchanged |
| Prompt/template semantics | `generic-self-composition-v1` | unchanged |
| Temperature / top-p | 0.2 / 0.95 | unchanged |
| Server context | 4,096 | unchanged |
| Completion cap per call | 700 | **2,048** |
| Reasoning setting | no separate Phi-4 control | unchanged / absent |
| Candidate slots | 3 | unchanged |
| Model calls per slot | 2 | unchanged |
| Plans requested per slot | 16 | unchanged |
| Steps per plan | 4 | unchanged |
| Representation attempts | 48 per world | unchanged |
| Final candidate slots | 3 | unchanged |
| Interventions per candidate | 1 | unchanged |
| Repair / retry | none for malformed scientific output | unchanged |
| Primitives, worlds, seeds, J0-J5, hidden outcomes | frozen | unchanged |

The 2,048 cap is chosen before confirmatory execution. With the largest
archived phase-one prompt (1,187 tokens), prompt plus declared completion cap
is 3,235 tokens, leaving 861 tokens below the unchanged 4,096-token server
limit. The cap applies to both registered calls in a slot because the current
client has one condition-level `generation.max_tokens` field. No extra call,
slot, plan, selection pass, intervention or semantic feedback is introduced.

This is deliberately **not compute-matched** to historical C_self. Reports
must compare equal calls, equal representation attempts, equal final candidate
opportunity and equal interventions, while explicitly reporting unequal token
capacity and observed token use.

Before confirmatory execution, the protocol must freeze a new extension-only
condition ID, config hash, output namespace, retry policy and raw-response
schema. A safe implementation is to clone the historical compositional config
into `experiments/nmi_extension_v1/`, change only
`generation.max_tokens: 700 -> 2048`, and assert equality of every other
scientific/configuration field. The verifier should fail closed if any of
`candidate_slots`, `self_plans_per_slot`, `max_depth`,
`primitive_operation_budget`, families, seeds, prompt version, thresholds,
model/revision, quantization, temperature or top-p differs.

## Evidence boundary

No inference in this audit used a pilot or confirmatory benchmark world. No
conclusion is drawn about J0-J5, plan validity, or JSR under a larger budget,
BF16, 8-bit or constrained decoding. Those remain prospective questions.
