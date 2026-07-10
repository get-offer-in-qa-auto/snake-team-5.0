#!/usr/bin/env python3
# Проверяет negative authorization: protected endpoints без token и с неверным token.
import os
import time
import uuid

import allure
import pytest
import requests
from requests.auth import HTTPBasicAuth


def token():
    existing_token = os.getenv("TEAMCITY_TOKEN")
    if existing_token:
        return existing_token
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    username = os.getenv("TEAMCITY_USERNAME")
    password = os.getenv("TEAMCITY_PASSWORD")
    assert username and password, "Set TEAMCITY_TOKEN or TEAMCITY_USERNAME and TEAMCITY_PASSWORD"
    response = requests.post(
        f"{base_url}/app/rest/users/current/tokens?fields=name,value,creationTime",
        auth=HTTPBasicAuth(username, password),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json={"name": f"python-api-scenarios-{int(time.time())}-{uuid.uuid4().hex[:6]}"},
        timeout=int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20")),
    )
    assert response.status_code in (200, 201), response.text
    created_token = response.json().get("value")
    assert created_token, "TeamCity did not return token.value"
    os.environ["TEAMCITY_TOKEN"] = created_token
    return created_token


def unique_id(prefix):
    return f"{prefix}{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"


@allure.epic("TeamCity REST API")
@allure.feature("Authorization")
@allure.story("Negative authorization")
@allure.title("Protected endpoints reject missing or invalid token")
@pytest.mark.regression
def test_negative_authorization():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    project_id = unique_id("AutotestApiNoAuthProject")

    with allure.step("GET /app/rest/server without authorization"):
        no_auth_server = requests.get(
            f"{base_url}/app/rest/server",
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        assert no_auth_server.status_code in (200, 401, 403), no_auth_server.text

    with allure.step("POST /app/rest/projects without authorization"):
        no_auth_create = requests.post(
            f"{base_url}/app/rest/projects",
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json={"id": project_id, "name": project_id},
            timeout=timeout,
        )
        assert no_auth_create.status_code in (401, 403), no_auth_create.text

    with allure.step("POST /app/rest/projects with invalid bearer token"):
        invalid_create = requests.post(
            f"{base_url}/app/rest/projects",
            headers={
                "Authorization": "Bearer invalid-token-for-negative-checks",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"id": f"{project_id}Invalid", "name": "Invalid Token Project"},
            timeout=timeout,
        )
        assert invalid_create.status_code in (401, 403), invalid_create.text

    with allure.step("POST /app/rest/buildQueue with invalid bearer token"):
        invalid_queue = requests.post(
            f"{base_url}/app/rest/buildQueue",
            headers={
                "Authorization": "Bearer invalid-token-for-negative-checks",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"buildType": {"id": "NotExistingBuildType"}},
            timeout=timeout,
        )
        assert invalid_queue.status_code in (401, 403), invalid_queue.text

    with allure.step("GET project with admin token to prove it was not created"):
        admin_check = requests.get(
            f"{base_url}/app/rest/projects/id:{project_id}",
            headers={"Authorization": f"Bearer {token()}", "Accept": "application/json"},
            timeout=timeout,
        )
        assert admin_check.status_code == 404, admin_check.text


if __name__ == "__main__":
    test_negative_authorization()
