from typing import Protocol

from requests import Response

from src.main.api.models.base_model import BaseModel


class CrudEndpointInterface(Protocol):
    def post(
        self,
        model: BaseModel | None = None,
        path: str | None = None,
        allow_redirects: bool = True,
    ) -> Response: ...

    def get(self, id: int | str | None = None) -> Response: ...

    def update(self, model: BaseModel | None = None) -> Response: ...

    def delete(self, id: int | str) -> Response: ...
