"""
Contains the base class for all steps: `Step`.
"""

import dataclasses
from shimbboleth.internal.clay.model import Model, field, FieldAlias
from shimbboleth.internal.clay.validation import ValidationError
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.internal.clay.json_load import JSONLoadError
from shimbboleth.buildkite.pipeline_config.notify import Notify, _parse_notify
from shimbboleth.buildkite.pipeline_config._types import BKStrList, BKBool, BKStr
from uuid import UUID
from typing import ClassVar, final


class BKKey(BKStr):
    @staticmethod
    def __shimbboleth_json_schema__():
        return {
            "anyOf": [
                {
                    "type": "string",
                    "not": {
                        "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                    },
                },
                {"type": "integer"},
                {"type": "null"},
            ]
        }

    def __set__(self, instance, value: str | int | None) -> None:
        if isinstance(value, int):
            value = str(value)
        if isinstance(value, str):
            try:
                UUID(value)
            except ValueError:
                pass
            else:
                raise ValidationError(value, expectation="not be a valid UUID")
        super().__set__(instance, value)


class Step(Model):
    class Dependency(Model, extra=False):
        step: str

        allow_failure: BKBool = BKBool(default=False)

    key: BKKey = BKKey()
    """A unique identifier for a step, must not resemble a UUID"""

    allow_dependency_failure: BKBool = BKBool(default=False)
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


class SubStep(Step):
    branches: BKStrList = BKStrList()
    """Which branches will include this step in their builds"""
