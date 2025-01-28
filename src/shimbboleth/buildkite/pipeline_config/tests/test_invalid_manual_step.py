"""
Tests using invalid pipelines for manual steps (block and input).
"""

import pytest


@pytest.fixture(params=["block", "input"])
def invalid_manual(invalid_pipeline, request):
    def inner(step_fields, *, path, **kwargs):
        return invalid_pipeline(
            {"steps": [{"type": request.param, **step_fields}]},
            path=f".steps[0]{path}",
            **kwargs,
        )

    return inner


def test_missing_field_type(*, invalid_manual):
    invalid_manual(
        {"fields": [{}]},
        error="Expected `{}` to contain `text` or `select`",
        path=".fields[0]",
        id="missing_field_type",
    )


class TestTextField:
    """Tests for invalid text field configurations."""

    @pytest.fixture
    @staticmethod
    def invalid_text_field(invalid_manual):
        def inner(field_config, *, path, **kwargs):
            return invalid_manual(
                {"fields": [{"text": "text", **field_config}]},
                path=f".fields[0]{path}",
                **kwargs,
            )

        return inner

    def test_missing_key(self, *, invalid_text_field):
        invalid_text_field(
            {},
            error="Expected required fields `'key'` to be provided for model `ManualStep.Text`",
            path="",
            id="missing_text_key",
        )

    def test_invalid_key_colon(self, *, invalid_text_field):
        invalid_text_field(
            {"key": "has:a:colon"},
            error="Expected `'has:a:colon'` to match regex `^[a-zA-Z0-9-_]+$`",
            path=".key",
            id="bad_key_colon",
        )

    def test_invalid_key_space(self, *, invalid_text_field):
        invalid_text_field(
            {"key": "has a space"},
            error="Expected `'has a space'` to match regex `^[a-zA-Z0-9-_]+$`",
            path=".key",
            id="bad_key_space",
        )

    def test_invalid_format_regex(self, *, invalid_text_field):
        invalid_text_field(
            {"key": "key", "format": "'[a-zA-Z++++'"},
            error="Expected `\"'[a-zA-Z++++'\"` to be a valid regex pattern",
            path=".format",
            id="invalid_regex",
        )


class TestSelectField:
    """Tests for invalid select field configurations."""

    @pytest.fixture
    @staticmethod
    def invalid_select_field(invalid_manual):
        def inner(field_config, *, path, **kwargs):
            base_config = {
                "select": "select",
                "options": [{"label": "label", "value": "value"}],
            }
            return invalid_manual(
                {"fields": [{**base_config, **field_config}]},
                path=f".fields[0]{path}",
                **kwargs,
            )

        return inner

    def test_invalid_key_colon(self, *, invalid_select_field):
        invalid_select_field(
            {"key": "has:a:colon"},
            error="Expected `'has:a:colon'` to match regex `^[a-zA-Z0-9-_]+$`",
            path=".key",
            id="bad_key_colon",
        )

    def test_invalid_key_space(self, *, invalid_select_field):
        invalid_select_field(
            {"key": "has a space"},
            error="Expected `'has a space'` to match regex `^[a-zA-Z0-9-_]+$`",
            path=".key",
            id="bad_key_space",
        )

    def test_missing_key(self, *, invalid_select_field):
        invalid_select_field(
            {},
            error="Expected required fields `'key'` to be provided for model `ManualStep.SingleSelect`",
            path="",
            id="missing_select_key",
        )

    def test_missing_options(self, *, invalid_manual):
        invalid_manual(
            {"fields": [{"key": "key", "select": "select"}]},
            error="Expected required fields `'options'` to be provided for model `ManualStep.SingleSelect`",
            path=".fields[0]",
            id="missing_options",
        )

    def test_empty_options(self, *, invalid_select_field):
        invalid_select_field(
            {"key": "key", "options": []},
            error="Expected `[]` to be non-empty",
            path=".options",
            id="empty_options",
        )

    def test_single_select_list_default(self, *, invalid_select_field):
        invalid_select_field(
            {"key": "key", "multiple": False, "default": ["value"]},
            error="Expected `['value']` to be of type `str | None`",
            path=".default",
            id="single_select_list_default",
            upstream_schema_valid=True,
        )
