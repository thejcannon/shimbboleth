"""
Contains the base class for all steps: `Step`.
"""

import dataclasses
from typing import Annotated, ClassVar, final
from uuid import UUID

from shimbboleth.buildkite.pipeline_config._converters import bk_bool, bk_key, bk_str
from shimbboleth.buildkite.pipeline_config._types import BKStrList, EmptyDict, EmptyList
from shimbboleth.buildkite.pipeline_config.notify import Notify, _parse_notify
from shimbboleth.internal.clay.json_load import JSONLoadError
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.internal.clay.model import FieldAlias, Model, field
from shimbboleth.internal.clay.validation import Not, ValidationError


# NB: This is a "forward declare" for `Step` such that
# `Step.Dependency` exists before `Step` is (fully) defined.
class Step(Model):
    class Dependency(Model, extra=False):
        step: str | None = field(default=None, converter=bk_str)
        allow_failure: bool = field(default=False, converter=bk_bool(default=False))


from shimbboleth.buildkite.pipeline_config.step._types import (
    DependsOnT,
    IfT,
)


# @TODO: Rename to "FieldAlias"
class _KeyAliasT:
    def __get__(self, instance, owner):
        if instance is None:
            return None
        return instance.key

    def __set__(
        self, instance, value: Annotated[str, Not[UUID]] | int | EmptyList | EmptyDict | None
    ) -> None:
        if value is None:
            return
        instance.key = value

class Step(Step):
    NotifyT = (
        Notify.BasecampCampfire
        | Notify.Slack
        | Notify.GitHubCheck
        | Notify.GitHubCommitStatus
    )

    key: str | None = field(default=None, converter=bk_key)
    """A unique identifier for a step, must not resemble a UUID"""

    allow_dependency_failure: bool = field(default=False, converter=bk_bool(default=False))
    """Whether to proceed with this step and further steps if a step named in the depends_on attribute fails"""

    depends_on: DependsOnT = DependsOnT()
    """The step keys for a step to depend on"""

    # @TEST: Is an empty string considered a skip?
    # @TODO: Rename `if_`
    if_condition: IfT = IfT()
    """A boolean expression that omits the step when false"""

    id: str | None = _KeyAliasT()
    identifier: str | None = _KeyAliasT()

    def __post_init__(self) -> None:
        if self.key is None:
            self.key = self.identifier
        if self.key is None:
            self.key = self.id


    @final
    @classmethod
    def _get_canonical_type(cls) -> str | None:
        type_field = cls.__dataclass_fields__.get("type")
        if type_field is not None:
            return type_field.default
        return None  # GroupStep :|

    def model_dump(self) -> JSONObject:
        val = super().model_dump()

        type_tag = self._get_canonical_type()
        if type_tag is not None:
            val["type"] = type_tag

        return val

    # @TODO: Move this to JSON compat
    @staticmethod
    def _parse_notify(value: list[str | JSONObject]) -> list[NotifyT]:
        ret = []
        for index, elem in enumerate(value):
            with ValidationError.context(index=index):
                notify = _parse_notify(elem)
                if isinstance(notify, (Notify.Email, Notify.Webhook, Notify.Pagerduty)):
                    field = dataclasses.fields(notify)[1]
                    keyname = field.metadata.get("json_alias", field.name)
                    # NB: It IS a valid _build_ notification though
                    raise JSONLoadError(
                        value=keyname, expectation="be a valid step notification"
                    )
                ret.append(notify)
        return ret


class SubStep(Step):
    branches: BKStrList = BKStrList()
    """Which branches will include this step in their builds"""
