#!/usr/bin/env python3
# Проверяет, что в TeamCity есть authorized/connected/enabled agent для запуска build.
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
@allure.feature("Agent")
@allure.story("Agent readiness")
@allure.title("Authorized connected agent is available")
@pytest.mark.smoke
def test_agent_readiness():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    headers = {"Authorization": f"Bearer {token()}", "Accept": "application/json"}

    with allure.step("GET /app/rest/agents"):
        agents_response = requests.get(
            f"{base_url}/app/rest/agents?fields=agent(id,name,authorized,connected,enabled,href)",
            headers=headers,
            timeout=timeout,
        )
        assert agents_response.status_code == 200, agents_response.text
        agents = agents_response.json().get("agent", [])

    with allure.step("Find ready agent"):
        ready_agent = None
        for agent in agents:
            if agent.get("authorized") is True and agent.get("connected") is True and agent.get("enabled") is not False:
                ready_agent = agent
                break
        assert ready_agent, f"No authorized/connected/enabled agent found. Agents: {agents}"

    with allure.step("GET selected agent details"):
        agent_id = ready_agent.get("id") or ready_agent.get("name")
        details_response = requests.get(
            f"{base_url}/app/rest/agents/id:{agent_id}?fields=id,name,authorized,connected,enabled,pool(id,name)",
            headers=headers,
            timeout=timeout,
        )
        assert details_response.status_code == 200, details_response.text
        details = details_response.json()

    with allure.step("Check selected agent state"):
        assert details.get("authorized") is True
        assert details.get("connected") is True
        assert details.get("enabled") is not False


if __name__ == "__main__":
    test_agent_readiness()
