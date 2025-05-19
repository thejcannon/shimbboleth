from typing import Callable, Literal


def bk_bool(*, default: bool) -> Callable[[bool | Literal["true", "false"] | None], bool]:
    def bk_bool(value: bool | Literal["true", "false"] | None) -> bool:
        if value is None:
            return default
        if value in (True, "true"):
            return True
        elif value in (False, "false"):
            return False
        else:
            raise ValueError(f"Invalid value for bool: {value}")
    return bk_bool
