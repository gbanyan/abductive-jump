import io
import json
from pathlib import Path
from urllib import request

from abductive_jump.conditions import Condition, PromptSpec, ProposalSource
from abductive_jump.llm import ModelManifest, OpenAICompatibleClient


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return io.StringIO(json.dumps(self.payload))

    def __exit__(self, *_args):
        return False


def test_extension_transport_captures_reasoning_and_preserves_v1_url(monkeypatch, tmp_path: Path):
    captured = {}
    payload = {
        "choices": [{"message": {"content": '{"ok":true}', "reasoning": "private work"}}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 7,
            "total_tokens": 17,
            "completion_tokens_details": {"reasoning_tokens": 5},
        },
    }

    def fake_urlopen(req: request.Request, timeout: int):
        captured["url"] = req.full_url
        captured["body"] = json.loads(req.data)
        captured["timeout"] = timeout
        return _Response(payload)

    monkeypatch.setattr(request, "urlopen", fake_urlopen)
    manifest = ModelManifest(
        "deepseek-v4-flash-vision-exp",
        "local-audited",
        "runtime-native",
        "openai-compatible",
        "audited",
        32768,
        0.2,
        0.95,
        4096,
        reasoning_effort="max",
        response_format={"type": "json_object"},
        transport_retries=2,
    )
    client = OpenAICompatibleClient(
        "http://192.168.30.16:8888/v1", manifest, tmp_path / "calls.jsonl"
    )
    prompt = PromptSpec(
        "toy-v1", Condition.B0_DIRECT_LLM, ProposalSource.P0_LLM, "system", "user"
    )
    output, record = client.generate(
        prompt, world_id="toy", world_seed=-1, decoding_seed=123
    )

    assert captured["url"] == "http://192.168.30.16:8888/v1/chat/completions"
    assert captured["body"]["reasoning_effort"] == "max"
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert output == '{"ok":true}'
    assert record.reasoning_output == "private work"
    assert record.reasoning_tokens == 5
    assert record.answer_tokens == 2
    assert record.total_tokens == 17
    assert json.loads(record.raw_response_json) == payload
