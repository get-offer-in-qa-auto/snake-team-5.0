#!/usr/bin/env python3
# Проверяет permissions: limited user не может создавать project без нужных прав.
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
@allure.feature("Permissions")
@allure.story("Limited user permissions")
@allure.title("Limited user cannot create project without permissions")
@pytest.mark.regression
def test_limited_user_permissions():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    admin_headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")
    limited_username = unique_id("autotest_limited_")
    limited_password = f"Autotest-{limited_username}!"
    limited_locator = f"username:{limited_username}"

    try:
        with allure.step("Create reference project as admin"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=admin_headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Create limited user"):
            response = requests.post(
                f"{base_url}/app/rest/users?fields=username,name,email,roles(role(roleId,scope))",
                headers=admin_headers,
                json={
                    "username": limited_username,
                    "name": "Autotest Limited User",
                    "password": limited_password,
                    "email": "autotest-limited@example.test",
                },
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            assert response.json().get("username") == limited_username

        with allure.step("Create token for limited user"):
            response = requests.post(
                f"{base_url}/app/rest/users/{limited_locator}/tokens?fields=name,value,creationTime",
                headers=admin_headers,
                json={"name": unique_id("autotest-limited-token-")},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            limited_token = response.json().get("value")
            assert limited_token, "TeamCity did not return limited user token value"

        with allure.step("Try to create project as limited user"):
            forbidden_project_id = unique_id("AutotestApiLimitedForbidden")
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers={
                    "Authorization": f"Bearer {limited_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json={"id": forbidden_project_id, "name": forbidden_project_id},
                timeout=timeout,
            )
            assert response.status_code == 403, response.text
    finally:
        with allure.step("DELETE limited user and reference project"):
            requests.delete(f"{base_url}/app/rest/users/{limited_locator}", headers=admin_headers, timeout=timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=admin_headers, timeout=timeout)


if __name__ == "__main__":
    test_limited_user_permissions()
