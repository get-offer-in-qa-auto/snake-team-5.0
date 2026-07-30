import allure
from playwright.sync_api import Page, expect

from src.main.ui.pages.base_page import BasePage
from src.main.ui.routes.teamcity_routes import TeamCityRoutes


class BuildStepsPage(BasePage):
    def __init__(self, page: Page, build_configuration_id: str) -> None:
        super().__init__(page)
        self.build_configuration_id = build_configuration_id

    @property
    def path(self) -> str:
        return TeamCityRoutes.build_steps(self.build_configuration_id)

    @allure.step("Verify build steps page is opened")
    def should_be_opened(self) -> "BuildStepsPage":
        expect(self.page).to_have_url(f"{self.base_url}{self.path}")
        return self
