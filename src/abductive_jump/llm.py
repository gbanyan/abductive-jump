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


class OpenAICompatibleClient:
    def __init__(self, base_url: str, manifest: ModelManifest, log_path: Path):
        self.url = base_url.rstrip("/") + "/v1/chat/completions"
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
        request = urllib.request.Request(
            self.url,
            json.dumps(body).encode(),
            {"Content-Type": "application/json"},
        )
        start = time.perf_counter()
        with urllib.request.urlopen(request, timeout=600) as response:
            payload: dict[str, Any] = json.load(response)
        latency = time.perf_counter() - start
        output = payload["choices"][0]["message"]["content"]
        usage = payload.get("usage", {})
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
