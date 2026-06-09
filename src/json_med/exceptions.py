"""Exceptions raised by json-med."""

from __future__ import annotations


class RepairError(ValueError):
    """Raised when a JSON string cannot be repaired into valid JSON."""

    def __init__(self, message: str, original: str) -> None:
        super().__init__(message)
        self.original = original
