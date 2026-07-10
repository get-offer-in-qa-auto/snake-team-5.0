#!/usr/bin/env python3
# Проверяет cleanup созданных test data: build, build configuration, VCS root и project.
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
@allure.feature("Cleanup")
@allure.story("Cleanup test data")
@allure.title("Cleanup removes generated TeamCity test data")
@pytest.mark.regression
def test_cleanup_test_data():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    request_timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    build_timeout = int(os.getenv("TEAMCITY_BUILD_TIMEOUT", "300"))
    poll_interval = int(os.getenv("TEAMCITY_BUILD_POLL_INTERVAL", "3"))
    headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")
    build_type_id = unique_id("AutotestApiBuild")
    vcs_root_id = unique_id("AutotestApiVcs")
    step_id = unique_id("AutotestApiStep")
    vcs_entry_id = unique_id("AutotestApiVcsEntry")
    build_id = None
    cleaned = False

    try:
        with allure.step("Create project"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Create build configuration"):
            response = requests.post(
                f"{base_url}/app/rest/projects/id:{project_id}/buildTypes?fields=id,name,project(id,name),href",
                headers=headers,
                json={"id": build_type_id, "name": build_type_id},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Create Git VCS root"):
            response = requests.post(
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
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Attach VCS root to build configuration"):
            response = requests.post(
                f"{base_url}/app/rest/buildTypes/id:{build_type_id}/vcs-root-entries?fields=vcs-root-entry(id,vcs-root(id,name),checkout-rules)",
                headers=headers,
                json={"id": vcs_entry_id, "vcs-root": {"id": vcs_root_id}, "checkout-rules": ""},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Add successful Command Line build step"):
            response = requests.post(
                f"{base_url}/app/rest/buildTypes/id:{build_type_id}/steps?fields=id,name,type,properties(property(name,value))",
                headers=headers,
                json={
                    "id": step_id,
                    "name": step_id,
                    "type": "simpleRunner",
                    "properties": {
                        "property": [
                            {"name": "script.content", "value": "echo autotest"},
                            {"name": "use.custom.script", "value": "true"},
                            {"name": "teamcity.step.mode", "value": "default"},
                        ]
                    },
                },
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Queue build"):
            response = requests.post(
                f"{base_url}/app/rest/buildQueue",
                headers=headers,
                json={"buildType": {"id": build_type_id}},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text
            build_id = response.json().get("id")
            assert build_id is not None, response.text

        with allure.step("Wait for build to finish"):
            deadline = time.monotonic() + build_timeout
            build = None
            while time.monotonic() < deadline:
                response = requests.get(
                    f"{base_url}/app/rest/builds/id:{build_id}?fields=id,state,status",
                    headers=headers,
                    timeout=request_timeout,
                )
                assert response.status_code == 200, response.text
                build = response.json()
                if build.get("state") == "finished":
                    break
                time.sleep(poll_interval)
            assert build and build.get("state") == "finished", build

        with allure.step("DELETE build, build configuration, VCS root and project"):
            requests.delete(f"{base_url}/app/rest/builds/id:{build_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/buildTypes/id:{build_type_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}", headers=headers, timeout=request_timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=request_timeout)
            cleaned = True

        with allure.step("GET deleted project"):
            response = requests.get(
                f"{base_url}/app/rest/projects/id:{project_id}",
                headers=headers,
                timeout=request_timeout,
            )
            assert response.status_code == 404, response.text
    finally:
        if not cleaned:
            with allure.step("Cleanup after failed scenario"):
                if build_id:
                    requests.delete(f"{base_url}/app/rest/builds/id:{build_id}", headers=headers, timeout=request_timeout)
                requests.delete(f"{base_url}/app/rest/buildTypes/id:{build_type_id}", headers=headers, timeout=request_timeout)
                requests.delete(f"{base_url}/app/rest/vcs-roots/id:{vcs_root_id}", headers=headers, timeout=request_timeout)
                requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=request_timeout)


if __name__ == "__main__":
    test_cleanup_test_data()
