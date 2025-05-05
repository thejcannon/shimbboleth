# Shimbboleth Development Guide

## Development

- This project uses `uv`. Use `uv run python` or `uv run pytest` to run things.

## Testing

### Parameterization

- Prefer parameterization over repeated code
- Use `from pytest import param` instead of `pytets.param` (for brevity)
- Always provide `id=` for parameterized tests (use consise yet neaningful IDs)
  - But each (single) ID should use `_` instead of `-` (since `-` is the joiner between multiple IDs)

### Fixtures

- Avoid fixtures when possible (instead using regular functions, decorators, or context managers)
