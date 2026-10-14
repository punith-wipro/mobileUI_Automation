"""Product list actions used by the assessment flows."""

from selenium.common.exceptions import TimeoutException

from mobile_qa.pages.base_page import BasePage


class InventoryPage(BasePage):
    def is_open(self) -> bool:
        return self.exists("products_heading", timeout=8)

    def add_first_product_to_cart(self) -> None:
        # The sample app renders the available item buttons in list order.
        self.tap("add_to_cart")

    def first_product_is_in_cart(self) -> bool:
        return self.exists("remove_from_cart", timeout=5)

    def sign_out(self) -> None:
        # Wait for the drawer to open before looking for LOGOUT. This matters on
        # iOS because the accessibility tree includes off-screen drawer items.
        self.tap("menu_button")
        try:
            self.tap("logout_button")
        except TimeoutException as exc:
            LOGGER = __import__("logging").getLogger(__name__)
            LOGGER.error("Logout item did not become visible after opening the menu")
            raise exc
