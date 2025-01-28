"""
Tests using invalid pipelines for command steps.
"""

import pytest
from pytest import param


@pytest.fixture
def invalid_command(invalid_pipeline):
    def inner(step_fields, *, path, **kwargs):
        return invalid_pipeline(
            {"steps": [{"type": "command", **step_fields}]},
            path=f".steps[0]{path}",
            **kwargs
        )

    return inner


def test_plugins_multiple_props(*, invalid_command):
    invalid_command(
        {"plugins": [{"key1": {}, "key2": {}}]},
        error="Expected `{'key1': {}, 'key2': {}}` to have only one key",
        path=".plugins[0]",
        id="plugins_multiple_props",
    )


def test_cache_missing_paths(*, invalid_command):
    invalid_command(
        {"cache": {}},
        error="Expected required fields `'paths'` to be provided for model `CommandStep.Cache`",
        path=".cache",
        id="cache_missing_paths",
    )


def test_cache_bad_size(*, invalid_command):
    invalid_command(
        {"cache": {"paths": [], "size": "1"}},
        error="Expected `'1'` to match regex `^\\d+g$`",
        path=".cache.size",
        id="cache_bad_size",
    )


def test_retry_big_limit(*, invalid_command):
    invalid_command(
        {"retry": {"automatic": [{"limit": 11}]}},
        error="Expected `11` to be <= 10",
        path=".retry.automatic[0].limit",
        id="retry_big_limit",
    )


class TestNotify:
    """Tests for invalid notify configurations."""

    @pytest.fixture
    @staticmethod
    def invalid_notify(invalid_command):
        def inner(notify_config, *, path, **kwargs):
            return invalid_command(
                {"notify": notify_config},
                path=f".notify{path}",
                **kwargs,
            )

        return inner

    def test_unknown(self, *, invalid_notify):
        invalid_notify(
            ["unknown"],
            error="Expected `'unknown'` to be a valid notification type",
            path="[0]",
            id="notify_unknown",
        )

    def test_email(self, *, invalid_notify):
        invalid_notify(
            [{"email": "hello@example.com"}],
            error="Expected `'email'` to be a valid step notification",
            path="[0]",
            id="notify_email",
        )

    def test_webhook(self, *, invalid_notify):
        invalid_notify(
            [{"webhook": "https://example.com"}],
            error="Expected `'webhook'` to be a valid step notification",
            path="[0]",
            id="notify_webhook",
        )

    def test_pagerduty(self, *, invalid_notify):
        invalid_notify(
            [{"pagerduty_change_event": "pagerduty_change_event"}],
            error="Expected `'pagerduty_change_event'` to be a valid step notification",
            path="[0]",
            id="notify_pagerduty",
        )


    def test_slack_empty_channels(self, *, invalid_notify):
        invalid_notify(
            [{"slack": {"channels": []}}],
            error="Expected `[]` to be non-empty",
            path="[0].slack.channels",
            id="notify_slack_empty",
            upstream_schema_valid=True,
        )


class TestMatrix:
    """Tests for invalid matrix configurations."""

    @pytest.fixture
    @staticmethod
    def invalid_matrix(invalid_command):
        def inner(matrix_config, *, path, **kwargs):
            return invalid_command(
                {"matrix": matrix_config},
                path=f".matrix{path}",
                **kwargs,
            )

        return inner

    def test_empty_setup_list(self, *, invalid_matrix):
        invalid_matrix(
            {"setup": []},
            error="Expected `[]` to be non-empty",
            path=".setup",
            id="matrix_empty_setup",
            upstream_schema_valid=True,
        )

    def test_empty_setup_dict(self, *, invalid_matrix):
        invalid_matrix(
            {"setup": {}},
            error="Expected `{}` to be non-empty",
            path=".setup",
            id="matrix_empty_setup",
            upstream_schema_valid=True,
        )

    def test_single_mismatched_adjustment(self, *, invalid_matrix):
        invalid_matrix(
            {"setup": [""], "adjustments": [{"with": {"": ""}}]},
            error="Expected `{'': ''}` to be of type `str`",
            path=".adjustments[0].with",
            id="matrix_single_mismatched_adj",
            upstream_schema_valid=True,
        )

    def test_multi_mismatched_adjustment(self, *, invalid_matrix):
        invalid_matrix(
            {"setup": {"": []}, "adjustments": [{"with": []}]},
            error="Expected `[]` to be of type `dict`",
            path=".adjustments[0].with",
            id="matrix_multi_mismatched_adj",
        )

    def test_single_empty_adjustment(self, *, invalid_matrix):
        invalid_matrix(
            {"setup": [""], "adjustments": [{}]},
            error="Expected required fields `'with_value'` to be provided for model `CommandStep.Matrix.SingleDim.Adjustment`",
            path=".adjustments[0]",
            id="matrix_single_empty_adj",
        )

    def test_multi_empty_adjustment(self, *, invalid_matrix):
        invalid_matrix(
            {"setup": {"a": ["b"]}, "adjustments": [{}]},
            error="Expected required fields `'with_value'` to be provided for model `CommandStep.Matrix.MultiDim.Adjustment`",
            path=".adjustments[0]",
            id="matrix_multi_empty_adj",
        )

    def test_bad_key(self, *, invalid_matrix):
        invalid_matrix(
            {"setup": {"": []}},
            error="Expected key `''` to match regex `^[a-zA-Z0-9_]+$",
            path=".setup",
            id="matrix_bad_key",
        )
