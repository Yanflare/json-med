"""Tests for json-med.repair."""

from __future__ import annotations

import json

import pytest

from json_med import RepairError, repair
from tests.fixtures.corpus import CORPUS

# ------------------------------------------------------------------ corpus ---


@pytest.mark.parametrize("fixture", CORPUS, ids=[f.label for f in CORPUS])
def test_corpus(fixture):  # type: ignore[no-untyped-def]
    result = repair(fixture.raw)
    assert json.loads(result) == fixture.expected


# ------------------------------------------------------------ type errors ---


def test_repair_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        repair(123)  # type: ignore[arg-type]


# ---------------------------------------------------------- unrecoverable ---


def test_repair_raises_on_garbage() -> None:
    with pytest.raises(RepairError) as exc_info:
        repair("this is not json at all !!!")
    assert exc_info.value.original == "this is not json at all !!!"


def test_repair_raises_stores_original() -> None:
    bad = "<<<not json>>>"
    with pytest.raises(RepairError) as exc_info:
        repair(bad)
    assert exc_info.value.original == bad


# --------------------------------------------------------- repair details ---


def test_strips_bom() -> None:
    result = repair('\ufeff{"k": 1}')
    assert json.loads(result) == {"k": 1}


def test_strips_json_fence() -> None:
    result = repair('```json\n{"a": 1}\n```')
    assert json.loads(result) == {"a": 1}


def test_strips_plain_fence() -> None:
    result = repair("```\n[1, 2]\n```")
    assert json.loads(result) == [1, 2]


def test_trailing_comma_object() -> None:
    result = repair('{"x": 1,}')
    assert json.loads(result) == {"x": 1}


def test_trailing_comma_array() -> None:
    result = repair("[1, 2, 3,]")
    assert json.loads(result) == [1, 2, 3]


def test_single_quotes() -> None:
    result = repair("{'key': 'val'}")
    assert json.loads(result) == {"key": "val"}


def test_truncated_object() -> None:
    result = repair('{"a": 1')
    assert json.loads(result) == {"a": 1}


def test_truncated_array() -> None:
    result = repair("[1, 2, 3")
    assert json.loads(result) == [1, 2, 3]


def test_truncated_string() -> None:
    result = repair('{"msg": "hello')
    assert json.loads(result) == {"msg": "hello"}


def test_already_valid_passthrough() -> None:
    valid = '{"name": "test", "value": 42}'
    result = repair(valid)
    assert json.loads(result) == {"name": "test", "value": 42}


def test_fence_plus_trailing_comma() -> None:
    result = repair('```json\n{"a": 1,}\n```')
    assert json.loads(result) == {"a": 1}
