from typing import Literal

from shimbboleth.internal.clay.model import Model


class ExitStatus(Model, extra=True):
    exit_status: Literal["*"] | int
    """The exit status number that will cause this job to soft-fail"""
