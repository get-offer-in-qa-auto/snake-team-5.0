from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from playwright.sync_api import Page

from src.main.ui.configuration import teamcity_ui_base_url

TPage = TypeVar("TPage", bound="BasePage")


class BasePage(ABC):
    def __init__(self, page: Page) -> None:
        self.page = page
        self.base_url = teamcity_ui_base_url()

    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    def open(self: TPage) -> TPage:
        self.page.goto(f"{self.base_url}{self.path}", wait_until="domcontentloaded")
        return self

    def get_page(self, page_class: type[TPage]) -> TPage:
        return page_class(self.page)
