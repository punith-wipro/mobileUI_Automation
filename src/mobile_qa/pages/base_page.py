"""Common wait and interaction helpers shared by page objects."""

from __future__ import annotations

import logging
from typing import Any

from selenium.common.exceptions import (
    InvalidSelectorException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait

from mobile_qa.pages.locators import SELECTORS

LOGGER = logging.getLogger(__name__)


class BasePage:
    def __init__(self, driver: Any, platform: str, timeout: int = 12):
        self.driver = driver
        self.platform = platform.lower()
        self.timeout = timeout

    def _candidates(self, name: str):
        selector = SELECTORS[name]
        return selector["shared"] + selector.get(self.platform, [])

    def find(self, name: str, timeout: int | None = None):
        """Return the first visible, enabled match within one explicit wait.

        Appium can return off-screen iOS elements from the accessibility tree. A
        presence-only lookup can therefore select a hidden drawer item (for
        example LOGOUT before the menu is open). Filtering for visibility and
        enabled state avoids interacting with those elements.
        """
        candidates = self._candidates(name)

        def find_first(driver):
            for by, value in candidates:
                try:
                    for element in driver.find_elements(by, value):
                        try:
                            if element.is_displayed() and element.is_enabled():
                                return element
                        except StaleElementReferenceException:
                            continue
                except (NoSuchElementException, InvalidSelectorException):
                    continue
            return False

        try:
            return WebDriverWait(
                self.driver, timeout or self.timeout, poll_frequency=0.3
            ).until(find_first, message=f"Could not find visible '{name}'. Tried: {candidates}")
        except TimeoutException:
            LOGGER.error(
                "Timed out waiting for visible element '%s' on %s; candidates=%s",
                name,
                self.platform,
                candidates,
            )
            raise

    def exists(self, name: str, timeout: int = 3) -> bool:
        try:
            self.find(name, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def tap(self, name: str) -> None:
        element = self.find(name)
        element.click()

    def enter_text(self, name: str, value: str) -> None:
        """Enter text and verify it using attributes supported by the platform.

        UiAutomator2 does not expose the WebDriver ``value`` attribute for
        native Android elements. Android verification therefore uses the
        supported ``text`` attribute; iOS may use either ``value`` or ``text``.
        """
        element = self.find(name)
        element.click()
        element.clear()

        if self.platform == "ios":
            try:
                element.set_value(value)
            except Exception:
                # Fall back to keyboard entry on XCUITest versions where
                # set_value is not supported reliably.
                element.clear()
                element.send_keys(value)
        else:
            element.send_keys(value)

        def read_supported_text():
            """Read supported attributes without masking driver errors."""
            attributes = ("text", "value") if self.platform == "ios" else ("text",)
            for attribute in attributes:
                try:
                    actual = element.get_attribute(attribute)
                except Exception as exc:
                    # Unsupported attributes vary by platform/driver version.
                    LOGGER.debug("Could not read '%s' attribute for '%s': %s",
                                 attribute, name, exc)
                    continue
                if actual not in (None, ""):
                    return actual
            return ""

        def value_matches(_driver):
            actual = read_supported_text()
            if actual == value:
                return True

            # Password fields can expose masked characters instead of their
            # real value. Accept only a mask with the expected character count.
            if name == "password" and actual:
                mask_chars = {"•", "*", "●"}
                return len(actual) == len(value) and set(actual) <= mask_chars
            return False

        try:
            WebDriverWait(self.driver, 3, poll_frequency=0.2).until(value_matches)
        except TimeoutException:
            if self.platform == "ios":
                # Retry keyboard entry once, then verify again.
                LOGGER.warning("Text entry did not verify for '%s'; retrying keyboard entry", name)
                element.click()
                element.clear()
                element.send_keys(value)
                try:
                    WebDriverWait(self.driver, 3, poll_frequency=0.2).until(value_matches)
                    return
                except TimeoutException:
                    pass

            actual = read_supported_text()
            LOGGER.error(
                "Text entry verification failed for '%s' on %s (visible value=%r)",
                name, self.platform, actual,
            )
            raise AssertionError(
                f"Could not verify the expected text in '{name}' on {self.platform}"
            )
