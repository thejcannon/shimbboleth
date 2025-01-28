"""
Tests using invalid pipelines for group steps.
"""

import pytest
from pytest import param


@pytest.fixture
def invalid_group(invalid_pipeline):
    def inner(step_fields, *, path, **kwargs):
        return invalid_pipeline(
            {"steps": [{"group": "group", **step_fields}]},
            path=f".steps[0]{path}",
            **kwargs
        )

    return inner


def test_missing_steps(*, invalid_group):
    invalid_group(
        {},
        error="Expected required fields `'steps'` to be provided for model `GroupStep`",
        path="",
        id="missing_steps",
    )


def test_empty_steps(*, invalid_group):
    invalid_group(
        {"steps": []},
        error="Expected `[]` to be non-empty",
        path=".steps",
        id="empty_steps",
    )


def test_notify_unknown(*, invalid_group):
    invalid_group(
        {"steps": ["wait"], "notify": ["unknown"]},
        error="Expected `'unknown'` to be a valid notification type",
        path=".notify[0]",
        id="notify_unknown",
    )


def test_notify_email(*, invalid_group):
    invalid_group(
        {"steps": ["wait"], "notify": [{"email": "hello@example.com"}]},
        error="Expected `'email'` to be a valid step notification",
        path=".notify[0]",
        id="notify_email",
        upstream_schema_valid=True
    )


def test_notify_webhook(*, invalid_group):
    invalid_group(
        {"steps": ["wait"], "notify": [{"webhook": "https://example.com"}]},
        error="Expected `'webhook'` to be a valid step notification",
        path=".notify[0]",
        id="notify_webhook",
        upstream_schema_valid=True
    )


def test_notify_pagerduty(*, invalid_group):
    invalid_group(
        {"steps": ["wait"], "notify": [{"pagerduty_change_event": "pagerduty_change_event"}]},
        error="Expected `'pagerduty_change_event'` to be a valid step notification",
        path=".notify[0]",
        id="notify_pagerduty",
        upstream_schema_valid=True
    )


def test_notify_slack_empty_channels(*, invalid_group):
    invalid_group(
        {"steps": ["wait"], "notify": [{"slack": {"channels": []}}]},
        error="Expected `[]` to be non-empty",
        path=".notify[0].slack.channels",
        id="notify_slack_empty",
        upstream_schema_valid=True
    )
