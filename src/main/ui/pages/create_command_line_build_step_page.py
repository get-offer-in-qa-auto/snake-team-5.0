import allure
from playwright.sync_api import Locator, Page

from src.main.api.models.create_build_step_request import (
    CreateBuildStepRequest,
)
from src.main.ui.pages.base_page import BasePage
from src.main.ui.routes.teamcity_routes import TeamCityRoutes


class CreateCommandLineBuildStepPage(BasePage):
    COMMAND_LINE_RUNNER_LOCATOR = '[data-test="build-step-selector-item runner"]'
    COMMAND_LINE_RUNNER_NAME = "Command Line"

    STEP_NAME_INPUT_SELECTOR = "#buildStepName"
    SCRIPT_EDITOR_SELECTOR = ".CodeMirror"
    SAVE_BUTTON_SELECTOR = 'input[name="submitButton"][value="Save"]'

    def __init__(self, page: Page, build_configuration_id: str) -> None:
        super().__init__(page)
        self.build_configuration_id = build_configuration_id

    @property
    def path(self) -> str:
        return TeamCityRoutes.create_build_step(self.build_configuration_id)

    @property
    def command_line_runner(self) -> Locator:
        return self.page.locator(self.COMMAND_LINE_RUNNER_LOCATOR).filter(
            has_text=self.COMMAND_LINE_RUNNER_NAME
        )

    @property
    def step_name_input(self) -> Locator:
        return self.page.locator(self.STEP_NAME_INPUT_SELECTOR)

    @property
    def script_editor(self) -> Locator:
        return self.page.locator(self.SCRIPT_EDITOR_SELECTOR).first

    @property
    def save_button(self) -> Locator:
        return self.page.locator(self.SAVE_BUTTON_SELECTOR).first

    @allure.step("Create Command Line build step")
    def create_build_step(
        self, build_step_request: CreateBuildStepRequest
    ) -> "CreateCommandLineBuildStepPage":
        self.command_line_runner.click()
        self.step_name_input.wait_for(state="visible")

        self.step_name_input.fill(build_step_request.name)

        self._fill_script(self._get_script(build_step_request))

        self.save_button.click()
        return self

    def _fill_script(self, script: str) -> None:
        self.script_editor.evaluate(
            """
            (element, value) => {
                element.CodeMirror.setValue(value);
                element.CodeMirror.save();
            }
            """,
            script,
        )

    @staticmethod
    def _get_script(build_step_request: CreateBuildStepRequest) -> str:
        return next(
            property_.value
            for property_ in build_step_request.properties.property
            if property_.name == "script.content"
        )
