#!/usr/bin/env python3
"""Minimal frozen OpenAI-compatible server for the Phi-4 8-bit sensitivity run."""

from __future__ import annotations

import argparse
import hashlib
import json
import threading
import time
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--served-model-name", default="microsoft/phi-4")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--max-model-len", type=int, default=4096)
    return parser.parse_args()


class PhiServer:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        quantization = BitsAndBytesConfig(load_in_8bit=True)
        self.tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            args.model_path,
            quantization_config=quantization,
            device_map={"": 0},
            torch_dtype=torch.bfloat16,
            local_files_only=True,
        )
        self.model.eval()
        self.lock = threading.Lock()
        identity = {
            "model_path": args.model_path,
            "served_model_name": args.served_model_name,
            "max_model_len": args.max_model_len,
            "transformers": __import__("transformers").__version__,
            "torch": torch.__version__,
        }
        self.fingerprint = "phi8-" + hashlib.sha256(
            json.dumps(identity, sort_keys=True).encode()
        ).hexdigest()[:16]

    def generate(self, body: dict[str, Any]) -> dict[str, Any]:
        if body.get("model") != self.args.served_model_name:
            raise ValueError("unknown model alias")
        if body.get("response_format") is not None:
            raise ValueError("response_format is unsupported by the frozen 8-bit server")
        messages = body.get("messages")
        if not isinstance(messages, list):
            raise TypeError("messages must be a list")
        max_tokens = int(body.get("max_tokens", 16))
        seed = int(body.get("seed", 0))
        temperature = float(body.get("temperature", 1.0))
        top_p = float(body.get("top_p", 1.0))
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to("cuda:0")
        if input_ids.shape[-1] + max_tokens > self.args.max_model_len:
            raise ValueError("prompt plus max_tokens exceeds frozen context limit")
        generation: dict[str, Any] = {
            "input_ids": input_ids,
            "max_new_tokens": max_tokens,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.eos_token_id,
            "return_dict_in_generate": True,
        }
        if temperature > 0:
            generation.update({"temperature": temperature, "top_p": top_p})
        with self.lock, torch.inference_mode():
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            output = self.model.generate(**generation)
        new_tokens = output.sequences[0, input_ids.shape[-1] :]
        content = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        finish_reason = "length" if len(new_tokens) >= max_tokens else "stop"
        prompt_tokens = int(input_ids.shape[-1])
        completion_tokens = len(new_tokens)
        return {
            "id": "chatcmpl-" + uuid.uuid4().hex,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self.args.served_model_name,
            "system_fingerprint": self.fingerprint,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }


def _handler(server_state: PhiServer) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _json(self, status: HTTPStatus, value: Any) -> None:
            payload = json.dumps(value, sort_keys=True).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._json(HTTPStatus.OK, {"status": "ok"})
            elif self.path == "/v1/models":
                self._json(
                    HTTPStatus.OK,
                    {
                        "object": "list",
                        "data": [
                            {
                                "id": server_state.args.served_model_name,
                                "object": "model",
                                "owned_by": "local",
                            }
                        ],
                    },
                )
            else:
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path != "/v1/chat/completions":
                self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = json.loads(self.rfile.read(length))
                self._json(HTTPStatus.OK, server_state.generate(body))
            except Exception as exc:  # noqa: BLE001 -- HTTP boundary must serialize failures
                self._json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": {"type": type(exc).__name__, "message": str(exc)}},
                )

        def log_message(self, fmt: str, *args: Any) -> None:
            print(json.dumps({"time": time.time(), "message": fmt % args}), flush=True)

    return Handler


def main() -> None:
    args = _parse_args()
    state = PhiServer(args)
    server = ThreadingHTTPServer((args.host, args.port), _handler(state))
    print(json.dumps({"status": "ready", "fingerprint": state.fingerprint}), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
