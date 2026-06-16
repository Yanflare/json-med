# json-med

[![PyPI version](https://img.shields.io/pypi/v/json-med.svg)](https://pypi.org/project/json-med/)
[![CI](https://github.com/Yanflare/json-med/actions/workflows/ci.yml/badge.svg)](https://github.com/Yanflare/json-med/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/json-med.svg)](https://pypi.org/project/json-med/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## The problem

LLM responses often come back wrapped in markdown fences, using single quotes, or with trailing
commas. You lose the rest of the pipeline over one small formatting mistake that the model keeps
repeating. `json-med` repairs it so your code can continue.

You could wrap `json.loads()` in a try/except. But in a real pipeline you do not want the whole
thing to fail because one model response had a trailing comma. You want it to recover cleanly so
the rest of your code keeps running.

## Install

`````bash
pip install json-med

# With Pydantic validation support:
pip install "json-med[pydantic]"
`````

## Usage

### `repair()` — returns a valid JSON string

`````python
from json_med import repair

raw = """```json
{'user': 'Alice', 'scores': [98, 87, 92,], 'active': True}
````"""

fixed = repair(raw)
# '{"user": "Alice", "scores": [98, 87, 92], "active": true}'
````

### `parse()` — repair + Pydantic validation

````python
from pydantic import BaseModel
from json_med import parse

class User(BaseModel):
    user: str
    scores: list[int]
    active: bool

raw = """```json
{'user': 'Alice', 'scores': [98, 87, 92,], 'active': True}
```"""

user = parse(raw, User)
# User(user='Alice', scores=[98, 87, 92], active=True)
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
from json_med import repair, RepairError

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
