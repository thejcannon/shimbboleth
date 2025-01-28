import pytest

# NB: This has to come before the import
pytest.register_assert_rewrite("shimbboleth.buildkite.pipeline_config.tests.yamlgen")
