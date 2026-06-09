"""
Fixture corpus — (input, expected_parsed_value) pairs for repair().

Each entry is:
    label       : human-readable description
    raw         : the malformed string as an LLM might produce it
    expected    : the Python value json.loads(repair(raw)) should equal
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Fixture:
    label: str
    raw: str
    expected: Any


CORPUS: list[Fixture] = [
    # ------------------------------------------------------------------ fences
    Fixture(
        label="json fence with newlines",
        raw='```json\n{"key": "value"}\n```',
        expected={"key": "value"},
    ),
    Fixture(
        label="plain fence no language tag",
        raw='```\n{"a": 1}\n```',
        expected={"a": 1},
    ),
    Fixture(
        label="fence with leading whitespace",
        raw='  ```json\n{"x": true}\n```  ',
        expected={"x": True},
    ),
    Fixture(
        label="fence uppercase JSON tag",
        raw='```JSON\n{"n": 42}\n```',
        expected={"n": 42},
    ),
    # --------------------------------------------------------- trailing commas
    Fixture(
        label="trailing comma in object",
        raw='{"a": 1, "b": 2,}',
        expected={"a": 1, "b": 2},
    ),
    Fixture(
        label="trailing comma in array",
        raw="[1, 2, 3,]",
        expected=[1, 2, 3],
    ),
    Fixture(
        label="trailing comma nested",
        raw='{"list": [1, 2,], "obj": {"x": 9,}}',
        expected={"list": [1, 2], "obj": {"x": 9}},
    ),
    # ---------------------------------------------------------- single quotes
    Fixture(
        label="single-quoted object",
        raw="{'name': 'Alice', 'age': 30}",
        expected={"name": "Alice", "age": 30},
    ),
    Fixture(
        label="mixed quote styles",
        raw="""{"key": 'value', 'other': "fine"}""",
        expected={"key": "value", "other": "fine"},
    ),
    # ------------------------------------------------------- truncated output
    Fixture(
        label="truncated object — missing closing brace",
        raw='{"name": "Bob", "score": 99',
        expected={"name": "Bob", "score": 99},
    ),
    Fixture(
        label="truncated array — missing closing bracket",
        raw="[1, 2, 3",
        expected=[1, 2, 3],
    ),
    Fixture(
        label="truncated nested — missing two closers",
        raw='{"items": [1, 2',
        expected={"items": [1, 2]},
    ),
    Fixture(
        label="truncated string value",
        raw='{"msg": "hello',
        expected={"msg": "hello"},
    ),
    # -------------------------------------------------------------------- bom
    Fixture(
        label="UTF-8 BOM prefix",
        raw='\ufeff{"bom": true}',
        expected={"bom": True},
    ),
    # ---------------------------------------------------------- already valid
    Fixture(
        label="already valid object — no repairs needed",
        raw='{"clean": "input", "count": 5}',
        expected={"clean": "input", "count": 5},
    ),
    Fixture(
        label="already valid array",
        raw="[1, 2, 3]",
        expected=[1, 2, 3],
    ),
    Fixture(
        label="already valid nested structure",
        raw='{"a": {"b": [1, 2, {"c": null}]}}',
        expected={"a": {"b": [1, 2, {"c": None}]}},
    ),
    # --------------------------------------------------------- combined faults
    Fixture(
        label="fence + trailing comma",
        raw='```json\n{"x": 1, "y": 2,}\n```',
        expected={"x": 1, "y": 2},
    ),
    Fixture(
        label="fence + single quotes",
        raw="```json\n{'hello': 'world'}\n```",
        expected={"hello": "world"},
    ),
    Fixture(
        label="fence + truncation",
        raw='```json\n{"a": 1, "b": [1, 2',
        expected={"a": 1, "b": [1, 2]},
    ),
]
