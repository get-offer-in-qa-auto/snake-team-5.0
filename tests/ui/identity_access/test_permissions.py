import pytest
from playwright.sync_api import Page

from src.main.api.models.project_response import ProjectResponse
from src.main.ui.pages.project_page import ProjectPage


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.user_session("project_viewer_user")
def test_project_viewer_cannot_create_entities(page: Page, project: ProjectResponse):
    ProjectPage(page, project).open().should_be_opened().should_not_allow_creation()
