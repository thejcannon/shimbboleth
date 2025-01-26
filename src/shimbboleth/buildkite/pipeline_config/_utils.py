from typing import Any

def _rubystr_inner(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, list):
        return "[" + ", ".join(_rubystr_inner(v) for v in value) + "]"
    elif isinstance(value, dict):
        return (
            "{"
            + ", ".join(f'"{k}"=>{_rubystr_inner(v)}' for k, v in value.items())
            + "}"
        )
    elif value is None:
        return "nil"
    else:
        raise ValueError(f"Unsupported type: {type(value)}")


def rubystr(value: Any) -> str:
    if isinstance(value, str):
        return value
    return _rubystr_inner(value)
