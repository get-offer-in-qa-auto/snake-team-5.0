from enum import Enum
from http import HTTPStatus
from typing import Callable
from requests import Response


class ResponseError(str, Enum):
    PROJECT_ID_ALREADY_USED = "already used"
    PROJECT_NAME_ALREADY_EXISTS = "with this name already exists"
    PROJECT_NOT_FOUND = "No project found"
    BUILD_CONFIGURATION_ID_ALREADY_USED = "already used"
    BUILD_CONFIGURATION_NAME_ALREADY_EXISTS = "already exists in project"
    BUILD_CONFIGURATION_NOT_FOUND = "No build type nor template is found"
    USERNAME_ALREADY_EXISTS = "already exists"
    USER_NOT_FOUND = "User not found"
    INCORRECT_USERNAME_OR_PASSWORD = "Incorrect username or password"
    BUILD_STEP_NOT_FOUND = "No step with id"



class ResponseSpecs:
    @staticmethod
    def _make_status_checker(expected_statuses: list[HTTPStatus]) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code in expected_statuses, (
                f"Expected status {expected_statuses}, but got {response.status_code}. "
                f"Response body: {response.text}"
            )
        return check

    @staticmethod
    def request_returns_ok() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK])

    @staticmethod
    def entity_was_created() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.CREATED])

    @staticmethod
    def entity_was_created_or_ok() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK, HTTPStatus.CREATED])

    @staticmethod
    def entity_was_deleted() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([
            HTTPStatus.OK,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT,
        ])

    @staticmethod
    def request_returns_bad_request(
        error_key: str,
        error_value: str
    ) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"Expected 400 BAD_REQUEST, got {response.status_code}. Response: {response.text}"
            )
            try:
                actual_value = response.json().get(error_key)
            except ValueError:
                actual_value = response.text

            assert error_value in actual_value, (
                f"Expected error field '{error_key}' to be '{error_value}', but got '{actual_value}'."
            )
        return check

    @staticmethod
    def request_returns_status_with_text(
        expected_status: HTTPStatus,
        expected_text: str
    ) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == expected_status, (
                f"Expected {expected_status.value} {expected_status.phrase}, "
                f"got {response.status_code}. Response: {response.text}"
            )
            assert expected_text in response.text, (
                f"Expected response text to contain '{expected_text}', "
                f"but got '{response.text}'."
            )
        return check

    @staticmethod
    def request_returns_bad_request_with_text(
        error_text: ResponseError | str
    ) -> Callable[[Response], None]:
        expected_error = (
            error_text.value
            if isinstance(error_text, ResponseError)
            else str(error_text)
        )
        return ResponseSpecs.request_returns_status_with_text(
            HTTPStatus.BAD_REQUEST,
            expected_error
        )

    @staticmethod
    def request_returns_not_found_with_text(
        error_text: ResponseError | str
    ) -> Callable[[Response], None]:
        expected_error = (
            error_text.value
            if isinstance(error_text, ResponseError)
            else str(error_text)
        )
        return ResponseSpecs.request_returns_status_with_text(
            HTTPStatus.NOT_FOUND,
            expected_error
        )

    @staticmethod
    def request_returns_unauthorized() -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == HTTPStatus.UNAUTHORIZED, (
                f"Expected 401 UNAUTHORIZED, got {response.status_code}. "
                f"Response: {response.text}"
            )
            assert "Authentication required" in response.text, (
                "Expected TeamCity authentication error, "
                f"but got '{response.text}'."
            )
        return check

    @staticmethod
    def request_returns_unauthorized_with_text(
        error_text: ResponseError | str
    ) -> Callable[[Response], None]:
        expected_error = (
            error_text.value
            if isinstance(error_text, ResponseError)
            else str(error_text)
        )
        return ResponseSpecs.request_returns_status_with_text(
            HTTPStatus.UNAUTHORIZED,
            expected_error
        )

    @staticmethod
    def request_returns_unauthorized_status() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.UNAUTHORIZED])

    @staticmethod
    def request_returns_forbidden() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.FORBIDDEN])
