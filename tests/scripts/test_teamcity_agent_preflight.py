from unittest.mock import Mock

import pytest

from scripts import teamcity_agent_preflight


@pytest.mark.regression
def test_authorizes_and_waits_for_expanded_agent_status(monkeypatch):
    unauthorized_response = Mock()
    unauthorized_response.json.return_value = {
        "agent": [
            {
                "id": 1,
                "name": "ci-agent-1",
                "authorized": False,
                "connected": True,
                "enabled": True,
            }
        ]
    }
    ready_response = Mock()
    ready_response.json.return_value = {
        "agent": [
            {
                "id": 1,
                "name": "ci-agent-1",
                "authorized": True,
                "connected": True,
                "enabled": True,
            }
        ]
    }
    get = Mock(side_effect=[unauthorized_response, ready_response])
    put = Mock()

    monkeypatch.setattr(teamcity_agent_preflight.requests, "get", get)
    monkeypatch.setattr(teamcity_agent_preflight.requests, "put", put)
    monkeypatch.setattr(
        teamcity_agent_preflight.RequestSpecs,
        "_server_url",
        staticmethod(lambda: "http://localhost:8111"),
    )
    monkeypatch.setattr(
        teamcity_agent_preflight.RequestSpecs,
        "admin_auth_spec",
        staticmethod(lambda csrf=False: {"Authorization": "Bearer test-token"}),
    )
    monkeypatch.setattr(teamcity_agent_preflight.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        teamcity_agent_preflight.sys,
        "argv",
        ["teamcity-agent-preflight", "--name", "ci-agent-1", "--timeout", "1"],
    )

    assert teamcity_agent_preflight.main() == 0
    assert get.call_count == 2
    assert get.call_args.kwargs["params"] == {
        "locator": "authorized:any,defaultFilter:false",
        "fields": "agent(id,name,authorized,connected,enabled)",
    }
    put.assert_called_once()
