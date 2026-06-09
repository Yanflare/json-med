"""Tests for json-med.parse."""

from __future__ import annotations

import pytest

pydantic = pytest.importorskip("pydantic", reason="pydantic not installed")

from pydantic import BaseModel, ValidationError  # noqa: E402

from json_med import RepairError, parse  # noqa: E402


class User(BaseModel):
    name: str
    age: int


class Config(BaseModel):
    debug: bool
    retries: int
    tags: list[str]


# ----------------------------------------------------------- happy paths ---


def test_parse_clean_json() -> None:
    result = parse('{"name": "Alice", "age": 30}', User)
    assert result.name == "Alice"
    assert result.age == 30


def test_parse_fenced_json() -> None:
    result = parse('```json\n{"name": "Bob", "age": 25}\n```', User)
    assert result.name == "Bob"


def test_parse_trailing_comma() -> None:
    result = parse('{"name": "Carol", "age": 40,}', User)
    assert result.age == 40


def test_parse_single_quotes() -> None:
    result = parse("{'name': 'Dave', 'age': 22}", User)
    assert result.name == "Dave"


def test_parse_truncated() -> None:
    result = parse('{"name": "Eve", "age": 99', User)
    assert result.age == 99


def test_parse_complex_model() -> None:
    raw = '{"debug": true, "retries": 3, "tags": ["a", "b", "c"]}'
    result = parse(raw, Config)
    assert result.debug is True
    assert result.retries == 3
    assert result.tags == ["a", "b", "c"]


# -------------------------------------------------------- error handling ---


def test_parse_raises_repair_error_on_garbage() -> None:
    with pytest.raises(RepairError):
        parse("not json at all", User)


def test_parse_raises_validation_error_on_schema_mismatch() -> None:
    # Valid JSON, but wrong schema
    with pytest.raises(ValidationError):
        parse('{"name": "Frank", "age": "not-an-int"}', User)


def test_parse_raises_type_error_on_bad_model() -> None:
    with pytest.raises(TypeError):
        parse('{"name": "test"}', dict)  # type: ignore[arg-type]
