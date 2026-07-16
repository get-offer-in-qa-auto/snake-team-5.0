import os
from typing import TypeVar

import requests

from src.main.api.configs.config import Config
from src.main.api.models.base_model import BaseModel
from src.main.api.requests.skeleton.http_request import HttpRequest
from src.main.api.requests.skeleton.interfaces.crud_end_interface import (
    CrudEndpointInterface,
)

T = TypeVar("T", bound=BaseModel)


class CrudRequester(HttpRequest, CrudEndpointInterface):
    @property
    def base_url(self) -> str:
        server_url = (
            os.getenv("TEAMCITY_URL")
            or os.getenv("TEAMCITY_BASE_URL")
            or Config.get("server")
        ).rstrip("/")
        return f"{server_url}{Config.get('apiBasePath')}"

    def post(
        self,
        model: T | None = None,
        path: str | None = None,
        allow_redirects: bool = True,
    ) -> requests.Response:
        body = model.model_dump() if model is not None else ""

        response = requests.post(
            url=(
                f"{self.base_url}{self.endpoint.value.url}"
                f"{('/' + path) if path is not None else ''}"
            ),
            headers=self.request_spec,
            json=body,
            allow_redirects=allow_redirects,
        )
        self.response_spec(response)
        return response

    def get(self, id: int | str | None = None):
        response = requests.get(
            url=f"{self.base_url}{self.endpoint.value.url}{('/' + str(id)) if id is not None else ''}",
            headers=self.request_spec,
        )
        self.response_spec(response)
        return response

    def update(
        self, model: T | None = None, path: str | None = None
    ) -> requests.Response:
        body = model.model_dump() if model is not None else ""

        response = requests.put(
            url=(
                f"{self.base_url}{self.endpoint.value.url}"
                f"{('/' + path) if path is not None else ''}"
            ),
            headers=self.request_spec,
            json=body,
        )
        self.response_spec(response)
        return response

    def delete(self, id: int | str) -> requests.Response:
        response = requests.delete(
            url=f"{self.base_url}{self.endpoint.value.url}/{id}",
            headers=self.request_spec,
        )
        self.response_spec(response)
        return response
