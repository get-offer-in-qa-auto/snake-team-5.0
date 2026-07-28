from unittest.mock import Mock

import pytest
import requests

from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester


@pytest.mark.parametrize(
    ("crud_method", "requests_method"),
    [
        ("post", "post"),
        ("get", "get"),
        ("update", "put"),
        ("delete", "delete"),
    ],
)
def test_crud_request_uses_configured_timeout(
    monkeypatch, crud_method, requests_method
):
    monkeypatch.setenv("TEAMCITY_URL", "http://teamcity.test")
    response = Mock()
    request = Mock(return_value=response)
    monkeypatch.setattr(requests, requests_method, request)
    requester = CrudRequester(
        request_spec={},
        endpoint=Endpoint.GET_PROJECT,
        response_spec=lambda _: None,
    )

    getattr(requester, crud_method)()

    assert request.call_args.kwargs["timeout"] == requester.request_timeout
