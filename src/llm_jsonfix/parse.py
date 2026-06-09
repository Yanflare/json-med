"""repair() + Pydantic model validation."""

from __future__ import annotations

import json
from typing import Any, TypeVar

from llm_jsonfix.repair import repair

T = TypeVar("T")


def parse(text: str, model: type[T]) -> T:
    """
    Repair *text* and validate it against a Pydantic ``BaseModel`` subclass.

    Parameters
    ----------
    text:
        Raw LLM response text containing (possibly malformed) JSON.
    model:
        A Pydantic v2 ``BaseModel`` subclass to validate against.

    Returns
    -------
    T
        A validated instance of *model*.

    Raises
    ------
    RepairError
        When the text cannot be repaired into valid JSON.
    ImportError
        When pydantic is not installed.
    pydantic.ValidationError
        When the repaired JSON does not match the model schema.
    """
    try:
        from pydantic import BaseModel
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "pydantic is required for parse(). Install it with: pip install llm-jsonfix[pydantic]"
        ) from exc

    if not (isinstance(model, type) and issubclass(model, BaseModel)):
        raise TypeError(f"model must be a Pydantic BaseModel subclass, got {model!r}")

    repaired = repair(text)
    data: Any = json.loads(repaired)
    return model.model_validate(data)
