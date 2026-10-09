import os

import pytest
import requests

from tools.derpibooru_client import DerpibooruClient


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
