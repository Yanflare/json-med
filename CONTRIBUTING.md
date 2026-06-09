# Contributing to json-med

Thanks for your interest. Contributions are welcome.

## Setup

`````bash
git clone https://github.com/Yanflare/json-med.git
cd json-med
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
`````

## Running checks

`````bash
ruff check .           # lint
ruff format --check .  # formatting
mypy src/              # type check
pytest                 # tests + coverage
`````

## Submitting a PR

1. Fork the repo and create a branch (`feat/my-feature`)
2. Make your changes with tests
3. Ensure all checks pass
4. Open a PR — use the PR template

## Repair strategy contributions

New repair strategies belong in `src/json-med/repair.py`. Each strategy should:
- Be a pure function (`str → str`)
- Have its own test cases in `tests/test_repair.py`
- Be documented with a clear docstring
- Not introduce required dependencies
