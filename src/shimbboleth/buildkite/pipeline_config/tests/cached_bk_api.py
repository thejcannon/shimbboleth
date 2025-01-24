import hashlib
import os
import httpx
import json

from _pytest.cacheprovider import Cache


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


class CachedAPITransport(httpx.HTTPTransport):
    def __init__(self, cache: Cache):
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
