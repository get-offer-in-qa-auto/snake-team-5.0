from http import HTTPStatus
from typing import Optional, TypeVar, Union
import requests

from src.main.api.configs.config import Config
from src.main.api.models.base_model import BaseModel
from src.main.api.requests.skeleton.http_request import HttpRequest
from src.main.api.requests.skeleton.interfaces.crud_end_interface import CrudEndpointInterface

T = TypeVar('T', bound=BaseModel)


class CrudRequester(HttpRequest, CrudEndpointInterface):
    @property
    def base_url(self) -> str:
        return f"{Config.get('server')}{Config.get('apiBasePath')}"

    def post(
        self,
        model: Optional[T] = None,
        path: Optional[str] = None,
        allow_redirects: bool = True
    ) -> requests.Response:
        body = model.model_dump() if model is not None else ''

        response = requests.post(
            url=(
                f'{self.base_url}{self.endpoint.value.url}'
                f'{("/" + path) if path is not None else ""}'
            ),
            headers=self.request_spec,
            json=body,
            allow_redirects=allow_redirects
        )
        self.response_spec(response)
        return response

    def get(self, id: Optional[Union[int, str]] = None):
        response = requests.get(
            url=f'{self.base_url}{self.endpoint.value.url}{("/" + str(id)) if id is not None else ""}',
            headers=self.request_spec
        )
        self.response_spec(response)
        return response

    def update(self, model: Optional[T] = None, path: Optional[str] = None) -> requests.Response:
        body = model.model_dump() if model is not None else ''

        response = requests.put(
            url=(
                f'{self.base_url}{self.endpoint.value.url}'
                f'{("/" + path) if path is not None else ""}'
            ),
            headers=self.request_spec,
            json=body,
        )

        self.response_spec(response)
        return response


    def delete(self, path: str | None = None) -> requests.Response:
        response = requests.delete(
            url=(
                f"{self.base_url}{self.endpoint.value.url}"
                f'{("/" + path) if path is not None else ""}'
            ),
            headers=self.request_spec,
        )
        self.response_spec(response)
        return response
