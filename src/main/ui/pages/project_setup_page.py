import re
from urllib.parse import quote

from playwright.sync_api import Locator, expect

from src.main.ui.pages.base_page import BasePage


class ProjectSetupPage(BasePage):
    def __init__(self, page, project_id: str) -> None:
        super().__init__(page)
        self.project_id = project_id

    @property
    def path(self) -> str:
        encoded_project_id = quote(self.project_id, safe="")
        return f"/projects/create?setup=build&projectId={encoded_project_id}"

    @property
    def project_setup(self) -> Locator:
        return self.page.locator('[data-test="setup-project-page"]')

    def should_be_opened(self) -> "ProjectSetupPage":
        encoded_project_id = re.escape(quote(self.project_id, safe=""))
        expect(self.page).to_have_url(
            re.compile(
                rf".*/projects/create\?.*[?&]projectId={encoded_project_id}(?:&|$)"
            )
        )
        expect(self.project_setup).to_contain_text("New connection")
        return self
