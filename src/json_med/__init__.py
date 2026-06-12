"""json-med — repair malformed LLM JSON output."""

from __future__ import annotations

from json_med.exceptions import RepairError
from json_med.parse import parse, parse_array
from json_med.repair import repair

__all__ = ["repair", "parse", "parse_array", "RepairError"]
__version__ = "0.2.0"
