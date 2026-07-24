import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.constants.teamcity import TeamCityLocator
from src.main.reporting.allure.tags import AllureTag, api_regression_tags


@allure.title("Create subproject")
@api_regression_tags(AllureTag.PROJECT)
@pytest.mark.api
@pytest.mark.regression
def test_create_subproject(api_manager: ApiManager, project_request_factory):
    parent_request = project_request_factory()
    parent_project = api_manager.admin_steps.create_project(parent_request)
    child_request = project_request_factory(
        parent_locator=TeamCityLocator.by_id(parent_project.id)
    )

    child_project = api_manager.admin_steps.create_project(child_request)
    stored_child_project = api_manager.admin_steps.get_project(child_project.id)

    api_manager.admin_steps.verify_project_stored(
        child_request, stored_child_project, parent_project.id
    )


@allure.title("Projects with same name can be created in different parents")
@api_regression_tags(AllureTag.PROJECT)
@pytest.mark.api
@pytest.mark.regression
def test_create_projects_with_same_name_in_different_parents(
    api_manager: ApiManager, project_request_factory
):
    first_parent = api_manager.admin_steps.create_project(project_request_factory())
    second_parent = api_manager.admin_steps.create_project(project_request_factory())
    shared_name = project_request_factory().name
    first_child_request = project_request_factory(
        name=shared_name, parent_locator=TeamCityLocator.by_id(first_parent.id)
    )
    second_child_request = project_request_factory(
        name=shared_name, parent_locator=TeamCityLocator.by_id(second_parent.id)
    )

    first_child = api_manager.admin_steps.create_project(first_child_request)
    second_child = api_manager.admin_steps.create_project(second_child_request)
    stored_first_child = api_manager.admin_steps.get_project(first_child.id)
    stored_second_child = api_manager.admin_steps.get_project(second_child.id)

    api_manager.admin_steps.verify_project_stored(
        first_child_request, stored_first_child, first_parent.id
    )
    api_manager.admin_steps.verify_project_stored(
        second_child_request, stored_second_child, second_parent.id
    )
