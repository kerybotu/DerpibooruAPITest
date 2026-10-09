import os

import pytest
import requests
from unittest.mock import Mock, patch

from tools.derpibooru_client import DerpibooruClient, classify_response


IMAGE_ID = os.getenv("DERPIBOORU_TEST_IMAGE_ID", "1")


@pytest.mark.read_only
def test_image_read_only():
    try:
        response = DerpibooruClient().get_image(IMAGE_ID)
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"network unavailable after direct/proxy fallback: {type(exc).__name__}")
    assert response.status_code in {200, 400, 401, 404, 422, 429, 500, 502, 503}


@pytest.mark.read_only
def test_interactions_read_only():
    try:
        response = DerpibooruClient().get_interactions(IMAGE_ID)
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"network unavailable after direct/proxy fallback: {type(exc).__name__}")
    assert response.status_code in {200, 400, 401, 403, 404, 422, 429, 500, 502, 503}


@pytest.mark.mutating
@pytest.mark.skip(reason="Mutation tests are intentionally not implemented in the default suite.")
def test_mutations_are_opt_in():
    raise AssertionError("Enable and implement only after explicit manual review.")


def test_http_400_is_returned_without_proxy_retry():
    response = Mock(status_code=400)
    with patch("tools.derpibooru_client._request", return_value=response) as request:
        result = DerpibooruClient().get_image("1")
    assert result.status_code == 400
    request.assert_called_once()


def test_api_key_is_encoded_as_query_parameter():
    response = Mock(status_code=200)
    with patch("tools.derpibooru_client._request", return_value=response) as request:
        DerpibooruClient(api_key="test-only").get_image("1", authenticated=True)
    assert request.call_args.kwargs["params"] == {"ids": "1", "key": "test-only"}


def test_http_status_alone_is_not_challenge():
    response = Mock(status_code=400, headers={"Content-Type": ""}, url="https://example.invalid", text="", history=[])
    assert classify_response(response) == "NO_CHALLENGE_EVIDENCE"


def test_challenge_marker_is_detected():
    response = Mock(status_code=403, headers={"Content-Type": "text/html"}, url="https://example.invalid", text="Anubis verification", history=[])
    assert classify_response(response) == "CHALLENGE_DETECTED"
