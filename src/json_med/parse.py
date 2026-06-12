"""repair() + Pydantic model validation."""

from __future__ import annotations

import json
from typing import Any, TypeVar

from json_med.repair import repair

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
            "pydantic is required for parse(). Install it with: pip install json-med[pydantic]"
        ) from exc

    if not (isinstance(model, type) and issubclass(model, BaseModel)):
        raise TypeError(f"model must be a Pydantic BaseModel subclass, got {model!r}")

    repaired = repair(text)
    data: Any = json.loads(repaired)
    return model.model_validate(data)


def parse_array(text: str, model: type[T]) -> list[T]:
    """
    Repair *text* and validate each element against a Pydantic ``BaseModel``
    subclass, returning a typed list.

    This is the array-root counterpart to :func:`parse`.  Use it when the
    LLM response is a JSON array whose elements all conform to a single
    schema — e.g. ``[{"name": "Alice"}, {"name": "Bob"}]``.

    Parameters
    ----------
    text:
        Raw LLM response text containing (possibly malformed) JSON whose
        root value is an array.
    model:
        A Pydantic v2 ``BaseModel`` subclass to validate each element
        against.

    Returns
    -------
    list[T]
        A list of validated *model* instances.

    Raises
    ------
    RepairError
        When the text cannot be repaired into valid JSON.
    ImportError
        When pydantic is not installed.
    TypeError
        When *model* is not a Pydantic BaseModel subclass, or when the
        repaired JSON root is not an array.
    pydantic.ValidationError
        When any element does not match the model schema.
    """
    try:
        from pydantic import BaseModel
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "pydantic is required for parse_array(). "
            "Install it with: pip install json-med[pydantic]"
        ) from exc

    if not (isinstance(model, type) and issubclass(model, BaseModel)):
        raise TypeError(f"model must be a Pydantic BaseModel subclass, got {model!r}")

    repaired = repair(text)
    data: Any = json.loads(repaired)

    if not isinstance(data, list):
        raise TypeError(f"Expected a JSON array at root, got {type(data).__name__}")

    return [model.model_validate(item) for item in data]
