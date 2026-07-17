from typing import Any

import allure

from src.main.api.models.comparison.model_assertions import ModelAssertions


class BaseSteps:
    def __init__(self, created_objects: list[Any]):
        self.created_objects = created_objects

    @allure.step("Verify response matches expected model")
    def verify_response_matches(self, expected: Any, actual: Any) -> None:
        ModelAssertions(expected, actual).match()

    @allure.step("Verify entity has different id and name")
    def verify_distinct_id_and_name(self, entity: Any) -> None:
        assert entity.id != entity.name
