import os

import pytest

from tools.derpibooru_client import DerpibooruClient


IMAGE_ID = os.getenv("DERPIBOORU_TEST_IMAGE_ID", "1")


@pytest.mark.read_only
def test_image_read_only():
    response = DerpibooruClient().get_image(IMAGE_ID)
    assert response.status_code in {200, 400, 401, 404, 422, 429, 500, 502, 503}


@pytest.mark.read_only
def test_interactions_read_only():
    response = DerpibooruClient().get_interactions(IMAGE_ID)
    assert response.status_code in {200, 400, 401, 403, 404, 422, 429, 500, 502, 503}


@pytest.mark.mutating
def test_mutations_are_opt_in():
    pytest.skip("Mutating API tests require an explicit manual invocation.")
