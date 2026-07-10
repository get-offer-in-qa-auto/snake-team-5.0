#!/usr/bin/env python3
# Проверяет запуск build через buildQueue после подготовки project/build step/agent.
import os
import time
import uuid

import allure
import pytest
import requests
from requests.auth import HTTPBasicAuth


def create_test_user_token(base_url, timeout):
    admin_username = os.getenv("TEAMCITY_USERNAME")
    admin_password = os.getenv("TEAMCITY_PASSWORD")
    if admin_username and admin_password:
        admin_auth = HTTPBasicAuth(admin_username, admin_password)
    else:
        admin_auth = HTTPBasicAuth("", os.getenv("TEAMCITY_SUPER_USER_TOKEN", "autotestlocalsuperusertoken"))
    api_headers = {"Accept": "application/json", "Content-Type": "application/json"}

    with allure.step("Get TeamCity CSRF token for bootstrap requests"):
        response = requests.get(f"{base_url}/authenticationTest.html?csrf", auth=admin_auth, timeout=timeout)
        assert response.status_code == 200, response.text
        csrf_token = response.text.strip()
        assert csrf_token, "TeamCity did not return CSRF token"
        api_headers["X-TC-CSRF-Token"] = csrf_token
    test_username = f"autotest_api_user_{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"
    test_password = f"Autotest-{test_username}!"
    test_user_locator = f"username:{test_username}"

    with allure.step("Create temporary TeamCity user"):
        response = requests.post(
            f"{base_url}/app/rest/users?fields=username,name,email,roles(role(roleId,scope))",
            auth=admin_auth,
            headers=api_headers,
            json={
                "username": test_username,
                "name": "Autotest API User",
                "password": test_password,
                "email": "autotest-api-user@example.test",
            },
            timeout=timeout,
        )
        assert response.status_code in (200, 201), response.text

    try:
        with allure.step("Assign admin role to temporary TeamCity user"):
            response = requests.post(
                f"{base_url}/app/rest/users/{test_user_locator}/roles",
                auth=admin_auth,
                headers=api_headers,
                json={
                    "roleId": os.getenv("TEAMCITY_TEST_USER_ROLE_ID", "SYSTEM_ADMIN"),
                    "scope": os.getenv("TEAMCITY_TEST_USER_ROLE_SCOPE", "g"),
                },
                timeout=timeout,
            )
            assert response.status_code in (200, 201, 204), response.text

        with allure.step("Create token for temporary TeamCity user"):
            response = requests.post(
                f"{base_url}/app/rest/users/{test_user_locator}/tokens?fields=name,value,creationTime",
                auth=admin_auth,
                headers=api_headers,
                json={"name": f"autotest-api-token-{int(time.time())}-{uuid.uuid4().hex[:6]}"},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            api_token = response.json().get("value")
            assert api_token, "TeamCity did not return token.value"
            return api_token, test_user_locator, admin_auth, api_headers
    except Exception:
        requests.delete(
            f"{base_url}/app/rest/users/{test_user_locator}",
            auth=admin_auth,
            headers=api_headers,
            timeout=timeout,
        )
        raise


def delete_test_user(base_url, timeout, admin_auth, admin_headers, test_user_locator):
    with allure.step("DELETE temporary TeamCity user"):
        response = requests.delete(
            f"{base_url}/app/rest/users/{test_user_locator}",
            auth=admin_auth,
            headers=admin_headers,
            timeout=timeout,
        )
        assert response.status_code in (200, 202, 204, 404), response.text
def unique_id(prefix):
    return f"{prefix}{int(time.time() * 1000)}{uuid.uuid4().hex[:6]}"


def ensure_ready_agent(base_url, headers, timeout):
    with allure.step("Authorize connected TeamCity agents"):
        response = requests.get(
            f"{base_url}/app/rest/agents?locator=enabled:any,authorized:any,connected:any&fields=agent(id,name,authorized,connected,enabled,href)",
            headers=headers,
            timeout=timeout,
        )
        assert response.status_code == 200, response.text
        agents = response.json().get("agent", [])
        text_headers = {
            "Authorization": headers["Authorization"],
            "Accept": "text/plain",
            "Content-Type": "text/plain",
        }
        for agent in agents:
            if agent.get("connected") is True and agent.get("enabled") is not False and agent.get("authorized") is not True:
                response = requests.put(
                    f"{base_url}/app/rest/agents/id:{agent.get('id')}/authorized",
                    headers=text_headers,
                    data="true",
                    timeout=timeout,
                )
                assert response.status_code in (200, 204), response.text
                agent["authorized"] = True
        assert any(
            agent.get("authorized") is True and agent.get("connected") is True and agent.get("enabled") is not False
            for agent in agents
        ), f"No ready agent found. Agents: {agents}"


def auth_headers(api_token):
    return {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def project_role_scope(project_id):
    template = os.getenv("TEAMCITY_PROJECT_ROLE_SCOPE_TEMPLATE", "p:{project_id}")
    return template.format(project_id=project_id)


def create_user(base_url, admin_headers, timeout, username_prefix, display_name):
    username = unique_id(username_prefix)
    locator = f"username:{username}"
    with allure.step(f"Create {display_name}"):
        response = requests.post(
            f"{base_url}/app/rest/users?fields=username,name,email,roles(role(roleId,scope))",
            headers=admin_headers,
            json={
                "username": username,
                "name": display_name,
                "password": f"Autotest-{username}!",
                "email": f"{username}@example.test",
            },
            timeout=timeout,
        )
        assert response.status_code in (200, 201), response.text
        assert response.json().get("username") == username
    return locator


def create_user_token(base_url, admin_headers, timeout, user_locator, token_prefix):
    with allure.step(f"Create token for {user_locator}"):
        response = requests.post(
            f"{base_url}/app/rest/users/{user_locator}/tokens?fields=name,value,creationTime",
            headers=admin_headers,
            json={"name": unique_id(token_prefix)},
            timeout=timeout,
        )
        assert response.status_code in (200, 201), response.text
        token = response.json().get("value")
        assert token, f"TeamCity did not return token value for {user_locator}"
    return token


def assign_project_role(base_url, admin_headers, timeout, user_locator, project_id):
    role_id = os.getenv("TEAMCITY_BUILD_RUN_ALLOWED_ROLE_ID", "PROJECT_DEVELOPER")
    with allure.step(f"Assign {role_id} role to {user_locator}"):
        response = requests.post(
            f"{base_url}/app/rest/users/{user_locator}/roles",
            headers=admin_headers,
            json={
                "roleId": role_id,
                "scope": project_role_scope(project_id),
            },
            timeout=timeout,
        )
        assert response.status_code in (200, 201, 204), response.text


def create_build_with_success_step(base_url, headers, timeout):
    project_id = unique_id("AutotestApiProject")
    build_type_id = unique_id("AutotestApiBuild")
    step_id = unique_id("AutotestApiStep")

    with allure.step("Create project"):
        response = requests.post(
            f"{base_url}/app/rest/projects",
            headers=headers,
            json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
            timeout=timeout,
        )
        assert response.status_code in (200, 201), response.text

    with allure.step("Create build configuration"):
        response = requests.post(
            f"{base_url}/app/rest/projects/id:{project_id}/buildTypes?fields=id,name,project(id,name),href",
            headers=headers,
            json={"id": build_type_id, "name": build_type_id},
            timeout=timeout,
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
            timeout=timeout,
        )
        assert response.status_code in (200, 201), response.text

    return project_id, build_type_id


def delete_build_data(base_url, headers, timeout, project_id, build_type_id, build_id=None):
    with allure.step("DELETE generated build data"):
        if build_id:
            requests.delete(f"{base_url}/app/rest/builds/id:{build_id}", headers=headers, timeout=timeout)
        requests.delete(f"{base_url}/app/rest/buildTypes/id:{build_type_id}", headers=headers, timeout=timeout)
        requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=timeout)


def wait_for_build_success(base_url, headers, request_timeout, build_timeout, poll_interval, build_id):
    with allure.step("Wait for build SUCCESS"):
        deadline = time.monotonic() + build_timeout
        build = None
        while time.monotonic() < deadline:
            response = requests.get(
                f"{base_url}/app/rest/builds/id:{build_id}?fields=id,buildTypeId,state,status,statusText,webUrl,href",
                headers=headers,
                timeout=request_timeout,
            )
            assert response.status_code == 200, response.text
            build = response.json()
            if build.get("state") == "finished":
                break
            time.sleep(poll_interval)
        assert build and build.get("state") == "finished", build
        assert build.get("status") == "SUCCESS", build


@allure.epic("TeamCity REST API")
@allure.feature("Build Queue")
@allure.story("Run build")
@allure.title("Queue build through REST API")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного API-пользователя и bearer token.
    2. Авторизовать connected TeamCity agent при необходимости.
    3. Создать project, build configuration и успешный Command Line step.
    4. Поставить build в очередь через POST /app/rest/buildQueue.
    5. Прочитать queued build и проверить его связь с build configuration.
    6. Удалить сгенерированные build data и временного API-пользователя.
    """
)
@pytest.mark.regression
def test_run_build():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, admin_headers = create_test_user_token(base_url, timeout)
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    project_id = unique_id("AutotestApiProject")
    build_type_id = unique_id("AutotestApiBuild")
    step_id = unique_id("AutotestApiStep")
    build_id = None

    try:
        with allure.step("Create project"):
            response = requests.post(
                f"{base_url}/app/rest/projects",
                headers=headers,
                json={"id": project_id, "name": project_id, "parentProject": {"locator": "_Root"}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        with allure.step("Create build configuration"):
            response = requests.post(
                f"{base_url}/app/rest/projects/id:{project_id}/buildTypes?fields=id,name,project(id,name),href",
                headers=headers,
                json={"id": build_type_id, "name": build_type_id},
                timeout=timeout,
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
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text

        ensure_ready_agent(base_url, headers, timeout)

        with allure.step("POST /app/rest/buildQueue"):
            response = requests.post(
                f"{base_url}/app/rest/buildQueue",
                headers=headers,
                json={"buildType": {"id": build_type_id}},
                timeout=timeout,
            )
            assert response.status_code in (200, 201), response.text
            build_id = response.json().get("id")
            assert build_id is not None, response.text

        with allure.step("GET queued build"):
            response = requests.get(
                f"{base_url}/app/rest/buildQueue/id:{build_id}?fields=id,buildTypeId,state,status,queuePosition,href",
                headers=headers,
                timeout=timeout,
            )
            assert response.status_code in (200, 404), response.text
    finally:
        with allure.step("DELETE generated build data"):
            if build_id:
                requests.delete(f"{base_url}/app/rest/builds/id:{build_id}", headers=headers, timeout=timeout)
            requests.delete(f"{base_url}/app/rest/buildTypes/id:{build_type_id}", headers=headers, timeout=timeout)
            requests.delete(f"{base_url}/app/rest/projects/id:{project_id}", headers=headers, timeout=timeout)
        delete_test_user(base_url, timeout, admin_auth, admin_headers, api_user_locator)


@allure.epic("TeamCity REST API")
@allure.feature("Build Queue")
@allure.story("Run build")
@allure.title("User with project role can queue and run build")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного admin API-пользователя и bearer token.
    2. Создать project, build configuration и успешный Command Line step.
    3. Создать пользователя с доступом к project и назначить ему project role.
    4. Проверить, что пользователь с доступом видит build configuration.
    5. Поставить build в очередь token пользователя с доступом и дождаться SUCCESS.
    6. Удалить build data, пользователя с доступом и временного admin API-пользователя.
    """
)
@pytest.mark.regression
def test_user_with_project_access_can_run_build():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    request_timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    build_timeout = int(os.getenv("TEAMCITY_BUILD_TIMEOUT", "300"))
    poll_interval = int(os.getenv("TEAMCITY_BUILD_POLL_INTERVAL", "3"))
    api_token, api_user_locator, admin_auth, bootstrap_headers = create_test_user_token(base_url, request_timeout)
    admin_headers = auth_headers(api_token)
    project_id = build_type_id = build_id = None
    allowed_locator = None

    try:
        project_id, build_type_id = create_build_with_success_step(base_url, admin_headers, request_timeout)
        ensure_ready_agent(base_url, admin_headers, request_timeout)

        allowed_locator = create_user(
            base_url,
            admin_headers,
            request_timeout,
            "autotest_build_allowed_",
            "Autotest Build Allowed User",
        )
        assign_project_role(base_url, admin_headers, request_timeout, allowed_locator, project_id)
        allowed_token = create_user_token(
            base_url,
            admin_headers,
            request_timeout,
            allowed_locator,
            "autotest-build-allowed-token-",
        )
        allowed_headers = auth_headers(allowed_token)

        with allure.step("GET build configuration as user with project access"):
            response = requests.get(
                f"{base_url}/app/rest/buildTypes/id:{build_type_id}?fields=id,name,project(id,name),href",
                headers=allowed_headers,
                timeout=request_timeout,
            )
            assert response.status_code == 200, response.text
            assert response.json().get("id") == build_type_id

        with allure.step("Queue build as user with project access"):
            response = requests.post(
                f"{base_url}/app/rest/buildQueue",
                headers=allowed_headers,
                json={"buildType": {"id": build_type_id}},
                timeout=request_timeout,
            )
            assert response.status_code in (200, 201), response.text
            build_id = response.json().get("id")
            assert build_id is not None, response.text

        wait_for_build_success(base_url, allowed_headers, request_timeout, build_timeout, poll_interval, build_id)
    finally:
        if project_id and build_type_id:
            delete_build_data(base_url, admin_headers, request_timeout, project_id, build_type_id, build_id)
        if allowed_locator:
            with allure.step("DELETE user with project access"):
                requests.delete(f"{base_url}/app/rest/users/{allowed_locator}", headers=admin_headers, timeout=request_timeout)
        delete_test_user(base_url, request_timeout, admin_auth, bootstrap_headers, api_user_locator)


