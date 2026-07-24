import allure
from playwright.sync_api import Locator, Page, expect


class TeamCityHeader:
    ROOT_LOCATOR = '[data-test-main-nav="true"]'
    TEAMCITY_LINK_LOCATOR = '[data-test-title="TeamCity"] [data-test="ring-link"]'
    PROJECTS_LINK_LOCATOR = '[data-test-title="Projects"] [data-test="ring-link"]'

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def root(self) -> Locator:
        return self.page.locator(self.ROOT_LOCATOR)

    @property
    def teamcity_link(self) -> Locator:
        return self.root.locator(self.TEAMCITY_LINK_LOCATOR)

    @property
    def projects_link(self) -> Locator:
        return self.root.locator(self.PROJECTS_LINK_LOCATOR)

    @allure.step("Verify TeamCity header is visible")
    def should_be_visible(self) -> "TeamCityHeader":
        expect(self.root).to_be_visible(timeout=15_000)
        expect(self.teamcity_link).to_be_visible()
        expect(self.projects_link).to_be_visible()
        return self
