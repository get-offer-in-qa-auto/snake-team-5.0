import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.api.specs.response_specs import ResponseError


@allure.title("Create project")
@allure.tag("api", "smoke", "regression", "project")
@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.regression
def test_create_project(api_manager: ApiManager, project_request: CreateProjectRequest):
    project_response = api_manager.admin_steps.create_project(project_request)
    stored_project = api_manager.admin_steps.get_project(project_response.id)

    ModelAssertions(project_request, project_response).match()
    ModelAssertions(project_request, stored_project).match()
    assert project_response.href
    assert stored_project.parentProject is not None
    assert stored_project.parentProject.id == "_Root"


@allure.title("Created project is persisted in database")
@allure.tag("api", "regression", "project", "database")
@pytest.mark.api
@pytest.mark.regression
def test_created_project_is_persisted_in_database(
    api_manager: ApiManager, project_request: CreateProjectRequest
):
    project_response = api_manager.admin_steps.create_project(project_request)

    database_project = api_manager.database_steps.verify_project_persisted(
        project_response.id
    )

    assert database_project.external_id == project_response.id
    assert database_project.internal_id.startswith("project")
    assert database_project.config_id


@allure.title("Create subproject")
@allure.tag("api", "regression", "project")
@pytest.mark.api
@pytest.mark.regression
def test_create_subproject(api_manager: ApiManager, project_request_factory):
    parent_request = project_request_factory()
    parent_project = api_manager.admin_steps.create_project(parent_request)
    child_request = project_request_factory(parent_locator=f"id:{parent_project.id}")

    child_project = api_manager.admin_steps.create_project(child_request)
    stored_child_project = api_manager.admin_steps.get_project(child_project.id)

    ModelAssertions(child_request, stored_child_project).match()
    assert stored_child_project.parentProject is not None
    assert stored_child_project.parentProject.id == parent_project.id


@allure.title("Project cannot be created with existing id")
@allure.tag("api", "regression", "project", "negative")
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
    ModelAssertions(project_request, stored_project).match()


@allure.title("Project cannot be created with existing name in same parent")
@allure.tag("api", "regression", "project", "negative")
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


@allure.title("Projects with same name can be created in different parents")
@allure.tag("api", "regression", "project")
@pytest.mark.api
@pytest.mark.regression
def test_create_projects_with_same_name_in_different_parents(
    api_manager: ApiManager, project_request_factory
):
    first_parent = api_manager.admin_steps.create_project(project_request_factory())
    second_parent = api_manager.admin_steps.create_project(project_request_factory())
    shared_name = project_request_factory().name
    first_child_request = project_request_factory(
        name=shared_name, parent_locator=f"id:{first_parent.id}"
    )
    second_child_request = project_request_factory(
        name=shared_name, parent_locator=f"id:{second_parent.id}"
    )

    first_child = api_manager.admin_steps.create_project(first_child_request)
    second_child = api_manager.admin_steps.create_project(second_child_request)
    stored_first_child = api_manager.admin_steps.get_project(first_child.id)
    stored_second_child = api_manager.admin_steps.get_project(second_child.id)

    assert stored_first_child.id != stored_second_child.id
    assert stored_first_child.name == stored_second_child.name == shared_name
    assert stored_first_child.parentProject is not None
    assert stored_second_child.parentProject is not None
    assert stored_first_child.parentProject.id == first_parent.id
    assert stored_second_child.parentProject.id == second_parent.id


@allure.title("Project cannot be created with unknown parent")
@allure.tag("api", "regression", "project", "negative")
@pytest.mark.api
@pytest.mark.regression
def test_create_project_with_unknown_parent(
    api_manager: ApiManager, project_request_factory
):
    project_request = project_request_factory(
        parent_locator="id:MissingParentForAutotest"
    )

    api_manager.admin_steps.create_project_not_found(
        project_request, ResponseError.PROJECT_NOT_FOUND
    )
    api_manager.admin_steps.check_project_does_not_exist(project_request.id)


@allure.title("Project cannot be created without authorization")
@allure.tag("api", "regression", "project", "authorization", "negative")
@pytest.mark.api
@pytest.mark.regression
def test_create_project_without_authorization(
    api_manager: ApiManager, project_request: CreateProjectRequest
):
    api_manager.admin_steps.create_project_without_authorization(project_request)
    api_manager.admin_steps.check_project_does_not_exist(project_request.id)
    api_manager.database_steps.verify_project_not_created(project_request.id)


@allure.title("Delete project")
@allure.tag("api", "regression", "project", "database")
@pytest.mark.api
@pytest.mark.regression
def test_delete_project(
    api_manager: ApiManager,
    project_request: CreateProjectRequest,
    created_objects: list,
):
    project = api_manager.admin_steps.create_project(project_request)

    api_manager.admin_steps.delete_project(project.id)
    created_objects.remove(project)

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

    assert project_request.id != project_request.name
    ModelAssertions(project_request, stored_project).match()
