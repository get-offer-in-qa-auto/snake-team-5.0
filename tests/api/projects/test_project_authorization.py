import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_project_request import CreateProjectRequest


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
