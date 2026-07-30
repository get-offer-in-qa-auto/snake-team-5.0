import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.constants.teamcity import ROOT_PROJECT_ID
from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.ui.pages.projects_page import ProjectsPage


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.admin_session
@pytest.mark.entity_will_be_created("project_request")
def test_admin_can_create_project(
    page: Page,
    api_manager: ApiManager,
    project_request: CreateProjectRequest,
):
    (
        ProjectsPage(page)
        .open()
        .open_create_project()
        .create_project_success(project_request)
        .should_be_opened()
    )

    ProjectsPage(page).open().should_contain_project(project_request)

    stored_project = api_manager.admin_steps.get_project(project_request.id)
    api_manager.admin_steps.verify_project_stored(
        project_request, stored_project, ROOT_PROJECT_ID
    )
