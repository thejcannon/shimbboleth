"""
Contains the base class for all steps: `Step`.
"""

import dataclasses
from shimbboleth.internal.clay.model import Model, field, FieldAlias
from shimbboleth.internal.clay.validation import Not, ValidationError
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.internal.clay.json_load import JSONLoadError
from shimbboleth.buildkite.pipeline_config._types import bool_from_json
from shimbboleth.buildkite.pipeline_config.notify import Notify, _parse_notify
from uuid import UUID
from typing import ClassVar, final, Annotated


class Step(Model):
    class Dependency(Model, extra=False):
        # @TODO: Make a PR upstream, this isn't required upstream?
        step: str

        allow_failure: bool = field(default=False)

    key: Annotated[str, Not[UUID]] | None = field(default=None)
    """A unique identifier for a step, must not resemble a UUID"""

    allow_dependency_failure: bool = field(default=False)
    """Whether to proceed with this step and further steps if a step named in the depends_on attribute fails"""

    depends_on: list[Dependency] = field(default_factory=list)
    """The step keys for a step to depend on"""

    # @TEST: Is an empty string considered a skip?
    if_condition: str | None = field(default=None, json_alias="if")
    """A boolean expression that omits the step when false"""

    id: ClassVar = FieldAlias("key", deprecated=True)
    identifier: ClassVar = FieldAlias("key")

    # NB: Used in `GroupStep` and `CommandStep`
    NotifyT = (
        Notify.BasecampCampfire
        | Notify.Slack
        | Notify.GitHubCheck
        | Notify.GitHubCommitStatus
    )

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


# @TODO: Substep class? (e.g. branches field and friends)
