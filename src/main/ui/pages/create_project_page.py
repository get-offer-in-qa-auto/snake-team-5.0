from playwright.sync_api import Locator, expect

from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.ui.pages.base_page import BasePage


class CreateProjectPage(BasePage):
    path = "/projects/create?projectId=_Root"

    @property
    def project_name_input(self) -> Locator:
        return self.page.locator('[data-test="project-name-input"]')

    @property
    def project_id_input(self) -> Locator:
        return self.page.locator('[data-test="project-id-input"]')

    @property
    def create_button(self) -> Locator:
        return self.page.get_by_role("button", name="Create", exact=True)

    @property
    def project_setup(self) -> Locator:
        return self.page.locator('[data-test="setup-project-page"]')

    def create_project(
        self, project_request: CreateProjectRequest
    ) -> "CreateProjectPage":
        self.project_name_input.fill(project_request.name)
        self.project_id_input.fill(project_request.id)
        self.create_button.click()
        expect(self.project_setup).to_contain_text("New connection")
        return self
