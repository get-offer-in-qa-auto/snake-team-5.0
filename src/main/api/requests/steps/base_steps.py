from collections.abc import Callable
from typing import Any

import allure

from src.main.api.models.comparison.model_assertions import ModelAssertions


class BaseSteps:
    def __init__(self, created_objects: list[Any]):
        self.created_objects = created_objects

    def _unregister_created_objects(self, predicate: Callable[[Any], bool]) -> None:
        """Stop cleanup from deleting entities already removed by a test action."""
        self.created_objects[:] = [
            obj for obj in self.created_objects if not predicate(obj)
        ]

    @allure.step("Verify response matches expected model")
    def verify_response_matches(self, expected: Any, actual: Any) -> None:
        ModelAssertions(expected, actual).match()

    @allure.step("Verify entity has different id and name")
    def verify_distinct_id_and_name(self, entity: Any) -> None:
        assert entity.id != entity.name
