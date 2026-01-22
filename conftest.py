import logging
import os
from collections.abc import MutableMapping
from typing import Any

import pytest
import requests
from faker import Faker

fake = Faker()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080/api/v1")

def pytest_tavern_beta_before_every_request(request_args: MutableMapping):
    message = f"Request: {request_args['method']} {request_args['url']}"

    params = request_args.get("params", None)
    if params:
        message += f"\nQuery parameters: {params}"

    message += f"\nRequest body: {request_args.get('json', '<no body>')}"

    logging.info(message)


def pytest_tavern_beta_after_every_response(expected: Any, response: Any) -> None:
    logging.info(f"Response: {response.status_code} {response.text}")


@pytest.fixture
def generate_random_email() -> str:
    return fake.unique.email()

@pytest.fixture(scope="session")
def admin_credentials():
    return {
        "email": "admin@mail.ru",
        "password": "123123123aA!"
    }

@pytest.fixture(scope="session")
def admin_token(admin_credentials):
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=admin_credentials)
        if resp.status_code == 200:
            return resp.json()["accessToken"]
    except requests.RequestException:
        pass
    return "admin_token_placeholder" # Fallback if service is down during collect

@pytest.fixture(scope="session")
def admin_auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
def created_user():
    email = fake.unique.email()
    password = "Password123!"
    payload = {
        "email": email,
        "password": password,
        "fullName": fake.name(),
        "age": 25,
        "region": "US",
        "gender": "MALE",
        "maritalStatus": "SINGLE"
    }
    try:
        resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
        if resp.status_code == 201:
            data = resp.json()
            return {
                "token": data["accessToken"],
                "user": data["user"],
                "password": password
            }
    except requests.RequestException:
        pass
    return None

@pytest.fixture(scope="function")
def user_token(created_user):
    return created_user["token"] if created_user else "user_token_placeholder"

@pytest.fixture(scope="function")
def user_auth_header(user_token):
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def future_timestamp() -> str:
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()

@pytest.fixture
def past_timestamp() -> str:
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()

@pytest.fixture
def old_timestamp() -> str:
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(days=95)).isoformat()

@pytest.fixture
def recent_timestamp() -> str:
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

@pytest.fixture(scope="function")
def user_id(created_user):
    return created_user["user"]["id"] if created_user else "user_id_placeholder"

@pytest.fixture(scope="function")
def other_user_id():
    import uuid
    return str(uuid.uuid4())