import os

import pytest

from scripts.teamcity_start_smoke import is_expected_first_start, request_url


@pytest.mark.smoke
@pytest.mark.short
def test_teamcity_web_endpoint_is_opened():
    teamcity_url = os.getenv("TEAMCITY_URL", "http://localhost:8111")

    status, body = request_url(teamcity_url, timeout=10)

    assert status is not None, f"TeamCity did not return an HTTP response: {body}"
    assert (200 <= status < 500) or is_expected_first_start(status, body), (
        f"TeamCity returned unexpected HTTP {status}. "
        f"Response snippet: {body[:500]}"
    )