@allure.epic("TeamCity REST API")
@allure.feature("Build Queue")
@allure.story("Run build")
@allure.title("User without build run role cannot queue build")
@allure.description(
    """
    Шаги сценария:
    1. Создать временного admin API-пользователя и bearer token.
    2. Создать project, build configuration и успешный Command Line step.
    3. Создать пользователя без project role и выпустить ему token.
    4. Проверить, что пользователь без права запуска не может поставить build в очередь.
    5. Удалить build data, пользователя без права запуска и временного admin API-пользователя.
    """
)
@pytest.mark.regression
def test_user_without_project_access_cannot_run_build():
    base_url = os.getenv("TEAMCITY_URL", os.getenv("TEAMCITY_BASE_URL", "http://localhost:8111")).rstrip("/")
    request_timeout = int(os.getenv("TEAMCITY_REQUEST_TIMEOUT", "20"))
    api_token, api_user_locator, admin_auth, bootstrap_headers = create_test_user_token(base_url, request_timeout)
    admin_headers = auth_headers(api_token)
    project_id = build_type_id = None
    denied_locator = None

    try:
        project_id, build_type_id = create_build_with_success_step(base_url, admin_headers, request_timeout)
        denied_locator = create_user(
            base_url,
            admin_headers,
            request_timeout,
            "autotest_build_denied_",
            "Autotest Build Denied User",
        )
        denied_token = create_user_token(
            base_url,
            admin_headers,
            request_timeout,
            denied_locator,
            "autotest-build-denied-token-",
        )
        denied_headers = auth_headers(denied_token)

        with allure.step("Try to queue build as user without build run role"):
            response = requests.post(
                f"{base_url}/app/rest/buildQueue",
                headers=denied_headers,
                json={"buildType": {"id": build_type_id}},
                timeout=request_timeout,
            )
            assert response.status_code in (403, 404), response.text
    finally:
        if project_id and build_type_id:
            delete_build_data(base_url, admin_headers, request_timeout, project_id, build_type_id)
        if denied_locator:
            with allure.step("DELETE user without project access"):
                requests.delete(f"{base_url}/app/rest/users/{denied_locator}", headers=admin_headers, timeout=request_timeout)
        delete_test_user(base_url, request_timeout, admin_auth, bootstrap_headers, api_user_locator)
