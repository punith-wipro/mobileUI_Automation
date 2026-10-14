"""Common wait and interaction helpers shared by page objects."""

from __future__ import annotations

import logging
from typing import Any

from selenium.common.exceptions import InvalidSelectorException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from mobile_qa.pages.locators import SELECTORS

LOGGER = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver: Any, platform: str, timeout: int = 12):
        self.driver = driver
        self.platform = platform
        self.timeout = timeout

    def _candidates(self, name: str):
        selector = SELECTORS[name]
        return selector["shared"] + selector.get(self.platform, [])

    def find(self, name: str, timeout: int | None = None):
        """Try known locator options inside one overall explicit wait."""
        candidates = self._candidates(name)

        def find_first(driver):
            for by, value in candidates:
                try:
                    element = driver.find_element(by, value)
                    if element is not None:
                        return element
                except (NoSuchElementException, InvalidSelectorException):
                    continue
            return False

        try:
            return WebDriverWait(
                self.driver, timeout or self.timeout, poll_frequency=0.4
            ).until(find_first, message=f"Could not find '{name}'. Tried: {candidates}")
        except TimeoutException:
            LOGGER.error("Timed out waiting for element '%s' on %s", name, self.platform)
            raise

    def exists(self, name: str, timeout: int = 3) -> bool:
        try:
            return self.find(name, timeout=timeout).is_displayed()
        except TimeoutException:
            return False

    def tap(self, name: str) -> None:
        element = self.find(name)
        element.click()

    def enter_text(self, name: str, value: str) -> None:
        element = self.find(name)
        element.clear()
        element.send_keys(value)
