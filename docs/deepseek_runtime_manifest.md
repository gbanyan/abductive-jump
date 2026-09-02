# DeepSeek V4 Flash Vision Exp runtime manifest

## Scope and integrity boundary

This is the Phase 2 audit of the local DeepSeek endpoint on 3 September 2026 (Asia/Taipei). It used only `/v1/models`, health/version/OpenAPI metadata, the exact `PING` smoke test, and synthetic JSON toys. It did **not** inspect or query AJ5/CJ5 confirmatory worlds, extension confirmatory worlds, hidden outcomes, or benchmark performance. No settings were tuned against scientific outcomes.

The machine-readable companion is `experiments/nmi_extension_v1/runtime/deepseek_manifest.json`.

## Exact identity

| Field | Observed value |
|---|---|
| API base | `http://192.168.30.16:8888/v1` |
| API alias | `deepseek-v4-flash-vision-exp` |
| `/v1/models` root | `deepseek-ai/DeepSeek-V4-Flash-Vision-Exp` |
| Hugging Face revision | `86f746b36186f0e567729a5c06a8c918caba82a9` |
| Local snapshot on audited host | `/home/gbanyan/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-V4-Flash-Vision-Exp/snapshots/86f746b36186f0e567729a5c06a8c918caba82a9` |
| Architecture | `DeepseekV4ForCausalLM` |
| Model type | `deepseek_v4` |
| Maximum model length | 1,048,576 tokens |
| Tokenizer | `PreTrainedTokenizerFast`, maximum length 1,048,576 |
| `config.json` SHA256 | `6cd841bdd6702f5e2ac34671bc78047ed80817102465525ae2a41c502abbcd75` |
| `tokenizer_config.json` SHA256 | `6ac8c8dc065ed118161d02dd532749ae3f52c243deac27872134fae2f50d8547` |
| Weights | 48 sharded `safetensors` files; snapshot approximately 157 GB |
| Weight quantization | FP8, E4M3, dynamic activations, UE8M0 scales, 128 x 128 blocks |
| Declared Torch dtype | BF16 |

This identity must not be shortened to, or equated with, a “0731” checkpoint. The running model and tokenizer came from the pinned Vision-Exp snapshot. The image entrypoint contains a fallback for a 0731 encoding file, but that fallback was not used: the Vision-Exp snapshot contains its own `encoding/encoding_dsv4.py`. Its source hash was `b4bbb74b…d1701`; the live copy became `d70cc346…b09c` after startup hotfixing.

## Serving environment

The reachable host was `gbgx10`, running Linux `6.17.0-1031-nvidia` on AArch64. The audited node exposed one NVIDIA GB10 GPU (driver `580.173.02`, compute capability 12.1) and 130,596,184,064 bytes of system memory. The service launch declares two nodes and tensor parallelism 2; only rank 0 was directly inspected, so the hardware identity of rank 1 remains unverified.

| Component | Observed value |
|---|---|
| Container | `ghcr.io/anemll/dspark-vllm-gx10:0.1.1` |
| Image digest | `sha256:a83948492cf13df455170fb42885f5ef4db54fefe0feff0f841ecbff464ac9d8` |
| Image ID | `sha256:3430d6614a8e2925f34d059af6caf05aff42387326db4d05639a60f10f2654d8` |
| vLLM | `0.25.2.dev0+g752a3a504.d20260714` |
| PyTorch / CUDA | `2.11.0+cu130` / 13.0 |
| Transformers | `5.13.1` |
| Parallelism | 2 nodes, TP=2, PP=1, distributed backend `mp` |
| Weight precision | model-declared FP8 quantization |
| KV-cache precision | `nvfp4_ds_mla` |
| Speculation | DSpark, 6 speculative tokens, probabilistic draft sampling |

The launch also fixed: `--max-model-len 1048576`, `--max-num-seqs 4`, `--max-num-batched-tokens 16384`, `--block-size 256`, `--gpu-memory-utilization 0.835`, chunked prefill, prefix caching, async scheduling, the `deepseek_v4` tokenizer and reasoning parser, and vLLM generation config. The server default chat-template effort is `max`, but every experiment must send its frozen setting explicitly.

This is a patched DSpark runtime, not pristine upstream vLLM. Startup logs confirmed application of the Vision-Exp model/encoding/DSpark hotfixes and fixes labelled issue 55, 27, 43, 26 and 133. The machine-readable manifest records the model encoding hashes and image digest. Several additional patches are mounted or conditional; mounted presence is not treated as proof of activation.

## Reasoning interface

The normal answer is returned in `choices[0].message.content`; reasoning is separately returned in `choices[0].message.reasoning`. No `reasoning_content` field was present.

All seven values advertised by the live OpenAPI schema were accepted on PING toys: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, and `max`. The live patched tokenizer maps them to four distinct regimes:

| Submitted value | Effective regime |
|---|---|
| `none` | thinking disabled |
| `minimal`, `low`, `medium` | low |
| `high` | high |
| `xhigh`, `max` | max |

Accordingly, the scientifically relevant settings remain `none`, `low`, `high`, and `max`. Aliases should not be treated as additional independent treatment levels.

All four required PING checks returned ordinary content exactly equal to `PING`. Reasoning was absent for `none` and present for `low`, `high`, and `max`.

## Usage accounting

Responses exposed:

- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `prompt_tokens_details.cached_tokens`
- `prompt_tokens_details.multimodal_tokens`

They did not expose a separate reasoning-token count. With reasoning enabled, `completion_tokens` accounts jointly for reasoning and the final answer, even though the strings are returned in separate fields. The top-level `metrics` key was present but null in the tested non-streaming responses. Extension accounting must therefore retain raw responses and report the missing reasoning/answer token split explicitly; it must not manufacture one from text tokenization.

Prompt-token counts varied across reasoning regimes because the server applies different chat-template control material. Equal user text is therefore not equal API-reported prompt tokens.

## Determinism check

Three identical requests used `temperature=0`, `seed=424242`, and `max_completion_tokens=128`.

- At `reasoning_effort=none`, all three returned the same `PING`, no reasoning, and 3 completion tokens.
- At `reasoning_effort=max`, all three returned the same final `PING`, but the reasoning text had two distinct forms and completion counts were 29, 27 and 27.

The stable system fingerprint was `vllm-0.25.2.dev0+g752a3a504.d20260714-tp2-34fb5568`. Nevertheless, fixed seed plus temperature zero does not establish byte-deterministic reasoning on this runtime, plausibly in the presence of its probabilistic speculative-decoding path. This is an interface observation, not a causal diagnosis. Confirmatory execution must capture every raw generation and rely on deterministic downstream replay, not regeneration.

## Constrained JSON capability

Two toy-only tests succeeded:

- `response_format={"type":"json_object"}` returned syntactically valid JSON.
- A strict `json_schema` requiring `{"label":"alpha","count":2}` returned an exactly schema-valid object at both `reasoning_effort=none` and `reasoning_effort=max`; reasoning remained separate from the constrained final content at `max`.

Thus constrained JSON is available at this endpoint. It must be a separate, prospectively declared condition if used; it must not be silently enabled for matched or no-repair runs. These toys establish API availability, not reliability on benchmark plans.

## Audit limits

- Rank 1 hardware and container identity were not independently observed.
- No separate tokenizer revision beyond the pinned shared snapshot was found.
- Exact reasoning-token counts are unavailable from response usage.
- Bitwise generation determinism under production concurrency is not established.
- Conditional hotfix activation cannot be inferred merely from mounted files.
- Vision input was not used.
- No benchmark or confirmatory result was exposed during this audit.
