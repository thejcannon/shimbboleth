from typing import Any, Literal, TypeAlias

from shimbboleth.internal.clay.model import Model

EmptyList: TypeAlias = list[Any]
EmptyDict: TypeAlias = dict[str, Any]


class ExitStatus(Model, extra=True):
    exit_status: Literal["*"] | int
    """The exit status number that will cause this job to soft-fail"""
