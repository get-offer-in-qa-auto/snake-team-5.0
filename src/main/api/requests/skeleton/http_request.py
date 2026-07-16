from collections.abc import Callable

from src.main.api.requests.skeleton.endpoint import Endpoint


class HttpRequest:
    def __init__(
        self, request_spec: dict[str, str], endpoint: Endpoint, response_spec: Callable
    ):
        self.request_spec = request_spec
        self.endpoint = endpoint
        self.response_spec = response_spec
