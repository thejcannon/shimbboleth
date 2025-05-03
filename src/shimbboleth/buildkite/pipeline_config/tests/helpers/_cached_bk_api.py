import hashlib
import os
import httpx
import json
import pytest
import yaml
from typing import Any


def _get_key(request: httpx.Request) -> str:
    components = {
        "method": request.method,
        "url": str(request.url),
        "content": request.content.decode() if request.content else "",
    }
    sorted_json = json.dumps(
        components,
        sort_keys=True,
        indent=None,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    hashed = hashlib.sha256(sorted_json.encode()).hexdigest()
    return f"bk_api_cache/{hashed}"


class _CachedAPITransport(httpx.HTTPTransport):
    def __init__(self, cache: pytest.Cache):
        super().__init__()
        self.cache = cache

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        key = _get_key(request)
        result = self.cache.get(key, None)
        if result is not None:
            status_code, response_body = result
            return httpx.Response(status_code=status_code, content=response_body)

        response = super().handle_request(request)
        response.read()

        if response.status_code in (200, 422):
            self.cache.set(key, (response.status_code, response.text))

        return response


def cached_bk_api(api_token: str):
    """
    An `httpx.Client` around the Buildkite API, which caches responses.
    """
    # @TODO: Can we mark as skip if the token isn't set?
    #   (and/or if we haven't pulled from the cache?)
    # E.g. run it if we can, safely but if skip if not, and if asked to run it always run it

    from shimbboleth.buildkite.pipeline_config.tests.conftest import PYTEST_CONFIG

    return httpx.Client(
        base_url="https://api.buildkite.com/v2/",
        headers={"Authorization": f"Bearer {api_token}"},
        transport=_CachedAPITransport(PYTEST_CONFIG.cache),
    )
    # @TODO: Cache the results in the GitHub Actions workflow?


def is_valid_upstream(pipeline_config: dict[str, Any]) -> bool:
    api_token = os.getenv("BK_PIPELINE_API_TOKEN")
    if not api_token:
        pytest.skip("No API token provided")

    response = cached_bk_api(api_token).patch(
        "organizations/thejcannon/pipelines/step-blaster",
        json={"configuration": yaml.dump(pipeline_config)},
    )
    if 500 <= response.status_code < 600:
        response.raise_for_status()

    return response.status_code == 200
