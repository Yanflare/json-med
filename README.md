# llm-jsonfix

[![PyPI version](https://img.shields.io/pypi/v/llm-jsonfix.svg)](https://pypi.org/project/llm-jsonfix/)
[![CI](https://github.com/Yanflare/llm-jsonfix/actions/workflows/ci.yml/badge.svg)](https://github.com/Yanflare/llm-jsonfix/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/llm-jsonfix.svg)](https://pypi.org/project/llm-jsonfix/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Repair malformed JSON from LLM responses. No required dependencies.

---

## The problem

LLMs routinely return broken JSON:

`````text
````json
{'name': 'Alice', 'scores': [98, 87, 92,],
````

`json.loads()` raises. Your pipeline breaks. `llm-jsonfix` fixes it.

## Install

````bash
pip install llm-jsonfix
# With Pydantic validation support:
pip install "llm-jsonfix[pydantic]"
````

## Usage

### `repair()` — returns a valid JSON string

````python
from llm_jsonfix import repair

raw = """```json
{'name': 'Alice', 'scores': [98, 87, 92,],
```"""

fixed = repair(raw)
# '{"name": "Alice", "scores": [98, 87, 92]}'
```

### `parse()` — repair + Pydantic validation

```python
from pydantic import BaseModel
from llm_jsonfix import parse

class User(BaseModel):
    name: str
    scores: list[int]

user = parse(raw, User)
# User(name='Alice', scores=[98, 87, 92])
```

## What gets repaired

| Issue | Example input | After repair |
|---|---|---|
| Markdown fences | ` ```json\n{...}\n``` ` | `{...}` |
| Trailing commas | `{"a": 1,}` | `{"a": 1}` |
| Single quotes | `{'k': 'v'}` | `{"k": "v"}` |
| Truncated output | `{"name": "Alice"` | `{"name": "Alice"}` |
| UTF-8 BOM | `\ufeff{"k": 1}` | `{"k": 1}` |

## Error handling

```python
from llm_jsonfix import repair, RepairError

try:
    result = repair("not json at all")
except RepairError as e:
    print(f"Unrecoverable: {e}")
    print(f"Original input: {e.original}")
```

## Roadmap

- [ ] Streaming partial-JSON parsing
- [ ] Configurable repair strategy pipeline
- [ ] JSON arrays at root level (extended support)
- [ ] Cookbook: OpenAI / Anthropic API integration examples

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All checks must pass before opening a PR.

## License

MIT — see [LICENSE](LICENSE).
