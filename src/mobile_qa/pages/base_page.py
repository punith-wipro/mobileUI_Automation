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
        """Replace a field's contents and verify the text was actually entered.

        Some React Native/iOS text fields can drop characters when `clear()` is
        immediately followed by `send_keys()`. Verify the resulting value and
        fall back to Appium's set-value command rather than submitting a subtly
        corrupted username or password.
        """
        element = self.find(name)
        element.click()
        element.clear()

        def is_empty(_driver):
            try:
                current = element.get_attribute("value")
                return current in (None, "", "Username", "Password")
            except StaleElementReferenceException:
                return False

        if self.platform == "ios":
            try:
                WebDriverWait(self.driver, 2, poll_frequency=0.2).until(is_empty)
            except TimeoutException:
                LOGGER.debug("Field '%s' did not report empty after clear; continuing with set-value", name)
            try:
                element.set_value(value)
            except Exception:
                # Older Appium/XCUITest combinations may not support set_value
                # consistently; normal key entry remains the compatibility path.
                element.clear()
                element.send_keys(value)
        else:
            element.send_keys(value)

        def value_matches(_driver):
            try:
                actual = element.get_attribute("text") or element.get_attribute("value")
                if actual == value:
                    return True
                # Secure iOS fields can return a masked value rather than the
                # password itself, so only validate its length when masked.
                if self.platform == "ios" and name == "password" and actual:
                    return len(actual) == len(value) and set(actual) <= {"•", "*"}
                return False
            except StaleElementReferenceException:
                return False

        try:
            WebDriverWait(self.driver, 3, poll_frequency=0.2).until(value_matches)
        except TimeoutException:
            if self.platform == "ios":
                # Retry once with keyboard entry if set_value did not stick.
                # This fallback is verified too, so we never silently submit a
                # partially entered username (the observed `sndard_user` case).
                LOGGER.warning("set_value did not stick for '%s'; retrying with clear/send_keys", name)
                element.click()
                element.clear()
                element.send_keys(value)
                try:
                    WebDriverWait(self.driver, 3, poll_frequency=0.2).until(value_matches)
                    return
                except TimeoutException:
                    pass
            actual = element.get_attribute("value")
            LOGGER.error("Text entry verification failed for '%s' on %s (actual=%r)", name, self.platform, actual)
            raise AssertionError(f"Could not enter the expected value into '{name}' on {self.platform}")
