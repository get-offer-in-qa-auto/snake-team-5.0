from collections.abc import Callable
from enum import StrEnum
from typing import Any, TypeVar, cast

import allure


class AllureTag(StrEnum):
    API = "api"
    REGRESSION = "regression"
    SMOKE = "smoke"

    AUTHORIZATION = "authorization"
    BUILD_CONFIGURATION = "build-configuration"
    BUILD_STEP = "build-step"
    CONFIGURATION = "configuration"
    DATABASE = "database"
    NEGATIVE = "negative"
    PERMISSIONS = "permissions"
    PROJECT = "project"
    TOKEN = "token"
    USER = "user"


TestCallable = TypeVar("TestCallable", bound=Callable[..., Any])


def allure_tags(*tags: AllureTag) -> Callable[[TestCallable], TestCallable]:
    unique_values = tuple(tag.value for tag in dict.fromkeys(tags))
    decorator = allure.tag(*unique_values)

    def apply(test: TestCallable) -> TestCallable:
        return cast(TestCallable, decorator(test))

    return apply


def api_regression_tags(
    *tags: AllureTag,
    smoke: bool = False,
) -> Callable[[TestCallable], TestCallable]:
    common_tags = [AllureTag.API]
    if smoke:
        common_tags.append(AllureTag.SMOKE)
    common_tags.append(AllureTag.REGRESSION)

    return allure_tags(*common_tags, *tags)
