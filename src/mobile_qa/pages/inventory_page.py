"""Product list actions used by the assessment flows."""

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
        self.tap("menu_button")
        self.tap("logout_button")
