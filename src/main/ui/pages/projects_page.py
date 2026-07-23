from __future__ import annotations

from typing import TYPE_CHECKING

import allure
from playwright.sync_api import Locator, expect

from src.main.api.models.create_project_request import CreateProjectRequest
from src.main.ui.components.teamcity_header import TeamCityHeader
from src.main.ui.pages.base_page import BasePage

if TYPE_CHECKING:
    from src.main.ui.pages.create_project_page import CreateProjectPage


class ProjectsPage(BasePage):
    path = "/favorite/projects"

    @property
    def header(self) -> TeamCityHeader:
        return TeamCityHeader(self.page)

    @property
    def create_project_link(self) -> Locator:
        return self.page.locator('[data-test="sidebar"] [data-test-title="Create"] a')

    @allure.step("Open project creation page")
    def open_create_project(self) -> CreateProjectPage:
        from src.main.ui.pages.create_project_page import CreateProjectPage

        self.create_project_link.click()
        return CreateProjectPage(self.page)

    @allure.step("Verify user is authenticated")
    def should_be_authenticated(self) -> ProjectsPage:
        self.header.should_be_visible()
        return self

    @allure.step("Verify project is displayed")
    def should_contain_project(
        self, project_request: CreateProjectRequest
    ) -> ProjectsPage:
        project_card = self.page.locator(
            f'[data-test="subproject"][data-project-id="{project_request.id}"]'
        )
        expect(project_card).to_be_visible()
        expect(project_card).to_contain_text(project_request.name)
        return self
