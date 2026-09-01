from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

ALLOWED_OPS = frozenset({"const", "var", "raw_var", "add", "sub", "mul", "div", "pow", "neg", "history_sum", "if_eq"})


@dataclass(frozen=True, slots=True)
class Expression:
    tree: Mapping[str, Any]

    def validate(self, allowed_variables: frozenset[str], *, max_nodes: int = 64, max_depth: int = 12) -> tuple[str, ...]:
        errors: list[str] = []
        count = 0

        def walk(node: Any, depth: int) -> None:
            nonlocal count
            count += 1
            if count > max_nodes:
                errors.append("expression_node_budget")
                return
            if depth > max_depth:
                errors.append("expression_depth_budget")
                return
            if not isinstance(node, dict) or node.get("op") not in ALLOWED_OPS:
                errors.append("invalid_expression_node")
                return
            op = node["op"]
            if op == "const":
                value = node.get("value")
                if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
                    errors.append("invalid_constant")
            elif op in {"var", "raw_var", "history_sum"}:
                name = node.get("name")
                if name not in allowed_variables:
                    errors.append(f"forbidden_variable:{name}")
            elif op in {"neg"}:
                walk(node.get("arg"), depth + 1)
            elif op in {"add", "sub", "mul", "div", "pow"}:
                walk(node.get("left"), depth + 1)
                walk(node.get("right"), depth + 1)
            elif op == "if_eq":
                walk(node.get("left"), depth + 1)
                walk(node.get("right"), depth + 1)
                walk(node.get("then"), depth + 1)
                walk(node.get("else"), depth + 1)

        walk(self.tree, 0)
        return tuple(sorted(set(errors)))

    @property
    def canonical_json(self) -> str:
        return json.dumps(self.tree, sort_keys=True, separators=(",", ":"), allow_nan=False)

    @property
    def expression_hash(self) -> str:
        return hashlib.sha256(self.canonical_json.encode()).hexdigest()

    def evaluate(self, inputs: Mapping[str, Any], intervention: Mapping[str, Any]) -> float:
        def run(node: Mapping[str, Any]) -> float:
            op = node["op"]
            if op == "const":
                return float(node["value"])
            if op == "var":
                value = intervention[node["name"]] if node["name"] in intervention else inputs[node["name"]]
                if isinstance(value, (list, tuple)):
                    return sum(float(item) for item in value)
                return float(value)
            if op == "raw_var":
                return float(inputs[node["name"]])
            if op == "history_sum":
                return sum(float(v) for v in inputs[node["name"]])
            if op == "neg":
                return -run(node["arg"])
            if op == "add":
                return run(node["left"]) + run(node["right"])
            if op == "sub":
                return run(node["left"]) - run(node["right"])
            if op == "mul":
                return run(node["left"]) * run(node["right"])
            if op == "div":
                denominator = run(node["right"])
                if abs(denominator) < 1e-12:
                    raise ValueError("division by zero")
                return run(node["left"]) / denominator
            if op == "pow":
                value = run(node["left"]) ** run(node["right"])
                if isinstance(value, complex) or not math.isfinite(float(value)):
                    raise ValueError("invalid power result")
                return float(value)
            if op == "if_eq":
                return run(node["then"]) if abs(run(node["left"]) - run(node["right"])) <= 1e-12 else run(node["else"])
            raise ValueError(op)

        value = run(self.tree)
        if not math.isfinite(value):
            raise ValueError("non-finite expression result")
        return value


def const(value: float) -> dict[str, Any]:
    return {"op": "const", "value": value}


def var(name: str, *, raw: bool = False) -> dict[str, Any]:
    return {"op": "raw_var" if raw else "var", "name": name}


def binary(op: str, left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    return {"op": op, "left": dict(left), "right": dict(right)}
