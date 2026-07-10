#!/usr/bin/env python3
# Проверяет, что TeamCity Server и REST API доступны, а Swagger содержит нужные paths.
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


@allure.epic("TeamCity REST API")
@allure.feature("Readiness")
@allure.story("Server readiness")
@allure.title("TeamCity server and REST API are ready")
@pytest.mark.smoke
def test_server_readiness():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    headers = {"Authorization": f"Bearer {token()}", "Accept": "application/json"}

    with allure.step("GET /app/rest/server"):
        server_response = requests.get(
            f"{base_url}/app/rest/server?fields=version,buildNumber,startTime,currentTime",
            headers=headers,
            timeout=timeout,
        )
        assert server_response.status_code == 200, server_response.text
        server = server_response.json()

    with allure.step("GET /app/rest/swagger.json"):
        swagger_response = requests.get(
            f"{base_url}/app/rest/swagger.json",
            headers=headers,
            timeout=timeout,
        )
        assert swagger_response.status_code == 200, swagger_response.text
        swagger = swagger_response.json()

    with allure.step("GET /app/rest/apiVersion"):
        version_response = requests.get(
            f"{base_url}/app/rest/apiVersion",
            headers={"Authorization": f"Bearer {token()}", "Accept": "text/plain"},
            timeout=timeout,
        )
        assert version_response.status_code == 200, version_response.text

    with allure.step("Check server and Swagger data"):
        assert server.get("version"), server
        assert server.get("buildNumber"), server
        assert swagger.get("swagger") == "2.0", swagger.get("swagger")
        for path in ["/app/rest/server", "/app/rest/agents", "/app/rest/projects", "/app/rest/buildQueue"]:
            assert path in swagger.get("paths", {}), f"Swagger path not found: {path}"


if __name__ == "__main__":
    test_server_readiness()
