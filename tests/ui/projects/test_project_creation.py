import pytest
from playwright.sync_api import Page

from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.ui.pages.projects_page import ProjectsPage


@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.admin_session
@pytest.mark.entity_will_be_created("project_request")
def test_admin_can_create_project(page: Page, project_request: CreateProjectRequest):
    (
        ProjectsPage(page)
        .open()
        .open_create_project()
        .create_project_success(project_request)
        .should_be_opened()
    )

    ProjectsPage(page).open().should_contain_project(project_request)
