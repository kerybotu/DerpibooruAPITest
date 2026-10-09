"""Minimal Derpibooru client for verified/read-only API research.

The client deliberately performs one request at a time and only retries a
connection-level failure through the configured local proxy.
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional

import requests

BASE_URL = os.getenv("DERPIBOORU_BASE_URL", "https://derpibooru.org")
DEFAULT_PROXY = os.getenv("DERPIBOORU_PROXY", "http://127.0.0.1:7898")
NO_PROXY_FALLBACK = os.getenv("DERPIBOORU_NO_PROXY_FALLBACK") == "1"
TIMEOUT = float(os.getenv("DERPIBOORU_TIMEOUT", "15"))


def _key() -> Optional[str]:
    value = os.getenv("DERPIBOORU_API_KEY")
    if value:
        return value.strip()
    path = os.getenv("DERPIBOORU_KEY_FILE", "tempapikey.txt")
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().strip() or None
    except OSError:
        return None


def request_with_fallback(method: str, path: str, *, params=None, json_body=None,
                          headers=None, cookies=None, timeout: float = TIMEOUT) -> requests.Response:
    """Send direct, then once via proxy only for connection-level failures."""
    url = path if path.startswith("http") else BASE_URL.rstrip("/") + "/" + path.lstrip("/")
    request_kwargs = dict(params=params, json=json_body, headers=headers, cookies=cookies, timeout=timeout)
    try:
        return requests.request(method, url, **request_kwargs)
    except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout,
            requests.exceptions.ProxyError, requests.exceptions.SSLError):
        if NO_PROXY_FALLBACK:
            raise
        return requests.request(method, url, proxies={"http": DEFAULT_PROXY, "https": DEFAULT_PROXY}, **request_kwargs)


class DerpibooruClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else _key()

    def _params(self, params=None, authenticated=False):
        result = dict(params or {})
        if authenticated and self.api_key:
            result.setdefault("key", self.api_key)
        return result

    def get_image(self, image_id: int | str, authenticated=False) -> requests.Response:
        return request_with_fallback("GET", "/api/v2/images/show.json",
                                     params=self._params({"ids": str(image_id)}, authenticated))

    def get_interactions(self, image_id: int | str) -> requests.Response:
        return request_with_fallback("GET", "/api/v2/interactions/interacted.json",
                                     params=self._params({"class": "Image", "ids": str(image_id)}, True))

    def get_tags(self, query: str = "", page: int = 1) -> requests.Response:
        return request_with_fallback("GET", "/tags.json", params={"q": query, "page": page})

    def get_user(self, user_id: int | str) -> requests.Response:
        return request_with_fallback("GET", f"/users/{user_id}.json")

    def favorite(self, image_id: int | str, value: bool) -> requests.Response:
        body = {"class": "Image", "id": str(image_id), "value": value, "_method": "PUT"}
        return request_with_fallback("PUT", "/api/v2/interactions/fave", json_body=body,
                                     params=self._params({}, True))

    def vote(self, image_id: int | str, value: str | bool) -> requests.Response:
        body = {"class": "Image", "id": str(image_id), "value": value, "_method": "PUT"}
        return request_with_fallback("PUT", "/api/v2/interactions/vote", json_body=body,
                                     params=self._params({}, True))


def response_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None
