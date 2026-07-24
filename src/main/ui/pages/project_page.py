from __future__ import annotations

from urllib.parse import quote

import allure
from playwright.sync_api import Locator, expect

from src.main.api.models.project_response import ProjectResponse
from src.main.ui.pages.base_page import BasePage


class ProjectPage(BasePage):
    def __init__(self, page, project: ProjectResponse) -> None:
        super().__init__(page)
        self.project = project

    @property
    def path(self) -> str:
        return f"/project/{quote(self.project.id, safe='')}"

    @property
    def heading(self) -> Locator:
        return self.page.locator("main h1")

    @property
    def create_entity_button(self) -> Locator:
        return self.page.locator(
            'main [data-hint-container-id="project-create-entity"]'
        )

    @allure.step("Verify project page is opened")
    def should_be_opened(self) -> ProjectPage:
        expect(self.heading).to_contain_text(self.project.name)
        return self

    @allure.step("Verify project creation actions are unavailable")
    def should_not_allow_creation(self) -> ProjectPage:
        expect(self.create_entity_button).not_to_be_visible()
        return self
