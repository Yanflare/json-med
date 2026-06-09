"""Core JSON repair logic — zero required dependencies."""

from __future__ import annotations

import json
import re

from llm_jsonfix.exceptions import RepairError

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_FENCE_RE = re.compile(
    r"^```(?:json)?\s*\n?(.*?)\n?\s*```$",
    re.DOTALL | re.IGNORECASE,
)

_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def _strip_fence(text: str) -> str:
    """Remove markdown code fences if present."""
    stripped = text.strip()
    m = _FENCE_RE.match(stripped)
    if m:
        return m.group(1).strip()
    # Handle fences without closing backticks (truncated output)
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Drop the opening fence line
        inner = "\n".join(lines[1:])
        return inner.strip()
    return stripped


def _strip_bom(text: str) -> str:
    """Remove UTF-8 BOM if present."""
    return text.lstrip("\ufeff")


def _fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ]."""
    return _TRAILING_COMMA_RE.sub(r"\1", text)


def _fix_single_quotes(text: str) -> str:
    """
    Convert single-quoted JSON strings to double-quoted.

    This handles the common LLM mistake of outputting:
        {'key': 'value'}  →  {"key": "value"}

    Strategy: tokenise carefully to avoid replacing apostrophes inside
    already-double-quoted strings or inside values.
    """
    result: list[str] = []
    i = 0
    in_double = False

    while i < len(text):
        ch = text[i]

        if in_double:
            result.append(ch)
            if ch == "\\" and i + 1 < len(text):
                # Consume escaped character verbatim
                i += 1
                result.append(text[i])
            elif ch == '"':
                in_double = False
        elif ch == '"':
            in_double = True
            result.append(ch)
        elif ch == "'":
            # Start of a single-quoted string — scan to closing quote
            result.append('"')
            i += 1
            while i < len(text):
                inner = text[i]
                if inner == "\\" and i + 1 < len(text):
                    next_ch = text[i + 1]
                    result.append(inner)
                    result.append(next_ch)
                    i += 2
                    continue
                if inner == "'":
                    break
                # Escape any unescaped double-quotes inside
                if inner == '"':
                    result.append('\\"')
                else:
                    result.append(inner)
                i += 1
            result.append('"')
        else:
            result.append(ch)

        i += 1

    return "".join(result)


def _close_truncated(text: str) -> str:
    """
    Best-effort closure of truncated JSON.

    Tracks open braces/brackets and appends the minimum closing tokens
    required to produce syntactically valid JSON.  Also closes unterminated
    string literals before appending closers.
    """
    stack: list[str] = []
    in_string = False
    escape_next = False

    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in ("{", "["):
            stack.append(ch)
        elif ch == "}":
            if stack and stack[-1] == "{":
                stack.pop()
        elif ch == "]" and stack and stack[-1] == "[":
            stack.pop()

    suffix_parts: list[str] = []

    # Close unterminated string
    if in_string:
        suffix_parts.append('"')

    # Close open containers in reverse order
    for opener in reversed(stack):
        suffix_parts.append("}" if opener == "{" else "]")

    return text + "".join(suffix_parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def repair(text: str) -> str:
    """
    Attempt to repair a malformed JSON string produced by an LLM.

    Repairs applied (in order):
    1. Strip UTF-8 BOM
    2. Strip markdown code fences (```json ... ```)
    3. Fix trailing commas before ``}`` or ``]``
    4. Convert single-quoted strings to double-quoted
    5. Close truncated structures (unclosed braces/brackets/strings)

    Parameters
    ----------
    text:
        Raw text from an LLM response that should contain JSON.

    Returns
    -------
    str
        A string that parses as valid JSON, or raises ``RepairError`` if
        the input is unrecoverable.

    Raises
    ------
    RepairError
        When the repaired string still cannot be parsed as JSON.
    """
    if not isinstance(text, str):
        raise TypeError(f"repair() expects str, got {type(text).__name__}")

    original = text

    text = _strip_bom(text)
    text = text.strip()
    text = _strip_fence(text)
    text = text.strip()
    text = _fix_trailing_commas(text)
    text = _fix_single_quotes(text)
    text = _close_truncated(text)

    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        raise RepairError(
            f"Could not repair JSON: {exc}",
            original=original,
        ) from exc

    return text
