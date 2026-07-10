#!/usr/bin/env python3
# Проверяет изоляцию тестовых данных: первый project удаляется, второй создается без конфликтов.
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
@allure.feature("Data Isolation")
@allure.story("Data isolation and rerun")
@allure.title("Generated test data can be recreated without conflicts")
@pytest.mark.regression
def test_data_isolation_rerun():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    first_project_id = unique_id("AutotestApiProject")
    second_project_id = unique_id("AutotestApiProject")

    try:
        with allure.step("Create first project"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": first_project_id, "name": first_project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("DELETE first project"):
            response = requests.delete(
                f"{base_url}/app/rest/projects/id:{first_project_id}",
                headers=headers,
                timeout=timeout,
            )
            assert response.status_code in (200, 202, 204), response.text

        with allure.step("GET first project after cleanup"):
            response = requests.get(
                f"{base_url}/app/rest/projects/id:{first_project_id}",
                headers=headers,
                timeout=timeout,
            )
            assert response.status_code == 404, response.text

        with allure.step("Create second project with another generated id"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": second_project_id, "name": second_project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("GET second project"):
            response = requests.get(
                f"{base_url}/app/rest/projects/id:{second_project_id}",
                headers=headers,
                timeout=timeout,
            )
            assert response.status_code == 200, response.text
    finally:
        with allure.step("DELETE second project"):
            requests.delete(f"{base_url}/app/rest/projects/id:{second_project_id}", headers=headers, timeout=timeout)


if __name__ == "__main__":
    test_data_isolation_rerun()
