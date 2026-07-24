import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.constants.teamcity import TeamCityLocator
from src.main.api.specs.response_specs import ResponseError
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Project cannot be created with existing id")
@api_regression_tags(AllureTag.PROJECT, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_create_project_with_existing_id(
    api_manager: ApiManager, project_request_factory
):
    project_request = project_request_factory()
    api_manager.admin_steps.create_project(project_request)
    duplicate_request = project_request_factory(project_id=project_request.id)

    api_manager.admin_steps.create_project_bad_request(
        duplicate_request, ResponseError.PROJECT_ID_ALREADY_USED
    )

    stored_project = api_manager.admin_steps.get_project(project_request.id)
    api_manager.admin_steps.verify_response_matches(project_request, stored_project)


@allure.title("Project cannot be created with existing name in same parent")
@api_regression_tags(AllureTag.PROJECT, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_create_project_with_existing_name_in_same_parent(
    api_manager: ApiManager, project_request_factory
):
    project_request = project_request_factory()
    api_manager.admin_steps.create_project(project_request)
    duplicate_request = project_request_factory(name=project_request.name)

    api_manager.admin_steps.create_project_bad_request(
        duplicate_request, ResponseError.PROJECT_NAME_ALREADY_EXISTS
    )

    api_manager.admin_steps.check_project_does_not_exist(duplicate_request.id)


@allure.title("Project cannot be created with unknown parent")
@api_regression_tags(AllureTag.PROJECT, AllureTag.NEGATIVE)
@pytest.mark.api
@pytest.mark.regression
def test_create_project_with_unknown_parent(
    api_manager: ApiManager,
    project_request_factory,
    nonexistent_project_id: str,
):
    project_request = project_request_factory(
        parent_locator=TeamCityLocator.by_id(nonexistent_project_id)
    )

    api_manager.admin_steps.create_project_not_found(
        project_request, ResponseError.PROJECT_NOT_FOUND
    )
    api_manager.admin_steps.check_project_does_not_exist(project_request.id)
