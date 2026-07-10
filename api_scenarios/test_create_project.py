#!/usr/bin/env python3
# Проверяет создание test project через REST API и чтение созданного project.
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
@allure.feature("Projects")
@allure.story("Create project")
@allure.title("Create TeamCity project through REST API")
@pytest.mark.regression
def test_create_project():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")

    try:
        with allure.step("POST /app/rest/projects"):
            create_response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert create_response.status_code in (200, 201), create_response.text

        with allure.step("GET created project"):
            project_response = requests.get(
                f"{base_url}/app/rest/projects/id:{project_id}?fields=id,name,parentProject(id,name),href",
                headers=headers,
                timeout=timeout,
            )
            assert project_response.status_code == 200, project_response.text
            project = project_response.json()

        with allure.step("Check created project fields"):
            assert project.get("id") == project_id
            assert project.get("name") == project_id
    finally:
        with allure.step("DELETE test project"):
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=timeout)


if __name__ == "__main__":
    test_create_project()
