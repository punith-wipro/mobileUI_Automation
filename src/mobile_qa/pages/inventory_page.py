"""Product list actions used by the assessment flows."""

import logging
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

from mobile_qa.pages.base_page import BasePage
from mobile_qa.pages.login_page import LoginPage

LOGGER = logging.getLogger(__name__)


class InventoryPage(BasePage):
    def is_open(self) -> bool:
        return self.exists("products_heading", timeout=8)

    def add_first_product_to_cart(self) -> None:
        # The sample app renders the available item buttons in list order.
        self.tap("add_to_cart")

    def first_product_is_in_cart(self) -> bool:
        return self.exists("remove_from_cart", timeout=5)

    def _confirm_logout_alert_if_present(self) -> bool:
        """Confirm a native logout prompt, but never accept unrelated alerts."""
        try:
            alert = self.driver.switch_to.alert
            message = (alert.text or "").lower()
            if any(word in message for word in ("logout", "log out", "sign out", "sign-out")):
                LOGGER.info("Confirming native logout alert: %s", message)
                alert.accept()
                return True
        except (NoAlertPresentException, WebDriverException):
            pass
        return False

    def _wait_for_login_screen(self, timeout: float = 8.0) -> bool:
        login_page = LoginPage(self.driver, self.platform, self.timeout)
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.3).until(
                lambda _driver: login_page.is_open(timeout=1)
            )
            return True
        except TimeoutException:
            return False

    def sign_out(self) -> None:
        """Open the navigation drawer, select logout, and verify the login screen.

        Do not use the logout item itself to infer whether the drawer is open:
        XCUITest can expose off-screen React Native drawer elements in the
        accessibility tree. The dedicated close-menu control is the indicator
        that the drawer is actually open.
        """
        # Starting from the inventory screen, open the drawer unless its close
        # control is already visible. This avoids tapping a hidden/off-screen
        # logout element that Appium may still report as displayed on iOS.
        if not self.exists("menu_close", timeout=1):
            self.tap("menu_button")

        logout = self.find("logout_button", timeout=8)
        logout.click()

        if self._confirm_logout_alert_if_present() and self._wait_for_login_screen():
            return
        if self._wait_for_login_screen(timeout=10):
            return

        # One controlled recovery: the first menu action may have missed during
        # a transition. Reopen the drawer only when its close control is absent.
        if not self.exists("menu_close", timeout=1):
            self.tap("menu_button")
        self.find("logout_button", timeout=5).click()
        self._confirm_logout_alert_if_present()
        if not self._wait_for_login_screen(timeout=10):
            raise AssertionError(
                f"Logout action did not return the {self.platform} app to the login screen"
            )
