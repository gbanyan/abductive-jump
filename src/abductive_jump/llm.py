from __future__ import annotations

import hashlib
import json
import threading
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .conditions import PromptSpec

_LOG_LOCK = threading.Lock()


@dataclass(frozen=True, slots=True)
class ModelManifest:
    model: str
    revision: str
    quantization: str
    engine: str
    engine_version: str
    context_limit: int
    temperature: float
    top_p: float
    max_tokens: int
    reasoning_effort: str | None = None
    response_format: dict[str, Any] | None = None
    transport_retries: int = 0


@dataclass(frozen=True, slots=True)
class CallRecord:
    condition: str
    proposal_source: str
    world_id: str
    world_seed: int
    decoding_seed: int
    prompt_template_version: str
    prompt_hash: str
    full_prompt_json: str
    full_output: str
    prompt_tokens: int
    completion_tokens: int
    latency_seconds: float
    model: str
    revision: str
    quantization: str
    candidate_parent: str
    mutation_ancestry: tuple[str, ...]
    representation_hash: str
    reasoning_output: str = ""
    raw_response_json: str = ""
    answer_tokens: int | None = None
    reasoning_tokens: int | None = None
    total_tokens: int | None = None
    usage_json: str = "{}"
    attempt_count: int = 1


class OpenAICompatibleClient:
    def __init__(self, base_url: str, manifest: ModelManifest, log_path: Path):
        normalized = base_url.rstrip("/")
        self.url = (
            normalized + "/chat/completions"
            if normalized.endswith("/v1")
            else normalized + "/v1/chat/completions"
        )
        self.manifest = manifest
        self.log_path = log_path

    def generate(
        self,
        prompt: PromptSpec,
        *,
        world_id: str,
        world_seed: int,
        decoding_seed: int,
        candidate_parent: str = "",
        mutation_ancestry: tuple[str, ...] = (),
        representation_hash: str = "",
    ) -> tuple[str, CallRecord]:
        messages = [{"role": "system", "content": prompt.system}, {"role": "user", "content": prompt.user}]
        prompt_json = json.dumps(messages, sort_keys=True, separators=(",", ":"))
        body = {
            "model": self.manifest.model,
            "messages": messages,
            "temperature": self.manifest.temperature,
            "top_p": self.manifest.top_p,
            "max_tokens": self.manifest.max_tokens,
            "seed": decoding_seed,
        }
        if self.manifest.reasoning_effort is not None:
            body["reasoning_effort"] = self.manifest.reasoning_effort
        if self.manifest.response_format is not None:
            body["response_format"] = self.manifest.response_format
        start = time.perf_counter()
        payload: dict[str, Any] | None = None
        attempt = 0
        while payload is None:
            attempt += 1
            request = urllib.request.Request(
                self.url,
                json.dumps(body).encode(),
                {"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=600) as response:
                    payload = json.load(response)
            except (OSError, TimeoutError) as exc:
                error = {
                    "attempt": attempt,
                    "error": f"{type(exc).__name__}:{exc}",
                    "request_body": body,
                    "world_id": world_id,
                    "world_seed": world_seed,
                }
                error_path = self.log_path.with_suffix(self.log_path.suffix + ".transport-errors")
                error_path.parent.mkdir(parents=True, exist_ok=True)
                with _LOG_LOCK, error_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(error, sort_keys=True) + "\n")
                if attempt > self.manifest.transport_retries:
                    raise
        latency = time.perf_counter() - start
        message = payload["choices"][0]["message"]
        output = str(message.get("content") or "")
        reasoning = str(message.get("reasoning") or message.get("reasoning_content") or "")
        usage = payload.get("usage", {})
        completion_details = usage.get("completion_tokens_details", {}) or {}
        reasoning_tokens = usage.get("reasoning_tokens", completion_details.get("reasoning_tokens"))
        answer_tokens = usage.get("answer_tokens")
        if answer_tokens is None and usage.get("completion_tokens") is not None:
            answer_tokens = int(usage["completion_tokens"]) - int(reasoning_tokens or 0)
        record = CallRecord(
            prompt.condition.value,
            prompt.proposal_source.value,
            world_id,
            world_seed,
            decoding_seed,
            prompt.template_version,
            hashlib.sha256(prompt_json.encode()).hexdigest(),
            prompt_json,
            output,
            int(usage.get("prompt_tokens", 0)),
            int(usage.get("completion_tokens", 0)),
            latency,
            self.manifest.model,
            self.manifest.revision,
            self.manifest.quantization,
            candidate_parent,
            mutation_ancestry,
            representation_hash,
            reasoning,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            int(answer_tokens) if answer_tokens is not None else None,
            int(reasoning_tokens) if reasoning_tokens is not None else None,
            int(usage["total_tokens"]) if usage.get("total_tokens") is not None else None,
            json.dumps(usage, sort_keys=True, separators=(",", ":")),
            attempt,
        )
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with _LOG_LOCK, self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
        return output, record


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    decoder = json.JSONDecoder()
    for index, char in enumerate(stripped):
        if char == "{":
            try:
                value, _ = decoder.raw_decode(stripped[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    raise ValueError("no JSON object in model output")
