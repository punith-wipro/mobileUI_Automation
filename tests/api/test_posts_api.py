"""Small API examples, intentionally runnable without launching Appium."""

import os

import pytest
import requests
from dotenv import load_dotenv

from mobile_qa.config import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")
BASE_URL = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com").rstrip("/")


@pytest.mark.api
def test_existing_post_can_be_retrieved():
    response = requests.get(f"{BASE_URL}/posts/1", timeout=10)

    assert response.status_code == 200
    post = response.json()
    assert post["id"] == 1
    assert post["title"]


@pytest.mark.api
def test_post_endpoint_accepts_a_new_post():
    payload = {"title": "mobile assessment check", "body": "created by API smoke test", "userId": 1}
    response = requests.post(f"{BASE_URL}/posts", json=payload, timeout=10)

    assert response.status_code == 201
    created = response.json()
    assert created["title"] == payload["title"]
    assert created["body"] == payload["body"]
    assert created["userId"] == payload["userId"]
