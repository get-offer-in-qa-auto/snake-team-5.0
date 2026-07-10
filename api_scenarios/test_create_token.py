#!/usr/bin/env python3
# Проверяет bootstrap авторизации: создает TeamCity access token из username/password или берет готовый token.
import os
import time
import uuid

import allure
import pytest
import requests
from requests.auth import HTTPBasicAuth


@allure.epic("TeamCity REST API")
@allure.feature("Authorization")
@allure.story("Token bootstrap")
@allure.title("Create or reuse TeamCity access token")
@pytest.mark.smoke
def test_create_token():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))

    with allure.step("Check existing TEAMCITY_TOKEN"):
        existing_token = os.getenv("TEAMCITY_TOKEN")
        if existing_token:
            assert existing_token
            return

    with allure.step("Read username and password from environment"):
        username = os.getenv("TEAMCITY_USERNAME")
        password = os.getenv("TEAMCITY_PASSWORD")
        assert username and password, "Set TEAMCITY_TOKEN or TEAMCITY_USERNAME and TEAMCITY_PASSWORD"

    with allure.step("Create TeamCity access token"):
        token_name = f"python-api-scenarios-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        response = requests.post(
            f"{base_url}/app/rest/users/current/tokens?fields=name,value,creationTime",
            auth=HTTPBasicAuth(username, password),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json={"name": token_name},
            timeout=timeout,
        )
        assert response.status_code in (200, 201), response.text

    with allure.step("Check token value"):
        token_value = response.json().get("value")
        assert token_value, "TeamCity did not return token.value"
        os.environ["TEAMCITY_TOKEN"] = token_value


if __name__ == "__main__":
    test_create_token()
