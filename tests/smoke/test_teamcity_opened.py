import os

import allure
import pytest

from scripts.teamcity_start_smoke import (
    classify_teamcity_response,
    format_readiness_message,
    request_url,
)


@allure.epic("TeamCity")
@allure.feature("Readiness")
@allure.story("Web endpoint")
@allure.title("TeamCity web endpoint is opened")
@pytest.mark.smoke
@pytest.mark.regression
def test_teamcity_web_endpoint_is_opened():
    teamcity_url = os.getenv("TEAMCITY_URL", "http://localhost:8111/login.html")

    status, body = request_url(teamcity_url, timeout=10)
    readiness = classify_teamcity_response(status, body)

    assert readiness.opened, (
        f"{format_readiness_message(readiness, teamcity_url)} "
        f"Response snippet: {body[:500]}"
    )
