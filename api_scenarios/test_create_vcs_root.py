#!/usr/bin/env python3
# Проверяет создание Git VCS root внутри test project и чтение его properties.
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
@allure.feature("VCS Roots")
@allure.story("Create VCS root")
@allure.title("Create Git VCS root through REST API")
@pytest.mark.regression
def test_create_vcs_root():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")
    vcs_root_id = unique_id("AutotestApiVcs")

    try:
        with allure.step("POST /app/rest/projects"):
            project_response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert project_response.status_code in (200, 201), project_response.text

        with allure.step("POST /app/rest/vcs-roots"):
            vcs_response = requests.post(
                f"{base_url}/app/rest/vcs-roots?fields=id,name,vcsName,project(id,name),properties(property(name,value))",
                headers=headers,
                json={
                    "id": vcs_root_id,
                    "name": vcs_root_id,
                    "vcsName": "jetbrains.git",
                    "project": {"id": project_id},
                    "properties": {
                        "property": [
                            {
                                "name": "url",
                                "value": os.getenv(
                                    "TEAMCITY_REPOSITORY_URL",
                                    "https://github.com/get-offer-in-qa-auto/snake-team-5.0.git",
                                ),
                            },
                            {"name": "branch", "value": os.getenv("TEAMCITY_REPOSITORY_BRANCH", "refs/heads/main")},
                            {"name": "authMethod", "value": os.getenv("TEAMCITY_VCS_AUTH_METHOD", "ANONYMOUS")},
                        ]
                    },
                },
                timeout=timeout,
            )
            assert vcs_response.status_code in (200, 201), vcs_response.text

        with allure.step("GET created VCS root"):
            root_response = requests.get(
                f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}?fields=id,name,vcsName,project(id,name),properties(property(name,value))",
                headers=headers,
                timeout=timeout,
            )
            assert root_response.status_code == 200, root_response.text
            root = root_response.json()

        with allure.step("Check VCS root fields"):
            assert root.get("id") == vcs_root_id
            assert root.get("vcsName") == "jetbrains.git"
            assert root.get("project", {}).get("id") == project_id
    finally:
        with allure.step("DELETE VCS root and project"):
            requests.delete(f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}", headers=headers, timeout=timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=timeout)


if __name__ == "__main__":
    test_create_vcs_root()
