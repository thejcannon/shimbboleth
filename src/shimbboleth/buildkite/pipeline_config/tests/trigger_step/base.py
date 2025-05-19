from typing import Any

from shimbboleth.buildkite.pipeline_config.trigger_step import TriggerStep


class TestBase:
    MODEL = TriggerStep
    UPSTREAM_SCHEMA_DEF_NAME = "triggerStep"
    TYPENAME = "trigger"

    @classmethod
    def ctor(cls, **kwargs) -> TriggerStep:
        return cls.MODEL(**kwargs, trigger="trigger")

    @classmethod
    def model_load(cls, data: dict[str, Any] = {}) -> TriggerStep:
        data.setdefault("trigger", "trigger")
        return cls.MODEL.model_load(data)
