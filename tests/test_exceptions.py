"""Tests for llm_jsonfix.exceptions."""

from __future__ import annotations

from llm_jsonfix.exceptions import RepairError


def test_repair_error_stores_original() -> None:
    err = RepairError("something failed", original="bad input")
    assert err.original == "bad input"
    assert str(err) == "something failed"


def test_repair_error_is_value_error() -> None:
    err = RepairError("msg", original="x")
    assert isinstance(err, ValueError)
