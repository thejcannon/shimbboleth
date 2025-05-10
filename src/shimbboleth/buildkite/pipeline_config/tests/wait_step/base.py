from shimbboleth.buildkite.pipeline_config.wait_step import WaitStep

class TestBase:
    MODEL = WaitStep
    UPSTREAM_SCHEMA_DEF_NAME = "waitStep"
    TYPENAME = "wait"
