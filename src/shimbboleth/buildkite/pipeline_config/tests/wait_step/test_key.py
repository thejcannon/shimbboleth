from shimbboleth.buildkite.pipeline_config.tests.wait_step.base import TestBase
from shimbboleth.buildkite.pipeline_config.tests.bases.bk_str import (
    BKStrTest,
    BKStrDefaultTest,
)
from pytest import param


class Test_Default(TestBase, BKStrDefaultTest):
    ATTR_NAME = "key"
    DEFAULT = None


class Test_Pipelines(TestBase, BKStrTest):
    ATTR_NAME = "key"

    # @TODO: "Step keys may only contain alphanumeric characters, underscores, dashes and colons"

    VALID_STEPS = [
        param(
            {"key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "type": "wait"},
            id="uuid_format_with_x",
        ),
        param(
            {"key": "12345678-1234-1234-1234-1234567890123456", "type": "wait"},
            id="uuid_too_long",
        ),
        param(
            {"key": "12345678-1234-1234-1234-123", "type": "wait"}, id="uuid_too_short"
        ),
        param(
            {"key": "test-12345678-1234-1234-1234-123456789012", "type": "wait"},
            id="uuid_with_prefix",
        ),
    ]

    INVALID_STEPS = [
        param(
            {"key": "550e8400-e29b-41d4-a716-446655440000", "type": "wait"},
            id="uuid_v4",
        ),
        param(
            {"key": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "type": "wait"},
            id="uuid_v1",
        ),
        param(
            {"key": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "type": "wait"},
            id="uuid_v3",
        ),
        param(
            {"key": "6ba7b814-9dad-11d1-80b4-00c04fd430c8", "type": "wait"},
            id="uuid_v5",
        ),
        param(
            {"key": "123e4567-e89b-12d3-a456-426614174000", "type": "wait"},
            id="another_uuid",
        ),
    ]
