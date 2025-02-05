# shimbboleth

Josh's opinionated (and typed) shims library.

- supports (syncronous), `asyncio`, and `trio`
- only requires `httpx`

## Buildkite

### Agent shims

`shimbboleth.buildkite.agent` provides shims around a subset of the [Buildkite agent CLI](https://buildkite.com/docs/agent/v3/cli-reference).

See module for more details.

## (Development)

This project uses `uv`, `lefthook`, `ruff`, `pyright` and `pytest`.
