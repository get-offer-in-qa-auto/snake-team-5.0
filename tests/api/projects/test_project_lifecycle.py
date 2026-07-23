import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_project_request import CreateProjectRequest


@allure.title("Create project")
@allure.tag("api", "smoke", "regression", "project")
@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
def test_create_project(api_manager: ApiManager, project_request: CreateProjectRequest):
    project_response = api_manager.admin_steps.create_project(project_request)
    stored_project = api_manager.admin_steps.get_project(project_response.id)

    api_manager.admin_steps.verify_project_created(
        project_request, project_response, stored_project
    )


@allure.title("Created project is persisted in database")
@allure.tag("api", "regression", "project", "database")
@pytest.mark.api
@pytest.mark.regression
def test_created_project_is_persisted_in_database(
    api_manager: ApiManager, project_request: CreateProjectRequest
):
    project_response = api_manager.admin_steps.create_project(project_request)

    api_manager.database_steps.verify_project_persisted(project_response)


@allure.title("Delete project")
@allure.tag("api", "regression", "project", "database")
@pytest.mark.api
@pytest.mark.regression
def test_delete_project(
    api_manager: ApiManager,
    project_request: CreateProjectRequest,
):
    project = api_manager.admin_steps.create_project(project_request)

    api_manager.admin_steps.delete_project(project.id)

    api_manager.admin_steps.check_project_does_not_exist(project.id)
    api_manager.database_steps.verify_project_deleted(project.id)


@allure.title("Create project with different id and name")
@allure.tag("api", "regression", "project")
@pytest.mark.api
@pytest.mark.regression
def test_create_project_with_different_id_and_name(
    api_manager: ApiManager, project_request_factory
):
    project_request = project_request_factory()

    project_response = api_manager.admin_steps.create_project(project_request)
    stored_project = api_manager.admin_steps.get_project(project_response.id)

    api_manager.admin_steps.verify_distinct_id_and_name(project_request)
    api_manager.admin_steps.verify_response_matches(project_request, stored_project)
