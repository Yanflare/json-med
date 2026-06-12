# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [SemVer](https://semver.org/)

## [Unreleased]

## [0.2.0] — 2026-06-12
### Added
- `parse_array(text: str, model: type[BaseModel]) -> list[BaseModel]` — repair + per-element Pydantic v2 validation for JSON arrays at root (closes #6)
- Handles all existing repair strategies at array root: fenced output, trailing commas, single quotes, truncation, BOM
- 13 new tests in `tests/test_array.py`; 58 total; 91% coverage

## [0.1.0] — 2026-06-09

### Added
- `repair(text: str) -> str` — repairs malformed LLM JSON:
  - Strips UTF-8 BOM
  - Removes markdown code fences (` ```json ` and plain ` ``` `)
  - Removes trailing commas before `}` or `]`
  - Converts single-quoted strings to double-quoted
  - Closes truncated structures (unclosed braces, brackets, string literals)
- `parse(text: str, model: type[BaseModel]) -> BaseModel` — repair + Pydantic v2 validation
- `RepairError` exception with `.original` attribute for unrecoverable inputs
- Pydantic v2 is an optional extra (`pip install json-med[pydantic]`)
- 20-fixture test corpus covering all repair strategies
- CI matrix: Python 3.10, 3.11, 3.12
- PyPI trusted publisher via GitHub Actions OIDC

[Unreleased]: https://github.com/Yanflare/json-med/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Yanflare/json-med/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Yanflare/json-med/releases/tag/v0.1.0
