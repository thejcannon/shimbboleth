"""
Contains descriptors specific to steps.
"""

from uuid import UUID
from typing import Annotated
from shimbboleth.internal.clay.validation import ValidationError, Not
from shimbboleth.internal.clay.jsonT import JSONObject
from shimbboleth.buildkite.pipeline_config._types import (
    BKStr,
    _DescriptorBase,
    EmptyList,
    EmptyDict,
)
from shimbboleth.buildkite.pipeline_config.step import Step


class KeyT(BKStr):
    @classmethod
    def __shimbboleth_json_schema__(
        cls, *, model_defs: dict[str, JSONObject]
    ) -> JSONObject:
        return {
            "anyOf": [
                {
                    "type": "string",
                    "not": {
                        "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
                    },
                },
                {"type": "integer"},
                {"type": "array", "maxItems": 0},
                {"type": "object", "maxProperties": 0},
                {"type": "null"},
            ]
        }

    def __set__(
        self, instance, value: str | int | EmptyList | EmptyDict | None
    ) -> None:
        if isinstance(value, str):
            try:
                UUID(value)
            except ValueError:
                pass
            else:
                raise ValidationError(value, expectation="not be a valid UUID")
        super().__set__(instance, value)


class DependsOnT(_DescriptorBase):
    @classmethod
    def __shimbboleth_json_schema__(cls, *, model_defs: dict[str, JSONObject]):
        schema = super().__shimbboleth_json_schema__(model_defs=model_defs)
        schema["anyOf"][0]["not"] = {"const": ""}
        return schema

    # @TODO: Overload
    def __get__(self, instance, owner) -> list[Step.Dependency]:
        if instance is None:
            from dataclasses import field

            return field(default_factory=list)
        return instance.__dict__[self.name]

    # @TODO: Add `dict` in there as well
    def __set__(
        self,
        instance,
        value: Annotated[str, Not[""]] | int | list[str | int | Step.Dependency] | None,
    ) -> None:
        if isinstance(value, str):
            if not value:
                raise ValidationError(value, expectation="not be an empty string")
            value = [Step.Dependency(step=value)]
        elif isinstance(value, int):
            value = [Step.Dependency(step=str(value))]
        elif isinstance(value, list):
            coerced = []
            for index, elem in enumerate(value):
                with ValidationError.context(index=index):
                    coerced.append(
                        elem
                        if isinstance(elem, Step.Dependency)
                        else Step.Dependency(step=elem)
                        if isinstance(elem, (str, int))
                        else Step.Dependency(**elem)
                    )
            value = coerced
        elif value is None:
            value = []
        super().__set__(instance, value)


class IfT(_DescriptorBase):
    # @TODO: Overload
    def __get__(self, instance, owner):
        if instance is None:
            from dataclasses import field

            return field(default=None, metadata={"json_alias": "if"})
        return instance.__dict__[self.name]

    def __set__(
        self,
        instance,
        value: str | EmptyList | EmptyDict | None
    ) -> None:
        if isinstance(value, (list, dict)):
            if value:
                raise ValidationError(value, expectation="be an empty list/dict")
            value = None  # @TODO: Is this right? Are these truthy or falsey?
        super().__set__(instance, value)
