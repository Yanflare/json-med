"""Tests for json-med.parse_array — Issue #6: first-class JSON array support."""

from __future__ import annotations

import pytest

pydantic = pytest.importorskip("pydantic", reason="pydantic not installed")

from pydantic import BaseModel, ValidationError  # noqa: E402

from json_med import RepairError, parse_array  # noqa: E402


class User(BaseModel):
    name: str
    age: int


class Tag(BaseModel):
    label: str
    value: int


# ----------------------------------------------------------- happy paths ---


def test_parse_array_clean() -> None:
    result = parse_array('[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]', User)
    assert len(result) == 2
    assert result[0].name == "Alice"
    assert result[1].age == 25


def test_parse_array_single_element() -> None:
    result = parse_array('[{"name": "Solo", "age": 1}]', User)
    assert len(result) == 1
    assert result[0].name == "Solo"


def test_parse_array_empty() -> None:
    result = parse_array("[]", User)
    assert result == []


def test_parse_array_fenced() -> None:
    raw = '```json\n[{"name": "Alice", "age": 30}]\n```'
    result = parse_array(raw, User)
    assert result[0].name == "Alice"


def test_parse_array_trailing_comma() -> None:
    result = parse_array('[{"name": "Carol", "age": 40},]', User)
    assert result[0].age == 40


def test_parse_array_single_quotes() -> None:
    result = parse_array("[{'name': 'Dave', 'age': 22}]", User)
    assert result[0].name == "Dave"


def test_parse_array_truncated() -> None:
    # Truncated array — _close_truncated should close it
    result = parse_array('[{"name": "Eve", "age": 99}', User)
    assert result[0].age == 99


def test_parse_array_multiple_models() -> None:
    raw = '[{"label": "alpha", "value": 1}, {"label": "beta", "value": 2}]'
    result = parse_array(raw, Tag)
    assert result[0].label == "alpha"
    assert result[1].value == 2


def test_parse_array_bom() -> None:
    raw = '\ufeff[{"name": "BOM", "age": 5}]'
    result = parse_array(raw, User)
    assert result[0].name == "BOM"


# -------------------------------------------------------- error handling ---


def test_parse_array_raises_repair_error_on_garbage() -> None:
    with pytest.raises(RepairError):
        parse_array("not json at all !!!", User)


def test_parse_array_raises_type_error_on_bad_model() -> None:
    with pytest.raises(TypeError):
        parse_array('[{"name": "test"}]', dict)  # type: ignore[arg-type]


def test_parse_array_raises_type_error_on_object_root() -> None:
    with pytest.raises(TypeError, match="Expected a JSON array at root"):
        parse_array('{"name": "Alice", "age": 30}', User)


def test_parse_array_raises_validation_error_on_schema_mismatch() -> None:
    with pytest.raises(ValidationError):
        parse_array('[{"name": "Frank", "age": "not-an-int"}]', User)
