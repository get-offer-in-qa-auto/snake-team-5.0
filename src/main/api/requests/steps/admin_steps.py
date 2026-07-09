from typing import List
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


class AdminSteps(BaseSteps):
    def create_user(self, user_request: CreateUserRequest):
        pass

    def create_invalid_user(self, user_request: CreateUserRequest, error_key: str, error_value: str):
        pass

    def delete_user(self, user_id: int):
        pass

    def get_all_users(self) -> List[CreateUserRequest]:
        response = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_GET_ALL_USERS,
            ResponseSpecs.request_returns_ok()
        ).get()
        return response