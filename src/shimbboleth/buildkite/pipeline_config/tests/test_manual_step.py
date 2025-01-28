import re
import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config.tests.conftest import (
    STEP_TYPE_PARAMS,
    BOOLVALS,
)


@pytest.fixture(params=[STEP_TYPE_PARAMS["block"], STEP_TYPE_PARAMS["input"]])
def load_step(load_pipeline, request):
    def inner(step_fields, *, id=None):
        return load_pipeline(
            {"steps": [{**step_fields, **request.param.dumped_default}]}, id=id
        ).steps[0]

    return inner


def test_prompt(*, load_step):
    assert load_step({"prompt": "prompt"}).prompt == "prompt"


class TestTextField:
    @pytest.fixture
    @staticmethod
    def load_text_field(load_step):
        def inner(text_field_fields, *, id=None):
            return load_step(
                {"fields": [{**text_field_fields, "text": "text", "key": "key"}]}, id=id
            ).fields[0]

        return inner

    def test_no_extra_fields(self, *, load_text_field):
        field = load_text_field({})
        assert field.text == "text"
        assert field.key == "key"

    def test_hint(self, *, load_text_field):
        assert load_text_field({"hint": "hint"}).hint == "hint"

    def test_default(self, *, load_text_field):
        assert load_text_field({"default": "default"}).default == "default"

    def test_format(self, *, load_text_field):
        assert load_text_field({"format": "^$"}).format == re.compile(r"^$")

    @pytest.mark.parametrize("value, expected", BOOLVALS.items())
    def test_required(self, value, expected, *, load_text_field):
        assert load_text_field({"required": value}).required == expected


class TestSelectField:
    @pytest.fixture
    @staticmethod
    def load_select_field(load_step):
        def inner(select_field_fields, *, id=None):
            return load_step(
                {
                    "fields": [
                        {
                            **select_field_fields,
                            "select": "select",
                            "key": "key",
                            "options": [{"label": "label", "value": "value"}],
                        }
                    ]
                },
                id=id,
            ).fields[0]

        return inner

    def test_bare_select_field(self, *, load_select_field):
        field = load_select_field({})
        assert field.select == "select"
        assert field.key == "key"
        assert field.options

    def test_single_select_default(self, *, load_select_field):
        field = load_select_field({"default": "default"})
        assert field.default == "default"
        assert field.multiple is False

    @pytest.mark.parametrize("value, expected", BOOLVALS.items())
    def test_multiple_select(self, value, expected, *, load_select_field):
        assert load_select_field({"multiple": value}).multiple == expected

    def test_multi_select_default(self, *, load_select_field):
        assert (
            load_select_field(
                {"multiple": True, "default": "default"}, id="scalar"
            ).default
            == load_select_field(
                {"multiple": True, "default": ["default"]}, id="list"
            ).default
            == ["default"]
        )
