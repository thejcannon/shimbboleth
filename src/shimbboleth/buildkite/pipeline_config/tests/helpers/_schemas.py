import httpx

from functools import cache

import jsonschema
from shimbboleth.buildkite.pipeline_config import get_schema


UPSTREAM_JSON_SCHEMA_COMMIT = "2fbbfc199bd66c0ff64303a2d9c7072ad24f3ce3"
UPSTREAM_JSON_SCHEMA_URL = f"https://raw.githubusercontent.com/buildkite/pipeline-schema/{UPSTREAM_JSON_SCHEMA_COMMIT}/schema.json"


@cache
def get_generated_schema() -> jsonschema.Draft202012Validator:
    """
    A fixture that returns a JSON Schema validator for the generated schema.
    """
    return jsonschema.Draft202012Validator(
        get_schema(), format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )


@cache
def get_upstream_schema() -> jsonschema.Draft202012Validator:
    from shimbboleth.buildkite.pipeline_config.tests.conftest import PYTEST_CONFIG

    assert PYTEST_CONFIG is not None, "called too early!"

    cache_key = f"BKSchema/schema.{UPSTREAM_JSON_SCHEMA_COMMIT}.json"
    schema = PYTEST_CONFIG.cache.get(cache_key, None)
    if not schema:
        response = httpx.get(UPSTREAM_JSON_SCHEMA_URL)
        response.raise_for_status()
        schema = response.json()
        PYTEST_CONFIG.cache.set(cache_key, schema)

    return jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )
